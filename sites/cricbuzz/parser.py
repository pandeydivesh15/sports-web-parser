import os
import threading
import json
import atexit
from icrawler import Feeder, Parser, ImageDownloader
from bs4 import BeautifulSoup
from utils import get_logger
from collections import defaultdict


LOGGER = get_logger("CricBuzz")


class CricBuzzCommon():
    BASE_PATH = "https://www.cricbuzz.com/cricket-team/india/2/photos"
    HTML_DATA_PATH = "data/20240518_cricbuzz.html"
    BASE_OUTPUT_PATH = "data/cricbuzz/"

    DIR_LOCK = threading.Lock()
    DIR_DICT = {}

    PAGE_TITLE_INDEX_PATH = f"{BASE_OUTPUT_PATH}/page_title_and_images_index.json"

    @staticmethod
    def register_downloaded_image(page_url, page_title, filename, descripion, position):
        with CricBuzzCommon.DIR_LOCK:
            CricBuzzCommon.DIR_DICT[page_url]["contents"].append(dict(
                page_title=page_title,
                filename=filename,
                descripion=descripion,
                position=position
            ))

    @staticmethod
    def register_url_date(page_url, date):
        with CricBuzzCommon.DIR_LOCK:
            CricBuzzCommon.DIR_DICT[page_url] = {
                "date": date,
                "contents": []
            }

    @staticmethod
    @atexit.register
    def dump_common_data():
        with CricBuzzCommon.DIR_LOCK:
            data = CricBuzzCommon.DIR_DICT
            if not data:
                return
            json_data = json.dumps(data, indent=2)
            with open(CricBuzzCommon.PAGE_TITLE_INDEX_PATH, "w") as f:
                f.write(json_data)


class CricBuzzFeeder(Feeder):
    def feed(self, *args, **kwargs):
        max_pages = kwargs.get("max_pages", 5)
        LOGGER.info(f"Feeding at max {max_pages} pages")
        soup = None
        with open(CricBuzzCommon.HTML_DATA_PATH, "r") as foo:
            soup = BeautifulSoup(foo, "lxml")
        
        # Hope they never change it
        data_pts = soup.find_all("div", class_="cb-pht-block cb-col-50")
        data_pts = data_pts[:max_pages]
        for pt in data_pts:
            href = pt.find("a")["href"]
            date_str = pt.find("div", class_="cb-pht-subtitle").contents[0]
            CricBuzzCommon.register_url_date(href, date_str)
            self.output(href)


class CricBuzzParser(Parser):
    def parse(self, response, *args, **kwargs):
        soup = BeautifulSoup(response.content, "lxml")
        page_title = soup.find("h1").contents[0]
        images_data = soup.find("div", class_="cb-col-67 center-block").find_all("img")
        for i, img in enumerate(images_data):
            description = img["title"]
            image_link = img["source"]
            yield dict(
                file_url=image_link,
                page_url=response.url,
                description=description, 
                position=i, 
                page_title=page_title
            )


class CricBuzzDownloader(ImageDownloader):
    def process_meta(self, task, *args, **kwargs):
        if not task.get("success", False):
            return

        page_url = task["page_url"]
        description = task["description"]
        position = task["position"]
        page_title = task["page_title"]
        filename = task["filename"]        
        
        CricBuzzCommon.register_downloaded_image(
            page_url,
            page_title,
            filename,
            description,
            position
        )

        return super().process_meta(task)
        



