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
last_seen = {}  # chat_id: timestamp

romantic_questions = [
    "Do you believe in love at first sight or should I walk by again Raj? 😍",
    "What's your idea of a perfect date night Raj? 🌟",
    "Raj...If we were characters in a romantic movie, what would our story be? 🎓💕",
    "Raj...What’s the most romantic thing someone has ever done for you? 😘",
    "Raj...Would you rather watch a sunset together or stargaze all night? 🌇"
]

shorten_cache = {}  # Cache to store already-shortened URLs


def find_and_shorten_links(text):
    if not text:
        return ""

    url_pattern = r'(https?://\S+)'
    urls = re.findall(url_pattern, text)
    unique_urls = list(set(urls))

    for url in unique_urls:
        if not validators.url(url):
            continue

        if url in shorten_cache:
            short_url = shorten_cache[url]
        else:
            short_url = None
            for attempt in range(2):  # Retry twice
                try:
                    time.sleep(0.3)  # Delay between API calls
                    response = requests.get(
                        f"https://shortner.noirsane.com/api?api={API_KEY}&url={url}&format=text",
                        timeout=10
                    )
                    if response.ok:
                        short_url = response.text.strip()
                        shorten_cache[url] = short_url
                        break
                except Exception as e:
                    print(f"[Retry {attempt+1}] Error shortening {url}: {e}")
                    time.sleep(1)

        if short_url:
            text = text.replace(url, short_url)
        else:
            print(f"⚠️ Could not shorten: {url}")

    return text + DEFAULT_FOOTER if unique_urls else text


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message,
        "🌟 Welcome to the Premium Link Shortener Bot! 🌐\n\n"
        "📌 Just send any text, photo, or video with a link — I’ll shorten it instantly.\n"
        "💰 Login to earn: https://shortner.noirsane.com\n\n"
        "🚀 Crafted with ❤️ by Saptarshi Singh"
    )
    last_seen[message.chat.id] = time.time()

@bot.message_handler(content_types=['text'])
def handle_text(message):
    updated = find_and_shorten_links(message.text.strip())
    bot.reply_to(message, updated)
    last_seen[message.chat.id] = time.time()

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    caption = message.caption if message.caption else ""
    updated = find_and_shorten_links(caption)
    bot.send_photo(message.chat.id, message.photo[-1].file_id, caption=updated)
    last_seen[message.chat.id] = time.time()

@bot.message_handler(content_types=['video'])
def handle_video(message):
    caption = message.caption if message.caption else ""
    updated = find_and_shorten_links(caption)
    bot.send_video(message.chat.id, message.video.file_id, caption=updated)
    last_seen[message.chat.id] = time.time()

@bot.message_handler(content_types=['document'])
def handle_document(message):
    caption = message.caption if message.caption else ""
    updated = find_and_shorten_links(caption)
    bot.send_document(message.chat.id, message.document.file_id, caption=updated)
    last_seen[message.chat.id] = time.time()

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


# Start romantic engagement in background
threading.Thread(target=romance_engagement_loop, daemon=True).start()

# Run the bot
bot.infinity_polling(timeout=10, long_polling_timeout=5)
