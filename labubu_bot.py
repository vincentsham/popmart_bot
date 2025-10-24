import os
import random
from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError


import argparse
from bs4 import BeautifulSoup
from utils import (launch_chrome, send_email, reload_page, save_page_html)
from parameters import URL, CART_URL, CDP_URL, EMAIL_RECEIVER_NOTIFY, EMAIL_RECEIVER_ADD_TO_CART, WAIT_TIME, REFRESH_TIME


parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, default=9223, help="Remote debugging port for Chrome")
parser.add_argument("--toy_id", type=int, default=None, help="Toy ID")
parser.add_argument("--email_flag", action="store_true", default=False, help="Enable email notifications")
args = parser.parse_args()

port = args.port
TOY_ID = args.toy_id if args.toy_id else os.getenv("TOY_ID")
URL = f"{URL}/{TOY_ID}"
CDP_URL = f"{CDP_URL}:{port}"





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
    return new_url


def get_cart_item_count(page):
    try:
        # Wait for the div to render
        page.wait_for_selector('div.index_infoTitle__d5wSp', timeout=WAIT_TIME * 3)
        info_title = page.locator('div.index_infoTitle__d5wSp').first
        if info_title.is_visible():
            num_items = int(info_title.inner_text().strip())
            print(f"✅ Cart item count: {num_items}")
            return num_items
        else:
            print("❌ Cart item count not found.")
            return 0
    except Exception as e:
        print(f"❌ Error getting cart item count: {e}")
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
    
def search_box(page):
    try:
        page.wait_for_selector('div.index_row__LiAP8', state='attached', timeout=WAIT_TIME * 3)
        blocks = page.locator('div.index_normalBlock__2ch5j')
        count = blocks.count()
        print(f"🔍 Found {count} blocks with class 'index_normalBlock__2ch5j'.")
        return count
    except Exception as e:
        print(f"❌ Error finding blocks: {e}")
        return 0

def safe_click_box(page):
    try:
        # Wait for the bottom container div to be visible
        page.wait_for_selector('div.index_bottomContainer__BzOSK', state='visible', timeout=WAIT_TIME * 3)

        # Locate the "Select all" checkbox within the bottom container div
        select_all_checkbox = page.locator('div.index_bottomContainer__BzOSK input.ant-checkbox-input').first
        if select_all_checkbox.is_visible():
            select_all_checkbox.check()
            print("☑️ 'Select all' checkbox clicked successfully.")
        else:
            print("❌ 'Select all' checkbox is not visible.")
            return False

        # Locate and click the 'ADD TO BAG' button within the bottom container div
        add_to_bag_button = page.locator('div.index_bottomContainer__BzOSK button.ant-btn.ant-btn-primary.index_btn__Y5dKo').first
        if add_to_bag_button.is_visible():
            add_to_bag_button.click(timeout=WAIT_TIME)
            print("🛍️ 'ADD TO BAG' button clicked successfully.")
            return True
        else:
            print("❌ 'ADD TO BAG' button is not visible.")
            return False
    except Exception as e:
        print(f"❌ Error interacting with checkbox or button: {e}")
        return False



def notify_me_when_available(page):
    print("🔍 Monitoring availability...")
    email_flag = False 
    check_counter = 0

    while True:
        try:
            sold_out_button = page.locator("button.index_subscribe__HL9BU, button.index_noSale__PAmNM").first
            # print(f"🔍 Sold out button visible: {sold_out_flag}")
            if sold_out_button.is_visible():
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
                    else:
                        check_counter += 1
                except:
                    pass
        except:
            print("⚠️ Selector not found. Could be a good sign.")


        # Only reload every 3-5 checks to save time
        if check_counter >= 5:
            page = reload_page(page, URL)
            print("🔁 Reloading page after 5 checks...")
            check_counter = 0
            
        page.wait_for_timeout(REFRESH_TIME)

def click_choose_multity_button(page):
    try:
        # Wait for the button to be visible
        page.wait_for_selector('button.ant-btn.ant-btn-ghost.index_chooseMulitityBtn__n0MoA', state='visible', timeout=WAIT_TIME * 3)

        # Locate the button with the specified class
        button = page.locator('button.ant-btn.ant-btn-ghost.index_chooseMulitityBtn__n0MoA').first
        if button.is_visible():
            button.click(timeout=WAIT_TIME)
            print("🛍️ 'Choose Multity' button clicked successfully.")
            return True
        else:
            print("❌ 'Choose Multity' button is not visible.")
            return False
    except Exception as e:
        print(f"❌ Error clicking 'Choose Multity' button: {e}")
        return False

def get_box(page):

    num_items = 0
    email_sent = False

    while True:
        num_items = get_cart_item_count(page)
        # print(f"🛒 Number of items in cart: {num_items}")
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

        click_choose_multity_button(page)
        box_num = search_box(page)
        if box_num > 0:
            safe_click_box(page)

        if url :=next_url(page):
            reload_page(page, url)
        else:
            reload_page(page, URL)

        page.wait_for_timeout(REFRESH_TIME)


def run_playwright():
    with sync_playwright() as p:

        browser = p.chromium.connect_over_cdp(CDP_URL)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()

        page.goto(URL)
        page.wait_for_load_state("domcontentloaded", timeout=WAIT_TIME * 3)
        
        # save_page_html(page)
        notify_me_when_available(page)

        while True:
            try:
                get_box(page)
            except TimeoutError:
                print("⚠️ Timeout occurred. Retrying...")
                reload_page(page)
                continue
            except Exception as e:
                print(f"❌ An error occurred: {e}")
                break

    input("🕹️ Press Enter to exit. Browser remains open...")


def save_page_html(page, log_file="debug_log.html"):
    page.wait_for_timeout(WAIT_TIME * 5)
    try:
        # Get the full HTML content of the page
        body_content = page.locator("body").inner_html()

        # Use BeautifulSoup to prettify the HTML content
        soup = BeautifulSoup(body_content, "html.parser")
        pretty_html = soup.prettify()

        # Write the prettified HTML content to a log file
        with open(log_file, "w", encoding="utf-8") as file:
            file.write(pretty_html)
        print(f"✅ Page HTML saved to {log_file}")
    except Exception as e:
        print(f"❌ Failed to save page HTML: {e}")



if __name__ == "__main__":
    launch_chrome(port)
    run_playwright()


