# TweetPI: Tweet Photo Insight

Python library to get photos in Twitter feed, with a video and photo annotations. Part of EC601 as Mini Project 1.

![DEMO of annotated video](README_demo.gif)

This is very experimental, and thus the API may change at any time.

Agile Scrum board (with sprints): https://github.com/phy25/tweetpi/projects/1

## Contents

- [Breaking changes](#breaking-changes)
- [Install](#install)
- [Obtain service tokens](#obtain-service-tokens)
- [Use within shell](#use-within-shell)
- [Use as a library](#use-as-a-library)
- [Design](#design)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Breaking changes

### v1.0

- Video-related functions is no longer implemented as methods in `PhotoList`. They are now in a new module called `video`. So we have ``tweetpi.video.generate_video`, `tweetpi.video.generate_annotated_video`, with a new first argument receiving a PhotoList. This gives us fine-grained control over video tools check. The old method is kept in `PhotoList` with a deprecation notice.
- `PhotoList.photos` is deprecated. You are encourged to use PhotoList to iterate directly as a list. `PhotoList.get_list()`,`PhotoList.photos` is still kept for backward compatibility.
- Under the hood, `localphoto` is removed, instead `photo.ImOp` in introduced with (somewhat) chainable usage.

### v0.2

- `PhotoList.l` is changed to `PhotoList.photos`. Before it is encourged to use `PhotoList.get_list()`, but since we want to be more pythonic, `PhotoList.photos` will be supported in the future. If it is necessary to use function getter/setter, `PhotoList.photos` will be kept available.

## Install

### Ubuntu

This library is currently tested within Ubuntu. You need to install Python (tested with Python 3.5, 3.7.0 now), ffmpeg, and respective Python library.

```shell
$ git clone https://github.com/phy25/tweetpi.git
$ cd tweetpi
$ sudo apt-get install ffmpeg
$ pip install -r requirements.txt --user
```

### Windows

It's more convenient if you are using Windows 10 + [WSL](https://docs.microsoft.com/en-us/windows/wsl/install-win10); it's the same as on Ubuntu. But if you need to...

```shell
> git clone https://github.com/phy25/tweetpi.git
> cd tweetpi
> pip install -r requirements.txt --user
```
And finally, **grab an copy of `ffmpeg.exe` inside `tweetpi` folder** (You can [download here](https://ffmpeg.zeranoe.com/builds/)), or ensure `ffmpeg` is in PATH and thus is execuable from the shell.

## Obtain service tokens

You need to prepare your Twitter API token and Google Cloud Vision API service account JSON.

### How to config

A object called `options` will be passed to TweetPI.

If you intend to use the shell, you can put them as JSON in `options.json` in the folder. If you don't pass `--options` argument to the shell, the program will try to read options from `options.json`.

For example, if `options.twitter_consumer_key` is mentioned, it means here (***) in `options.json`. You just need to put the value in that position (without spaces before and after, and with `"` wrapped!).

```json
{
    "twitter_consumer_key":"***",
    "twitter_consumer_secret":"CHANGEME",
    "twitter_access_token":"CHANGEME",
    "twitter_access_secret":"CHANGEME",
    "google_key_json":"gapi.json"
}
```

If you are using the library from your Python code, I guess you are so wise to handle this.

### Twitter

Go to https://developer.twitter.com/en/apply/user and apply (Though this is harder than before :-( ). If you (already) have one, go to https://apps.twitter.com/ to obtain the following information, and fill them into options with `TweetPI()`. Note that we need read-only or broader access.

- Consumer Key (API Key) -> `options.twitter_consumer_key`
- Consumer Secret (API Secret) -> `options.twitter_consumer_secret`
- Access Token -> `options.twitter_access_token`
- Access Token Secret -> `options.twitter_access_secret`

### Google

Follow https://cloud.google.com/vision/docs/quickstart#set_up_your_project (only "Set up your project" part) to set up your project and [enable "Cloud Vision API"](https://console.cloud.google.com/flows/enableapi?apiid=vision.googleapis.com&redirect=https://console.cloud.google.com&_ga=2.107360394.-90131543.1534915532). You don't need to create a Cloud Storage bucket for using TweetPI.

Then you need to obtain a service account key (in JSON). If you don't have one, go to https://console.cloud.google.com/apis/credentials/serviceaccountkey, follow the guide (you don't need to choose a role for using TweetPI), choose JSON, and download the `.json` file to the TweetPI folder.

Currently TweetPI only supports JSON service account key. You can point to the JSON file by filling `options.google_key_json` (relative to working directory, e.g. `My Project f92e3234.json`).

## Use within shell

This library provides a shell access.

Examples first. I can get an annotated video like the demo above like:

```shell
$ TweetPI.py annotatedvideo --timeline POTUS --limit 50
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

Remember, a lot of arguments are optional, so it can be as easy as:

```shell
$ TweetPI.py list -tl
# This outputs images on my timeline
{'indices': [20, 43], 'source_status_id': 1044026378746654720, 'media_url_https': 'https://pbs.twimg.com/media/Dn0gca6X0AAl0NS.jpg', 'sizes': {'small': {'h': 680, 'resize': 'fit', 'w': 382}, 'medium': {'h': 1200, 'resize': 'fit', 'w': 675}, 'thumb': {'h': 150, 'resize': 'crop', 'w': 150}, 'large': {'h': 1334, 'resize': 'fit', 'w': 750}}, 'id_str': '1044026361252401152', 'id': 1044026361252401152, 'display_url': 'pic.twitter.com/qeJI8ZKoxX', 'source_status_id_str': '1044026378746654720', 'source_user_id': 126581934, 'type': 'photo', 'source_user_id_str': '126581934', 'media_url': 'http://pbs.twimg.com/media/Dn0gca6X0AAl0NS.jpg', 'url': 'https://t.co/qeJI8ZKoxX', 'expanded_url': 'https://twitter.com/dearemon/status/1044026378746654720/photo/1'}
{'indices': [39, 62], 'source_status_id': 1043885730798301184, 'media_url_https': 'https://pbs.twimg.com/media/Dnygh3oXUAATZ3u.jpg', 'sizes': {'small': {'h': 680, 'resize': 'fit', 'w': 510}, 'medium': {'h': 1200, 'resize': 'fit', 'w': 900}, 'thumb': {'h': 150, 'resize': 'crop', 'w': 150}, 'large': {'h': 2048, 'resize': 'fit', 'w': 1536}}, 'id_str': '1043885717372489728', 'id': 1043885717372489728, 'display_url': 'pic.twitter.com/NHc37bGipd', 'source_status_id_str': '1043885730798301184', 'source_user_id': 231652942, 'type': 'photo', 'source_user_id_str': '231652942', 'media_url': 'http://pbs.twimg.com/media/Dnygh3oXUAATZ3u.jpg', 'url': 'https://t.co/NHc37bGipd', 'expanded_url': 'https://twitter.com/dollywang05/status/1043885730798301184/photo/1'}
$ TweetPI.py annotate -tl
https://pbs.twimg.com/media/Dn0gca6X0AAl0NS.jpg: font, product, brand
https://pbs.twimg.com/media/Dnygh3oXUAATZ3u.jpg: child, girl, arm, black hair, hand, toddler, japanese idol, product
```

While it can be as complex as:

```shell
$ TweetPI.py download --timeline POTUS --limit 50 --options options.json
$ TweetPI.py annotatedvideo --timeline POTUS --limit 50 --size 640x320 --output test.mp4 --interval 1 --fontcolor 'rgb(255, 255, 255)' --fontsize 20
/home/tweetpi/test.mp4
```

Acutally you don't need to execute `download` before you execute the `video` command; it will be automatically downloaded (no duplicate download!).

If you want to deep further, I highly suggest you use `-h` to look up the help.

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

You can always use `-h` to get help information for a specific function. For reference, here they are (please consult with `-h` for up-to-date help info).

```shell
$ TweetPI.py list --help
usage: TweetPI.py list [-h] --timeline [TIMELINE] [--limit LIMIT]
                       [--options OPTIONS]

optional arguments:
  -h, --help            show this help message and exit
  --timeline [TIMELINE], -tl [TIMELINE]
                        from your home timeline or someone's user timeline
  --limit LIMIT         tweets limit
  --options OPTIONS     Init config for TweetPI library (JSON file path or
                        JSON string)
```
```
$ TweetPI.py download --help
usage: TweetPI.py download [-h] --timeline [TIMELINE] [--limit LIMIT]
                           [--options OPTIONS]

optional arguments:
  -h, --help            show this help message and exit
  --timeline [TIMELINE], -tl [TIMELINE]
                        from your home timeline or someone's user timeline
  --limit LIMIT         tweets limit
  --options OPTIONS     Init config for TweetPI library (JSON file path or
                        JSON string)
```
```
$ TweetPI.py video --help
usage: TweetPI.py video [-h] --timeline [TIMELINE] [--limit LIMIT]
                        [--options OPTIONS] [--size SIZE] [--output OUTPUT]
                        [--interval INTERVAL]

optional arguments:
  -h, --help            show this help message and exit
  --timeline [TIMELINE], -tl [TIMELINE]
                        from your home timeline or someone's user timeline
  --limit LIMIT         tweets limit
  --options OPTIONS     Init config for TweetPI library (JSON file path or
                        JSON string)
  --size SIZE           Video size, default: 1280x720
  --output OUTPUT       Output filename, default: timeline-id.mp4
  --interval INTERVAL   Seconds per image, default: 3
```
```
$ TweetPI.py annotate --help
usage: TweetPI.py annotate [-h] --timeline [TIMELINE] [--limit LIMIT]
                           [--options OPTIONS]

optional arguments:
  -h, --help            show this help message and exit
  --timeline [TIMELINE], -tl [TIMELINE]
                        from your home timeline or someone's user timeline
  --limit LIMIT         tweets limit
  --options OPTIONS     Init config for TweetPI library (JSON file path or
                        JSON string)
```
```
$ TweetPI.py annotatedvideo --help
usage: TweetPI.py annotatedvideo [-h] --timeline [TIMELINE] [--limit LIMIT]
                                 [--options OPTIONS] [--size SIZE]
                                 [--output OUTPUT] [--interval INTERVAL]
                                 [--fontfile FONTFILE] [--fontcolor FONTCOLOR]
                                 [--fontsize FONTSIZE]

optional arguments:
  -h, --help            show this help message and exit
  --timeline [TIMELINE], -tl [TIMELINE]
                        from your home timeline or someone's user timeline
  --limit LIMIT         tweets limit
  --options OPTIONS     Init config for TweetPI library (JSON file path or
                        JSON string)
  --size SIZE           Video size, default: 1280x720
  --output OUTPUT       Output filename, default: timeline-id.mp4
  --interval INTERVAL   Seconds per image, default: 3
  --fontfile FONTFILE   Optional font file path (should be ttf file)
  --fontcolor FONTCOLOR
                        Optional font color, default: rgb(255, 0, 0)
  --fontsize FONTSIZE   Optional font size, default: 50
```

Currently images on Twitter will be downloaded to the working directory by default.

## Use as a library

To make use of the library in Python, either:

- Refer to [README_demo.py](README_demo.py);
- Refer to the shell code in the end of TweetPI.py.

You can read the following [Design diagram](#design) to learn about what's inside the library.

## Design

The following diagram is the current design of the library.

```
 +-------+ .get_timeline() +---------+    list(Photos)    +-----------+
 |TweetPI+---------------->+PhotoList+------------------->+  Photos   |
 +-------+                 +---------+                    +-----------+
                                |                               |
                                | .download_all()               | .download()
                                |                               |
                                |                               |
                                | .get_annotations()            | .get_annotation()
                                |                               +
                                |
                                +----> video.generate_video()
                                       video.generate_annotated_video()
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
- Code review from @huangluyang001