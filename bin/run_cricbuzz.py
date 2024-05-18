import sys
import os
# Append parent repo directory in the path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import argparse
from sites.cricbuzz.parser import (
    CricBuzzDownloader,
    CricBuzzCommon,
    CricBuzzFeeder,
    CricBuzzParser
)
from icrawler import Crawler

if __name__ != "__main__":
    raise RuntimeError

parser = argparse.ArgumentParser()
parser.add_argument("--max-pages", default=2, type=int, help="Max Cricbuzz pages")
parser.add_argument("--max-num", default=1000, type=int, help="Max downloaded number")

args = parser.parse_args()
args_dict = args.__dict__
crawler = Crawler(
    feeder_cls=CricBuzzFeeder,
    parser_cls=CricBuzzParser,
    downloader_cls=CricBuzzDownloader,
    downloader_threads=4,
    storage={'backend': 'FileSystem', 'root_dir': CricBuzzCommon.BASE_OUTPUT_PATH}
)

crawler.crawl(
    feeder_kwargs=args_dict, 
    downloader_kwargs=dict(max_num=args.max_num, min_size=None), 
    parser_kwargs=args_dict
)
