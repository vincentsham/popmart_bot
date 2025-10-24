# parameters.py
import os
from dotenv import load_dotenv

load_dotenv()

# Define all parameters and constants here


CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
WAIT_TIME = 1000  # milliseconds
REFRESH_TIME = 500 # milliseconds


# Email settings
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER_NOTIFY = os.getenv("EMAIL_RECEIVER_NOTIFY").split(",")
EMAIL_RECEIVER_ADD_TO_CART = os.getenv("EMAIL_RECEIVER_ADD_TO_CART").split(",")



# URLs
URL = os.getenv("URL")
CART_URL = os.getenv("CART_URL")

# Debugging
DEBUG = os.getenv("DEBUG") == "True"

# Remote debugging
USER_DATA_DIR = f"/tmp/chrome-popmart"
CDP_URL = f"http://localhost"

