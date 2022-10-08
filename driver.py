import undetected_chromedriver.v2 as uc
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager


def get_driver():
    options = uc.ChromeOptions()
    options.add_argument("--no-first-run --no-service-autorun --password-store=basic")

    chrome_manager = ChromeDriverManager()
    version = chrome_manager.driver.get_latest_release_version()
    version_main = version.split(".")[0]
    driver = uc.Chrome(version_main=version_main, options=options)
    driver.maximize_window()

    stealth(
        driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    return driver
