import telebot
import requests
import validators
import re

# Your actual bot token and API key
bot = telebot.TeleBot('7670050222:AAEBCHD07v-Bauov9zjjSAoJucqHWFYSEa8')
API_KEY = '3258415006603e646926420840c3469a68c377a1'

def find_and_shorten_links(text):
    url_pattern = r'(https?://\S+)'
    urls = re.findall(url_pattern, text)
    for url in urls:
        if validators.url(url):
            try:
                api_url = f"https://shortner.noirsane.com/api?api={API_KEY}&url={url}&format=text"
                response = requests.get(api_url)
                short_url = response.text.strip()
                text = text.replace(url, short_url)
            except Exception as e:
                print(f"Error shortening {url}: {e}")
    return text

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message,
        "🌟 Welcome to the Premium Link Shortener Bot! 🌐\n\n"
        "📎 Just send any text or photo with a link, and I’ll convert it into a short branded URL instantly.\n"
        "💰 Want to shorten your own links and earn? Login now: https://shortner.noirsane.com\n\n"
        "🚀 Crafted with ❤️ by Saptarshi Singh"
    )

@bot.message_handler(content_types=['text'])
def handle_text(message):
    updated_text = find_and_shorten_links(message.text.strip())
    bot.reply_to(message, updated_text)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    caption = message.caption if message.caption else ""
    updated_caption = find_and_shorten_links(caption)
    bot.send_photo(chat_id=message.chat.id, photo=message.photo[-1].file_id, caption=updated_caption)

# Start polling
bot.polling()
