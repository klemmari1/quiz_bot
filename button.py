import random

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement


def move_to_element(driver: webdriver.Chrome, button: WebElement, pause=True):
    xrand = button.size["width"] * random.uniform(-0.2, 0.2)
    yrand = button.size["height"] * random.uniform(-0.2, 0.2)

    action = webdriver.ActionChains(driver)

    if pause:
        action.pause(random.uniform(0.8, 1.5))
    action.move_to_element_with_offset(button, xrand, yrand).perform()


def button_click(driver: webdriver.Chrome, button: WebElement, pause: bool = True):
    move_to_element(driver, button, pause)

    action = webdriver.ActionChains(driver)

    if pause:
        action.pause(random.uniform(0.2, 0.5))
    action.click_and_hold()
    if pause:
        action.pause(random.uniform(0.1, 0.2))
    action.release()
    action.perform()

    # from selenium.webdriver.common.action_chains import ActionChains
    # from selenium.webdriver.common.actions import interaction
    # from selenium.webdriver.common.actions.action_builder import ActionBuilder
    # from selenium.webdriver.common.actions.pointer_input import PointerInput

    # actions = ActionChains(driver)
    # actions.w3c_actions = ActionBuilder(
    #     driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch")
    # )

    # if pause:
    #     actions.w3c_actions.pointer_action.pause(random.uniform(0.5, 1.0))
    # actions.w3c_actions.pointer_action.move_to(button, xrand, yrand)
    # if pause:
    #     actions.w3c_actions.pointer_action.pause(random.uniform(0.2, 0.5))
    # actions.w3c_actions.pointer_action.click_and_hold()
    # if pause:
    #     actions.w3c_actions.pointer_action.pause(random.uniform(0.1, 0.2))
    # actions.w3c_actions.pointer_action.release()
    # actions.w3c_actions.perform()
