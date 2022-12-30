from dataclasses import dataclass
from django.utils.crypto import get_random_string
from bs4 import BeautifulSoup
from lxml import etree


@dataclass
class Profile:
    username: str
    posts_count: str


class BaseParser:
    def __init__(self, profile_page: str):
        self.profile_page = profile_page
        self.soup = BeautifulSoup(profile_page, "lxml")
        self.dom = etree.HTML(profile_page)


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
        if not username:
            username = f"test-{get_random_string(5)}"
        return username

    def parse_followers_posts(self, text: str) -> str:
        element = self.dom.xpath(f"//div[contains(text(), \'{text}\')]/span/span/text()")
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
