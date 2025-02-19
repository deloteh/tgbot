import logging
import openai
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor
import requests
from bs4 import BeautifulSoup

# Твой Telegram API токен
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
# Твой OpenAI API ключ
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

openai.api_key = OPENAI_API_KEY

# Функция для парсинга текста новости
def extract_text_from_url(url):
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        text = " ".join([p.get_text() for p in paragraphs])
        return text[:4000]  # Ограничение, чтобы не превышать лимит GPT
    except Exception as e:
        return f"Ошибка парсинга: {e}"

# Функция проверки фейковости через ChatGPT
def check_fake_news(text):
    prompt = f"Определи, является ли эта новость фейковой:\n{text}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"]

# Обработчик команды /start
@dp.message_handler(commands=["start"])
async def start(message: Message):
    await message.answer("Привет! Отправь мне ссылку на новость, и я проверю её на достоверность.")

# Обработчик ссылок
@dp.message_handler(lambda message: message.text.startswith("http"))
async def handle_url(message: Message):
    await message.answer("Проверяю новость, подожди...")
    text = extract_text_from_url(message.text)
    if "Ошибка парсинга" in text:
        await message.answer(text)
        return

    analysis = check_fake_news(text)
    await message.answer(f"🔍 Анализ новости:\n{analysis}")

# Запуск бота
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
