import os
import pickle
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from loguru import logger


class InstagramAuth(webdriver.Chrome):
    def __init__(self, username: str, password: str):
        super().__init__()
        self.username = self._is_valid_attribute(username, "username")
        self.password = self._is_valid_attribute(password, "password")
        self.maximize_window()

    def _is_valid_attribute(self, attribute: str, attr_name: str):
        if not attribute:
            raise ValueError(f"{attr_name} is required")
        if len(attribute) < 3:
            raise ValueError(f"{attr_name} must be at least 3 characters long")
        return attribute

    def close_browser(self) -> None:
        self.close()

    @property
    def driver(self) -> WebDriver:
        return self

    def login(self) -> None:
        if self._cookies_exists():
            self._initialize_cookies()
            return
        self.get('https://www.instagram.com/accounts/login/')
        self.write_username(self.username)
        self.write_password(self.password)
        try:
            WebDriverWait(self, 10).until(
                ec.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Profile') or contains(text(), "
                                                          "'Messages')]")))
        except TimeoutException:
            logger.warning("Not Authenticated, please try again later or use another credentials.")
        else:
            pickle.dump(self.get_cookies(), open("cookies.pkl", "wb"))

    def _cookies_exists(self) -> bool:
        if not os.path.exists("cookies.pkl"):
            return False
        # check file modification time to check cookie validity
        cookie_file_modified_time = datetime.fromtimestamp(os.path.getmtime("cookies.pkl"))
        current_time = datetime.now()
        difference = current_time - cookie_file_modified_time
        if difference > timedelta(days=3):
            return False
        return True

    def _initialize_cookies(self):
        """
         Checks cookies file
         Selenium webdriver is initialized with default url "data:".
         add_cookie() requires the current url to be under the same domain pattern as the cookie otherwise
         we get invalid domain exception.
         "data:" will not match any cookie domain, so we have to open site before add any cookie
         """
        with open("cookies.pkl", "rb") as f:
            cookies = pickle.load(f)
        self.get("https://www.instagram.com")
        self.delete_all_cookies()
        for cookie in cookies:
            self.add_cookie(cookie_dict=cookie)

    def write_username(self, username):
        WebDriverWait(self, 10).until(ec.presence_of_element_located((By.XPATH, "//input[@name='username']")))
        user_name_elem = self.find_element(By.XPATH, "//input[@name='username']")
        user_name_elem.clear()
        user_name_elem.send_keys(username)

    def write_password(self, password):
        password_elem = self.find_element(By.XPATH, "//input[@name='password']")
        password_elem.clear()
        password_elem.send_keys(password)
        password_elem.send_keys(Keys.RETURN)

    def get_profile_page(self, profile_page_url: str) -> str:
        self.get(profile_page_url)
        try:
            WebDriverWait(self, 10).until(ec.all_of(
                ec.presence_of_element_located((By.XPATH, "//div[contains(text(), 'followers')]")),
                ec.presence_of_element_located((By.XPATH, "//div[contains(@style,'position: relative; display: flex; "
                                                          "flex-direction: column; padding-bottom: 0px; padding-top: "
                                                          "0px;')]"))
            ))
        except TimeoutException:
            logger.warning("Cannot load the profile page")
        return self.page_source
