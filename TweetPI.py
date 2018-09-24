#!/usr/bin/env python
"""
Module TweetPI, by @phy25

@deps tweepy
@deps google-cloud-vision
@deps Pillow
"""

import sys, os
import json
import subprocess

import tweepy

from . import Photo, LocalPhoto, PhotoList, __version__ as tweetpi_version

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
        keys = ["twitter_consumer_key", "twitter_consumer_secret", "twitter_access_token", "twitter_access_secret", "google_key_json", "_local_folder"]
        if type(options) == dict:
            for k in keys:
                optional = k.startswith("_")
                key = k.strip("_")
                if key in options:
                    self.__setattr__(key, options[key])
                elif not optional:
                    raise Exception("{} not provided in the options".format(key))

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
        if username == "__home__":
            tweets = self.twitter_api.home_timeline(count=limit, page=page, trim_user=True, tweet_mode="extended")
        else:
            tweets = self.twitter_api.user_timeline(id=username, count=limit, page=page, trim_user=True, tweet_mode="extended")
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

def shell_print_exception(error_name=None):
    import traceback
    if error_name:
        print('=== {} ==='.format(error_name))
    traceback.print_exc(limit=1)

def shell_init_lib(args):
    o = {}

    options_str = "options.json"
    if 'options' in args and args.options:
        options_str = args.options
        if options_str.startswith('"\''):
            options_str = options_str.strip('"\'')
    try:
        try:
            with open(options_str, "r") as fp:
                o = json.load(fp)
        except IOError:
            o = json.loads(options_str)
    except Exception:
        shell_print_exception('Options load failure')
        sys.exit(1)
    tpi = TweetPI(o)
    return tpi

def shell_list(args):
    tpi = shell_init_lib(args)
    try:
        if 'timeline' in args:
            photolist = tpi.get_timeline(username=args.timeline, page=1, limit=args.limit)
        else:
            sys.exit(1)
    except Exception:
        shell_print_exception()
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
    except Exception:
        shell_print_exception()
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
            result = photolist.generate_video(name=args.output, size=size, shell=True, interval=args.interval)
            print(result)
        else:
            sys.exit(1)
    except Exception:
        shell_print_exception()
        sys.exit(2)

def shell_annotate(args):
    tpi = shell_init_lib(args)
    try:
        if 'timeline' in args:
            photolist = tpi.get_timeline(username=args.timeline, page=1, limit=args.limit)
            result = photolist.get_annotations()
        else:
            sys.exit(1)
    except Exception:
        shell_print_exception()
        sys.exit(2)

    for t in result:
        print('{}: {}'.format(t.remote_url, ", ".join([a.description for a in t.annotation.label_annotations])))

def shell_annotatedvideo(args):
    tpi = shell_init_lib(args)
    try:
        if 'timeline' in args:
            size = args.size if args.size else "1280x720"
            sizeParse = size.split('x')
            if not sizeParse[0].isdigit() or not sizeParse[1].isdigit():
                print("Size should be like 1280x720", file=sys.stderr)
                sys.exit(1)
            photolist = tpi.get_timeline(username=args.timeline, page=1, limit=args.limit)
            result = photolist.generate_annotated_video(name=args.output, size=size, shell=True, font_color=args.fontcolor, font_file=args.fontfile, interval=args.interval, font_size=args.fontsize)
            print(result)
        else:
            sys.exit(1)
    except Exception:
        shell_print_exception()
        sys.exit(2)

def main(argv=None):
    import argparse
    if not argv:
        argv = sys.argv[1:]

    argparser = argparse.ArgumentParser(prog="TweetPI.py", description='Tweet Photo Insight: Python library to get photos in Twitter feed, with a video and photo annotations.')
    argparser.add_argument('--version', action='version', version='%(prog)s {}'.format(tweetpi_version))
    subparsers = argparser.add_subparsers(help=".")

    parser_list = subparsers.add_parser('list', help='list images in Twitter feed')
    parser_list.add_argument('--timeline', '-tl', required=True, const="__home__", nargs="?", help="from your home timeline or someone's user timeline")
    parser_list.add_argument('--limit', help="tweets limit")
    parser_list.add_argument('--options', help="Init config for TweetPI library (JSON file path or JSON string)")
    parser_list.set_defaults(func=shell_list)

    parser_download = subparsers.add_parser('download', help='download images in Twitter feed')
    parser_download.add_argument('--timeline', '-tl', required=True, const="__home__", nargs="?", help="from your home timeline or someone's user timeline")
    parser_download.add_argument('--limit', help="tweets limit")
    parser_download.add_argument('--options', help="Init config for TweetPI library (JSON file path or JSON string)")
    parser_download.set_defaults(func=shell_download)

    parser_video = subparsers.add_parser('video', help='generate a video from images in Twitter feed')
    parser_video.add_argument('--timeline', '-tl', required=True, const="__home__", nargs="?", help="from your home timeline or someone's user timeline")
    parser_video.add_argument('--limit', help="tweets limit")
    parser_video.add_argument('--options', help="Init config for TweetPI library (JSON file path or JSON string)")
    parser_video.add_argument('--size', help="Video size, default: 1280x720")
    parser_video.add_argument('--output', help="Output filename, default: timeline-id.mp4")
    parser_video.add_argument('--interval', help="Seconds per image, default: 3", type=int, default=3)
    parser_video.set_defaults(func=shell_video)

    parser_annotate = subparsers.add_parser('annotate', help='get annotations of images in Twitter feed')
    parser_annotate.add_argument('--timeline', '-tl', required=True, const="__home__", nargs="?", help="from your home timeline or someone's user timeline")
    parser_annotate.add_argument('--limit', help="tweets limit")
    parser_annotate.add_argument('--options', help="Init config for TweetPI library (JSON file path or JSON string)")
    parser_annotate.set_defaults(func=shell_annotate)

    parser_annotatedvideo = subparsers.add_parser('annotatedvideo', help='get annotated video of photos in Twitter feed')
    parser_annotatedvideo.add_argument('--timeline', '-tl', required=True, const="__home__", nargs="?", help="from your home timeline or someone's user timeline")
    parser_annotatedvideo.add_argument('--limit', help="tweets limit")
    parser_annotatedvideo.add_argument('--options', help="Init config for TweetPI library (JSON file path or JSON string)")
    parser_annotatedvideo.add_argument('--size', help="Video size, default: 1280x720")
    parser_annotatedvideo.add_argument('--output', help="Output filename, default: timeline-id.mp4")
    parser_annotatedvideo.add_argument('--interval', help="Seconds per image, default: 3", type=int, default=3)
    parser_annotatedvideo.add_argument('--fontfile', help="Optional font file path (should be ttf file)", default="Roboto-Regular.ttf")
    parser_annotatedvideo.add_argument('--fontcolor', help="Optional font color, default: rgb(255, 0, 0)", default="rgb(255, 0, 0)")
    parser_annotatedvideo.add_argument('--fontsize', help="Optional font size, default: 40", type=int, default=40)
    parser_annotatedvideo.set_defaults(func=shell_annotatedvideo)

    if len(argv) == 0:
        argparser.print_help(sys.stderr)
        sys.exit(1)

    args = argparser.parse_args(args=argv)
    if 'func' in args:
        args.func(args)

if __name__ == "__main__":
    main()