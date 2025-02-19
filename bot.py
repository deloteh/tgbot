import asyncio
import logging
import os
import openai
import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message
from aiogram.filters import Command
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()
TOKEN = os.getenv("TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TOKEN or not OPENAI_API_KEY:
    raise ValueError("❌ Не установлены переменные окружения! Проверьте Railway Variables.")

# Настройки
logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()
openai_client = openai.Client(api_key=OPENAI_API_KEY)  # ✅ Новый клиент OpenAI

# Функция для парсинга текста новости
def extract_text_from_url(url):
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        text = " ".join([p.get_text() for p in paragraphs])
        return text[:4000]  # Ограничение для OpenAI
    except Exception as e:
        return f"Ошибка при парсинге: {e}"

# Функция для анализа новости через ChatGPT
async def check_fake_news(text):
    prompt = f"Определи, является ли эта новость фейковой:\n{text}"
    try:
        response = openai_client.chat.completions.create(  # ✅ Новый вызов OpenAI API
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Ошибка при анализе: {e}"

# Обработчик команды /start
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("Привет! Отправь мне ссылку на новость, и я проверю её на достоверность.")

# Обработчик ссылок
@dp.message(F.text.startswith("http"))
async def handle_url(message: Message):
    await message.answer("🔍 Проверяю новость, подожди немного...")

    # Парсим текст
    text = extract_text_from_url(message.text)
    if "Ошибка при парсинге" in text:
        await message.answer(text)
        return

    # Анализируем через OpenAI
    analysis = await check_fake_news(text)
    await message.answer(f"🤖 Анализ новости:\n{analysis}")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
