import time

from selenium.webdriver.common.by import By
from selenium import webdriver


# Custom ExpectedConditions here

def height_is_greater_than(previous_height: int):
    def _predicate(driver: webdriver.Chrome):
        height = driver.execute_script("return document.body.scrollHeight")
        if height != previous_height:
            return True
        return False
    return _predicate
