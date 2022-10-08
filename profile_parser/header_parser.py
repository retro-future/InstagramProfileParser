import os
import pickle
from datetime import datetime
from pprint import pprint

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


class InvalidCredentials(Exception):
    def __init__(self, message="Provide a valid not null credentials"):
        self.message = message
        super().__init__(self.message)


class InstagramAuth:
    """I could've use Union for the driver argument in constructor but,
     I ended up choosing chrome driver to make the type hints work  """

    def __init__(self, driver: webdriver.Chrome):
        self._driver = driver
        self._driver.maximize_window()

    def close_browser(self):
        self._driver.close()

    def check_and_update_cookies(self) -> bool:
        """
        Selenium webdriver is initialized with default url "data:".
        add_cookie() requires the current url to be under the same domain pattern as the cookie otherwise
        we get invalid domain exception.
        "data:" will not match any cookie domain, so we have to open site before add any cookie
        :return:
        """
        if not os.path.exists("cookies.pkl"):
            return False
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

    def login(self, username: str, password: str) -> None:
        if not username or not password:
            raise InvalidCredentials
        if self.check_and_update_cookies():
            return
        self._driver.get('https://www.instagram.com/accounts/login/')
        WebDriverWait(self._driver, 10).until(ec.presence_of_element_located((By.XPATH, "//input[@name='username']")))
        user_name_elem = self._driver.find_element(By.XPATH, "//input[@name='username']")
        password_elem = self._driver.find_element(By.XPATH, "//input[@name='password']")
        user_name_elem.clear()
        password_elem.clear()
        user_name_elem.send_keys(username)
        password_elem.send_keys(password)
        password_elem.send_keys(Keys.RETURN)
        try:
            WebDriverWait(self._driver, 10).until(
                ec.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Profile') or contains(text(), "
                                                          "'Messages')]")))
        except TimeoutException:
            print("not authenticated")

        pickle.dump(self._driver.get_cookies(), open("cookies.pkl", "wb"))

    @property
    def get_driver(self) -> webdriver.Chrome:
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


class BaseParser:
    def __init__(self, profile_page: str):
        self.profile_page = profile_page
        self.soup = BeautifulSoup(self.profile_page, "lxml")
        self.dom = etree.HTML(str(self.soup))


class HeaderParse(BaseParser):

    def parse_avatar_url(self) -> str:
        user_avatar = self.dom.xpath("//header//img/@src")
        if not user_avatar:
            return ""
        return user_avatar.pop()

    def parse_username(self) -> str:
        user_name_1 = self.dom.xpath("//header//*[self::h1 or self::h2]/text()")
        user_name_2 = self.soup.find(class_="_aacl _aacs _aact _aacx _aada")
        username = user_name_1.pop() if user_name_1 else user_name_2.text
        return username

    def parse_followers_posts(self, text: str) -> str:
        element = self.dom.xpath(f"//div[contains(text(), \'{text}\')]/span/text()")
        if not element:
            return ""
        return element.pop()

    def get_basic_info(self) -> str:
        user_avatar_url = self.parse_avatar_url()
        user_name = self.parse_username()
        user_posts_count = self.parse_followers_posts("posts")
        user_followers_count = self.parse_followers_posts("followers")
        user_following_count = self.parse_followers_posts("following")
        return f"User Name: {user_name}\nAvatar Url: {user_avatar_url}\nPosts: {user_posts_count}\n" \
               f"Followers: {user_followers_count}\nFollowing: {user_following_count}"


if __name__ == "__main__":
    UserIG = InstagramAuth(webdriver.Chrome())
    UserIG.login(env.str("IG_USERNAME"), env.str("IG_PASSWORD"))
    Insta_bot = InstagramBot(UserIG.get_driver)
    user_page = Insta_bot.get_profile_page("https://www.instagram.com/shvhzxd/")
    user_header = HeaderParse(user_page)
    # src_list = Insta_bot.parse_posts_links()
    print(user_header.get_basic_info())
    # print(src_list)
    # print(len(src_list))
    UserIG.close_browser()

