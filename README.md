# 🛍️ Pop Mart Pop Now Auto-Bot

An automated **Playwright + Chrome CDP** bot for monitoring and reserving limited-edition Pop Mart items the instant they become available.  
This script detects item availability, attempts to reserve or add to cart, and optionally sends email notifications when items drop — all while maintaining stealth-like behavior to mimic human interaction.

---

## 🚀 Features

- **Automatic Chrome launch** with remote debugging for live browser control  
- **Real-time availability monitoring** using dynamic selector checks  
- **Smart box reservation logic** that detects and clicks the best available box  
- **URL mutation & pagination** to explore adjacent box IDs  
- **Email notifications** (via Gmail SMTP) for availability and add-to-cart events  
- **Auto-reload logic** with human-like random delays  
- **Error-tolerant loops** to recover from transient network or timeout issues  

---

## ⚙️ Requirements

- macOS or Linux (Windows supported with Chrome path update)
- [Python 3.9+](https://www.python.org/downloads/)
- [Google Chrome](https://www.google.com/chrome/)
- [Playwright](https://playwright.dev/python/)
- A Gmail account for sending notifications (App Password required)

---

## 🧩 Installation

```bash
# Clone the repo
git clone https://github.com/<your-username>/popmart-bot.git
cd popmart-bot

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

---

## 🔐 Environment Variables

Create a `.env` file in the project root:

```bash
EMAIL_SENDER=youremail@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_RECEIVER_NOTIFY=recipient1@gmail.com,recipient2@gmail.com
EMAIL_RECEIVER_ADD_TO_CART=recipient3@gmail.com
URL=https://www.popmart.com/ca/product/box-id
CART_URL=https://www.popmart.com/ca/cart
DEBUG=True
```

> 💡 **Tip:** You’ll need to enable [2FA and App Passwords](https://support.google.com/mail/answer/185833?hl=en) for Gmail to work with this bot.
> 🗒️ **Note:** Replace `box-id` in the `URL` with the actual box ID. For example, `40`, `50`, and `195` correspond to Labubu boxes.

---

## 🧠 Usage

### Launch Chrome with remote debugging and start the bot:

```bash
python main.py --port 9222 --email_flag
```

**Arguments:**
| Flag | Description | Default |
|------|--------------|----------|
| `--port` | Chrome CDP debugging port | `9222` |
| `--email_flag` | Enable email notifications | `False` |

---

## 🪄 Behavior Overview

1. **Launch Chrome** in remote debugging mode (`--remote-debugging-port`).
2. **Connect Playwright** to the running Chrome instance.
3. **Monitor the item page** until it becomes available:
   - Detects “Sold Out” vs. “Pick One to Shake”.
   - Parses countdown timers (`Reserving Time: Xm Ys`).
4. **Attempt to reserve or add to cart** automatically.
5. **Send Gmail alerts** when:
   - An item becomes available.
   - An item has been added to cart and requires manual checkout.
6. **Auto-reload & rotate URLs** when needed to stay up-to-date.

---

## 🧾 Example Log Output

```
🚀 Launching Chrome with remote debugging...
✅ Chrome CDP port is open.
🔍 Monitoring availability...
⏳ Still unavailable. Waiting a bit...
✅ 'Pick One to Shake' detected — ITEM IS AVAILABLE!
📧 Email sent successfully.
🛍️ 'ADD TO BAG' button clicked.
```

---

## 🧱 Project Structure

```
popmart-bot/
├── main.py                  # Core automation logic
├── .env                     # Environment variables
├── requirements.txt         # Python dependencies
├── README.md                # This file
└── utils/                   # (optional) future helpers
```

---

## ⚠️ Disclaimer

This project is for **educational and personal use only**.  
Automating purchases or web interactions may violate Pop Mart’s Terms of Service.  
Use responsibly and at your own risk.

---

## 💡 Future Improvements

- Add stealth headers and mouse movement randomization  
- Support headless/headful toggles  
- Integrate Telegram or Discord alerts  
- Store successful reservation logs in SQLite  
- Add configurable selector patterns for different product pages  

---

### 🧑‍💻 Author

**Vincent Sham**  
AI Engineer • Automation Enthusiast • Pop Mart Collector  
📧 [Contact Me](mailto:youremail@gmail.com)

---

> ⭐ If you find this useful, please star the repo and share with other collectors!
