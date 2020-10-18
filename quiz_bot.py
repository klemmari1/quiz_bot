import pickle
import random
import sys
import time
from os import path

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

ANSWER_FILE = "answers.pkl"


def get_input_args():
    url = sys.argv[1]
    player_name = sys.argv[2]
    status = int(sys.argv[3])
    execute_click = int(sys.argv[4])
    name = sys.argv[5]
    email = sys.argv[6]
    print("url: %s" % url)
    print("player_name: %s" % player_name)
    print("status: %s" % status)
    print("execute_click: %s" % execute_click)
    print("name: %s" % name)
    print("email: %s" % email)

    return url, player_name, status, execute_click, name, email


def get_driver(url):
    options = webdriver.ChromeOptions()

    options.add_argument("start-maximized")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--log-level=OFF")
    options.add_argument("disable-infobars")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    WebDriverWait(driver, 5).until(
        EC.frame_to_be_available_and_switch_to_it((By.ID, "frame"))
    )
    return driver


def save_answers(answers):
    with open(ANSWER_FILE, "wb") as answer_file:
        pickle.dump(answers, answer_file)


def get_answers():
    if path.isfile(ANSWER_FILE):
        with open(ANSWER_FILE, "rb") as answer_file:
            return pickle.load(answer_file)
    else:
        return {}


def button_click(driver, button):
    action = webdriver.ActionChains(driver)

    xrand = button.size["width"] * random.uniform(0.1, 0.9)
    yrand = button.size["height"] * random.uniform(0.1, 0.9)

    action.pause(random.uniform(0.05, 0.1)).move_to_element_with_offset(
        button, xrand, yrand
    ).pause(random.uniform(0.001, 0.01)).click_and_hold().pause(
        random.uniform(0.001, 0.01)
    ).release()
    action.perform()


def start_quiz(driver, player_name, status):
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
        name_input.send_keys(player_name)
    except NoSuchElementException:
        pass

    if status > -3:
        custom_button = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "button.custom-button"))
        )
        button_click(driver, custom_button)


def get_answer_text(answer_element):
    return answer_element.find_element_by_tag_name("span").text


def get_choice(question, choices, answers):
    answer = answers.get(question)
    if answer:
        for choice in choices:
            answer_text = get_answer_text(choice)
            if answer_text == answer:
                return choice
    return choices[0]


def get_correct_answer(driver):
    correct_answer_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "is-correct"))
    )
    return get_answer_text(correct_answer_element)


def answer_question(driver, answers, question, execute_click):
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


def quiz_loop(driver, answers, execute_click):
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


def claim_prize(driver: webdriver.Chrome, name: str, email: str, status: int):
    try:
        if status == 0:
            close_button = WebDriverWait(driver, 30).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "span.cta-box button.close-button")
                )
            )
            time.sleep(1)
            button_click(driver, close_button)

        get_prize_button = WebDriverWait(driver, 60 * 60).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "span.prize-box button.main-button")
            )
        )
        time.sleep(1)
        button_click(driver, get_prize_button)

    except TimeoutException:
        return -2

    # Opens another tab

    time.sleep(2)
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(2)

    name_input = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name='name']"))
    )
    name_input.send_keys(name)

    time.sleep(0.5)

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
    time.sleep(5)
    return 1


def run():
    url, player_name, status, execute_click, name, email = get_input_args()

    driver = get_driver(url)
    answers = get_answers()

    while status <= 0:
        print("current status: %s" % status)
        time.sleep(3)

        start_quiz(driver, player_name, status)
        if status > -2:
            status = quiz_loop(driver, answers, execute_click)
        print("current url: %s" % driver.current_url)

        if status != -1:
            status = claim_prize(driver, name, email, status)
        if status < 0:
            driver.refresh()

    driver.close()


if __name__ == "__main__":
    run()
