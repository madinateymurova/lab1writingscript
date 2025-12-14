import re
import csv
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager


def parse_price(text: str):
    if not text:
        return None
    cleaned = text.replace(",", "")
    m = re.search(r"(\d+(?:\.\d{1,2})?)", cleaned)
    return float(m.group(1)) if m else None


def is_captcha_or_blocked(driver) -> bool:
    page = driver.page_source.lower()
    keywords = [
        "captcha",
        "enter the characters you see below",
        "sorry, we just need to make sure you're not a robot",
        "robot check",
    ]
    return any(k in page for k in keywords)


def safe_click_if_exists(driver, by, selector, timeout=3):
    try:
        el = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, selector))
        )
        driver.execute_script("arguments[0].click();", el)
        return True
    except Exception:
        return False


def get_title(driver) -> str:
    el = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "productTitle"))
    )
    return el.text.strip()


def get_price(driver) -> str:
    wait = WebDriverWait(driver, 15)

    selectors = [
        (By.CSS_SELECTOR, "span.a-price span.a-offscreen"),
        (By.CSS_SELECTOR, "#corePriceDisplay_desktop_feature_div span.a-offscreen"),
        (By.CSS_SELECTOR, "#corePrice_feature_div span.a-offscreen"),
        (By.CSS_SELECTOR, "#apex_desktop span.a-price span.a-offscreen"),
        (By.CSS_SELECTOR, "#price_inside_buybox"),
        (By.ID, "priceblock_ourprice"),
        (By.ID, "priceblock_dealprice"),
    ]

    for by, sel in selectors:
        try:
            el = wait.until(EC.presence_of_element_located((by, sel)))
            txt = el.text.strip()
            if txt:
                return txt
        except TimeoutException:
            pass

    try:
        whole = driver.find_element(By.CSS_SELECTOR, "span.a-price-whole").text.strip().replace(",", "")
        frac = driver.find_element(By.CSS_SELECTOR, "span.a-price-fraction").text.strip()
        if whole:
            return f"${whole}.{frac if frac else '00'}"
    except NoSuchElementException:
        pass

    try:
        link = driver.find_element(By.PARTIAL_LINK_TEXT, "See all buying options")
        driver.execute_script("arguments[0].click();", link)
        el = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.a-price span.a-offscreen")))
        txt = el.text.strip()
        if txt:
            return txt
    except Exception:
        pass

    raise TimeoutException("Price element not found with known selectors.")


def save_debug(driver):
    try:
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
    except Exception:
        pass
    try:
        driver.save_screenshot("debug_screenshot.png")
    except Exception:
        pass


def main():
    product_url = "https://www.amazon.com/dp/B0CGY3VF3K"

    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get("https://www.amazon.com")

        safe_click_if_exists(driver, By.XPATH, "//*[text()='Continue shopping']", timeout=5)

        driver.get(product_url)

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        if is_captcha_or_blocked(driver):
            save_debug(driver)
            raise RuntimeError(
                "CAPTCHA / robot check detected. Debug saved: debug_page.html and debug_screenshot.png"
            )

        title = get_title(driver)
        price_text = get_price(driver)
        price_value = parse_price(price_text)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open("amazon_price_history.csv", "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([now, title, price_text, price_value, product_url])

        print("Product:", title)
        print("Price:", price_text)
        print("Saved to amazon_price_history.csv")

    except Exception as e:
        save_debug(driver)
        print("ERROR:", e)
        print("Debug saved: debug_page.html and debug_screenshot.png")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()

