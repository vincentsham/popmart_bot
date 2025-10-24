import subprocess

import time
import socket
import os

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from bs4 import BeautifulSoup

from parameters import CHROME_PATH, EMAIL_SENDER, EMAIL_PASSWORD, DEBUG, USER_DATA_DIR, WAIT_TIME




def launch_chrome(port):
    print("🚀 Launching Chrome with remote debugging...")
    proc = subprocess.Popen([
        CHROME_PATH,
        f"--remote-debugging-port={port}",
        f"--user-data-dir={USER_DATA_DIR}_{port}",
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

    wait_for_cdp_port(port)
    pass


def send_email(subject, body, receiver):
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



def reload_page(page, url):
    page.goto(url, timeout=WAIT_TIME * 3)
    page.wait_for_load_state("domcontentloaded")
    return page



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


