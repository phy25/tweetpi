#!/usr/bin/env python
"""
Module TweetPI, by @phy25

@deps tweepy
@deps google-cloud-vision
@deps Pillow
"""

import sys, os
import json
import collections
import subprocess

import urllib.request
import shutil

import tweepy
from PIL import Image
import tempfile

class TweetPI:
    twitter_consumer_key = None
    twitter_consumer_secret = None
    twitter_access_token = None
    twitter_access_secret = None
    google_key_json = None
    local_folder = None
    twitter_api = None
    gvision_client = None
    def __init__(self, options):
        keys = ["twitter_consumer_key", "twitter_consumer_secret", "twitter_access_token", "twitter_access_secret", "google_key_json", "local_folder"]
        if type(options) == dict:
            for k in keys:
                if k in options:
                    self.__setattr__(k, options[k])

        # Init Twitter API
        tauth = tweepy.OAuthHandler(self.twitter_consumer_key, self.twitter_consumer_secret)
        tauth.set_access_token(self.twitter_access_token, self.twitter_access_secret)
        self.twitter_api = tweepy.API(tauth)

        # Init Google Vision API
        from google.oauth2 import service_account
        credentials = service_account.Credentials.from_service_account_file(self.google_key_json)
        #scoped_credentials = credentials.with_scopes(['https://www.googleapis.com/auth/cloud-platform'])
        from google.cloud import vision
        self.gvision_client = vision.ImageAnnotatorClient(credentials=credentials)

    def get_timeline(self, username, page, limit, order_latest=False):
        tweets = self.twitter_api.user_timeline(id=username, count=limit, page=page)
        photos = []
        if not order_latest:
            tweets.reverse()
        for tweet in tweets:
            try:
                for m in tweet.extended_entities['media']:
                    if m['type'] == 'photo':
                        photos.append(Photo(parent=self, tweet_json=m))
            except AttributeError:
                pass

        return PhotoList(list=photos, source="timeline-"+username, parent=self)

# Thanks to https://stackoverflow.com/a/2704866/4073795
class Photo(collections.Mapping):
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

    def get_annotation(self):
        if self.annotation:
            return self.annotation
        from google.cloud import vision
        response = self.parent.gvision_client.label_detection(
            {'source': {'image_uri': self.remote_url}}
        )
        self.annotation = response.label_annotations
        return response.label_annotations

class LocalPhoto:
    local_path = ""
    PILim = None
    def __init__(self, local_path):
        self.local_path = local_path

    def resize(self, width=1280, height=720, fill_color=(0, 0, 0)):
        if not self.PILim:
            self.PILim = Image.open(self.local_path)
        x, y = self.PILim.size
        final_x, final_y = width, height
        if x/y > width/height:
            # too long
            final_y = round(y*(width/x))
        else:
            final_x = round(x*(height/y))
        resized_im = self.PILim.resize((final_x, final_y), Image.LANCZOS)
        new_im = Image.new('RGB', (width, height), fill_color)
        new_im.paste(resized_im, (round((width - final_x) / 2), round((height - final_y) / 2)))
        resized_im = None
        return new_im

    def resize_to_temp(self, width=1280, height=720, fill_color=(0, 0, 0, 0)):
        im = self.resize(width=width, height=height, fill_color=fill_color)
        name = os.path.join(tempfile.gettempdir(), os.path.basename(self.local_path))
        im.save(name)
        return name

class PhotoList:
    l = list()
    source = "unknown"
    parent = None
    def __init__(self, list, source="", parent=None):
        refined_list = [o for o in set(list)]
        # unique things
        self.l = refined_list
        self.parent = parent
        if source:
            self.source = source

    def download_all(self, shell=False, force=True):
        completed = 0
        successful = True
        total = len(self.l)
        if shell:
            print("{} items to be downloaded".format(total))
        for p in self.l:
            completed += 1
            try:
                res = p.download(force=force)
                if shell:
                    print("({}/{}) Downloaded: {}".format(completed, total, p.remote_url))
            except Exception:
                print("({}/{}) Failed: {}".format(completed, total, p.remote_url))
                successful = False
        return successful

    def generate_video(self, name=None, size="1280x720", shell=False):
        if not name:
            name = self.source+".mp4"
        fullpath = os.path.abspath(name)
        d = self.download_all(shell=shell, force=False)
        if not d:
            return False
        sizes = size.split('x')
        files = []
        for p in self.l:
            lp = LocalPhoto(local_path=p.local_path)
            temp_path = lp.resize_to_temp(width=int(sizes[0]), height=int(sizes[1]))
            files.append(temp_path)

        # generate concat files
        concat_path = os.path.join(tempfile.gettempdir(), name+".txt")
        with open(concat_path, "w") as concat_file:
            for f in files:
                concat_file.write("file '{}'\n".format(f))
                concat_file.write("duration 3\n")
        # run
        try:
            proc = subprocess.run(["ffmpeg", "-f", "concat", "-safe", "0", "-i", concat_path, "-pix_fmt", "yuv420p", "-video_size", size, "-y", name], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            print(e.stderr.decode('utf-8'))
            raise
        finally:
            # unlink temp files
            os.unlink(concat_path)
            for f in files:
                os.unlink(f)

        return fullpath

    def fetch_annotations(self):
        for p in self.l:
            p.get_annotation()

    def get_annotations(self):
        self.fetch_annotations()
        return self.l

    def get_list(self):
        return self.l

def shell_init_lib(args):
    o = {}
    try:
        if 'options' in args:
            o = json.loads(args.options)
    except Exception:
        raise
    tpi = TweetPI(o)
    return tpi

def shell_list(args):
    tpi = shell_init_lib(args)
    try:
        if 'timeline' in args:
            photolist = tpi.get_timeline(username=args.timeline, page=1, limit=args.limit)
        else:
            sys.exit(1)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(2)

    for t in photolist.get_list():
        print(t)

def shell_download(args):
    tpi = shell_init_lib(args)
    try:
        if 'timeline' in args:
            photolist = tpi.get_timeline(username=args.timeline, page=1, limit=args.limit)
            photolist.download_all(shell=True)
        else:
            sys.exit(1)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(2)

def shell_video(args):
    tpi = shell_init_lib(args)
    try:
        if 'timeline' in args:
            size = args.size if args.size else "1280x720"
            sizeParse = size.split('x')
            if not sizeParse[0].isdigit() or not sizeParse[1].isdigit():
                print("Size should be like 1280x720", file=sys.stderr)
                sys.exit(1)
            photolist = tpi.get_timeline(username=args.timeline, page=1, limit=args.limit)
            result = photolist.generate_video(name=args.output, size=size, shell=True)
            print(result)
        else:
            sys.exit(1)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(2)

def shell_annotate(args):
    tpi = shell_init_lib(args)
    try:
        if 'timeline' in args:
            photolist = tpi.get_timeline(username=args.timeline, page=1, limit=args.limit)
            result = photolist.get_annotations()
        else:
            sys.exit(1)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(2)

    for t in result:
        print('{}: {}'.format(t.remote_url, ", ".join([a.description for a in t.annotation])))

def main(argv=None):
    import argparse
    if not argv:
        argv = sys.argv[1:]

    argparser = argparse.ArgumentParser(prog="TweetPI.py", description='Tweet Photo Insight: Python API to get photos in Twitter feed, with a video and photo annotations.')
    subparsers = argparser.add_subparsers(help=".")

    parser_list = subparsers.add_parser('list', help='list images in Twitter feed')
    parser_list.add_argument('--timeline', required=True, help="from someone's timeline")
    parser_list.add_argument('--limit', help="tweets limit")
    parser_list.add_argument('--options', help="Init config for TweetPI library in JSON format")
    parser_list.set_defaults(func=shell_list)

    parser_download = subparsers.add_parser('download', help='download images in Twitter feed')
    parser_download.add_argument('--timeline', required=True, help="from someone's timeline")
    parser_download.add_argument('--limit', help="tweets limit")
    parser_download.add_argument('--options', help="Init config for TweetPI library in JSON format")
    parser_download.set_defaults(func=shell_download)

    parser_video = subparsers.add_parser('video', help='generate a video from images in Twitter feed')
    parser_video.add_argument('--timeline', required=True, help="from someone's timeline")
    parser_video.add_argument('--limit', help="tweets limit")
    parser_video.add_argument('--options', help="Init config for TweetPI library in JSON format")
    parser_video.add_argument('--size', help="Video size, default: 1280x720")
    parser_video.add_argument('--output', help="Output filename, default: timeline-id.mp4")
    parser_video.set_defaults(func=shell_video)

    parser_annotate = subparsers.add_parser('annotate', help='get annotations of images in Twitter feed')
    parser_annotate.add_argument('--timeline', required=True, help="from someone's timeline")
    parser_annotate.add_argument('--limit', help="tweets limit")
    parser_annotate.add_argument('--options', help="Init config for TweetPI library in JSON format")
    parser_annotate.set_defaults(func=shell_annotate)

    '''
    # Reserved for future
    parser_annotatedvideo = subparsers.add_parser('annotatedvideo', help='get annotated video of photos in Twitter feed')
    parser_annotatedvideo.add_argument('--timeline', required=True, help="from someone's timeline")
    parser_annotatedvideo.add_argument('--limit', help="tweets limit")
    parser_annotatedvideo.add_argument('--options', help="Init config for TweetPI library in JSON format")
    parser_annotatedvideo.add_argument('--size', help="Video size, default: 1280x720")
    parser_annotatedvideo.add_argument('--output', help="Output filename, default: timeline-id.mp4")
    parser_annotatedvideo.set_defaults(func=shell_annotatedvideo)
    '''

    if len(argv) == 0:
        argparser.print_help(sys.stderr)
        sys.exit(1)

    args = argparser.parse_args(args=argv)
    if 'func' in args:
        args.func(args)

if __name__ == "__main__":
    main()