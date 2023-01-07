from typing import Callable

from loguru import logger

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait


from instagram_parser.custom_ec import document_height_is_not_equal


class PostsParser:
    def __init__(self, driver: webdriver.Chrome, progress_updater: Callable = None):
        self._driver = driver
        self.img_srcs = list()
        self.progress_updater = progress_updater

    @staticmethod
    def __get_img_src(element_list: list) -> list:
        srcs = list()
        for element in element_list:
            img_tag = element.find_elements(By.XPATH, ".//img")
            srcs.extend([img.get_attribute("src") for img in img_tag])
        return srcs

    def scrollDownToEnd(self) -> bool:
        previous_height = self._driver.execute_script("return document.body.scrollHeight")
        self._driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        try:
            WebDriverWait(self._driver, 10).until(document_height_is_not_equal(previous_height))
        except TimeoutException:
            logger.info("End of the profile page")
            return True

    def parse_posts_block(self) -> WebElement:
        return self._driver.find_element(By.XPATH,
                                         "//div[contains(@style,'position: relative; display: flex; "
                                         "flex-direction: column; padding-bottom: 0px; padding-top: "
                                         "0px;')]")

    def parse_img_src(self, posts_block: WebElement) -> None:
        end_of_page = False
        while not end_of_page:
            rows = posts_block.find_elements(By.XPATH, "./div[position()<=4]")
            self.img_srcs.extend(self.__get_img_src(rows))
            end_of_page = self.scrollDownToEnd()
            if self.progress_updater:
                current_progress = len(dict.fromkeys(self.img_srcs))
                self.progress_updater(current_progress)
        else:
            self.img_srcs.extend(self.__get_img_src(posts_block.find_elements(By.XPATH, "./div")))
            current_progress = len(dict.fromkeys(self.img_srcs))
            self.progress_updater(current_progress)

    def parse_posts_links(self, progress_updater: Callable = None) -> list:
        """Have to convert 'img_srcs' into dict and vice versa
           in order to preserve posts order and remove the same items
        """
        self.parse_img_src(self.parse_posts_block())
        return list(dict.fromkeys(self.img_srcs))


