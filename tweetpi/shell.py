import json
import sys
import os
from tweetpi import TweetPI, video, __version__ as tweetpi_version

def shell_print_exception(error_name=None):
    import traceback
    if error_name:
        print('=== {} ==='.format(error_name))
    traceback.print_exc(limit=2)

def shell_init_lib(args):
    o = {}

    options_str = "options.json"
    if 'options' in args and args.options:
        options_str = args.options
        if options_str.startswith('"\''):
            options_str = options_str.strip('"\'')
    try:
        try:
            with open(options_str, "r") as fp:
                o = json.load(fp)
            if not "conf_folder" in o:
                o["conf_folder"] = os.path.dirname(os.path.abspath(options_str))
        except IOError:
            o = json.loads(options_str)
    except Exception:
        shell_print_exception('Options load failure')
        sys.exit(1)
    tpi = TweetPI(o)
    return tpi

def shell_list(args):
    tpi = shell_init_lib(args)
    try:
        if 'timeline' in args:
            photolist = tpi.get_timeline(username=args.timeline, page=1, limit=args.limit)
        else:
            sys.exit(1)
    except Exception:
        shell_print_exception()
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
    except Exception:
        shell_print_exception()
        sys.exit(2)

def shell_video(args):
    tpi = shell_init_lib(args)
    try:
        if 'timeline' in args:
            size = args.size if args.size else "1280x720"
            sizeParse = size.split('x')
            if not sizeParse[0].isdigit() or not sizeParse[1].isdigit():
                print("Size should be like 1280x720", file=sys.stderr)
                sys.exit(1)
            photolist = tpi.get_timeline(username=args.timeline, page=1, limit=args.limit)
            result = video.generate_video(photos=photolist, name=args.output, size=size, shell=True, interval=args.interval, parent=tpi)
            print(result)
        else:
            sys.exit(1)
    except Exception:
        shell_print_exception()
        sys.exit(2)

def shell_annotate(args):
    tpi = shell_init_lib(args)
    try:
        if 'timeline' in args:
            photolist = tpi.get_timeline(username=args.timeline, page=1, limit=args.limit)
            result = photolist.get_annotations()
        else:
            sys.exit(1)
    except Exception:
        shell_print_exception()
        sys.exit(2)

    for t in result:
        print('{}: {}'.format(t.remote_url, ", ".join([a.description for a in t.annotation.label_annotations])))

def shell_annotatedvideo(args):
    tpi = shell_init_lib(args)
    try:
        if 'timeline' in args:
            size = args.size if args.size else "1280x720"
            sizeParse = size.split('x')
            if not sizeParse[0].isdigit() or not sizeParse[1].isdigit():
                print("Size should be like 1280x720", file=sys.stderr)
                sys.exit(1)
            photolist = tpi.get_timeline(username=args.timeline, page=1, limit=args.limit)
            result = video.generate_annotated_video(photos=photolist, name=args.output, size=size, shell=True,
                                                    font_color=args.fontcolor, font_file=args.fontfile, interval=args.interval, font_size=args.fontsize, parent=tpi)
            print(result)
        else:
            sys.exit(1)
    except Exception:
        shell_print_exception()
        sys.exit(2)


def shell_get_total_by_type(args):
    tpi = shell_init_lib(args)
    try:
        if tpi.db_client:
            result = tpi.db_client.get_total_by_type()
            table = "{:>16} {:>8}"
            print(table.format("Type", "Count"))
            print(table.format("-"*16, "-"*8))
            for i in result:
                print(table.format(i["type"], i["count"]))
        else:
            sys.exit(1)
    except Exception:
        shell_print_exception()
        sys.exit(2)

def shell_get_annotation_keywords_list(args):
    tpi = shell_init_lib(args)
    try:
        if tpi.db_client:
            result = tpi.db_client.get_annotation_keywords_list(limit=args.limit)
            table = "{:>32} {:>8}"
            print(table.format("Keyword", "Count"))
            print(table.format("-"*32, "-"*8))
            for i in result:
                print(table.format(i["keyword"], i["count"]))
        else:
            sys.exit(1)
    except Exception:
        shell_print_exception()
        sys.exit(2)

def shell_get_total_by_session_id(args):
    tpi = shell_init_lib(args)
    try:
        if tpi.db_client:
            result = tpi.db_client.get_total_by_session_id(limit=args.limit)
            table = "{:>32} {:>8}"
            print(table.format("Session ID", "Count"))
            print(table.format("-"*32, "-"*8))
            for i in result:
                print(table.format(i["session_id"], i["count"]))
        else:
            sys.exit(1)
    except Exception:
        shell_print_exception()
        sys.exit(2)

def shell_search_by_keyword(args):
    tpi = shell_init_lib(args)
    try:
        if tpi.db_client:
            result = tpi.db_client.search_by_keyword(keyword=args.KEYWORD)
            for i in result:
                print(i)
            print("{} results in total".format(len(result)))
        else:
            sys.exit(1)
    except Exception:
        shell_print_exception()
        sys.exit(2)


def shell_install_db(args):
    tpi = shell_init_lib(args)
    try:
        if tpi.db_client:
            tpi.db_client.install()
        else:
            sys.exit(1)
    except Exception:
        shell_print_exception()
        sys.exit(2)


def main(argv=None):
    import argparse
    if not argv:
        argv = sys.argv[1:]

    argparser = argparse.ArgumentParser(prog="TweetPI.py", description='Tweet Photo Insight: Python library to get photos in Twitter feed, with a video and photo annotations.')
    argparser.add_argument('--version', action='version', version='%(prog)s {}'.format(tweetpi_version))
    subparsers = argparser.add_subparsers(help=".")

    parser_list = subparsers.add_parser('list', help='list images in Twitter feed')
    parser_list.add_argument('--timeline', '-tl', required=True, const="__home__", nargs="?", help="from your home timeline or someone's user timeline")
    parser_list.add_argument('--limit', help="tweets limit")
    parser_list.add_argument('--options', help="Init config for TweetPI library (JSON file path or JSON string)")
    parser_list.set_defaults(func=shell_list)

    parser_download = subparsers.add_parser('download', help='download images in Twitter feed')
    parser_download.add_argument('--timeline', '-tl', required=True, const="__home__", nargs="?", help="from your home timeline or someone's user timeline")
    parser_download.add_argument('--limit', help="tweets limit")
    parser_download.add_argument('--options', help="Init config for TweetPI library (JSON file path or JSON string)")
    parser_download.set_defaults(func=shell_download)

    parser_video = subparsers.add_parser('video', help='generate a video from images in Twitter feed')
    parser_video.add_argument('--timeline', '-tl', required=True, const="__home__", nargs="?", help="from your home timeline or someone's user timeline")
    parser_video.add_argument('--limit', help="tweets limit")
    parser_video.add_argument('--options', help="Init config for TweetPI library (JSON file path or JSON string)")
    parser_video.add_argument('--size', help="Video size, default: 1280x720")
    parser_video.add_argument('--output', help="Output filename, default: timeline-id.mp4")
    parser_video.add_argument('--interval', help="Seconds per image, default: 3", type=int, default=3)
    parser_video.set_defaults(func=shell_video)

    parser_annotate = subparsers.add_parser('annotate', help='get annotations of images in Twitter feed')
    parser_annotate.add_argument('--timeline', '-tl', required=True, const="__home__", nargs="?", help="from your home timeline or someone's user timeline")
    parser_annotate.add_argument('--limit', help="tweets limit")
    parser_annotate.add_argument('--options', help="Init config for TweetPI library (JSON file path or JSON string)")
    parser_annotate.set_defaults(func=shell_annotate)

    parser_annotatedvideo = subparsers.add_parser('annotatedvideo', help='get annotated video of photos in Twitter feed')
    parser_annotatedvideo.add_argument('--timeline', '-tl', required=True, const="__home__", nargs="?", help="from your home timeline or someone's user timeline")
    parser_annotatedvideo.add_argument('--limit', help="tweets limit")
    parser_annotatedvideo.add_argument('--options', help="Init config for TweetPI library (JSON file path or JSON string)")
    parser_annotatedvideo.add_argument('--size', help="Video size, default: 1280x720")
    parser_annotatedvideo.add_argument('--output', help="Output filename, default: timeline-id.mp4")
    parser_annotatedvideo.add_argument('--interval', help="Seconds per image, default: 3", type=int, default=3)
    parser_annotatedvideo.add_argument('--fontfile', help="Optional font file path (should be ttf file)", default="Roboto-Regular.ttf")
    parser_annotatedvideo.add_argument('--fontcolor', help="Optional font color, default: rgb(255, 0, 0)", default="rgb(255, 0, 0)")
    parser_annotatedvideo.add_argument('--fontsize', help="Optional font size, default: 40", type=int, default=40)
    parser_annotatedvideo.set_defaults(func=shell_annotatedvideo)

    parser_get_annotation_keywords_list = subparsers.add_parser('get_annotation_keywords_list', help='get annotation keywords list in db')
    parser_get_annotation_keywords_list.add_argument('--options', help="Init config for TweetPI library (JSON file path or JSON string)")
    parser_get_annotation_keywords_list.add_argument('--limit', help="results limit", type=int, default=20)
    parser_get_annotation_keywords_list.set_defaults(func=shell_get_annotation_keywords_list)

    parser_get_total_by_session_id = subparsers.add_parser('get_total_by_session_id', help='get total by session_id in db')
    parser_get_total_by_session_id.add_argument('--options', help="Init config for TweetPI library (JSON file path or JSON string)")
    parser_get_total_by_session_id.add_argument('--limit', help="results limit", type=int, default=20)
    parser_get_total_by_session_id.set_defaults(func=shell_get_total_by_session_id)

    parser_get_total_by_type = subparsers.add_parser('get_total_by_type', help='get total by type in db')
    parser_get_total_by_type.add_argument('--options', help="Init config for TweetPI library (JSON file path or JSON string)")
    parser_get_total_by_type.set_defaults(func=shell_get_total_by_type)

    parser_search_by_keyword = subparsers.add_parser('search_by_keyword', help='search logs by keyword in db')
    parser_search_by_keyword.add_argument('--options', help="Init config for TweetPI library (JSON file path or JSON string)")
    parser_search_by_keyword.add_argument('KEYWORD', help="word searched in keyword field")
    parser_search_by_keyword.set_defaults(func=shell_search_by_keyword)

    parser_install_db = subparsers.add_parser('install_db', help='search logs by keyword in db')
    parser_install_db.add_argument('--options', help="Init config for TweetPI library (JSON file path or JSON string)")
    parser_install_db.set_defaults(func=shell_install_db)


    if len(argv) == 0:
        argparser.print_help(sys.stderr)
        sys.exit(1)

    args = argparser.parse_args(args=argv)
    if 'func' in args:
        args.func(args)