import bs4
import sys
import time
import smtplib
import platform
import os
import signal
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, TimeoutException, \
    WebDriverException, ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

# Read environment variables (provide defaults as needed)
url = os.environ.get("BESTBUY_URL", "https://www.bestbuy.com/site/amd-ryzen-9-7900x-12-core-24-thread-4-7-ghz-5-6-ghz-max-boost-socket-am5-desktop-processor-silver/6519473.p?skuId=6519473")
EMAIL_FROM = os.environ.get("EMAIL_FROM", "your_email@example.com")
EMAIL_TO = os.environ.get("EMAIL_TO", "recipient@example.com")
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "your_email_password")

# ---------------------------------------------Please Read--------------------------------------------------------------

# Updated: 6/15/2021

# Hello everyone! Welcome to my Best Buy script.
# Let's go over the checklist for the script to run properly.
#   1. Product URL
#   2. Firefox Profile
#   3. Credit Card CVV Number
#   4. Twilio Account (Optional)

# This Script only accepts Product URL's that look like this. I hope you see the difference between page examples.

# Example 1 - Nvidia RTX 3080:
# https://www.bestbuy.com/site/nvidia-geforce-rtx-3080-10gb-gddr6x-pci-express-4-0-graphics-card-titanium-and-black/6429440.p?skuId=6429440
# Example 2 - PS5:
# https://www.bestbuy.com/site/sony-playstation-5-console/6426149.p?skuId=6426149
# Example 3 - Ryzen 5600x:
# https://www.bestbuy.com/site/amd-ryzen-5-5600x-4th-gen-6-core-12-threads-unlocked-desktop-processor-with-wraith-stealth-cooler/6438943.p?skuId=6438943

# This Script does not accept Product URL's that look like this.
# https://www.bestbuy.com/site/searchpage.jsp?st=rtx+3080&_dyncharset=UTF-8&_dynSessConf=&id=pcat17071&type=page&sc=Global&cp=1&nrp=&sp=&qp=&list=n&af=true&iht=y&usc=All+Categories&ks=960&keys=keys

# Highly Recommend To set up Twilio Account to receive text messages. So if bot doesn't work you'll at least get a phone
# text message with the url link. You can click the link and try manually purchasing on your phone.

# Twilio is free. Get it Here.
# www.twilio.com/referral/BgLBXx

# -----------------------------------------------Steps To Complete------------------------------------------------------

# Test Link (Ryzen 5800x) - The Ryzen 5800x is always available and still uses Bestbuy's Queue System.
# https://www.bestbuy.com/site/amd-ryzen-7-5800x-4th-gen-8-core-16-threads-unlocked-desktop-processor-without-cooler/6439000.p?skuId=6439000
test_mode = False  # Set test_mode to True when testing bot checkout process, and set it to False when your done testing.
headless_mode = True  # Set False for testing. If True, it will hide Firefox in background for faster checkout speed.
webpage_refresh_timer = 3  # Default 3 seconds. If slow internet and the page isn't fully loading, increase this.
bot_started = False

# 1. Product URL
# url = 'https://www.bestbuy.com/site/lg-ultragear-45-oled-curved-wqhd-240hz-0-03ms-freesync-and-nvidia-g-sync-compatible-gaming-monitor-with-hdr10-black/6530356.p?skuId=6530356'
# url = 'https://www.bestbuy.com/site/amd-ryzen-9-7900x-12-core-24-thread-4-7-ghz-5-6-ghz-max-boost-socket-am5-desktop-processor-silver/6519473.p?skuId=6519473'


# 2. Firefox Profile
def create_driver():
    options = Options()
    options.headless = headless_mode
    if platform.system() != "Linux":
        # Set your Windows Firefox profile only when not on Linux.
        options.add_argument("-profile")
        options.add_argument(r"C:\Users\Alen\AppData\Roaming\Mozilla\Firefox\Profiles\w54zfjay.default-release")
    service = Service(GeckoDriverManager().install())
    web_driver = webdriver.Firefox(options=options, service=service)
    return web_driver


def send_email(subject, body, to_addr, from_addr, smtp_server, smtp_port, password):
    """
    Send an email using SMTP.
    """
    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(from_addr, password)
        server.send_message(msg)
    print("Email sent! ✅")

def send_notification():
    try:
        print("Sending Email Notification... 📧")
        subject = "BestBuy Inventory Notification"
        body = f"Your item is in the cart! You just have to checkout: {url}"
        send_email(subject, body, 
                   to_addr=EMAIL_TO,
                   from_addr=EMAIL_FROM,
                   smtp_server=SMTP_SERVER, 
                   smtp_port=SMTP_PORT,
                   password=EMAIL_PASSWORD)
    except Exception as e:
        print(f"Failed to send email: {e} ⛔")
        
def send_start_notification():
    """Send an email notification that the bot has started."""
    subject = "BestBuy Bot Started"
    body = """
    <html>
    <body>
        <h2>BestBuy Bot Notification</h2>
        <p>The BestBuy bot has started successfully.</p>
    </body>
    </html>
    """
    send_email(subject, body, to_addr=EMAIL_TO,
               from_addr=EMAIL_FROM,
               smtp_server=SMTP_SERVER,
               smtp_port=SMTP_PORT,
               password=EMAIL_PASSWORD)

def send_stop_notification(reason):
    """Send an email notification that the bot is stopping."""
    subject = "BestBuy Bot Stopped"
    body = f"The BestBuy bot has been stopped. Reason: {reason}"
    send_email(subject, body, to_addr=EMAIL_TO,
               from_addr=EMAIL_FROM,
               smtp_server=SMTP_SERVER,
               smtp_port=SMTP_PORT,
               password=EMAIL_PASSWORD)

def time_sleep(x, driver):
    """Sleep timer for page refresh."""
    for i in range(x, -1, -1):
        sys.stdout.write('\r')
        sys.stdout.write('\nMonitoring Page. Refreshing in {:2d} seconds'.format(i))
        sys.stdout.flush()
        time.sleep(1)
    driver.execute_script('window.localStorage.clear();')
    driver.refresh()


def extract_page():
    """bs4 page parser."""
    html = driver.page_source
    soup = bs4.BeautifulSoup(html, 'html.parser')
    return soup


def wait_for_page_load(driver, timeout=30):
    """Wait until the page has fully loaded."""
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

def searching_for_product(driver):
    """Scanning for product."""
    driver.get(url)
    wait_for_page_load(driver)
    
    print("\nWelcome to Best Buy Bot! 🚀 Join our Discord for real-time updates on GPU and console drops! ❤️")
    print("Bot deployed successfully! ✅")
    
    # Get page title
    page_title = driver.title
    print(f"\n👁️ Looking for: {page_title}")

    while True:
        wait_for_page_load(driver)
        soup = extract_page()
        wait = WebDriverWait(driver, 15)
        wait2 = WebDriverWait(driver, 15)

        try:
            print("\n\nWaiting for 'Add To Cart' button to appear... ⏳")
            add_to_cart_button = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "[data-test-id='add-to-cart'].relative.border-xs.border-solid.rounded-lg.justify-center.items-center.self-start.flex.flex-row.cursor-pointer.px-300.py-100.bg-comp-surface-secondary-emphasis.border-comp-outline-secondary-muted.w-full")
                )
            )

            if add_to_cart_button:
                print("'Add To Cart' button loaded! ✅\n")

                while True:
                    try:
                        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-test-id='add-to-cart']")))
                        time.sleep(1)
                        add_to_cart_button = driver.find_element(By.CSS_SELECTOR, "[data-test-id='add-to-cart']")
                        print("Attempting to click the 'Add To Cart' button... 🔄")
                        add_to_cart_button.click()
                        print("'Add To Cart' button clicked successfully! ✅\n")
                        break
                    except (NoSuchElementException, TimeoutException) as error:
                        print(f"Could not click 'Add To Cart': {error} ⛔")

                driver.get('https://www.bestbuy.com/cart')
                wait_for_page_load(driver)

                try:
                    wait.until(EC.presence_of_element_located(
                        (By.XPATH, "//*[@class='btn btn-lg btn-block btn-primary']")
                    ))
                    time.sleep(1)
                    checkout_button = driver.find_element(By.XPATH, "//*[@class='btn btn-lg btn-block btn-primary']")
                    checkout_button.click()
                    print("Item is still in your cart! 🛒✅\n")
                except (NoSuchElementException, TimeoutException):
                    print("Item is not in cart anymore. Retrying... ⛔🔄")
                    time_sleep(3, driver)
                    searching_for_product(driver)

                print("Item added to cart! ✅\n")
                
                # Sending Email Notification to let you know you're in the queue system.
                try:
                    print("Sending Email Notification... 📧")
                    send_notification()
                except Exception as e:
                    print(f"Failed to send email: {e} ⛔")
                
                # time.sleep(1800)
                print("Closing browser... 👋")
                driver.quit()
            else:
                print("Unable to locate 'Add To Cart' button. Refreshing page... ⛔🔄")
                time_sleep(webpage_refresh_timer, driver)

        except:
            print("Product is currently unavailable. ⛔")

        time_sleep(webpage_refresh_timer, driver)


def handle_exit(signum, frame):
    """Signal handler for graceful termination."""
    print(f"Received termination signal ({signum}). Shutting down...")
    send_stop_notification(f"Terminated by signal {signum}")
    # Make sure to quit the driver if it exists
    try:
        driver.quit()
    except Exception:
        pass
    sys.exit(0)

# Register termination signal handlers
signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

if __name__ == '__main__':
    # Send notification at startup
    try:
        send_start_notification()
    except Exception as e:
        print(f"Failed to send start notification: {e}")

    driver = create_driver()
    try:
        searching_for_product(driver)
    except Exception as e:
        print(f"Bot encountered an error: {e}")
        send_stop_notification(str(e))
        driver.quit()
        sys.exit(1)