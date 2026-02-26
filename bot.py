import logging
import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

logging.basicConfig(level=logging.INFO)

API_TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Константы
DEVICE_PRICE_USD = 5000
DAILY_BTC_FLOW = 0.00038 
MONTHLY_CONS = 2520
GRID_TARIFF = 4.32 # грн за 1 кВт

def get_live_rates():
    try:
        btc_data = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd").json()
        btc_price = btc_data['bitcoin']['usd']
        uah_data = requests.get("https://api.exchangerate-api.com/v4/latest/USD").json()
        usd_to_uah = uah_data['rates']['UAH']
        return btc_price, usd_to_uah
    except:
        return 90000, 41.5

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    kb.add("📊 Сезонный отчет (кВт)", "💰 Финансы (Сальдо ₴/$)", "🚀 Окупаемость S21 (Live)", "📅 Годовой баланс СЭС")
    await message.answer(f"Алексей, добавлена финансовая аналитика для Боярки (оя)!", reply_markup=kb)

@dp.message_handler(lambda m: "Финансы" in m.text)
async def finance_report(message: types.Message):
    btc_p, usd_r = get_live_rates()
    
    # 1. Доход от майнинга в месяц (чистый BTC)
    monthly_btc = DAILY_BTC_FLOW * 30.5
    monthly_rev_usd = monthly_btc * btc_p
    monthly_rev_uah = monthly_rev_usd * usd_r

    # 2. Расчет по периодам
    # ЛЕТО (Плюс в кВт превращаем в экономию)
    summer_profit_uah = (monthly_rev_uah * 3) # Свет 0 грн
    
    # ОСЕНЬ/ВЕСНА (Докупаем свет)
    mid_deficit_kwh = 720 # в месяц
    mid_light_cost = mid_deficit_kwh * GRID_TARIFF
    mid_profit_uah = (monthly_rev_uah - mid_light_cost) * 6

    # ЗИМА (Докупаем много света)
    winter_deficit_kwh = 2070 # в месяц
    winter_light_cost = winter_deficit_kwh * GRID_TARIFF
    winter_profit_uah = (monthly_rev_uah - winter_light_cost) * 3

    total_year_uah = summer_profit_uah + mid_profit_uah + winter_profit_uah

    text = (
        f"💰 **ФИНАНСОВОЕ САЛЬДО (Курс: {btc_p}$ / {usd_r}₴):**\n\n"
        f"☀️ **ЛЕТО (3 мес):**\n"
        f"Добыча: ₿{round(monthly_btc*3, 4)}\n"
        f"Сальдо: **+{round(summer_profit_uah):,} ₴** (${round(summer_profit_uah/usd_r)})\n"
        f"*Свет полностью перекрыт*\n\n"
        
        f"🍂🌻 **ОСЕНЬ/ВЕСНА (6 мес):**\n"
        f"Затраты на свет: -{round(mid_light_cost * 6):,} ₴\n"
        f"Сальдо: **+{round(mid_profit_uah):,} ₴** (${round(mid_profit_uah/usd_r)})\n\n"
        
        f"❄️ **ЗИМА (3 мес):**\n"
        f"Затраты на свет: -{round(winter_light_cost * 3):,} ₴\n"
        f"Сальдо: **+{round(winter_profit_uah):,} ₴** (${round(winter_profit_uah/usd_r)})\n"
        f"--- \n"
        f"🏆 **ЧИСТЫЙ ПРОФИТ ЗА ГОД:**\n"
        f"🔥 **{round(total_year_uah):,} ₴** (${round(total_year_uah/usd_r)})\n\n"
        f"Алексей, это твои реальные деньги на руки после оплаты всех счетов за свет."
    )
    await message.answer(text)

# Остальные хендлеры (Сезонный отчет, Окупаемость, Баланс) остаются как в прошлом коде

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
