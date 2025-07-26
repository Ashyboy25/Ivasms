from dotenv import load_dotenv
load_dotenv()

import os
import time
import re
from datetime import datetime
from flask import Flask
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import telegram

app = Flask(__name__)

# --- Configuration (from environment variables) ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
IVASMS_EMAIL = os.getenv("IVASMS_EMAIL")
IVASMS_PASSWORD = os.getenv("IVASMS_PASSWORD")

if not BOT_TOKEN or not CHAT_ID or not IVASMS_EMAIL or not IVASMS_PASSWORD:
    print("Error: Missing one or more environment variables. Please set BOT_TOKEN, CHAT_ID, IVASMS_EMAIL, and IVASMS_PASSWORD.")
    # In a real application, you might want to exit or raise an exception here.

bot = telegram.Bot(token=BOT_TOKEN)

# --- Global Variables ---
last_scraped_message_id = None

# --- Helper Functions ---
def get_chrome_options():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_argument = "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
    chrome_options.add_argument(chrome_argument)
    return chrome_options

def extract_otp_and_service(sms_text):
    # Regex to find common OTP patterns
    otp_match = re.search(r"\b(\d{3}[- ]?\d{3}|\d{4,8})\b", sms_text)
    otp_code = otp_match.group(1) if otp_match else "N/A"

    service = "Unknown"
    sms_lower = sms_text.lower()
    if "whatsapp" in sms_lower:
        service = "WhatsApp"
    elif "facebook" in sms_lower:
        service = "Facebook"
    elif "apple" in sms_lower or "icloud" in sms_lower:
        service = "Apple"
    elif "google" in sms_lower or "gmail" in sms_lower:
        service = "Google"
    elif "telegram" in sms_lower:
        service = "Telegram"
    elif "microsoft" in sms_lower:
        service = "Microsoft"
    elif "amazon" in sms_lower:
        service = "Amazon"
    elif "twitter" in sms_lower:
        service = "Twitter"
    elif "instagram" in sms_lower:
        service = "Instagram"
    elif "discord" in sms_lower:
        service = "Discord"
    return otp_code, service

def scrape_ivasms_otp():
    global last_scraped_message_id
    driver = None
    try:
        service = ChromeService(executable_path="/usr/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=get_chrome_options())
        driver.get("https://www.ivasms.com/portal/sms/received")

        # Login
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "email"))).send_keys(IVASMS_EMAIL)
        driver.find_element(By.NAME, "password").send_keys(IVASMS_PASSWORD)
        driver.find_element(By.XPATH, "//button[contains(text(), 'Sign in')]").click()

        # Wait for navigation to the received SMS page
        WebDriverWait(driver, 20).until(EC.url_to_be("https://www.ivasms.com/portal/sms/received"))

        # Scrape the latest OTP
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//table[@id='DataTables_Table_0']/tbody/tr[1]")))
        
        # Get the first row (latest message)
        first_row = driver.find_element(By.XPATH, "//table[@id='DataTables_Table_0']/tbody/tr[1]")
        
        # Extract data from cells
        cols = first_row.find_elements(By.TAG_NAME, "td")
        
        # Assuming the order: Date, Number, SMS, Actions (adjust if different)
        # The first column is usually an ID or checkbox, so we start from index 1 for Date
        
        # Check if there are enough columns
        if len(cols) < 3: # Expecting at least Date, Number, SMS
            print("Not enough columns found in the table row.")
            return None

        # Adjust indices based on actual table structure
        # Assuming structure: ID, Date, Number, SMS, Actions
        # Let's re-evaluate based on typical IVASMS table structure:
        # Column 0: Checkbox/ID
        # Column 1: Date
        # Column 2: Number
        # Column 3: SMS Content
        
        # Let's try to get text content directly and then parse
        date_time_str = cols[1].text.strip() if len(cols) > 1 else "N/A"
        number = cols[2].text.strip() if len(cols) > 2 else "N/A"
        sms_text = cols[3].text.strip() if len(cols) > 3 else "N/A"

        current_message_id = f"{date_time_str}-{number}-{sms_text}" # Simple unique ID

        if current_message_id == last_scraped_message_id:
            print("No new OTPs. Skipping.")
            return None

        last_scraped_message_id = current_message_id

        otp_code, service = extract_otp_and_service(sms_text)

        # Format the message
        message = f"""✨ {service} OTP ALERT ✨\n\n🕐 Time: {date_time_str}\n📱 Number: {number}\n⚙️ Service: {service}\n\n🔑 OTP Code: {otp_code}\n\n# {sms_text}\n\nI'm Glad to Help You 😊"""
        return message

    except TimeoutException:
        print("Timeout while waiting for page elements.")
        return None
    except WebDriverException as e:
        print(f"WebDriver error: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during scraping: {e}")
        return None
    finally:
        if driver:
            driver.quit()

async def send_telegram_message(message):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message)
        print("Message sent to Telegram.")
    except telegram.error.TelegramError as e:
        print(f"Telegram error: {e}")

@app.route("/")
def home():
    return "IVASMS Telegram Bot is running!"

@app.route("/health")
def health_check():
    return "OK", 200

# This part is for local testing/running as a script
# In Render, Gunicorn will manage the Flask app, and a separate process/cron job
# would trigger the scraping function.
# For simplicity in this A-Z file, we'll include a basic loop.

async def main_loop():
    while True:
        print("Checking for new OTPs...")
        otp_message = scrape_ivasms_otp()
        if otp_message:
            await send_telegram_message(otp_message)
        time.sleep(30) # Check every 30 seconds

if __name__ == "__main__":
    import asyncio
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


