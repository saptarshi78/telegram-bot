import telebot
import requests
import validators
import re
import time

# Telegram Bot Token
bot = telebot.TeleBot('8166571880:AAH59oE0qwi00nIKJaau33bPxmMlV_4eEZY')

# Noirsane Shortener API Key
API_KEY = 'abf109fe4a9cc3c7b4d3b266d4c5e5a68d063261'

# Custom header and footer
DEFAULT_HEADER = "\n\n 🔞 https://t.me/+zNbzsB_y25AwNDJl 🔞 \n 👆🔞Join This backup channel🔞 👆 \n 🔗⚔━━━━━━━━━━━━━━━━━⚔"
DEFAULT_FOOTER = "\n ⚔━━━━━━━━━━━━━━━━━⚔ \n Backup - \n Join this chinnal guys 🔞🔞👇👇 \n https://t.me/+Rqe3fVJ_QBthNjFl \n \n Join this 🎥MOVIE🎥 channel  👇👇 \n https://t.me/+Tixf7zhZ6Ok2YzY1 \n\n 👉🔗 HOW TO DOWNLOAD🔗👈 \n https://t.me/publicc_778/56"

# Clean up forwarded messages
def clean_text(text):
    if not text:
        return ""

    # Remove Telegram links and joining lines
    text = re.sub(r'https?://t\.me/\S+', '', text)
    text = re.sub(r'(?i)join\s+this\s+channel.*', '', text)
    text = re.sub(r'(?i)Join.*👇.*', '', text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'\n{2,}', '\n', text)

    return text.strip()

# Find URLs and shorten them
def find_and_shorten_links(text):
    if not text:
        return DEFAULT_HEADER + "\n" + DEFAULT_FOOTER

    text = clean_text(text)

    url_pattern = r'(https?://\S+)'
    urls = list(set(re.findall(url_pattern, text)))

    for url in urls:
        if validators.url(url):
            try:
                response = requests.get(
                    f"https://shortner.noirsane.com/api?api={API_KEY}&url={url}&format=text",
                    timeout=5
                )
                if response.status_code == 200 and response.text.startswith("http"):
                    short_url = response.text.strip()
                    text = text.replace(url, short_url)
                else:
                    print(f"Failed to shorten: {url}")
            except Exception as e:
                print(f"Error shortening {url}: {e}")
            time.sleep(0.1)

    return DEFAULT_HEADER + "\n" + text + DEFAULT_FOOTER

# Handlers
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
    updated = find_and_shorten_links(message.text.strip())
    bot.reply_to(message, updated)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    caption = message.caption if message.caption else ""
    updated = find_and_shorten_links(caption)
    bot.send_photo(message.chat.id, message.photo[-1].file_id, caption=updated)

@bot.message_handler(content_types=['video'])
def handle_video(message):
    caption = message.caption if message.caption else ""
    updated = find_and_shorten_links(caption)
    bot.send_video(message.chat.id, message.video.file_id, caption=updated)

@bot.message_handler(content_types=['document'])
def handle_document(message):
    caption = message.caption if message.caption else ""
    updated = find_and_shorten_links(caption)
    bot.send_document(message.chat.id, message.document.file_id, caption=updated)

@bot.message_handler(func=lambda message: True)
def handle_bulk(message):
    try:
        time.sleep(0.3)
        if message.text:
            handle_text(message)
        elif message.photo:
            handle_photo(message)
        elif message.video:
            handle_video(message)
        elif message.document:
            handle_document(message)
    except Exception as e:
        print(f"Error in bulk processing: {e}")

# Start bot
bot.infinity_polling()
