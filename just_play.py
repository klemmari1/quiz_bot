import sys
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from quiz_bot import (
    button_click,
    enter_verification_code,
    game_loop,
    get_answers,
    get_driver,
    get_emails,
    get_input_args,
    get_verification_code,
    input_email_and_accept_terms,
    switch_to_frame,
    switch_to_frame2,
)


def push_replay_button(driver: webdriver.Firefox):
    try:
        close_button = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "div.prize-overlay div.popup-box div.popup-header button.close-button",
                )
            )
        )
        button_click(driver, close_button)
    except TimeoutException:
        pass

    try:
        checkbox_element = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "span.mc-checkmark"))
        )
        button_click(driver, checkbox_element)

        main_button = driver.find_elements_by_class_name("main-button")[0]
        button_click(driver, main_button)
    except TimeoutException:
        pass

    try:
        custom_buttons = WebDriverWait(driver, 5).until(
            EC.visibility_of_all_elements_located(
                (By.CSS_SELECTOR, "button.custom-button")
            )
        )
        custom_button = custom_buttons[-1]
        button_click(driver, custom_button)
    except TimeoutException:
        pass


def get_email():
    email_idx = int(sys.argv[1])
    return get_emails()[email_idx]


def run():
    email_addr, verification_code_email, password = get_email()
    if not email_addr:
        return
    print(email_addr)

    _, _, url, code_sender = get_input_args()

    driver = get_driver()
    answers = get_answers()

    status = 0

    while status <= 0:
        driver.get(url)
        print("current status: %s" % status)
        time.sleep(2)

        if status != -1:
            switch_to_frame(driver)
            input_email_and_accept_terms(driver, email_addr)

            # Wait for email to arrive
            time.sleep(8)

            verification_code = get_verification_code(
                verification_code_email, password, code_sender
            )

            switch_to_frame(driver)
            enter_verification_code(driver, verification_code)

        time.sleep(2)
        switch_to_frame2(driver)

        push_replay_button(driver)

        if status > -2:
            status = game_loop(driver, answers)

        current_url = driver.current_url
        if "http" in current_url:
            url = current_url

        time.sleep(5)

        status = -1

    driver.close()


if __name__ == "__main__":
    run()
