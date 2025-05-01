import telebot
import requests
import validators
import re
import time
import threading
from queue import Queue
from flask import Flask, request

# Flask app for Render
app = Flask(__name__)

# Telegram bot & Shortener setup
bot = telebot.TeleBot('8166571880:AAEZ7__xJzYoOR0zTr3n8ZbTWUYhDYfGezY')
API_KEY = 'abf109fe4a9cc3c7b4d3b266d4c5e5a68d063261'
DEFAULT_FOOTER = "\n\nJoin this channel for more videos 😚✅👇\nhttps://t.me/noirsanebackup"

# Create a queue to store incoming messages
message_queue = Queue()

# Infinite retry logic to shorten a URL
def shorten_with_retry(url):
    while True:
        try:
            response = requests.get(
                f"https://shortner.noirsane.com/api?api={API_KEY}&url={url}&format=text",
                timeout=10
            )
            if response.status_code == 200:
                short_url = response.text.strip()
                if short_url.startswith("http"):
                    return short_url
        except Exception as e:
            print(f"Retrying {url} due to: {e}")
        time.sleep(2)

# Find and shorten all URLs in a message
def find_and_shorten_links(text):
    if not text:
        return ""
    url_pattern = r'(https?://\S+)'
    urls = re.findall(url_pattern, text)
    unique_urls = list(set(urls))
    for url in unique_urls:
        if validators.url(url):
            short_url = shorten_with_retry(url)
            text = text.replace(url, short_url)
            time.sleep(2)  # Delay per link to prevent API overload
    return text + DEFAULT_FOOTER if unique_urls else text

# Welcome message
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message,
        "🌟 Welcome to the Premium Link Shortener Bot! 🌐\n\n"
        "📌 Just send any text, photo, or video with a link — I’ll shorten it instantly.\n"
        "💰 Login to earn: https://shortner.noirsane.com\n\n"
        "🚀 Crafted with ❤️ by Saptarshi Singh"
    )

# Handlers add messages to queue
@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'video', 'document'])
def queue_message(message):
    message_queue.put(message)

# Worker thread to process messages one-by-one
def process_queue():
    while True:
        message = message_queue.get()
        try:
            if message.text:
                updated = find_and_shorten_links(message.text.strip())
                bot.reply_to(message, updated)
            elif message.photo:
                caption = message.caption if message.caption else ""
                updated = find_and_shorten_links(caption)
                bot.send_photo(message.chat.id, message.photo[-1].file_id, caption=updated)
            elif message.video:
                caption = message.caption if message.caption else ""
                updated = find_and_shorten_links(caption)
                bot.send_video(message.chat.id, message.video.file_id, caption=updated)
            elif message.document:
                caption = message.caption if message.caption else ""
                updated = find_and_shorten_links(caption)
                bot.send_document(message.chat.id, message.document.file_id, caption=updated)
        except Exception as e:
            print(f"Error handling message: {e}")
        finally:
            message_queue.task_done()
        time.sleep(2)  # Delay per message to avoid flooding the API

# Webhook handler for Render Flask
@app.route('/', methods=['GET'])
def home():
    return 'Bot is running!'

def start_bot():
    bot.infinity_polling()

# Start everything
if __name__ == '__main__':
    # Start queue processor
    threading.Thread(target=process_queue, daemon=True).start()

    # Start the bot in another thread
    threading.Thread(target=start_bot).start()

    # Start Flask server
    app.run(host='0.0.0.0', port=10000)
