#!/usr/bin/env python
"""
Module TweetPI, by @phy25
"""

import sys

class TweetPI:
    def __init__(self, options):
        pass

    def get_timeline(self, username, page, limit):
        return PhotoList(list=list(), source="timeline")

class Photo:
    local_folder = None
    remote_url = ""
    local_path = None
    def __init__(self, local_folder, tweet_json = None):
        self.local_folder = local_folder
        if tweet_json:
            self.remote_url = tweet_json

    def download(self):
        return False

class PhotoList:
    l = list()
    source = ""
    def __init__(self, list, source=""):
        self.l = list
        if source:
            self.source = source

    def download_all(self):
        for p in self.l:
            p.download()

    def generate_video(self, name, output_format):
        fullpath = ""
        return fullpath

    def get_annotations(self):
        return list()

    def get_list(self):
        return self.l

def shell_list(args):
    tpi = TweetPI({})
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
    tpi = TweetPI({})
    try:
        if 'timeline' in args:
            photolist = tpi.get_timeline(username=args.timeline, page=1, limit=args.limit)
            photolist.download_all()
        else:
            sys.exit(1)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(2)

def shell_video(args):
    tpi = TweetPI({})
    try:
        if 'timeline' in args:
            photolist = tpi.get_timeline(username=args.timeline, page=1, limit=args.limit)
            result = photolist.generate_video(name=None, output_format=None)
            print(result)
        else:
            sys.exit(1)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(2)

def shell_annotate(args):
    tpi = TweetPI({})
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
        print(t)

def main(argv=None):
    import argparse
    if not argv:
        argv = sys.argv[1:]

    argparser = argparse.ArgumentParser(prog="TweetPI.py", description='Tweet Photo Insight: Python API to get photos in Twitter feed, with a video and photo annotations.')
    subparsers = argparser.add_subparsers(help=".")

    parser_list = subparsers.add_parser('list', help='list images in Twitter feed')
    parser_list.add_argument('--timeline', required=True, help="from someone's timeline")
    parser_list.add_argument('--limit', help="tweets limit")
    parser_list.set_defaults(func=shell_list)

    parser_download = subparsers.add_parser('download', help='download images in Twitter feed')
    parser_download.add_argument('--timeline', required=True, help="from someone's timeline")
    parser_download.add_argument('--limit', help="tweets limit")
    parser_download.set_defaults(func=shell_download)

    parser_video = subparsers.add_parser('video', help='generate a video from images in Twitter feed')
    parser_video.add_argument('--timeline', required=True, help="from someone's timeline")
    parser_video.add_argument('--limit', help="tweets limit")
    parser_video.set_defaults(func=shell_video)

    parser_annotate = subparsers.add_parser('annotate', help='get annotations of images in Twitter feed')
    parser_annotate.add_argument('--timeline', required=True, help="from someone's timeline")
    parser_annotate.add_argument('--limit', help="tweets limit")
    parser_annotate.set_defaults(func=shell_annotate)

    if len(argv) == 0:
        argparser.print_help(sys.stderr)
        sys.exit(1)

    args = argparser.parse_args(args=argv)
    if 'func' in args:
        args.func(args)

if __name__ == "__main__":
    main()