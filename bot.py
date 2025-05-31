import re
import asyncio
import aiohttp
import validators
from aiogram import Bot, Dispatcher, types
from aiogram.types import ContentType
from aiogram.utils import executor

# Telegram Bot Token
BOT_TOKEN = "8166571880:AAH59oE0qwi00nIKJaau33bPxmMlV_4eEZY"

# API Keys for link shortener
API_KEYS = [
    "abf109fe4a9cc3c7b4d3b266d4c5e5a68d063261",
    "3258415006603e646926420840c3469a68c377a1"
]

DEFAULT_HEADER = (
    "\n\n 🔞 https://t.me/+zNbzsB_y25AwNDJl 🔞 \n 👆🔞Join This backup channel🔞 👆 \n 🔗⚔━━━━━━━━━━━━━━━━━⚔"
)
DEFAULT_FOOTER = (
    "\n ⚔━━━━━━━━━━━━━━━━━⚔ \n Backup - \n Join this chinnal guys 🔞🔞👇👇 \n"
    "https://t.me/+Rqe3fVJ_QBthNjFl \n\n"
    "Join this 🎥MOVIE🎥 channel  👇👇 \n https://t.me/+Tixf7zhZ6Ok2YzY1 \n\n"
    "👉🔗 HOW TO DOWNLOAD🔗👈 \n https://t.me/publicc_778/56"
)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'https?://t\.me/\S+', '', text)
    text = re.sub(r'(?i)join\s+this\s+channel.*', '', text)
    text = re.sub(r'(?i)Join.*👇.*', '', text)
    text = re.sub(r'@', '', text)
    text = re.sub(r'\n{2,}', '\n', text)
    return text.strip()


async def shorten_url(session: aiohttp.ClientSession, url: str) -> str:
    for api_key in API_KEYS:
        try:
            async with session.get(
                "https://shortner.noirsane.com/api",
                params={
                    "api": api_key,
                    "url": url,
                    "format": "text"
                },
                timeout=10
            ) as response:
                if response.status == 200:
                    short_url = await response.text()
                    if short_url.startswith("http"):
                        print(f"✅ Shortened using key {api_key[:6]}: {short_url.strip()}")
                        return short_url.strip()
                    else:
                        print(f"❌ API key {api_key[:6]} invalid response: {short_url.strip()}")
        except asyncio.TimeoutError:
            print(f"⛔ Timeout with key {api_key[:6]}")
        except Exception as e:
            print(f"⛔ Error with key {api_key[:6]}: {e}")
    print("‼️ All keys failed. Using original URL.")
    return url


async def process_links(text: str) -> str:
    clean = clean_text(text)
    urls = list(set(re.findall(r'(https?://\S+)', clean)))

    async with aiohttp.ClientSession() as session:
        shortened_map = {}
        for url in urls:
            if validators.url(url):
                shortened = await shorten_url(session, url)
                shortened_map[url] = shortened
                await asyncio.sleep(0.1)

    for original, short in shortened_map.items():
        clean = clean.replace(original, short)

    return f"{DEFAULT_HEADER}\n{clean}{DEFAULT_FOOTER}"


@dp.message_handler(commands=["start", "help"])
async def start_cmd(message: types.Message):
    await message.reply(
        "🌟 Welcome to the Premium Link Shortener Bot! 🌐\n\n"
        "📎 Just send any text, photo, or video with a link — I’ll shorten it instantly.\n"
        "💰 Login to earn: https://shortner.noirsane.com\n\n"
        "🚀 Crafted with ❤️‍🔥"
    )


@dp.message_handler(content_types=ContentType.TEXT)
async def handle_text(message: types.Message):
    result = await process_links(message.text)
    await message.reply(result)


@dp.message_handler(content_types=ContentType.PHOTO)
async def handle_photo(message: types.Message):
    caption = message.caption or ""
    result = await process_links(caption)
    await bot.send_photo(message.chat.id, message.photo[-1].file_id, caption=result)


@dp.message_handler(content_types=ContentType.VIDEO)
async def handle_video(message: types.Message):
    caption = message.caption or ""
    result = await process_links(caption)
    await bot.send_video(message.chat.id, message.video.file_id, caption=result)

@dp.message_handler(content_types=ContentType.DOCUMENT)
async def handle_document(message: types.Message):
    caption = message.caption or ""
    result = await process_links(caption)
    await bot.send_document(message.chat.id, message.document.file_id, caption=result)


if __name__ == "__main__":
    print("🤖 Async bot is running...")
    executor.start_polling(dp, skip_updates=True)
