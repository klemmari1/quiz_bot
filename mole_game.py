import threading
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def press_mole_buttons(driver: webdriver.Chrome):
    while True:
        try:
            mole_button = WebDriverWait(driver, 2, 0.00000000001).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.mole-container button.shown:not(.golden)")
                )
            )
            time.sleep(0.2)
            mole_button.click()
            time.sleep(0.15)
        except:
            break


def press_golden_button(driver: webdriver.Chrome):
    while True:
        try:
            golden_button = WebDriverWait(driver, 10, 0.00000000001).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.mole-container button.golden")
                )
            )

            now = time.time()
            while time.time() - now < 2:
                time.sleep(0.2)
                golden_button.click()
                time.sleep(0.15)

            time.sleep(2)
        except:
            break


def mole_game_loop(driver: webdriver.Chrome, queue) -> int:
    try:
        WebDriverWait(driver, 2, 0.0001).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "div.mole-container button.mole")
            )
        )
    except:
        queue.put(-1)
        return -1

    x = threading.Thread(
        target=press_mole_buttons,
        args=(driver,),
    )
    x.start()

    y = threading.Thread(
        target=press_golden_button,
        args=(driver,),
    )
    y.start()

    x.join()

    queue.put(0)
    return 0
