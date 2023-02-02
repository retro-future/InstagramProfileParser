from dataclasses import dataclass
from django.utils.crypto import get_random_string
from bs4 import BeautifulSoup
from lxml import etree


@dataclass
class Profile:
    username: str
    avatar_url: str
    posts_count: int
    followers_count: str
    followings_count: str


class BaseParser:
    def __init__(self, profile_page: str):
        self.profile_page = profile_page
        self.soup = BeautifulSoup(profile_page, "lxml")
        self.dom = etree.HTML(profile_page)


class HeaderParse(BaseParser):

    def parse_avatar_url(self) -> str:
        avatar_url = self.dom.xpath("//header//img/@src")
        if not avatar_url:
            return ""
        return avatar_url.pop()

    def parse_username(self) -> str:
        user_name_1 = self.dom.xpath("//header//*[self::h1 or self::h2]/text()")
        user_name_2 = self.soup.find(class_="_aacl _aacs _aact _aacx _aada")
        username = user_name_1.pop() if user_name_1 else user_name_2.text
        if not username:
            username = f"test-{get_random_string(5)}"
        return username

    def parse_count_of(self, text: str) -> str:
        element = self.dom.xpath(f"//div[contains(text(), \'{text}\')]/span/span/text()")
        if not element:
            return ""
        return element.pop()

    def get_basic_info(self) -> Profile:
        user_name = self.parse_username()
        avatar_url = self.parse_avatar_url()
        posts_count = int(self.parse_count_of("posts"))
        followers_count = self.parse_count_of("followers")
        following_count = self.parse_count_of("following")
        return Profile(user_name, avatar_url, posts_count, followers_count, following_count)
