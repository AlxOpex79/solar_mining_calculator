import logging
import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

logging.basicConfig(level=logging.INFO)

API_TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- БАЗОВЫЕ ЗАТРАТЫ (в $) ---
SES_PRICE = 16000          # СЭС 30 кВт
POWER_UP_PRICE = 2000      # Ввод 30 кВт
ASIC_PRICE_ONE = 5000      # За 1 шт S21
TOTAL_INV_TWO_ASICS = SES_PRICE + POWER_UP_PRICE + (ASIC_PRICE_ONE * 2)

# --- ТЕХНИЧЕСКИЕ ПАРАМЕТРЫ ---
DAILY_BTC_ONE = 0.00038
DAILY_BTC_TWO = 0.00076
GRID_TARIFF_UAH = 4.32

def get_live_data():
    """Получает актуальные курсы BTC/USD и USD/UAH"""
    try:
        # Курс BTC
        btc_r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd").json()
        btc_p = btc_r['bitcoin']['usd']
        # Курс USD/UAH
        uah_r = requests.get("https://api.exchangerate-api.com/v4/latest/USD").json()
        usd_rate = uah_r['rates']['UAH']
        return btc_p, usd_rate
    except Exception as e:
        logging.error(f"Ошибка API: {e}")
        return 95000, 41.5 # Резерв, если API временно недоступно

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    kb.add(
        "🚀 Окупаемость: БИЗНЕС (2 ASIC)",
        "💰 Финансы (Сальдо 1 vs 2 ASIC)",
        "🏗️ Детализация затрат ($/₴)",
        "📊 Сезонный баланс кВт",
        "📅 Годовой итог СЭС"
    )
    await message.answer(f"Алексей, все данные теперь LIVE. Каждая кнопка пересчитывает курсы в реальном времени!", reply_markup=kb)

@dp.message_handler(lambda m: "Детализация затрат" in m.text)
async def costs_detail(message: types.Me
