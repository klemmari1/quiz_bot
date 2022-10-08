import time

from babel.numbers import parse_number
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from button import button_click


def play_simon_says(driver: webdriver.Chrome, blinks):
    blink_idx = 0
    correct_squares = []
    while blink_idx < blinks:
        try:
            square = WebDriverWait(driver, 10, 0.001).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "div.square-container div.blink")
                )
            )
            correct_squares.append(square)
            blink_idx += 1
            time.sleep(0.4)
        except:
            return False

    for square in correct_squares:
        button_click(driver, square)

    return True


def simon_says_loop(driver: webdriver.Chrome, queue, target_score: int = 3000) -> int:
    try:
        WebDriverWait(driver, 2, 0.0001).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.square-container"))
        )

        blinks = 2
        time.sleep(4)

        while True:
            is_playing = play_simon_says(driver, blinks)

            if not is_playing:
                return -1

            score_info = (
                WebDriverWait(driver, 5, 0.001)
                .until(
                    EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, "div.info-row span.right-info")
                    )
                )
                .text
            )
            score = score_info.split(" ")[0]
            score_int = parse_number(score, locale="de_DE")

            if score_int > target_score:
                time.sleep(30)
                break

            blinks += 1

    except:
        queue.put(-1)
        return -1

    queue.put(0)
    return 0
