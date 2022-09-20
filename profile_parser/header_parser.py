from bs4 import BeautifulSoup
from environs import Env
from lxml import etree
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait

env = Env()
env.read_env()


class DomElementNotFound(BaseException):
    pass


class InstagramBot:

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.driver = webdriver.Chrome()

    def close_browser(self):
        self.driver.close()

    def login(self):
        self.driver.get('https://www.instagram.com/accounts/login/')
        try:
            WebDriverWait(self.driver, 10).until(
                ec.presence_of_element_located((By.XPATH, "//input[@name='username']")))
        except TimeoutException:
            print("login page error")
        user_name_elem = self.driver.find_element(By.XPATH, "//input[@name='username']")
        user_name_elem.clear()
        user_name_elem.send_keys(self.username)
        password_elem = self.driver.find_element(By.XPATH, "//input[@name='password']")
        password_elem.clear()
        password_elem.send_keys(self.password)
        password_elem.send_keys(Keys.RETURN)
        try:
            WebDriverWait(self.driver, 10).until(
                ec.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div/div[1]/div/div/div/div['
                                                          '1]/div[1]/div[1]')))
        except TimeoutException:
            print("not authenticated")

    def get_profile_page(self, profile_page_url: str):
        self.driver.get(profile_page_url)
        try:
            WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.XPATH, '/html/body/div['
                                                                                           '1]/div/div/div/div['
                                                                                           '1]/div/div/div/div['
                                                                                           '1]/div[2]/div['
                                                                                           '2]/section/main/div/header')))
        except TimeoutException:
            print("I give up...")
        return self.driver.page_source


class BaseParser:
    def __init__(self, profile_page: str):
        self.profile_page = profile_page
        self.soup = BeautifulSoup(self.profile_page, "lxml")
        self.dom = etree.HTML(str(self.soup))


class HeaderParse(BaseParser):

    def parse_avatar_url(self) -> str:
        user_avatar = self.dom.xpath('/html/body/div[1]/div/div/div/div[1]/div/div/div/div[1]/div[2]/div['
                                     '2]/section/main/div/header/div/div/span/img/@src')
        user_avatar_1 = self.dom.xpath("/html/body/div[1]/div/div/div/div[1]/div/div/div/div[1]/div[2]/div["
                                       "2]/section/main/div/header/div/div/div/button/img/@src")
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
            raise DomElementNotFound
        block_class_name = post_row_block.attrib["class"]
        src_list = self._get_post_img_src(block_class_name)
        return src_list



if __name__ == "__main__":
    # UserIG = InstagramBot(env.str("IG_USERNAME"), env.str("IG_PASSWORD"))  # Add Account and Password
    # UserIG.login()
    # user_page = UserIG.get_profile_page("https://www.instagram.com/lostfrequencies/")
    # UserIG.close_browser()
    with open("index.html", "r", encoding="utf-8") as fp:
        user_page = fp.read()
    user_header = HeaderParse(user_page)
    user_posts = PostsParse(user_page)
    print(user_header.get_basic_info())
    print(user_posts.get_user_posts())

