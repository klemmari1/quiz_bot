import pickle
import sys
import time
from os import path

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

ANSWER_FILE = "answers.pkl"


def get_input_args():
    url = sys.argv[1]
    player_name = "Test123"
    execute_click = 1  # 0 / 1
    if len(sys.argv) >= 3:
        player_name = sys.argv[2]
    if len(sys.argv) >= 4:
        execute_click = int(sys.argv[3])
    return url, player_name, execute_click


def get_driver(url):
    options = webdriver.ChromeOptions()

    options.add_argument("start-maximized")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-blink-features=AutomationControlled")
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

    action.move_to_element(button).pause(0.005).click_and_hold(button).pause(
        0.005
    ).release(button)
    action.perform()


def start_quiz(driver, player_name):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "span.mc-checkmark"))
    )

    checkbox_element = driver.find_element_by_css_selector("span.mc-checkmark")
    button_click(driver, checkbox_element)

    main_button = driver.find_elements_by_class_name("main-button")[0]
    button_click(driver, main_button)

    try:
        name_input = driver.find_element_by_class_name("name-input")
        button_click(driver, name_input)
        name_input.send_keys(player_name)
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
    return choices[0]


def get_correct_answer(driver):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "is-correct"))
    )
    correct_answer_element = driver.find_element_by_class_name("is-correct")
    return get_answer_text(correct_answer_element)


def answer_question(driver, answers, question, execute_click):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "choice"))
    )
    choices = driver.find_elements_by_class_name("choice")

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
        question_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "question-text"))
        )
        if question_element == previous_question or not getattr(
            question_element, "text"
        ):
            continue
        answer_question(driver, answers, question_element.text, execute_click)
        save_answers(answers)
        previous_question = question_element
        question_count += 1


def run():
    url, player_name, execute_click = get_input_args()

    driver = get_driver(url)
    answers = get_answers()

    time.sleep(2)

    start_quiz(driver, player_name)
    quiz_loop(driver, answers, execute_click)

    print(driver.current_url)
    time.sleep(3)
    driver.close()


if __name__ == "__main__":
    run()
