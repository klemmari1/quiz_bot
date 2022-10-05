import undetected_chromedriver.v2 as uc


def get_driver():
    driver = uc.Chrome(version_main=105)

    return driver
