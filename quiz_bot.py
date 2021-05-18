import datetime
import pickle
import random
import sys
import time
from os import path

from nordvpn_switcher import initialize_VPN, rotate_VPN, terminate_VPN
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

ANSWER_FILE = "answers.pkl"
WORD_FILE = "/usr/share/dict/words"
WORDS = open(WORD_FILE).read().splitlines()

EMAILS = ".emails"
USED_EMAILS = "used_emails.pkl"
TODAY = datetime.date.today().isoformat()


def get_input_args():
    url = sys.argv[1]
    status = int(sys.argv[2])
    execute_click = int(sys.argv[3])
    print("url: %s" % url)
    print("status: %s" % status)
    print("execute_click: %s" % execute_click)

    return url, status, execute_click


def get_url_and_wait_for_frame(driver: webdriver.Chrome, url: str, status: int = 0):
    driver.get(url)
    try:
        WebDriverWait(driver, 30).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, "frame"))
        )
    except TimeoutException:
        return -3
    return status


def get_driver():
    options = webdriver.ChromeOptions()

    options.add_argument("start-maximized")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--log-level=OFF")
    options.add_argument("disable-infobars")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=options)
    return driver


def save_answers(answers: dict):
    with open(ANSWER_FILE, "wb") as answer_file:
        pickle.dump(answers, answer_file)


def get_answers():
    if path.isfile(ANSWER_FILE):
        with open(ANSWER_FILE, "rb") as answer_file:
            return pickle.load(answer_file)
    else:
        return {}


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


def save_email(email):
    email_dict = get_used_emails()

    if TODAY not in email_dict:
        email_dict[TODAY] = []
    email_dict[TODAY].append(email)

    with open(USED_EMAILS, "wb") as used_emails_file:
        pickle.dump(email_dict, used_emails_file)


def get_emails():
    if path.isfile(EMAILS):
        with open(EMAILS, "r") as emails_file:
            emails = emails_file.read().splitlines()

        used_emails = []
        used_emails_dict = get_used_emails()
        if TODAY in used_emails_dict:
            used_emails = used_emails_dict[TODAY]

        emails = [email for email in emails if email not in used_emails]
        return emails
    else:
        return []


def get_random_word():
    while True:
        random_word = random.choice(WORDS)
        if "'s" not in random_word:
            break
    return random_word.capitalize()


def button_click(driver: webdriver.Chrome, button: WebElement):
    action = webdriver.ActionChains(driver)

    xrand = button.size["width"] * random.uniform(0.1, 0.9)
    yrand = button.size["height"] * random.uniform(0.1, 0.9)

    action.pause(random.uniform(0.8, 2)).move_to_element_with_offset(
        button, xrand, yrand
    ).pause(random.uniform(0.1, 0.5)).click_and_hold().pause(
        random.uniform(0.1, 0.2)
    ).release()
    action.perform()


def start_quiz(driver: webdriver.Chrome, status: int):
    try:
        checkbox_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "span.mc-checkmark"))
        )
        button_click(driver, checkbox_element)

        main_button = driver.find_elements_by_class_name("main-button")[0]
        button_click(driver, main_button)
    except TimeoutException:
        pass

    try:
        name_input = driver.find_element_by_class_name("name-input")
        button_click(driver, name_input)
        name_input.send_keys(get_random_word())
    except NoSuchElementException:
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


def get_answer_text(answer_element: WebElement):
    return answer_element.find_element_by_tag_name("span").text


def get_choice(question: str, choices: list, answers: dict):
    answer = answers.get(question)
    if answer:
        for choice in choices:
            answer_text = get_answer_text(choice)
            if answer_text == answer:
                return choice
    return choices[0]


def get_correct_answer(driver: webdriver.Chrome):
    correct_answer_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "is-correct"))
    )
    return get_answer_text(correct_answer_element)


def answer_question(
    driver: webdriver.Chrome, answers: list, question: str, execute_click: int
):
    choices = WebDriverWait(driver, 10, 0.01).until(
        EC.visibility_of_all_elements_located((By.CLASS_NAME, "choice"))
    )
    choice = get_choice(question, choices, answers)
    print(get_answer_text(choice))
    if execute_click:
        button_click(driver, choice)
    else:
        driver.execute_script("arguments[0].style.color = 'green';", choice)

    correct_answer = get_correct_answer(driver)
    answers[question] = correct_answer


def quiz_loop(driver: webdriver.Chrome, answers: list, execute_click: int):
    previous_question = None
    question_count = 0
    while question_count < 7:
        try:
            question_element = WebDriverWait(driver, 10, 0.01).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "question-text"))
            )
        except TimeoutException:
            return -1
        if question_element == previous_question:
            continue
        answer_question(driver, answers, question_element.text, execute_click)
        save_answers(answers)
        previous_question = question_element
        question_count += 1
    return 0


def claim_prize(driver: webdriver.Chrome, status: int):
    close_button = None

    try:
        if status == 0:
            close_button = WebDriverWait(driver, 30).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "span.cta-box button.close-button")
                )
            )
    except TimeoutException:
        return -2

    time.sleep(1)

    if close_button:
        button_click(driver, close_button)

    try:
        get_prize_button = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "span.prize-box button.main-button")
            )
        )
    except:
        return 1

    time.sleep(1)
    button_click(driver, get_prize_button)

    # Opens another tab

    time.sleep(2)
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(2)

    name_input = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name='name']"))
    )
    name_input.send_keys(get_random_word())

    time.sleep(0.5)

    emails = get_emails()
    if len(emails):
        email = emails[0]
    else:
        return 1

    email_input = driver.find_element_by_css_selector("input[name='email']")
    email_input.send_keys(email)

    time.sleep(0.5)

    region_select = driver.find_element_by_css_selector("select[name='gameServer']")
    button_click(driver, region_select)

    time.sleep(0.5)

    euw = driver.find_element_by_css_selector("option[value='Europe West (EUW)']")
    euw.click()

    time.sleep(0.5)

    checkmark = driver.find_element_by_class_name("mc-checkmark")
    button_click(driver, checkmark)

    time.sleep(0.5)

    submit_button = driver.find_element_by_css_selector("input.custom-button")
    button_click(driver, submit_button)

    save_email(email)

    time.sleep(5)
    return 1


def run():

    emails = get_emails()
    if not emails:
        return

    initialize_VPN(save=1, area_input=["complete rotation"], skip_settings=1)
    rotate_VPN()

    url, status, execute_click = get_input_args()

    driver = get_driver()
    answers = get_answers()

    while status <= 0:
        status = get_url_and_wait_for_frame(driver, url, status)
        print("current status: %s" % status)
        time.sleep(3)

        start_quiz(driver, status)
        if status > -2:
            status = quiz_loop(driver, answers, execute_click)
        current_url = driver.current_url
        if "http" in current_url:
            url = current_url
        print(current_url)

        if status != -1:
            status = claim_prize(driver, status)

    driver.close()
    terminate_VPN()


if __name__ == "__main__":
    run()
