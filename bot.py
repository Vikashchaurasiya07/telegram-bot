import telebot
import requests
import os
import re
from bs4 import BeautifulSoup

# Replace with your Telegram bot token
BOT_TOKEN = "7754481758:AAFznAKN05qP33QljoT-WIXaS9GD7zne4rA"
bot = telebot.TeleBot(BOT_TOKEN)

# Function to extract Terabox video link
def extract_terabox_link(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    
    print(f"[INFO] Fetching Terabox URL: {url}")
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"[ERROR] Failed to fetch Terabox page. Status: {response.status_code}")
        return None
    
    # Extract direct video link
    match = re.search(r'https://.*?terabox\.com/.*?mp4', response.text)
    video_link = match.group(0) if match else None
    print(f"[INFO] Extracted Terabox Video Link: {video_link}")
    return video_link

# Function to extract Diskwala video link
def extract_diskwala_link(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    
    print(f"[INFO] Fetching Diskwala URL: {url}")
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"[ERROR] Failed to fetch Diskwala page. Status: {response.status_code}")
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find iframe source
    iframe = soup.find("iframe")
    if iframe and "src" in iframe.attrs:
        print(f"[INFO] Found Diskwala Iframe Source: {iframe['src']}")
        return iframe["src"]
    
    # Try direct .mp4 link
    match = re.search(r'https://.*?diskwala\.com/.*?mp4', response.text)
    video_link = match.group(0) if match else None
    print(f"[INFO] Extracted Diskwala Video Link: {video_link}")
    return video_link

# Start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    print(f"[INFO] User {message.chat.id} started the bot.")
    bot.reply_to(message, "Send me a Terabox or Diskwala video link!")

# Handle video links
@bot.message_handler(func=lambda message: True)
def download_custom_video(message):
    url = message.text
    print(f"[INFO] Received link from user {message.chat.id}: {url}")
    bot.reply_to(message, "Fetching video, please wait...")

    try:
        if "terabox.com" in url:
            video_url = extract_terabox_link(url)
        elif "diskwala.com" in url:
            video_url = extract_diskwala_link(url)
        else:
            bot.reply_to(message, "Unsupported website. Please send a Terabox or Diskwala link.")
            return

        if not video_url:
            print(f"[ERROR] Failed to extract video link for {url}")
            bot.reply_to(message, "Could not extract video link. Please check your URL.")
            return

        print(f"[INFO] Downloading video from: {video_url}")
        bot.reply_to(message, f"Downloading video from: {video_url}")

        # Download video
        filename = "video.mp4"
        with requests.get(video_url, stream=True) as video_response:
            with open(filename, 'wb') as f:
                for chunk in video_response.iter_content(1024):
                    f.write(chunk)

        print(f"[INFO] Video downloaded successfully: {filename}")

        # Send video
        with open(filename, 'rb') as video:
            bot.send_document(message.chat.id, video)

        print(f"[INFO] Video sent to user {message.chat.id}")
        os.remove(filename)

    except Exception as e:
        print(f"[ERROR] Exception occurred: {str(e)}")
        bot.reply_to(message, f"Error: {str(e)}")

print("[INFO] Bot is running...")
bot.polling()
