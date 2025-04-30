import telebot
import requests
import validators
import re
import time
import threading
import random

bot = telebot.TeleBot('8166571880:AAEZ7__xJzYoOR0zTr3n8ZbTWUYhDYfGezY')
API_KEY = 'abf109fe4a9cc3c7b4d3b266d4c5e5a68d063261'
DEFAULT_FOOTER = "\n\nJoin this channel for more videos 😚✅👇\nhttps://t.me/noirsanebackup"
last_seen = {}

romantic_questions = [
    "Do you believe in love at first sight or should I walk by again Raj? 😍",
    "What's your idea of a perfect date night Raj? 🌟",
    "Raj...If we were characters in a romantic movie, what would our story be? 🎓💕",
    "Raj...What’s the most romantic thing someone has ever done for you? 😘",
    "Raj...Would you rather watch a sunset together or stargaze all night? 🌇"
]

def safe_shorten(url):
    try:
        response = requests.get(
            f"https://shortner.noirsane.com/api?api={API_KEY}&url={url}&format=text",
            timeout=6
        )
        if response.ok and response.text.strip().startswith("http"):
            return response.text.strip()
    except Exception as e:
        print(f"❌ Error shortening {url}: {e}")
    return url  # fallback to original if failed

def find_and_shorten_links(text):
    if not text:
        return ""
    
    url_pattern = r'(https?://[^\s]+)'
    urls = list(set(re.findall(url_pattern, text)))
    if not urls:
        return text

    shortened_map = {}

    threads = []

    def shorten_and_store(u):
        shortened_map[u] = safe_shorten(u)

    for url in urls:
        t = threading.Thread(target=shorten_and_store, args=(url,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    for original, short in shortened_map.items():
        text = text.replace(original, short)

    return text + DEFAULT_FOOTER

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message,
        "🌟 Welcome to the Premium Link Shortener Bot! 🌐\n\n"
        "📌 Just send any text, photo, or video with a link — I’ll shorten it instantly.\n"
        "💰 Login to earn: https://shortner.noirsane.com\n\n"
        "🚀 Crafted with ❤️ by Saptarshi Singh"
    )
    last_seen[message.chat.id] = time.time()

def process_caption_and_respond(message, media_type):
    caption = message.caption if message.caption else ""
    updated = find_and_shorten_links(caption)

    try:
        if media_type == 'photo':
            bot.send_photo(message.chat.id, message.photo[-1].file_id, caption=updated)
        elif media_type == 'video':
            bot.send_video(message.chat.id, message.video.file_id, caption=updated)
        elif media_type == 'document':
            bot.send_document(message.chat.id, message.document.file_id, caption=updated)
    except Exception as e:
        print(f"⚠️ Failed to send media: {e}")

    last_seen[message.chat.id] = time.time()

@bot.message_handler(content_types=['text'])
def handle_text(message):
    updated = find_and_shorten_links(message.text.strip())
    bot.reply_to(message, updated)
    last_seen[message.chat.id] = time.time()

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    process_caption_and_respond(message, 'photo')

@bot.message_handler(content_types=['video'])
def handle_video(message):
    process_caption_and_respond(message, 'video')

@bot.message_handler(content_types=['document'])
def handle_document(message):
    process_caption_and_respond(message, 'document')

@bot.message_handler(func=lambda message: True)
def handle_bulk(message):
    try:
        time.sleep(0.2)
        if message.text:
            handle_text(message)
        elif message.photo:
            handle_photo(message)
        elif message.video:
            handle_video(message)
        elif message.document:
            handle_document(message)
    except Exception as e:
        print(f"💥 Error in bulk processing: {e}")

def romance_engagement_loop():
    while True:
        current_time = time.time()
        for chat_id, last_time in list(last_seen.items()):
            if current_time - last_time > 120:
                question = random.choice(romantic_questions)
                try:
                    bot.send_message(chat_id, question)
                    last_seen[chat_id] = current_time
                except:
                    pass
        time.sleep(60)

threading.Thread(target=romance_engagement_loop, daemon=True).start()
bot.infinity_polling(timeout=10, long_polling_timeout=5)
