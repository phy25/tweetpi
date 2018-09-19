#!/usr/bin/env python
from TweetPI import TweetPI
import sys

tpi = TweetPI({"twitter_consumer_key":"...", "twitter_consumer_secret":"...", "twitter_access_token":"...", "twitter_access_secret":"...", "google_key_json":"gapi.json"})
try:
    photolist = tpi.get_timeline(username="POTUS", page=1, limit=50)
except Exception as e:
    print(e, file=sys.stderr)
    sys.exit(2)

print(photolist.get_list())