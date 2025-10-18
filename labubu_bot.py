import subprocess


import time
import socket
import os
import random
from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError
from dotenv import load_dotenv

import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import argparse


load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, default=9222, help="Remote debugging port for Chrome")
parser.add_argument("--email_flag", action="store_true", default=False, help="Enable email notifications")
args = parser.parse_args()



CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
URL = os.getenv("URL")
CART_URL = os.getenv("CART_URL")
DEBUG = os.getenv("DEBUG") == "True"

BOX_ID = ""  # Example box ID, replace with actual one

REMOTE_DEBUG_PORT = args.port
USER_DATA_DIR = f"/tmp/chrome-popmart_{REMOTE_DEBUG_PORT}"
CDP_URL = f"http://localhost:{REMOTE_DEBUG_PORT}"
WAIT_TIME = 1000  # milliseconds
EMAIL_RECEIVER_NOTIFY = os.getenv("EMAIL_RECEIVER_NOTIFY").split(",")
EMAIL_RECEIVER_ADD_TO_CART = os.getenv("EMAIL_RECEIVER_ADD_TO_CART").split(",")
EMAIL_FLAG = args.email_flag  # Set to True to enable email notifications


PATTERN = r"Reserving Time:\s*(\d+)m\s+(\d+)s"


def launch_chrome():
    print("🚀 Launching Chrome with remote debugging...")
    proc = subprocess.Popen([
        CHROME_PATH,
        f"--remote-debugging-port={REMOTE_DEBUG_PORT}",
        f"--user-data-dir={USER_DATA_DIR}",
        "--no-first-run",
        "--log-level=3",  # Only fatal errors
        "--no-default-browser-check",
        "--disable-cloud-import",  # optional
        "--disable-notifications",  # disable push
        "--disable-background-networking",  # disable sync & GCM
        "--disable-webrtc",  # disable WebRTC
        "--disable-translate",  # disable translation prompts
    ],   
    stdout=subprocess.DEVNULL,  # Always suppress stdout (optional)
    stderr=None if DEBUG else subprocess.DEVNULL)


    wait_for_cdp_port(REMOTE_DEBUG_PORT)
    wait_for_cdp_port(REMOTE_DEBUG_PORT)


def send_email(subject, body, receiver):
    if EMAIL_FLAG is False:
        return 
    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = ", ".join(receiver)
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, receiver, msg.as_string())
        print("📧 Email sent successfully.")
    except Exception as e:
        print(f"❌ Failed to send email")
    return

def wait_for_cdp_port(port, timeout=10):
    print("⏳ Waiting for Chrome to open CDP port...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection(("localhost", port), timeout=1):
                print("✅ Chrome CDP port is open.")
                return
        except OSError:
            time.sleep(0.5)
    raise RuntimeError("❌ Timed out waiting for Chrome remote debugging port.")

def next_page(page):

    img = page.locator("img.index_nextImg__PTfZF").first
    if img.is_visible():
        try:
            img.click(timeout=WAIT_TIME)
            print("➡️ Clicked next page button.")
        except Exception as e:
            pass
    return 

def next_url(page):
    three_digits = f"{random.randint(0, 999):03d}"
    box_idx = ""
    try:
        locator = page.locator('div.index_boxNumber__7k_Uf').first
        if locator.is_visible():
            text = locator.inner_text().strip()
            if text.startswith("No."):
                box_idx = text[3:]
                print(f"🔍 Found box ID: {box_idx}")
            else:
                return False
    except Exception as e:
        return False
    
    # No.10011828800573
    box_idx = box_idx[:6] + three_digits + box_idx[9:]
    new_url = URL + '-' + box_idx
    print(f"🔗 Navigating to new URL: {new_url}")

    try:
        page.goto(new_url, timeout=WAIT_TIME * 3)
        page.wait_for_load_state("domcontentloaded", timeout=WAIT_TIME * 3)
        return True

    except Exception as e:
        print(f"❌ Error navigating to new URL: {e}")
        return False

def reload_page(page, context):
    page.close()
    page = context.new_page()
    page.goto(URL)
    return page
            

def add_to_bag(page):
    try:
        add_to_bag_btn = page.locator('button:has-text("ADD TO BAG")').first
        if add_to_bag_btn.is_visible():
            add_to_bag_btn.click(timeout=WAIT_TIME)
            print("🛍️ 'ADD TO BAG' button clicked.")
            return True
        else:
            return False
     
    except Exception as e:
        print(f"❌ Error clicking 'ADD TO BAG' button")
        return False

def get_cart_item_count(page):
    try:
        info_title = page.locator('div.index_infoTitle__d5wSp').first
        if info_title.is_visible():
            num_items = int(info_title.inner_text().strip())
            print(f"✅ Cart item count: {num_items}")
            return num_items
        else:
            print("❌ Cart item count not found.")
            return 0
    except Exception as e:
        print(f"❌ Error getting cart item count")
        return 0

def reserve_box(page):
    countdown = False
    try:
        page.goto(CART_URL)
        page.wait_for_timeout(WAIT_TIME * 5)
        # Step 1: Click the "POP NOW" tab to activate it
        pop_now_tab = page.locator('div[data-node-key="2"] div[role="tab"]')
        if pop_now_tab.is_visible():
            pop_now_tab.click()
            print("🖱️ Clicked 'POP NOW' tab.")
            page.wait_for_timeout(WAIT_TIME * 5)  # small wait to allow panel transition

        # Step 2: Click the "Confirm and Check out" button
        checkout_button = page.locator("button.ant-btn.ant-btn-primary.ant-btn-dangerous.index_checkout__V9YPC", 
                                       has_text="Confirm and Check out")
        if checkout_button.is_visible():
            checkout_button.click()
            print("🛒 Clicked checkout button.")

        page.wait_for_url("https://www.popmart.com/ca/order-confirmation?isBox=true", timeout=WAIT_TIME * 10)
        # Step 2: Extract the countdown time
        time_div = page.locator('div.index_placeOrder__eK_3g')
        if time_div.is_visible():
            time_text = time_div.text_content()
            print(f"⏳ Countdown text: {time_text}")
            
            # Extract time using regex (e.g., "2:54")
            import re
            match = re.search(r'(\d+:\d+)', time_text)
            if match:
                countdown = True
                return countdown
        return countdown
    except Exception as e:
        print(f"❌ Error during reservation")
        return countdown
    

def safe_click_box(page, idx):
    if idx == -1:
        # print("❌ No valid box index found.")
        return False
    try:
        box = page.locator('img.index_showBoxItem__5YQkR').nth(idx)
        
        if not box.is_visible():
            # print(f"⚠️ Box {idx} is not visible.")
            return False

        if not box.is_enabled():
            # print(f"⚠️ Box {idx} is not enabled.")
            return False

        box.hover(timeout=WAIT_TIME * 3)
        time.sleep(random.uniform(0.05, 0.15))  # simulate human-like delay
        box.click(timeout=WAIT_TIME * 3)
        # print(f"✅ Clicked box {idx}")
        return True

    except Exception as e:
        print(f"❌ Failed to click box {idx}")
        return False



def search_box(page, box_idx):
    if box_idx != -1:
        return box_idx
    box_time = 10000000
    box_list = page.locator('img.index_showBoxItem__5YQkR')
    box_count = box_list.count()
    lock_list = page.locator('div.index_popupBg__qRPjK')
    lock_count = lock_list.count()
    if box_count > lock_count:
        CLICK_TIME = 10
    else:
        CLICK_TIME = 1000
    print(f"📦 Found {box_count} boxes and {lock_count} locks on the page.")
    for i in reversed(range(box_list.count())):
        page.wait_for_timeout(CLICK_TIME)
        print(f"🔍 Checking box {i + 1}/{box_count}...")
        if safe_click_box(page, i):
            message_div = page.locator('div.ant-message-notice').last
            if message_div.is_visible():
                html = message_div.inner_html()
                match = re.search(PATTERN, html)
                if match:
                    minutes = int(match.group(1))
                    seconds = int(match.group(2))
                    print("⏰ Reserving time:", minutes, "minutes", seconds, "seconds")
                    if minutes * 60 + seconds < 30:
                        box_idx = i
                        return box_idx
                    if box_time > (minutes * 60 + seconds):
                        box_time = minutes * 60 + seconds
                        box_idx = i
        else:
            print(f"❌ Error clicking box {i + 1}")
            continue  

            
    return box_idx
                        

def notify_me_when_available(page, context):
    print("🔍 Monitoring availability...")
    email_flag = False 
    check_counter = 0

    while True:
        try:
            sold_out_button = page.locator("button.index_subscribe__HL9BU, button.index_noSale__PAmNM").first
            sold_out_flag = sold_out_button.is_visible(timeout=WAIT_TIME * 5)
            # print(f"🔍 Sold out button visible: {sold_out_flag}")
            if sold_out_flag:
                print("⏳ Still unavailable. Waiting a bit...")
                email_flag = True
                check_counter += 1
            else:
                try:
                    if page.locator("button.index_chooseRandomlyBtn__upKXA").first.is_visible():
                        print("✅ 'Pick One to Shake' detected — ITEM IS AVAILABLE!")
                        if email_flag:
                            send_email("Popmart Bot Alert", 
                                    f"The item is now available. Please check the website - {URL}",
                                    EMAIL_RECEIVER_NOTIFY)
                            email_flag = False
                        return
                    
                    box_idx = search_box(page, -1)
                    if box_idx != -1:
                        print("✅ Box is available for reservation!")
                        return
                except:
                    pass
        except:
            print("⚠️ Selector not found. Could be a good sign.")

        # try:
        #     if page.locator("button.index_chooseRandomlyBtn__upKXA").first.is_visible():
        #         print("✅ 'Pick One to Shake' detected — ITEM IS AVAILABLE!")
        #         if email_flag:
        #             send_email("Popmart Bot Alert", 
        #                        f"The item is now available. Please check the website - {URL}",
        #                        EMAIL_RECEIVER_NOTIFY)
        #             email_flag = False
        #         return
        #     if search_box(page, -1) != -1:
        #         print("✅ Box is available for reservation!")
        #         return
        # except:
        #     pass



        # Only reload every 3-5 checks to save time
        if check_counter >= 5:
            page = reload_page(page, context)
            print("🔁 Reloading page after 5 checks...")
            check_counter = 0
            
        page.wait_for_timeout(WAIT_TIME * 3)



def get_box(page):
    CLICK_TIME = 1000  # Initial click time in milliseconds
    box_idx = -1
    num_items = 0
    email_sent = False
    minutes = 10
    seconds = 10

    while True:
        if add_to_bag(page) and num_items == 0:
            print("🛍️ 'ADD TO BAG' button is visible. Exiting to proceed manually...")
            page.wait_for_timeout(WAIT_TIME * 3)
            continue

        num_items = get_cart_item_count(page)
        print(f"🛒 Number of items in cart: {num_items}")
        if num_items > 0:
            if not email_sent:
                print("📧 Sending email notification...")
                send_email("Popmart Bot Alert", 
                            "The 'ADD TO BAG' button is now visible. Please proceed manually.", 
                            EMAIL_RECEIVER_ADD_TO_CART)
                email_sent = True
            print("Reserving box...")
            reserve_box(page)
            page.wait_for_timeout(WAIT_TIME * 60 * 3)
            continue

        box_idx = search_box(page, box_idx)
        if safe_click_box(page, box_idx):
            message_div = page.locator('div.ant-message-notice').last
            if message_div.is_visible():
                pass
            else:
                page.wait_for_timeout(CLICK_TIME)
                continue
            html = message_div.inner_html()
            match = re.search(PATTERN, html)
            if match:
                minutes = int(match.group(1))
                seconds = int(match.group(2))
                
                if minutes == 0 and seconds < 3:
                    CLICK_TIME = 100
                    print("⏰ Reserving time:", minutes, "minutes", seconds, "seconds")
                elif minutes <= 2:
                    CLICK_TIME = 1000                     
                else:
                    CLICK_TIME = 1000
                    box_idx = -1
                    if not next_url(page):
                        next_page(page) 
        else:
            print(f"❌ Box {box_idx} is not clickable. Moving to next box.")
            CLICK_TIME = 1000
            box_idx = -1
            if not add_to_bag(page) and not next_url(page):
                    next_page(page)  

        page.wait_for_timeout(CLICK_TIME)


def run_playwright():
    with sync_playwright() as p:

        browser = p.chromium.connect_over_cdp(CDP_URL)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()

        url = URL if BOX_ID == "" else f"{URL}-{BOX_ID}"
        page.goto(url)
        page.wait_for_load_state("domcontentloaded", timeout=WAIT_TIME * 3)
        page.wait_for_timeout(WAIT_TIME * 5)


        notify_me_when_available(page, context)

        while True:
            try:
                get_box(page)
            except TimeoutError:
                print("⚠️ Timeout occurred. Retrying...")
                reload_page(page, context)
                continue
            except Exception as e:
                print(f"❌ An error occurred: {e}")
                break

    input("🕹️ Press Enter to exit. Browser remains open...")


if __name__ == "__main__":
    launch_chrome()
    run_playwright()


