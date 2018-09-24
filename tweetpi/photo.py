import os, shutil
import urllib.request

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
    tweet_json = None
    parent = None
    annotation = None
    def __init__(self, tweet_json = None, parent=None):
        self.parent = parent
        self.local_folder = self.parent.local_folder
        if not self.local_folder:
           self. local_folder = ""
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
                except Exception:
                    os.unlink(local_path)
                    raise
            else:
                raise Exception("Image download with wrong HTTP code: "+response.getcode())

    def get_annotation_request(self, force=False):
        if self.annotation and not force:
            return None

        from google.cloud import vision
        return {
            'image':{'source': {'image_uri': self.remote_url}},
            'features': [{'type': vision.enums.Feature.Type.LABEL_DETECTION}]
        }

    def get_annotation(self):
        if self.annotation:
            return self.annotation
        req = self.get_annotation_request()
        if not req:
            return False
        response = self.parent.gvision_client.annotate_image(req)
        self.annotation = response
        return response
