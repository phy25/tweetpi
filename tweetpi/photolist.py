import os, sys
import tempfile
import subprocess
from tweetpi import LocalPhoto

class PhotoList:
    photos = list()
    source = "unknown"
    parent = None
    def __init__(self, list, source="", parent=None):
        refined_list = [o for o in set(list)]
        # unique things
        self.photos = refined_list
        self.parent = parent
        if source:
            self.source = source

    def download_all(self, shell=False, force=True):
        completed = 0
        successful = True
        total = len(self.photos)
        if shell:
            print("{} items to be downloaded".format(total), file=sys.stderr)
        for p in self.photos:
            completed += 1
            try:
                res = p.download(force=force)
                if shell:
                    print("({}/{}) Downloaded: {}".format(completed, total, p.remote_url), file=sys.stderr)
            except Exception:
                print("({}/{}) Failed: {}".format(completed, total, p.remote_url), file=sys.stderr)
                successful = False
        return successful

    def generate_video(self, name=None, size="1280x720", shell=False, interval=3):
        if not name:
            name = self.source+".mp4"
        fullpath = os.path.abspath(name)
        d = self.download_all(shell=shell, force=False)
        if not d:
            return False
        sizes = size.split('x')
        files = []
        for p in self.photos:
            lp = LocalPhoto(local_path=p.local_path)
            temp_path = lp.resize_to_temp(width=int(sizes[0]), height=int(sizes[1]))
            files.append(temp_path)

        # generate concat files
        # https://trac.ffmpeg.org/wiki/Slideshow
        concat_path = os.path.join(tempfile.gettempdir(), name+".txt")
        with open(concat_path, "w") as concat_file:
            for f in files:
                concat_file.write("file '{}'\n".format(f))
                concat_file.write("duration {}\n".format(interval))
        # run
        try:
            proc = subprocess.run(["ffmpeg", "-f", "concat", "-safe", "0", "-i", concat_path, "-pix_fmt", "yuv420p", "-video_size", size, "-y", "-stats", "-loglevel", "error", name], check=True, stdout=subprocess.PIPE)
        except subprocess.CalledProcessError:
            raise
        finally:
            # unlink temp files
            os.unlink(concat_path)
            for f in files:
                os.unlink(f)

        return fullpath

    def generate_annotated_video(self, name=None, size="1280x720", shell=False, interval=3, font_file="Roboto-Regular.ttf", font_color="rgb(255, 0, 0)", font_size=40):
        if not name:
            name = self.source+".mp4"
        fullpath = os.path.abspath(name)
        d = self.download_all(shell=shell, force=False)
        if not d:
            return False

        self.fetch_annotations()
        sizes = size.split('x')
        files = []
        from PIL import ImageDraw, ImageFont
        from math import floor
        import textwrap
        font = ImageFont.truetype(font_file, size=font_size)

        for p in self.photos:
            lp = LocalPhoto(local_path=p.local_path)
            im = lp.resize(width=int(sizes[0]), height=int(sizes[1]))

            # Draw text
            # https://stackoverflow.com/a/7698300/4073795
            #Roboto-Regular.ttf
            draw = ImageDraw.Draw(im)
            message = ", ".join([l.description for l in p.annotation.label_annotations])
            lines = textwrap.wrap(message, width=floor((int(sizes[0])-4*font_size)/font_size)*2)
            font_linesize = font.getsize(lines[0])
            x_text = (int(sizes[0]) -font_linesize[0]) / 2
            y_text = max(0, int(sizes[1])-font_size*(len(lines)+1))
            for line in lines:
                draw.text((x_text, y_text), line, fill=font_color, font=font)
                y_text += font_linesize[1]
            # save the edited image
            temp_path = os.path.join(tempfile.gettempdir(), os.path.basename(p.local_path))
            im.save(temp_path)
            files.append(temp_path)

        # generate concat files
        concat_path = os.path.join(tempfile.gettempdir(), name+".txt")
        with open(concat_path, "w") as concat_file:
            for f in files:
                concat_file.write("file '{}'\n".format(f))
                concat_file.write("duration {}\n".format(interval))
        # run
        try:
            proc = subprocess.run(["ffmpeg", "-f", "concat", "-safe", "0", "-i", concat_path, "-pix_fmt", "yuv420p", "-video_size", size, "-y", "-stats", "-loglevel", "error", name], check=True, stdout=subprocess.PIPE)
        except subprocess.CalledProcessError:
            raise
        finally:
            # unlink temp files
            os.unlink(concat_path)
            for f in files:
                os.unlink(f)

        return fullpath


    def fetch_annotations(self):
        # figure out what shoule be requested
        photolist = []
        requests = []
        for p in self.photos:
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
        return self.photos

    def get_list(self):
        return self.photos