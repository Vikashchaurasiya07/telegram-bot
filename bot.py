import telebot
import requests
import re
import os
from bs4 import BeautifulSoup

# Telegram Bot Token
BOT_TOKEN = "7754481758:AAFznAKN05qP33QljoT-WIXaS9GD7zne4rA"
bot = telebot.TeleBot(BOT_TOKEN)

# Function to extract XHamster video link
def extract_xhamster_link(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    
    print(f"[INFO] Fetching XHamster URL: {url}")
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"[ERROR] Failed to fetch XHamster page. Status: {response.status_code}")
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")

    # Look for video link inside HTML
    match = re.search(r'https://[^"]+\.mp4', response.text)
    video_link = match.group(0) if match else None

    print(f"[INFO] Extracted XHamster Video Link: {video_link}")
    return video_link

# Start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Send me an XHamster video link!")

# Handle video links
@bot.message_handler(func=lambda message: True)
def process_video_request(message):
    url = message.text.strip()

    print(f"[DEBUG] Received message: {url}")  # Debugging
    bot.reply_to(message, "🔄 Fetching video, please wait...")

    if "xhamster.com" not in url:
        bot.reply_to(message, "❌ Unsupported website. Please send a valid XHamster link.")
        print("[DEBUG] URL does not contain 'xhamster.com'")
        return

    try:
        video_url = extract_xhamster_link(url)

        if not video_url:
            bot.reply_to(message, "❌ Could not extract video link. Please check your URL.")
            print("[ERROR] No video link found")
            return

        bot.reply_to(message, f"✅ Downloading video from: {video_url}")

        # Download the video
        filename = "xhamster_video.mp4"
        with requests.get(video_url, stream=True) as video_response:
            with open(filename, 'wb') as f:
                for chunk in video_response.iter_content(1024):
                    f.write(chunk)

        # Send the video
        with open(filename, 'rb') as video:
            bot.send_document(message.chat.id, video)

        # Clean up
        os.remove(filename)

    except Exception as e:
        print(f"[ERROR] Exception occurred: {str(e)}")
        bot.reply_to(message, f"❌ Error: {str(e)}")

print("[INFO] Bot is running...")
bot.polling()
