import pickle
from os import path

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from button import button_click

ANSWER_FILE = "answers.pkl"


def save_answers(answers: dict):
    with open(ANSWER_FILE, "wb") as answer_file:
        pickle.dump(answers, answer_file)


def get_answers() -> dict:
    if path.isfile(ANSWER_FILE):
        with open(ANSWER_FILE, "rb") as answer_file:
            return pickle.load(answer_file)
    else:
        return {}


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


def answer_question(driver: webdriver.Chrome, answers: list, question: str):
    choices = WebDriverWait(driver, 10, 0.01).until(
        EC.visibility_of_all_elements_located((By.CLASS_NAME, "choice"))
    )
    choice = get_choice(question, choices, answers)
    print(get_answer_text(choice))
    button_click(driver, choice)

    correct_answer = get_correct_answer(driver)
    answers[question] = correct_answer


def quiz_loop(driver: webdriver.Chrome, queue) -> int:
    answers = get_answers()
    previous_question = None
    try:
        question_info = (
            WebDriverWait(driver, 10)
            .until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "span.question-info")
                )
            )
            .text
        )
    except:
        queue.put(-1)
        return -1

    question_count = int(question_info.split(" ")[-1])

    question_idx = 0
    while question_idx < question_count:
        try:
            question_element = WebDriverWait(driver, 10, 0.01).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "question-text"))
            )
        except TimeoutException:
            return -1
        if question_element == previous_question:
            continue
        answer_question(driver, answers, question_element.text)
        save_answers(answers)
        previous_question = question_element
        question_idx += 1

    queue.put(0)
    return 0
