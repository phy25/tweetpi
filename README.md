# TweetPI: Tweet Photo Insight

Python library to get photos in Twitter feed, with a video and photo annotations. Part of EC601 as Mini Project 1.

![DEMO of annotated video](README_demo.gif)

This is very experimental, and thus the API may change at any time.

Agile Scrum board (with sprints): https://github.com/phy25/tweetpi/projects/1

## Contents

- [Breaking changes](#breaking-changes)
- [Design](#design)
- [Install](#install)
- [Use within shell](#use-within-shell)
- [Use as a library](#use-as-a-library)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Breaking changes

### v0.2

- `PhotoList.l` is changed to `PhotoList.photos`. Before it is encourged to use `PhotoList.get_list()`, but since we want to be more pythonic, `PhotoList.photos` will be supported in the future. If it is necessary to use function getter/setter, `PhotoList.photos` will be kept available.

## Design

```
 +-------+ .get_timeline() +---------+      .photos       +-----------+
 |TweetPI+---------------->+PhotoList+------------------->+  Photos   |
 +-------+                 +---------+                    +-----------+
                                |                               |
                                | .download_all()               | .download()
                                |                               |
                                |                               |
                                | .generate_video()             | LocalPhoto.resize()
                                |                               |
                                |                               |
                                | .get_annotations()            | .get_annotation()
                                |                               |
                                |                               |
                                | .generate_annotated_video()   | LocalPhoto.add_annotation()
                                |                               |
                                +                               +
```

\* `LocalPhoto` should be redesigned as `PhotoEditor(Photo)`. Currently `LocalPhoto` is intended to be a "private" class.

## Install

This library is currently tested within Ubuntu. You need to install Python (tested with Python 3.5 now), ffmpeg, and respective Python library.

```shell
$ git clone https://github.com/phy25/tweetpi.git
$ cd tweetpi
$ sudo apt-get install ffmpeg
$ pip install -r requirements.txt --user
```

Windows usage: not tested yet (does not work indeed), but it's more convenient if you are using Windows 10 + [WSL](https://docs.microsoft.com/en-us/windows/wsl/install-win10).

## Obtain the service token

You need to prepare your Twitter API token and Google Cloud Vision API service account JSON.

### Twitter

Go to https://developer.twitter.com/en/apply/user and apply (Though this is harder than before :-( ). If you (already) have one, go to https://apps.twitter.com/ to obtain the following information, and fill them into options with `TweetPI()`. Note that we need read-only or broader access.

- Consumer Key (API Key) -> `options.twitter_consumer_key`
- Consumer Secret (API Secret) -> `options.twitter_consumer_secret`
- Access Token -> `options.twitter_access_token`
- Access Token Secret -> `options.twitter_access_secret`

### Google

Follow https://cloud.google.com/vision/docs/quickstart#set_up_your_project (only "Set up your project" part) to set up your project and [enable "Cloud Vision API"](https://console.cloud.google.com/flows/enableapi?apiid=vision.googleapis.com&redirect=https://console.cloud.google.com&_ga=2.107360394.-90131543.1534915532). You don't need to create a Cloud Storage bucket for using TweetPI.

Then you need to obtain a service account key (in JSON). If you don't have one, go to https://console.cloud.google.com/apis/credentials/serviceaccountkey, follow the guide (you don't need to choose a role for using TweetPI), choose JSON, and download the `.json` file.

Currently TweetPI only supports JSON service account key. You can point to the JSON by filling `options.google_key_json` (relative to working directory, e.g. `gapi.json`).

## Use within shell

This library provides a shell access as follows.

```
usage: TweetPI.py [-h] {list,download,video,annotate,annotatedvideo} ...

Tweet Photo Insight: Python library to get photos in Twitter feed, with a
video and photo annotations.

positional arguments:
  {list,download,video,annotate,annotatedvideo}
                        .
    list                list images in Twitter feed
    download            download images in Twitter feed
    video               generate a video from images in Twitter feed
    annotate            get annotations of images in Twitter feed
    annotatedvideo      get annotated video of photos in Twitter feed

optional arguments:
  -h, --help            show this help message and exit
  ```

You can always use `--help` to get help information for a specific function. For example,

```shell
$ TweetPI.py list --help
usage: TweetPI.py list [-h] --timeline [TIMELINE] [--limit LIMIT]
                       [--options OPTIONS]

optional arguments:
  -h, --help            show this help message and exit
  --timeline [TIMELINE]
                        from your home timeline or someone's user timeline
  --limit LIMIT         tweets limit
  --options OPTIONS     Init config for TweetPI library in JSON format
```

For example, I can get an annotated video like the demo above like:

```shell
$ TweetPI.py annotatedvideo --timeline POTUS --limit 50 --options '{"twitter_consumer_key":"...", "twitter_consumer_secret":"...", "twitter_access_token":"...", "twitter_access_secret":"...", "google_key_json":"gapi.json"}'
7 items to be downloaded
(1/7) Downloaded: https://pbs.twimg.com/media/DnYrE1pX4AAMBbh.jpg
(2/7) Downloaded: https://pbs.twimg.com/media/DnUHepUX0AEZU1u.jpg
(3/7) Downloaded: https://pbs.twimg.com/media/DnaAWfsVsAAEuXG.jpg
(4/7) Downloaded: https://pbs.twimg.com/media/DnaAWfoVAAAQNR6.jpg
(5/7) Downloaded: https://pbs.twimg.com/media/DnaAWfqV4AAJ6_q.jpg
(6/7) Downloaded: https://pbs.twimg.com/media/DnaAWfhWwAUdk11.jpg
(7/7) Downloaded: https://pbs.twimg.com/media/DnU3UPDWsAsB7iX.jpg
/home/tweetpi/timeline-POTUS.mp4
```

Currently images on Twitter will be downloaded to the working directory by default.

## Use as a library

You can refer to the shell code in TweetPI.py. Also you can refer to [README_demo.py](README_demo.py).

```python
from TweetPI import TweetPI

tpi = TweetPI({"twitter_consumer_key":"...", "twitter_consumer_secret":"...", "twitter_access_token":"...", "twitter_access_secret":"...", "google_key_json":"gapi.json"})

try:
    photolist = tpi.get_timeline(username="POTUS", limit=50)
except Exception as e:
    # Error handling
    print(e)

print(photolist.get_list())
```

## License

[This project is licensed under MIT license.](LICENSE)

## Acknowledgements

I cannot finish this so fast without various online resources, including mature Python libraries, official reference, StackOverflow posts, and inspirations from my classmates. I have left credit to several StackOverflow posts in the source code, though they may not look like what they were on the answers, I would like to say: Thank you!

- TA's recommendation of `tweepy`
- state-of-the-art open-source `ffmpeg`
- Hashable class idea from https://stackoverflow.com/a/2704866/4073795
- Download image method from https://stackoverflow.com/a/7244263/4073795
- Resize image with Pillow from https://stackoverflow.com/a/44231784/4073795
- Multiline text with Pillow from https://stackoverflow.com/a/7698300/4073795
- [Professor's recommendation of `subprocess`](https://piazza.com/class/jlx16o3kyrv53w?cid=13)
- Classmates' oral discussion of using Google Vision Image API (instead of the video ones), ffmpeg's "width divided by 2" error, drawing annotations on the video (I really don't remember who they are, sorry!)