"""
Tweet Photo Insight: Python library to get photos in Twitter feed, with a video and photo annotations.

@author Phy25

@deps tweepy
@deps google-cloud-vision
@deps Pillow
"""
__version__ = '1.1'
__author__ = 'Phy25'
__license__ = 'MIT'

from tweetpi.photo import Photo, PhotoList, ImOp
from tweetpi.tweetpi import TweetPI
from tweetpi.shell import main
from tweetpi import video, database