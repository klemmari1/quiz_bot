import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from button import button_click
from email_utils import save_email


def claim_prize(driver: webdriver.Chrome, email_addr: str):
    try:
        claim_prize_button = WebDriverWait(driver, 50).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "div.prize-overlay button.main-button")
            )
        )
        button_click(driver, claim_prize_button)
    except:
        return -1

    # Opens another tab

    time.sleep(2)
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(2)

    name_input = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name='name']"))
    )
    name_input.send_keys(get_random_word())

    time.sleep(0.5)

    email_input = driver.find_element(by=By.CSS_SELECTOR, value="input[name='email']")
    email_input.send_keys(email_addr)

    time.sleep(0.5)

    region_select = driver.find_element(
        by=By.CSS_SELECTOR, value="select[name='gameServer']"
    )
    button_click(driver, region_select)

    time.sleep(0.5)

    euw = driver.find_element(
        by=By.CSS_SELECTOR, value="option[value='Europe West (EUW)']"
    )
    euw.click()

    time.sleep(0.5)

    checkmark = driver.find_element(by=By.CLASS_NAME, value="mc-checkmark")
    button_click(driver, checkmark)

    time.sleep(0.5)

    submit_button = driver.find_element(by=By.CSS_SELECTOR, value="input.custom-button")
    button_click(driver, submit_button)

    save_email(email_addr)

    time.sleep(5)
    return 1
