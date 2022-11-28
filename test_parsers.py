from environs import Env
from selenium import webdriver

from instagram_parser.parsers.header_parser import HeaderParse
from instagram_parser.ig_authorization import InstagramAuth
from instagram_parser.parsers.user_posts_parser import PostsParser
from user_profile.services.profile_service import ProfileService

env = Env()
env.read_env()


def main():
    UserIG = InstagramAuth(webdriver.Chrome())
    UserIG.login(env.str("IG_USERNAME"), env.str("IG_PASSWORD"))
    Insta_bot = PostsParser(UserIG.driver)
    user_page = Insta_bot.get_profile_page("https://www.instagram.com/yourock_666/")
    user_header = HeaderParse(user_page)
    srcs = Insta_bot.parse_posts_links()
    # instantiate_profile_service = ProfileService()
    # instantiate_profile_service.save_posts_to_db(username=user_header.parse_username(),
    #                                              avatar_url=user_header.parse_avatar_url(), url_list=srcs)
    print(user_header.get_basic_info())
    print(srcs)
    print(len(srcs))
    UserIG.close_browser()


if __name__ == "__main__":
    main()
