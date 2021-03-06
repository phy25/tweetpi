import tweepy

from tweetpi import Photo, PhotoList, database
import os

class TweetPI:
    twitter_consumer_key = None
    twitter_consumer_secret = None
    twitter_access_token = None
    twitter_access_secret = None
    google_key_json = None
    local_folder = None
    conf_folder = None
    twitter_api = None
    gvision_client = None
    db_enable = False
    db_uri = ""
    db_client = None


    def __init__(self, options):
        keys = ["twitter_consumer_key", "twitter_consumer_secret", "twitter_access_token", "twitter_access_secret", "google_key_json", "_local_folder", "_conf_folder", "_db_enable", "_db_uri"]
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
        credentials = service_account.Credentials.from_service_account_file(os.path.join(self.conf_folder, self.google_key_json))
        # scoped_credentials = credentials.with_scopes(['https://www.googleapis.com/auth/cloud-platform'])
        from google.cloud import vision
        self.gvision_client = vision.ImageAnnotatorClient(credentials=credentials)

        # Init Database
        if self.db_enable:
            self.db_client = database.init(self.db_uri)
        else:
            self.db_client = database.NoDBClient(debug=False)

    def get_timeline(self, username, page, limit, order_latest=False):
        self.db_client.log(type="get_timeline", keyword=username, key=username, text="", metadata={"page":page, "limit":limit})
        if username == "__home__":
            tweets = self.twitter_api.home_timeline(
                count=limit, page=page, trim_user=True, tweet_mode="extended")
        else:
            tweets = self.twitter_api.user_timeline(
                id=username, count=limit, page=page, trim_user=True, tweet_mode="extended")
        photos = []
        if not order_latest:
            tweets.reverse()
        for tweet in tweets:
            try:
                for m in tweet.extended_entities['media']:
                    if m['type'] == 'photo':
                        m['text'] = tweet.full_text
                        photos.append(Photo(parent=self, tweet_json=m))
            except AttributeError:
                pass

        return PhotoList(photos=photos, source="timeline-"+username, parent=self)
