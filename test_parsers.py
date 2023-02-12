from environs import Env
from instagram_parser.parsers.header_parser import HeaderParse
from instagram_parser.instagram_auth import InstagramAuth
from instagram_parser.parsers.user_posts_parser import PostsParser

env = Env()
env.read_env()


def main():
    UserIG = InstagramAuth(env.str("IG_USERNAME"), env.str("IG_PASSWORD"))
    UserIG.login()
    Insta_bot = PostsParser(UserIG.driver)
    user_page = UserIG.get_profile_page("https://www.instagram.com/mulcciberlife/")
    user_header = HeaderParse(user_page)
    srcs = Insta_bot.parse_posts()
    print(user_header.get_basic_info())
    print(srcs)
    UserIG.close_browser()


if __name__ == "__main__":
    main()
