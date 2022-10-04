from fake_useragent import UserAgent
from selenium import webdriver
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType


def get_driver():
    options = webdriver.ChromeOptions()

    # mobile_emulation = {
    #     "deviceMetrics": { "width": 360, "height": 640, "pixelRatio": 3.0 },
    #     "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19",
    # }
    # options.add_experimental_option("mobileEmulation", mobile_emulation)

    ua = UserAgent()

    options.add_argument("--window-size=480,860")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--log-level=OFF")
    options.add_argument("disable-infobars")
    options.add_argument(f"user-agent={ua.chrome}")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # driver_path = ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
    driver_path = ChromeDriverManager().install()

    # Anti bot-detection
    with open(driver_path, "rb") as f:
        new_file = f.read().replace(b"$cdc", b"$qbt")
    with open(driver_path, "wb") as f:
        f.write(new_file)

    driver = webdriver.Chrome(driver_path, options=options)

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
