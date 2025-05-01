import telebot
import requests
import validators
import re
import time

bot = telebot.TeleBot('8166571880:AAEZ7__xJzYoOR0zTr3n8ZbTWUYhDYfGezY')
API_KEY = 'abf109fe4a9cc3c7b4d3b266d4c5e5a68d063261'

DEFAULT_FOOTER = "\n\nJoin this channel for more videos 😚✅👇\nhttps://t.me/noirsanebackup"

def find_and_shorten_links(text):
    if not text:
        return ""
    url_pattern = r'(https?://\S+)'
    urls = re.findall(url_pattern, text)
    unique_urls = list(set(urls))
    for url in unique_urls:
        if validators.url(url):
            try:
                response = requests.get(
                    f"https://shortner.noirsane.com/api?api={API_KEY}&url={url}&format=text",
                    timeout=5
                )
                short_url = response.text.strip()
                text = text.replace(url, short_url)
            except Exception as e:
                print(f"Error shortening {url}: {e}")
    return text + DEFAULT_FOOTER if unique_urls else text

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message,
        "🌟 Welcome to the Premium Link Shortener Bot! 🌐\n\n"
        "📎 Just send any text, photo, or video with a link — I’ll shorten it instantly.\n"
        "💰 Login to earn: https://shortner.noirsane.com\n\n"
        "🚀 Crafted with ❤️ by Saptarshi Singh"
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

# Optional: handles forward spam or 50+ messages safely
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

# Run the bot
bot.infinity_polling() 
