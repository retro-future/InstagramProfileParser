import time
from typing import Callable, Iterable

from loguru import logger

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait

from instagram_parser.custom_ec import height_is_greater_than


class PostsParser:
    def __init__(self, driver: webdriver.Chrome, progress_updater: Callable[[int], None] = None):
        self._driver = driver
        self.img_srcs = dict()
        self.progress_updater = progress_updater

    def parse_posts(self) -> Iterable[str]:
        self.parse_posts_urls(self.parse_posts_block())
        return self.img_srcs

    def parse_posts_block(self) -> WebElement:
        return self._driver.find_element(By.XPATH,
                                         "//div[contains(@style,'position: relative; display: flex; "
                                         "flex-direction: column; padding-bottom: 0px; padding-top: "
                                         "0px;')]")

    def parse_posts_urls(self, posts_block: WebElement) -> None:
        while self.page_height_is_not_equal_previous():
            rows = posts_block.find_elements(By.XPATH, "./div[position()<=4]")
            self._get_img_src(rows)
            if self.progress_updater:
                current_progress = len(self.img_srcs)
                self.progress_updater(current_progress)
        else:
            self._get_img_src(posts_block.find_elements(By.XPATH, "./div"))
            current_progress = len(self.img_srcs)
            self.progress_updater(current_progress)

    def page_height_is_not_equal_previous(self) -> bool:
        previous_height = self._driver.execute_script("return document.body.scrollHeight")
        self._driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # scroll page
        try:
            WebDriverWait(self._driver, 15).until(height_is_greater_than(previous_height))
        except TimeoutException:
            logger.info("End of the profile page")
            return False
        else:
            return True

    def _get_img_src(self, elements: list) -> None:
        for element in elements:
            img_tag = element.find_elements(By.XPATH, ".//img")
            self.img_srcs.update(dict.fromkeys([img.get_attribute("src") for img in img_tag]))
