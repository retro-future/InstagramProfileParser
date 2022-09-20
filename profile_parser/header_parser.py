from bs4 import BeautifulSoup
import requests

from parser.tag_classes import AVATAR_CLASS

url = "https://www.instagram.com/shvhzxd/"
response = requests.get(url)
soup = BeautifulSoup(response.text,"lxml")

def parse_header():
    img = soup.find("img", _class=AVATAR_CLASS)
    print(img['src'])
