import json
import os
import pickle
from datetime import timedelta, datetime
from pprint import pprint

import redis
import requests
from bs4 import BeautifulSoup
from environs import Env
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException

from profile_parser.custom_ec import document_height_is_not_equal

env = Env()
env.read_env()


class InstagramAuth:
    """I could've use Union for the driver argument but,
     I ended up choosing chrome driver to make the type hints work  """

    def __init__(self, username: str, password: str, driver: webdriver.Chrome):
        self.username = username
        self.password = password
        self._driver = driver
        self._driver.maximize_window()
        self.redis_cache = redis.Redis()

    def close_browser(self):
        self._driver.close()

    def check_and_update_cookies(self):
        """
        Selenium webdriver is initialized with default url "data:".
        add_cookie() requires the current url to be under the same domain pattern as the cookie otherwise
        we get invalid domain exception.
        "data:" will not match any cookie domain, so we have to open site before add any cookie
        :return:
        """
        if not os.path.exists("cookies.pkl"):
            return None
        with open("cookies.pkl", "rb") as f:
            cookies = pickle.load(f)
            # there might be dicts without "expiry" key, so there's an additional check
            min_expiry_time = min([cookie.get("expiry") for cookie in cookies if cookie.get("expiry")])
            formatted_time = datetime.fromtimestamp(min_expiry_time)
            if formatted_time < datetime.now():
                return False
            self._driver.get("https://www.instagram.com")
            self._driver.delete_all_cookies()
            for cookie in cookies:
                self._driver.add_cookie(cookie_dict=cookie)
        return True

    def login(self):
        cookies_exists = self.check_and_update_cookies()
        if cookies_exists:
            return
        self._driver.get('https://www.instagram.com/accounts/login/')
        WebDriverWait(self._driver, 10).until(ec.presence_of_element_located((By.XPATH, "//input[@name='username']")))
        user_name_elem = self._driver.find_element(By.XPATH, "//input[@name='username']")
        user_name_elem.clear()
        user_name_elem.send_keys(self.username)
        password_elem = self._driver.find_element(By.XPATH, "//input[@name='password']")
        password_elem.clear()
        password_elem.send_keys(self.password)
        password_elem.send_keys(Keys.RETURN)
        try:
            WebDriverWait(self._driver, 10).until(
                ec.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Profile') or contains(text(), "
                                                          "'Messages')]")))
        except TimeoutException:
            print("not authenticated")

        pickle.dump(self._driver.get_cookies(), open("cookies.pkl", "wb"))

    @property
    def get_driver(self):
        return self._driver


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

    def get_profile_page(self, profile_page_url: str):
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


class BaseParser:
    def __init__(self, profile_page: str):
        self.profile_page = profile_page
        self.soup = BeautifulSoup(self.profile_page, "lxml")
        self.dom = etree.HTML(str(self.soup))


class HeaderParse(BaseParser):

    def parse_avatar_url(self) -> str:
        user_avatar = self.dom.xpath("//header/div/div/span/img/@src")
        user_avatar_1 = self.dom.xpath("//header/div/div/div/button/img/@src")
        return user_avatar[0] or user_avatar_1[0]

    def get_basic_info(self):
        user_avatar_url = self.parse_avatar_url()
        user_name = self.soup.find(class_="_aacl _aacs _aact _aacx _aada")
        user_info = self.soup.findAll("span", "_ac2a")
        user_posts_count = user_info[0]
        user_followers_count = user_info[1]
        user_following_count = user_info[2]
        return f"User Name: {user_name.text}\nAvatar Url: {user_avatar_url}\nPosts: {user_posts_count.text}\n" \
               f"Followers: {user_followers_count.text}\nFollowing: {user_following_count.text}"


class PostsParse(BaseParser):

    def _get_post_img_src(self, class_name: str) -> list:
        img_src_list = list()
        child_divs = self.soup.find("div", class_=class_name)
        for img in child_divs.findAll("img"):
            img_src_list.append(img["srcset"].split(",")[-1].split()[0])
        return img_src_list

    def get_user_posts(self):
        post_row_block = self.dom.xpath("/html/body/div[1]/div/div/div/div[1]/div/div/div/div[1]/div[2]/div["
                                        "2]/section/main/div/div[2]/article/div[1]/div/div[1]")
        if post_row_block:
            post_row_block = post_row_block[0]
        else:
            raise NoSuchElementException
        block_class_name = post_row_block.attrib["class"]
        src_list = self._get_post_img_src(block_class_name)
        return src_list


if __name__ == "__main__":
    UserIG = InstagramAuth(env.str("IG_USERNAME"), env.str("IG_PASSWORD"),
                           webdriver.Chrome())  # Add Account and Password
    UserIG.login()
    Insta_bot = InstagramBot(UserIG.get_driver)
    user_page = Insta_bot.get_profile_page("https://www.instagram.com/balabanoova/")
    user_header = HeaderParse(user_page)
    src_list = Insta_bot.parse_posts_links()
    print(user_header.get_basic_info())
    print(src_list)
    print(len(src_list))
    UserIG.close_browser()
    # with open("index.html", "r", encoding="utf-8") as fp:
    #     user_page = fp.read()
    # user_header = HeaderParse(user_page)
    # user_posts = PostsParse(user_page)
    # print(user_header.get_basic_info())
    # print(user_posts.get_user_posts())
