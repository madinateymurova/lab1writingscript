import re
import csv
import os
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


def ensure_csv_header(path):
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp",
                "title",
                "price_text",
                "price_value",
                "url"
            ])


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

    priority_selectors = [
        (By.CSS_SELECTOR, "span.a-price-to-pay span.a-offscreen"),
        (By.CSS_SELECTOR, "#corePriceDisplay_desktop_feature_div span.a-price-to-pay span.a-offscreen"),
        (By.CSS_SELECTOR, "#corePriceDisplay_desktop_feature_div span.a-price span.a-offscreen"),
        (By.ID, "priceblock_dealprice"),
        (By.ID, "priceblock_ourprice"),
        (By.CSS_SELECTOR, "#price_inside_buybox"),
    ]

    def looks_like_usd(t: str) -> bool:
        return t.startswith("$") and re.search(r"\d", t)

    for by, sel in priority_selectors:
        try:
            el = wait.until(EC.presence_of_element_located((by, sel)))
            txt = el.text.strip()
            if looks_like_usd(txt):
                return txt
        except TimeoutException:
            pass

    candidates = []
    try:
        els = driver.find_elements(By.CSS_SELECTOR, "span.a-price span.a-offscreen")
        for el in els:
            txt = el.text.strip()
            if looks_like_usd(txt):
                val = parse_price(txt)
                if val and val > 0:
                    candidates.append((txt, val))
    except Exception:
        pass

    if candidates:
        candidates.sort(key=lambda x: x[1])  # ən ucuz = real current price
        return candidates[0][0]

    try:
        whole = driver.find_element(By.CSS_SELECTOR, "span.a-price-whole").text.strip().replace(",", "")
        frac = driver.find_element(By.CSS_SELECTOR, "span.a-price-fraction").text.strip()
        if whole.isdigit():
            return f"${whole}.{frac if frac else '00'}"
    except NoSuchElementException:
        pass

    raise TimeoutException("Price not found")


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
            raise RuntimeError("CAPTCHA detected")

        title = get_title(driver)
        price_text = get_price(driver)
        price_value = parse_price(price_text)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        ensure_csv_header("amazon_price_history.csv")

        with open("amazon_price_history.csv", "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([now, title, price_text, price_value, product_url])

        print("Product:", title)
        print("Raw price text:", price_text)
        print("Parsed price value:", price_value)

    except Exception as e:
        save_debug(driver)
        print("ERROR:", e)
        print("Debug saved")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()


