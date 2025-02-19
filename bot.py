import asyncio
import logging
import os
import google.generativeai as genai
import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message
from aiogram.filters import Command
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()
TOKEN = os.getenv("TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not TOKEN or not GEMINI_API_KEY:
    raise ValueError("❌ Не установлены переменные окружения! Проверьте Railway Variables.")

# Настройки
logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Инициализация Google Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")  # Используем Gemini Pro

# Функция для парсинга текста новости
def extract_text_from_url(url):
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        text = " ".join([p.get_text() for p in paragraphs])
        return text[:3000]  # Ограничение символов
    except Exception as e:
        return f"Ошибка при парсинге: {e}"

# Функция для анализа новости через Gemini
async def check_fake_news(text):
    prompt = f"Определи, является ли эта новость фейковой:\n{text}"
    try:
        response = model.generate_content(prompt)
        return response.text  # Возвращаем текстовый ответ от Gemini
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

    # Анализируем через Gemini
    analysis = await check_fake_news(text)
    await message.answer(f"🤖 Анализ новости:\n{analysis}")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
