import telebot
import requests
import validators

# Replace 'YOUR_BOT_TOKEN' with your actual Telegram bot token
bot = telebot.TeleBot('7670050222:AAEBCHD07v-Bauov9zjjSAoJucqHWFYSEa8')

# Replace 'YOUR_API_KEY' with your actual API key from NoirSane URL shortener
API_KEY = '3258415006603e646926420840c3469a68c377a1'

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "👋 Hi! Send me any link, and I'll shorten it for you.")

@bot.message_handler(func=lambda message: True)
def shorten_url(message):
    url = message.text.strip()

    # Validate the URL
    if not validators.url(url):
        bot.reply_to(message, "❌ Please send a valid URL.")
        return

    try:
        # Shorten the URL using NoirSane API
        api_url = f"https://shortner.noirsane.com/api?api={API_KEY}&url={url}&format=text"
        response = requests.get(api_url)
        short_url = response.text.strip()

        if short_url:
            bot.reply_to(message, f"🔗 Here is your shortened link: {short_url}")
        else:
            bot.reply_to(message, "❌ Error shortening the link. Please check your URL.")
    except Exception as e:
        bot.reply_to(message, "⚠️ An error occurred while shortening the URL.")
        print(f"Error: {e}")

# Start the bot
bot.polling()
