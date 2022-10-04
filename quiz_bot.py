import datetime
import email
import imaplib
import pickle
import random
import sys
import threading
import time
from email.header import decode_header
from os import path
from queue import Queue

from nordvpn_switcher import initialize_VPN, rotate_VPN, terminate_VPN
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from button import button_click
from driver import get_driver
from mole_game import mole_game_loop
from quiz_game import quiz_loop
from simon_says import simon_says_loop

WORD_FILE = "words"
WORDS = open(WORD_FILE).read().splitlines()
TODAY = datetime.date.today().isoformat()

INPUT_ARGS = "input.pkl"
EMAILS = "emails.pkl"
USED_EMAILS = "used_emails.pkl"
ANSWER_FILE = "answers.pkl"

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


def get_used_emails():
    if path.isfile(USED_EMAILS):
        with open(USED_EMAILS, "rb") as used_emails_file:
            try:
                email_dict = pickle.load(used_emails_file)
            except EOFError:
                email_dict = {}
    else:
        email_dict = {}

    return email_dict


def save_email(email_addr):
    email_dict = get_used_emails()

    if TODAY not in email_dict:
        email_dict[TODAY] = []
    email_dict[TODAY].append(email_addr)

    with open(USED_EMAILS, "wb") as used_emails_file:
        pickle.dump(email_dict, used_emails_file)


def get_emails():
    emails = []
    if path.isfile(EMAILS):
        with open(EMAILS, "rb") as emails_file:
            emails = pickle.load(emails_file)
    return emails


def get_unused_emails() -> list:
    emails = get_emails()
    if not emails:
        return []
    used_emails = []
    used_emails_dict = get_used_emails()
    if TODAY in used_emails_dict:
        used_emails = used_emails_dict[TODAY]

    emails = [email_addr for email_addr in emails if email_addr[0] not in used_emails]
    return emails


def get_email():
    emails = get_unused_emails()
    if emails:
        return emails[0]
    else:
        return None, None, None


def get_random_word():
    while True:
        random_word = random.choice(WORDS)
        if "'s" not in random_word:
            break
    return random_word.capitalize()


def get_verification_code(email_address, password, code_sender):
    if "gmail" in email_address:
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
    else:
        imap = imaplib.IMAP4_SSL("outlook.office365.com")
    imap.login(email_address, password)

    _, messages = imap.select("INBOX")
    messages = int(messages[0])  # this is how many mails you have

    # count down as the highest number is latest email
    # this loop is top 5 emails
    for i in range(messages, messages - 5, -1):
        _, msg = imap.fetch(str(i), "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                # decode the email subject
                subject, _ = decode_header(msg["Subject"])[0]
                sender, _ = decode_header(msg.get("From"))[0]
                if isinstance(subject, bytes):
                    try:
                        subject = subject.decode()
                    except:
                        continue

                if sender == code_sender:
                    break

        if sender == code_sender:
            break

    imap.close()
    imap.logout()

    verification_code = subject.split(" ")[0]
    print(verification_code)
    return verification_code


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


def run():
    email_addr, verification_code_email, password = get_email()
    if not email_addr:
        print("No email addresses left to use")
        return
    print(email_addr)

    use_vpn, status, url, code_sender = get_input_args()

    if use_vpn:
        initialize_VPN(
            save=1,
            area_input=["random countries europe 25"],
            skip_settings=1,
        )
        rotate_VPN()

    driver = get_driver()

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
        terminate_VPN()


if __name__ == "__main__":
    run()
