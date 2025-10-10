from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Open Chrome browser using Service
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

driver.maximize_window()  # Maximize browser window to ensure all elements are visible

# Open Amazon homepage
driver.get("https://www.amazon.com")

# If a pop-up appears, click the "Continue shopping" button
try:
    continue_button = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, "//*[text()='Continue shopping']"))
    )
    continue_button.click()
    print("✅ 'Continue shopping' button clicked.")
except TimeoutException:
    print("⚠️ 'Continue shopping' button not found, continuing...")

# Product URL to track
product_url = 'https://www.amazon.com/LEGO-Creator-Forest-Animals-Transforms/dp/B0CGY3VF3K/?_encoding=UTF8&pd_rd_w=YRzFt&content-id=amzn1.sym.9929d3ab-edb7-4ef5-a232-26d90f828fa5&pf_rd_p=9929d3ab-edb7-4ef5-a232-26d90f828fa5&pf_rd_r=WZPJXWJT3BJTNDRNH8KJ&pd_rd_wg=aQ37x&pd_rd_r=4268b589-9572-458e-a005-24993e383b00&ref_=pd_hp_d_btf_crs_zg_bs_165793011'
driver.get(product_url)

# Extract product title and price
try:
    # Wait for the product title to appear
    title = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "productTitle"))
    ).text.strip()

    # Check multiple IDs for price
    price = None
    possible_price_ids = ["priceblock_ourprice", "priceblock_dealprice", "price_inside_buybox"]
    for pid in possible_price_ids:
        try:
            price = driver.find_element(By.ID, pid).text.strip()
            if price:
                break
        except NoSuchElementException:
            continue
    if not price:
        price = "Price not found"

    # Print results
    print(f"\nProduct: {title}")
    print(f"Price: {price}")

except TimeoutException:
    print("⚠️ Product information not found.")

# Close the browser
driver.quit()
