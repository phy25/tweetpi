import os
import tempfile
from tweetpi.photo import ImOp
import subprocess
from PIL import ImageFont


def _generate_video_from_path(files, name, size="1280x720", shell=False, interval=3, parent=None):
    fullpath = os.path.abspath(name)

    if not len(files):
        raise Exception("No images available for video creation")

    # generate concat files
    # https://trac.ffmpeg.org/wiki/Slideshow
    concat_path = os.path.join(tempfile.gettempdir(), name+".txt")
    with open(concat_path, "w") as concat_file:
        for f in files:
            concat_file.write("file '{}'\n".format(f))
            concat_file.write("duration {}\n".format(interval))
    # run
    try:
        proc = subprocess.run(["ffmpeg", "-f", "concat", "-safe", "0", "-i", concat_path, "-pix_fmt", "yuv420p", "-video_size", size, "-y", "-stats", "-loglevel", "error", name], check=True, stdout=subprocess.PIPE)
    except subprocess.CalledProcessError:
        raise
    finally:
        # unlink temp files
        os.unlink(concat_path)
        for f in files:
            os.unlink(f)
        if parent:
            parent.db_client.log(type="video", keyword="",
                                 key=name, text="", metadata={"files":files})

    return fullpath


def generate_video(photos, name=None, size="1280x720", shell=False, interval=3, parent=None):
    """
    Generate a simple video
    photos: PhotoList
    """
    if not name:
        name = photos.source+".mp4"
    sizes = size.split('x')

    d = photos.download_all(shell=shell, force=False)
    if not d:
        return False
    files = []

    for p in photos:
        im = ImOp(p).resize(width=int(sizes[0]), height=int(sizes[1]))
        files.append(im.save_as_temp(p.name))

    return _generate_video_from_path(files, name, size, shell, interval, parent=parent)


def generate_annotated_video(photos, name=None, size="1280x720", shell=False, interval=3,
                             font_file="Roboto-Regular.ttf", font_color="rgb(255, 0, 0)", font_size=40,  parent=None):
    if not name:
        name = photos.source+".mp4"
    sizes = size.split('x')

    d = photos.download_all(shell=shell, force=False)
    if not d:
        return False

    photos.fetch_annotations()
    files = []
    font = ImageFont.truetype(font_file, size=font_size)

    for p in photos:
        message = ", ".join([l.description for l in p.annotation.label_annotations])
        im = ImOp(p).resize(width=int(sizes[0]), height=int(sizes[1]))
        im.annotate(message, font, font_size, font_color)
        files.append(im.save_as_temp(p.name))

    return _generate_video_from_path(files, name, size, shell, interval, parent=parent)
