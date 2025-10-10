# lab1writingscript

# This Python script uses Selenium WebDriver to open a specific Amazon product page and automatically extract the product’s title and price.It also handles the “Continue shopping” pop-up if it appears, and safely continues if the pop-up or price is not found, thanks to try/except blocks.


# These lines import the required Python libraries.

# selenium → for web automation.

# webdriver_manager → automatically installs ChromeDriver.

# TimeoutException and NoSuchElementException → used for error handling when elements are not found.
![Alt text](https://github.com/madinateymurova/lab1writingscript/blob/main/Screenshot%202025-10-10%20154257.png?raw=true)

# ChromeDriverManager().install() automatically downloads the correct ChromeDriver version.

# Service() is a modern Selenium way to start ChromeDriver.

# webdriver.Chrome(service=service) opens a Chrome browser controlled by Selenium.

![](https://github.com/madinateymurova/lab1writingscript/blob/main/Screenshot%202025-10-10%20154528.png?raw=true)

# Maximizes the browser window so that all elements on Amazon’s page are fully visible and clickable.
# Opens the Amazon homepage in the browser.driver.get(url) navigates to any given URL.

![](https://github.com/madinateymurova/lab1writingscript/blob/main/Screenshot%202025-10-10%20154832.png?raw=true)

# The script waits up to 5 seconds for the “Continue shopping” button on Amazon to appear.If the button is found → it is clicked automatically and a success message is printed.If not found → a TimeoutException is caught, a warning is printed, and the script continues.

![](https://github.com/madinateymurova/lab1writingscript/blob/main/Screenshot%202025-10-10%20155303.png?raw=true)

# Navigates to the specific product page you want to track.
![](https://github.com/madinateymurova/lab1writingscript/blob/main/Screenshot%202025-10-10%20155606.png?raw=true)

# Waits up to 10 seconds for the product title to appear.Loops through several possible price element IDs to find the price.If found → prints the title and price.If not found → prints "Price not found".Handles TimeoutException if elements fail to load.
![](https://github.com/madinateymurova/lab1writingscript/blob/main/Screenshot%202025-10-10%20155831.png?raw=true)

