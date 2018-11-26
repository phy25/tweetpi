#!/usr/bin/env python
from TweetPI import TweetPI, video
import sys

# Change keys below or in `options.json` before you execute!
# To read options from file, use
import json
with open("options.json", "r") as fp:
   o = json.load(fp)
# To use the static options, use
# o = {"twitter_consumer_key":"...", "twitter_consumer_secret":"...", "twitter_access_token":"...", "twitter_access_secret":"...", "google_key_json":"gapi.json"}
tpi = TweetPI(o)

try:
    # list
    photolist = tpi.get_timeline(username="football", page=1, limit=50)
    print(photolist)
    # download
    photolist.download_all(shell=True)
    # annotate
    photolist.get_annotations()
    for t in photolist.get_list():
        print('{}: {}'.format(t.remote_url, ", ".join([a.description for a in t.annotation.label_annotations])))
    # video
    videopath = video.generate_video(photos=photolist, name='video1.mp4', size='1080x720', shell=True, interval=3)
    print(videopath)
    # annotated video
    videopath2 = video.generate_annotated_video(photos=photolist, name='video2.mp4', size='1080x720', shell=True, font_color='rgb(255,0,0)', font_file='Roboto-Regular.ttf', interval=3, font_size=30)
    print(videopath2)
except Exception as e:
    # Error handling
    print(e, file=sys.stderr)
    sys.exit(2)