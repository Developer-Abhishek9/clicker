import time
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- Selenium Imports ---
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# --- Dictionary to manage users ---
user_links = {}


# --- Function to simulate real click ---
def simulate_real_click(url):
    options = Options()
    options.add_argument("--headless")  # Run browser in background
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    print(f"Opening {url} in browser...")
    try:
        driver.get(url)
        time.sleep(5)
        print("✅ Click simulated.")
    except Exception as e:
        print(f"❌ Error during click: {e}")
    finally:
        driver.quit()

# --- Background loop ---
def auto_click_loop(link, chat_id):
    while user_links.get(chat_id) == link:
        simulate_real_click(link)
        time.sleep(120)  # Wait 2 minutes

# --- Telegram bot handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send /setlink <url> to start clicking the link every 2 mins.\nUse /stop to stop.")

async def setlink(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if len(context.args) != 1:
        await update.message.reply_text("❌ Usage: /setlink https://example.com")
        return

    link = context.args[0]
    if not link.startswith("http"):
        await update.message.reply_text("❌ Invalid URL. It must start with http or https.")
        return

    user_links[chat_id] = link
    threading.Thread(target=auto_click_loop, args=(link, chat_id), daemon=True).start()
    await update.message.reply_text(f"✅ Started simulating clicks on: {link} every 2 minutes.")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in user_links:
        del user_links[chat_id]
        await update.message.reply_text("🛑 Click simulation stopped.")
    else:
        await update.message.reply_text("ℹ️ No active click task to stop.")

# --- Bot initialization ---
app = ApplicationBuilder().token("7882193580:AAG5I-DmlhRKzyahSbAhxmWX9mCCOyLpzpo").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("setlink", setlink))
app.add_handler(CommandHandler("stop", stop))

print("🤖 Bot is running...")
app.run_polling()
