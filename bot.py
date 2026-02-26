import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# Настройки логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота
API_TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- ИСХОДНЫЕ ДАННЫЕ ---
DEVICE_PRICE = 5000       # Стоимость S21 в $
MINER_KW = 3.5            # Потребление S21 в кВт/час
MONTHLY_CONS = 2520       # Расход S21 в месяц (3.5 * 24 * 30)
DAILY_BTC = 0.00038       # Добыча BTC в сутки на 200 TH/s (актуально на 2026)
BTC_PRICE = 85000         # Прогнозный курс BTC для расчета

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    buttons = [
        "📊 Сезонный отчет (Разница кВт)",
        "🚀 Окупаемость S21 + Добыча BTC",
        "📅 Годовой баланс СЭС"
    ]
    keyboard.add(*buttons)
    await message.answer(
        f"Алексей, система настроена под СЭС 30 кВт в Боярке (оя).\n"
        f"Все расчеты приведены к общему порядку Net Billing.",
        reply_markup=keyboard
    )

@dp.message_handler(lambda message: "Сезонный отчет" in message.text)
async def seasonal_report(message: types.Message):
    # Логика: Генерация - Потребление (2520 кВт*ч)
    text = (
        f"📊 **Баланс по сезонам (кВт⋅ч):**\n\n"
        f"☀️ **ЛЕТО:**\n"
        f"Генерация: ~3800 | Расход: 2520\n"
        f"➕ Разница: **+1280 кВт⋅ч/мес** (в копилку)\n\n"
        f"🍂 **ОСЕНЬ/ВЕСНА:**\n"
        f"Генерация: ~1800 | Расход: 2520\n"
        f"➖ Разница: **-720 кВт⋅ч/мес** (из копилки)\n\n"
        f"❄️ **ЗИМА:**\n"
        f"Генерация: ~450 | Расход: 2520\n"
        f"➖ Разница: **-2070 кВт⋅ч/мес** (из копилки)\n\n"
        f"💡 *Благодаря Net Billing зимний дефицит гасится летним избытком.*"
    )
    await message.answer(text)

@dp.message_handler(lambda message: "Окупаемость S21" in message.text)
async def calculate_roi(message: types.Message):
    monthly_btc = DAILY_BTC * 30.5
    yearly_btc = DAILY_BTC * 365
    yearly_usd = yearly_btc * BTC_PRICE
    
    # При СЭС 30 кВт затраты на свет = 0
    roi_days = DEVICE_PRICE / (DAILY_BTC * BTC_PRICE)
    
    text = (
        f"🚀 **Расчет окупаемости S21:**\n\n"
        f"💰 **Добыча биткоина:**\n"
        f"• В месяц: ₿{round(monthly_btc, 5)}\n"
        f"• В год: **₿{round(yearly_btc, 5)}**\n\n"
        f"💵 **Финансо
