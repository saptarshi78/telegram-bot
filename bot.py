from flask import Flask, request
import telebot
import requests
import validators
import re
import time
import threading

API_KEY = 'abf109fe4a9cc3c7b4d3b266d4c5e5a68d063261'
BOT_TOKEN = '8166571880:AAEZ7__xJzYoOR0zTr3n8ZbTWUYhDYfGezY'
BASE_URL = 'https://shortner.noirsane.com'
DEFAULT_FOOTER = "\n\nJoin this channel for more videos 😚✅👇\nhttps://t.me/noirsanebackup"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

def shorten_link_with_retry(url):
    while True:
        try:
            response = requests.get(
                f"{BASE_URL}/api?api={API_KEY}&url={url}&format=text",
                timeout=8
            )
            if response.ok:
                return response.text.strip()
        except Exception:
            time.sleep(1)

def find_and_shorten_links(text):
    if not text:
        return ""
    urls = re.findall(r'(https?://\S+)', text)
    for url in set(urls):
        if validators.url(url):
            short = shorten_link_with_retry(url)
            text = text.replace(url, short)
    return text + DEFAULT_FOOTER if urls else text

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message,
        "🌟 Welcome to the Premium Link Shortener Bot! 🌐\n\n"
        "📌 Just send any text, photo, or video with a link — I’ll shorten it instantly.\n"
        "💰 Login to earn: https://shortner.noirsane.com\n\n"
        "🚀 Crafted with ❤️ by Saptarshi Singh"
    )

def process_message(msg):
    try:
        caption = msg.caption or ""
        if msg.text:
            updated = find_and_shorten_links(msg.text.strip())
            bot.reply_to(msg, updated)
        elif msg.photo:
            updated = find_and_shorten_links(caption)
            bot.send_photo(msg.chat.id, msg.photo[-1].file_id, caption=updated)
        elif msg.video:
            updated = find_and_shorten_links(caption)
            bot.send_video(msg.chat.id, msg.video.file_id, caption=updated)
        elif msg.document:
            updated = find_and_shorten_links(caption)
            bot.send_document(msg.chat.id, msg.document.file_id, caption=updated)
    except Exception as e:
        print(f"[ERROR] {e}")

@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'video', 'document'])
def handle_all(m):
    threading.Thread(target=process_message, args=(m,), daemon=True).start()

@app.route('/webhook', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "ok", 200

@app.route('/')
def index():
    return "Bot is active!", 200

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
