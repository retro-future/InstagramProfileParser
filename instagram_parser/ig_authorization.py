import os
import pickle
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from loguru import logger

from instagram_parser.custom_exceptions import InvalidCredentials


class InstagramAuth:
    """I could've use Union typing for the driver argument in constructor but,
     I ended up choosing chrome driver to make the type hints work  """

    def __init__(self, driver: webdriver.Chrome):
        self._driver = driver
        self._driver.maximize_window()

    def close_browser(self) -> None:
        self._driver.close()

    @property
    def driver(self) -> webdriver.Chrome:
        return self._driver

    def _cookies_exists(self) -> bool:
        """
        Checks cookies pickle file
        Selenium webdriver is initialized with default url "data:".
        add_cookie() requires the current url to be under the same domain pattern as the cookie otherwise
        we get invalid domain exception.
        "data:" will not match any cookie domain, so we have to open site before add any cookie
        :return: bool
        """
        if not os.path.exists("cookies.pkl"):
            return False
        # check for the cookies expiry_time, if cookies are expired then return False
        # there might be dicts without "expiry" key, so there's an additional check
        with open("cookies.pkl", "rb") as f:
            cookies = pickle.load(f)
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
        if self._cookies_exists():
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
            logger.warning("Not Authenticated, please try again later or use another credentials.")
        else:
            pickle.dump(self._driver.get_cookies(), open("cookies.pkl", "wb"))

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
            logger.warning("Cannot load the profile page")
        return self._driver.page_source
