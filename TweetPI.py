#!/usr/bin/env python
# TweetPI library by Phy25

class TweetPI:
    def __init__(self, options):
        pass

    def get_timeline(self, username, page, limit):
        return PhotoList(l=list(), source="timeline")

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
