import pickle
import time
import sys
from os import path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

ANSWER_FILE = "answers.pkl"
PLAYER_NAME = "SuperSayan"


def get_driver(url):
    driver = webdriver.Chrome()
    driver.get(url)
    driver.switch_to.frame("frame")
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
    driver.execute_script("arguments[0].click();", button)


def start_quiz(driver):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "span.mc-checkmark"))
    )

    checkbox_element = driver.find_element_by_css_selector("span.mc-checkmark")
    button_click(driver, checkbox_element)

    main_button = driver.find_elements_by_class_name("main-button")[0]
    button_click(driver, main_button)

    try:
        name_input = driver.find_element_by_class_name("name-input")
        name_input.send_keys(PLAYER_NAME)
    except NoSuchElementException:
        pass

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "button.custom-button"))
    )

    custom_button = driver.find_element_by_css_selector("button.custom-button")
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
        return
    else:
        return choices[1]


def get_correct_answer(driver):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "is-correct"))
    )
    correct_answer_element = driver.find_element_by_class_name("is-correct")
    return get_answer_text(correct_answer_element)


def answer_question(driver, answers, question):
    choices = driver.find_elements_by_class_name("choice")

    option_a = choices[0]
    option_b = choices[1]
    option_c = choices[2]

    choice = get_choice(question, choices, answers)
    button_click(driver, choice)
    correct_answer = get_correct_answer(driver)
    answers[question] = correct_answer


def quiz_loop(driver, answers):
    previous_question = None
    while True:
        question_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "question-text"))
        )
        if question_element == previous_question:
            continue
        time.sleep(0.5)
        answer_question(driver, answers, question_element.text)
        save_answers(answers)
        previous_question = question_element


def run(url):
    driver = get_driver(url)
    answers = get_answers()

    start_quiz(driver)

    quiz_loop(driver, answers)


if __name__ == "__main__":
    run(sys.argv[1])
