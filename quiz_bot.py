import pickle
import sys
import threading
import time
from queue import Queue

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from button import button_click
from claim_prize import claim_prize
from driver import get_driver
from email_utils import get_email, get_verification_code
from mole_game import mole_game_loop
from quiz_game import quiz_loop
from simon_says import simon_says_loop
from vpn import initialize_vpn, terminate_vpn
from words import get_random_word

INPUT_ARGS = "input.pkl"

WAIT_FOR_VERIFICATION_CODE_SECONDS = 60


def load_input_args() -> list:
    with open(INPUT_ARGS, "rb") as f:
        input_args = pickle.load(f)
    return input_args


def get_input_args():
    use_vpn, status, url, code_sender = load_input_args()
    if len(sys.argv) >= 2:
        use_vpn = int(sys.argv[1])
    if len(sys.argv) >= 3:
        status = int(sys.argv[2])
    if len(sys.argv) >= 4:
        url = sys.argv[3]
    if len(sys.argv) >= 5:
        code_sender = sys.argv[4]

    print("use vpn? %s" % use_vpn)
    print("status: %s" % status)
    print("url: %s" % url)
    print("code sender: %s" % code_sender)

    return use_vpn, status, url, code_sender


def switch_to_frame(driver: webdriver.Chrome):
    driver.switch_to.default_content()

    WebDriverWait(driver, 30).until(
        EC.frame_to_be_available_and_switch_to_it((By.ID, "frame"))
    )
    WebDriverWait(driver, 30).until(
        EC.frame_to_be_available_and_switch_to_it((By.ID, "stagecast-loyalty-program"))
    )


def switch_to_frame2(driver: webdriver.Chrome):
    driver.switch_to.default_content()

    WebDriverWait(driver, 30).until(
        EC.frame_to_be_available_and_switch_to_it((By.ID, "frame"))
    )
    WebDriverWait(driver, 30).until(
        EC.frame_to_be_available_and_switch_to_it((By.ID, "frame"))
    )


def input_email_and_accept_terms(driver: webdriver.Chrome, email_addr: str):
    email_input = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "input.form-control"))
    )

    button_click(driver, email_input)
    email_input.send_keys(email_addr)

    checkbox_elements = WebDriverWait(driver, 10).until(
        EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "span.mc-checkmark"))
    )
    for checkbox_element in checkbox_elements:
        button_click(driver, checkbox_element)

    main_button = driver.find_elements(by=By.CLASS_NAME, value="main-button")[0]
    button_click(driver, main_button)


def enter_verification_code(driver: webdriver.Chrome, verification_code: str):
    try:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "input.otp-input"))
        )
        actions = webdriver.ActionChains(driver)
        actions.send_keys(verification_code)
        actions.perform()
    except TimeoutException:
        pass


def start_quiz(driver: webdriver.Chrome, status: int):
    try:
        checkbox_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "span.mc-checkmark"))
        )
        button_click(driver, checkbox_element)

        main_button = driver.find_elements(by=By.CLASS_NAME, value="main-button")[0]
        button_click(driver, main_button)

        name_input = WebDriverWait(driver, 2).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "input.name-input"))
        )
        button_click(driver, name_input)
        name_input.send_keys(get_random_word())
    except (NoSuchElementException, TimeoutException):
        pass

    if status > -3:
        try:
            custom_button = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "button.custom-button")
                )
            )
            button_click(driver, custom_button)
        except TimeoutException:
            pass


def game_loop(driver: webdriver.Chrome) -> int:
    queue = Queue()
    quiz = threading.Thread(
        target=quiz_loop,
        args=(
            driver,
            queue,
        ),
    )
    quiz.start()

    simon_says = threading.Thread(
        target=simon_says_loop,
        args=(
            driver,
            queue,
        ),
    )
    simon_says.start()

    mole = threading.Thread(
        target=mole_game_loop,
        args=(
            driver,
            queue,
        ),
    )
    mole.start()

    threads = [quiz, simon_says, mole]
    statuses = []

    for _ in range(len(threads)):
        statuses.append(queue.get())

    return max(statuses)


def run():
    email_addr, verification_code_email, password = get_email()
    if not email_addr:
        print("No email addresses left to use")
        return
    print(email_addr)

    driver = get_driver()

    use_vpn, status, url, code_sender = get_input_args()

    if use_vpn:
        initialize_vpn()

    try:
        while status <= 0:
            driver.get(url)

            if status == -1:
                status = claim_prize(driver, email_addr)

            print("current status: %s" % status)
            time.sleep(2)

            if use_vpn:
                try:
                    switch_to_frame(driver)
                    skip_button = WebDriverWait(driver, 5).until(
                        EC.visibility_of_element_located(
                            (By.CSS_SELECTOR, "button.bg-transparent")
                        )
                    )
                    button_click(driver, skip_button)
                except:
                    pass
            elif status != -1:
                switch_to_frame(driver)
                input_email_and_accept_terms(driver, email_addr)

                # Wait for email to arrive
                time.sleep(WAIT_FOR_VERIFICATION_CODE_SECONDS)

                verification_code = get_verification_code(
                    verification_code_email, password, code_sender
                )

                switch_to_frame(driver)
                enter_verification_code(driver, verification_code)

            time.sleep(2)
            switch_to_frame2(driver)

            if status == -2:
                status = claim_prize(driver, email_addr)
                break

            start_quiz(driver, status)

            if status > -2:
                status = game_loop(driver)

            current_url = driver.current_url
            if "http" in current_url:
                url = current_url

            if status != -1:
                status = claim_prize(driver, email_addr)
    except Exception as e:
        print(e)
    driver.close()
    if use_vpn:
        terminate_vpn()


if __name__ == "__main__":
    run()
