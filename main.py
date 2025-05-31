import telebot
import requests
import validators
import re
import time
import random

# Telegram Bot Token
bot = telebot.TeleBot('8166571880:AAH59oE0qwi00nIKJaau33bPxmMlV_4eEZY')

# Multiple Noirsane Shortener API Keys
API_KEYS = [
    'abf109fe4a9cc3c7b4d3b266d4c5e5a68d063261',
    '3258415006603e646926420840c3469a68c377a1'
]

# Custom header and footer
DEFAULT_HEADER = "\n\n 🔞 https://t.me/+zNbzsB_y25AwNDJl 🔞 \n 👆🔞Join This backup channel🔞 👆 \n 🔗⚔━━━━━━━━━━━━━━━━━⚔"
DEFAULT_FOOTER = "\n ⚔━━━━━━━━━━━━━━━━━⚔ \n Backup - \n Join this chinnal guys 🔞🔞👇👇 \n https://t.me/+Rqe3fVJ_QBthNjFl \n \n Join this 🎥MOVIE🎥 channel  👇👇 \n https://t.me/+Tixf7zhZ6Ok2YzY1 \n\n 👉🔗 HOW TO DOWNLOAD🔗👈 \n https://t.me/publicc_778/56"

# Clean up forwarded messages
def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'https?://t\.me/\S+', '', text)
    text = re.sub(r'(?i)join\s+this\s+channel.*', '', text)
    text = re.sub(r'(?i)Join.*👇.*', '', text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'\n{2,}', '\n', text)
    return text.strip()

# Try shortening URL with all API keys and fallback
def shorten_with_noirsane(url):
    shuffled_keys = random.sample(API_KEYS, len(API_KEYS))  # Random order for load distribution
    for api_key in shuffled_keys:
        try:
            response = requests.get(
                "https://shortner.noirsane.com/api",
                params={
                    'api': api_key,
                    'url': url,
                    'format': 'text'
                },
                timeout=10
            )
            if response.status_code == 200 and response.text.startswith("http"):
                print(f"✅ Shortened using key {api_key[:6]}: {response.text.strip()}")
                return response.text.strip()
            else:
                print(f"❌ Key {api_key[:6]} failed - {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"⛔ Error with key {api_key[:6]}: {e}")
        time.sleep(0.2)  # slight delay before trying next key
    print("‼️ All keys failed. Using original URL.")
    return url

# Extract and shorten all valid URLs in a message
def find_and_shorten_links(text):
    if not text:
        return DEFAULT_HEADER + "\n" + DEFAULT_FOOTER

    cleaned_text = clean_text(text)
    url_pattern = r'(https?://[^\s\)\]]+)'  # improved pattern
    urls = list(set(re.findall(url_pattern, cleaned_text)))

    if not urls:
        return DEFAULT_HEADER + "\n" + cleaned_text + "\n" + DEFAULT_FOOTER

    # Replace each URL with its shortened version
    for url in urls:
        if validators.url(url):
            shortened = shorten_with_noirsane(url)
            cleaned_text = cleaned_text.replace(url, shortened)
            time.sleep(0.1)  # slight delay to avoid rate limits

    return DEFAULT_HEADER + "\n" + cleaned_text + "\n" + DEFAULT_FOOTER

# Telegram Handlers
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message,
        "🌟 Welcome to the Premium Link Shortener Bot! 🌐\n\n"
        "📎 Just send any text, photo, or video with a link — I’ll shorten it instantly.\n"
        "💰 Login to earn: https://shortner.noirsane.com\n\n"
        "🚀 Crafted with ❤️‍🔥"
    )

@bot.message_handler(content_types=['text'])
def handle_text(message):
    try:
        updated = find_and_shorten_links(message.text.strip())
        bot.reply_to(message, updated)
    except Exception as e:
        print(f"❌ Error processing text: {e}")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        caption = message.caption or ""
        updated = find_and_shorten_links(caption)
        bot.send_photo(message.chat.id, message.photo[-1].file_id, caption=updated)
    except Exception as e:
        print(f"❌ Error processing photo: {e}")

@bot.message_handler(content_types=['video'])
def handle_video(message):
    try:
        caption = message.caption or ""
        updated = find_and_shorten_links(caption)
        bot.send_video(message.chat.id, message.video.file_id, caption=updated)
    except Exception as e:
        print(f"❌ Error processing video: {e}")

@bot.message_handler(content_types=['document'])
def handle_document(message):
    try:
        caption = message.caption or ""
        updated = find_and_shorten_links(caption)
        bot.send_document(message.chat.id, message.document.file_id, caption=updated)
    except Exception as e:
        print(f"❌ Error processing document: {e}")

# Bulk fallback handler
@bot.message_handler(func=lambda message: True)
def handle_any(message):
    try:
        if message.text:
            handle_text(message)
        elif message.photo:
            handle_photo(message)
        elif message.video:
            handle_video(message)
        elif message.document:
            handle_document(message)
    except Exception as e:
        print(f"❌ General handler error: {e}")

# Start the bot
print("🤖 Bot is running...")
bot.infinity_polling()
