import time

from selenium.webdriver.common.by import By
from selenium import webdriver


class IsPaddingValueNotEqual:
    def __init__(self, initial_value: str = "0px"):
        self.initial_value = initial_value

    def __call__(self, driver: webdriver.Chrome):
        parent = driver.find_element(By.XPATH,
                                          "//div/div/div/div[1]/div/div/div/div[1]/section/main/div/div[3]/article/div[1]/div")
        padding_value = parent.value_of_css_property("padding-top")
        if padding_value == "0px":
            time.sleep(5)
            return True
        return self.initial_value != padding_value


class IsChildElementsNotEqual:
    def __init__(self, initial_element_list: list):
        self.initial_element_list = initial_element_list

    def __call__(self, driver: webdriver.Chrome):
        parent = driver.find_element(By.XPATH,
                                          "//div/div/div/div[1]/div/div/div/div[1]/section/main/div/div[3]/article/div[1]/div")
        child_elements = parent.find_elements(By.XPATH, "//div/img")
        print(len(child_elements))
        return len(self.initial_element_list) != len(child_elements)


def document_height_is_not_equal(previous_height: int):
    def _predicate(driver: webdriver.Chrome):
        height = driver.execute_script("return document.body.scrollHeight")
        if height != previous_height:
            return True
        return False
    return _predicate
