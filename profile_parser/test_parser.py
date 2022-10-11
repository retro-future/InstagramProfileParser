from environs import Env
from selenium import webdriver

from profile_parser.header_parser import HeaderParse
from profile_parser.ig_auth import InstagramAuth
from profile_parser.user_posts_parser import InstagramBot

env = Env()
env.read_env()


def main():
    UserIG = InstagramAuth(webdriver.Chrome())
    UserIG.login(env.str("IG_USERNAME"), env.str("IG_PASSWORD"))
    Insta_bot = InstagramBot(UserIG.get_driver)
    user_page = Insta_bot.get_profile_page("https://www.instagram.com/lostfrequencies/")
    user_header = HeaderParse(user_page)
    srcs = Insta_bot.parse_posts_links()
    print(user_header.get_basic_info())
    print(srcs)
    print(len(srcs))
    UserIG.close_browser()


if __name__ == "__main__":
    main()
