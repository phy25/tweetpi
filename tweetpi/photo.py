import os, sys
import shutil
import urllib.request
import tempfile
import subprocess
from google.cloud import vision
from PIL import Image, ImageDraw
from math import floor
import textwrap
import uuid

try:
    # Python 3
    from collections.abc import Mapping
except ImportError:
    # Python 2.7
    from collections import Mapping


# Thanks to https://stackoverflow.com/a/2704866/4073795
class Photo(Mapping):
    '''
    Inmutable, hashable
    '''
    local_folder = None
    remote_url = ""
    local_path = None
    name = None
    tweet_json = None
    parent = None
    annotation = None
    def __init__(self, tweet_json=None, parent=None):
        self.parent = parent
        self.local_folder = self.parent.local_folder
        if not self.local_folder:
           self.local_folder = ""
        if tweet_json:
            if 'id' in tweet_json:
                self.tweet_json = tweet_json
                self.remote_url = tweet_json['media_url_https']
            else:
                raise Exception('Media json should contain id')

    def __iter__(self):
        return iter(self.tweet_json)

    def __len__(self):
        return len(self.tweet_json)

    def __getitem__(self, key):
        return self.tweet_json[key]

    def __hash__(self):
        return self.tweet_json['id']

    def __str__(self):
        return self.tweet_json.__str__()

    def download(self, force=False):
        if not self.remote_url:
            raise Exception("No download URL specified")
        local_path = os.path.join(self.local_folder, os.path.basename(self.remote_url))
        if os.path.isfile(local_path) and not force:
            self.local_path = local_path
            return
        # https://stackoverflow.com/a/7244263/4073795
        with urllib.request.urlopen(self.remote_url) as response, open(local_path, 'wb') as out_file:
            if response.getcode() == 200:
                try:
                    shutil.copyfileobj(response, out_file)
                    self.local_path = local_path
                    self.name = os.path.basename(local_path)
                except Exception:
                    os.unlink(local_path)
                    raise
            else:
                raise Exception("Image download with wrong HTTP code: "+response.getcode())

    def get_im(self):
        if not self.local_path:
            self.download()

        # https://stackoverflow.com/a/44231784/4073795
        return Image.open(self.local_path)

    def get_annotation_request(self, force=False):
        if self.annotation and not force:
            return None

        return {
            'image':{'source': {'image_uri': self.remote_url}},
            'features': [{'type': vision.enums.Feature.Type.LABEL_DETECTION}]
        }

    def get_annotation(self):
        if not self.annotation:
            req = self.get_annotation_request()
            if not req:
                return False

            self.annotation = self.parent.gvision_client.annotate_image(req)

        return self.annotation

class PhotoList(list):
    source = "unknown"
    parent = None
    def __init__(self, photos, source="", parent=None):
        photos = [o for o in set(photos)]
        # unifiy photos
        self.parent = parent
        if source:
            self.source = source
        super(PhotoList, self).__init__(photos)

    def download_all(self, shell=False, force=True):
        completed = 0
        successful = True
        total = len(self)
        if shell:
            print("{} items to be downloaded".format(total), file=sys.stderr)
        for p in self:
            completed += 1
            try:
                p.download(force=force)
                if shell:
                    print("({}/{}) Downloaded: {}".format(completed, total, p.remote_url), file=sys.stderr)
            except Exception:
                print("({}/{}) Failed: {}".format(completed, total, p.remote_url), file=sys.stderr)
                successful = False
        return successful

    def get_list(self):
        """@deprecated"""
        return self

    def fetch_annotations(self):
        # figure out what shoule be requested
        photolist = []
        requests = []
        for p in self:
            r = p.get_annotation_request()
            if r:
                photolist.append(p)
                requests.append(r)

        # request
        resp = self.parent.gvision_client.batch_annotate_images(requests)
        assert len(resp.responses) == len(photolist)
        for r in resp.responses:
            photolist.pop(0).annotation = r

    def get_annotations(self):
        self.fetch_annotations()
        return self.get_list()

class ImOp():
    """Chainable local image operation"""
    im = None

    def __init__(self, im):
        if isinstance(im, Photo):
            im = im.get_im()
        if not isinstance(im, Image):
            raise TypeError("ImOp should have a PLI.Image")
        self.im = im

    def resize(self, width=1280, height=720, fill_color=(0, 0, 0)):
        # https://stackoverflow.com/a/44231784/4073795
        x, y = self.im.size
        final_x, final_y = width, height
        if x == final_x and y == final_y:
            pass
        else:
            if x/y > width/height:
                # too long
                final_y = round(y*(width/x))
            else:
                final_x = round(x*(height/y))
            resized_im = self.im.resize((final_x, final_y), Image.LANCZOS)
            self.im = Image.new('RGB', (width, height), fill_color)
            self.im.paste(resized_im, (round((width - final_x) / 2), round((height - final_y) / 2)))
            resized_im = None
        return self

    def annotate(self, message, font, font_size=40, font_color="rgb(255, 0, 0)"):
        width, height = self.im.size

        # Draw text: https://stackoverflow.com/a/7698300/4073795
        draw = ImageDraw.Draw(self.im)
        lines = textwrap.wrap(message, width=floor((width-4*font_size)/font_size)*2)
        font_linesize = font.getsize(lines[0])
        x_text = (width - font_linesize[0]) / 2
        y_text = max(0, height-font_size*(len(lines)+1))
        for line in lines:
            draw.text((x_text, y_text), line, fill=font_color, font=font)
            y_text += font_linesize[1]

        return self

    def save_as_temp(self, filename=None):
        if not filename:
            filename = uuid.uuid4()+".jpg"
        name = os.path.join(tempfile.gettempdir(), filename)
        self.im.save(name)
        return name
