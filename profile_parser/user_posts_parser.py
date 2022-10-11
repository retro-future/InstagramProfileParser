from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from profile_parser.custom_ec import document_height_is_not_equal


class InstagramBot:
    def __init__(self, driver: webdriver.Chrome):
        self._driver = driver

    @staticmethod
    def _get_img_src(element_list: list) -> list:
        src_list = list()
        for element in element_list:
            src = element.get_attribute('src')
            if src:
                src_list.append(src)
        return src_list

    def parse_posts_links(self) -> list:
        """Have to convert 'img_src_list' into dict and vice versa
            in order to preserve posts order
        """
        posts_row_block = self._driver.find_element(By.XPATH,
                                                    "//div[contains(@style,'position: relative; display: flex; "
                                                    "flex-direction: column; padding-bottom: 0px; padding-top: "
                                                    "0px;')]")
        img_src_list = list()
        while True:
            img_tag = posts_row_block.find_elements(By.XPATH, "//img[contains(@alt, 'Photo by') or contains(@style, "
                                                              "'object-fit: cover;')]")
            previous_height = self._driver.execute_script("return document.body.scrollHeight")
            img_src_list.extend(self._get_img_src(img_tag))
            self._driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            try:
                WebDriverWait(self._driver, 10).until(document_height_is_not_equal(previous_height))
            except TimeoutException:
                print("End of the profile page")
                break
        img_src_list = list(dict.fromkeys(img_src_list))
        return img_src_list

    def get_profile_page(self, profile_page_url: str) -> str:
        self._driver.get(profile_page_url)
        try:
            WebDriverWait(self._driver, 10).until(ec.all_of(
                ec.presence_of_element_located((By.XPATH, "//div[contains(text(), 'followers')]")),
                ec.presence_of_element_located((By.XPATH, "//div[contains(@style,'position: relative; display: flex; "
                                                          "flex-direction: column; padding-bottom: 0px; padding-top: "
                                                          "0px;')]"))
            ))
        except TimeoutException:
            print("cannot load profile page")
        return self._driver.page_source
