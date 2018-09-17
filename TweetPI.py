#!/usr/bin/env python
"""
Module TweetPI, by @phy25

@deps tweepy
"""

import sys
import tweepy
import json
import collections

class TweetPI:
    twitter_consumer_key = None
    twitter_consumer_secret = None
    twitter_access_token = None
    twitter_access_secret = None
    def __init__(self, options):
        keys = ["twitter_consumer_key", "twitter_consumer_secret", "twitter_access_token", "twitter_access_secret"]
        if type(options) == dict:
            for k in keys:
                if k in options:
                    self.__setattr__(k, options[k])

    def get_timeline(self, username, page, limit):
        auth = tweepy.OAuthHandler(self.twitter_consumer_key, self.twitter_consumer_secret)
        auth.set_access_token(self.twitter_access_token, self.twitter_access_secret)

        api = tweepy.API(auth)

        tweets = api.user_timeline(id=username, count=limit, page=page)
        photos = []
        for tweet in tweets:
            try:
                for m in tweet.extended_entities['media']:
                    if m['type'] == 'photo':
                        photos.append(Photo(local_folder=None, tweet_json=m))
            except AttributeError:
                pass

        return PhotoList(list=photos, source="timeline")

# Thanks to https://stackoverflow.com/a/2704866/4073795
class Photo(collections.Mapping):
    '''
    Inmutable, hashable
    '''
    local_folder = None
    remote_url = ""
    local_path = None
    tweet_json = None
    def __init__(self, local_folder, tweet_json = None):
        self.local_folder = local_folder
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

    def download(self):
        return False

class PhotoList:
    l = list()
    source = ""
    def __init__(self, list, source=""):
        refined_list = [o for o in set(list)]
        # unique things
        self.l = refined_list
        if source:
            self.source = source

    def download_all(self, shell=False):
        if shell:
            print("{} items to be downloaded".format(len(self.l)))
        for p in self.l:
            res = p.download()
            if shell:
                if res:
                    print("Downloaded: {}".format(p.remote_url))
                else:
                    print("Failed: {}".format(p.remote_url))

    def generate_video(self, name, output_format):
        fullpath = ""
        return fullpath

    def get_annotations(self):
        return list()

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