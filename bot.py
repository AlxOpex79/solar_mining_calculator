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
GRID_TARIFF = 4.32

def get_live_rates():
    try:
        btc_data = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd").json()
        btc_p = btc_data['bitcoin']['usd']
        uah_data = requests.get("https://api.exchangerate-api.com/v4/latest/USD").json()
        usd_r = uah_data['rates']['UAH']
        return btc_p, usd_r
    except:
        return 92000, 41.5

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    kb.add("📊 Сезонный отчет (кВт)", "💰 Финансы (Сальдо с перекрытием)", "🚀 Окупаемость S21 (Live)", "📅 Годовой баланс СЭС")
    await message.answer(f"Алексей, все вкладки починены! Логика Net Billing настроена через накопительный депозит.", reply_markup=kb)

@dp.message_handler(lambda m: "Финансы" in m.text)
async def finance_report(message: types.Message):
    btc_p, usd_r = get_live_rates()
    monthly_rev_uah = (DAILY_BTC_FLOW * 30.5) * btc_p * usd_r
    
    # ЛОГИКА ДЕПОЗИТА
    summer_surplus = 3840 # накопили за лето
    autumn_spring_deficit = 4320 # потратили за 6 мес
    winter_deficit = 6210 # потратили за зиму
    
    # Считаем реальный расход после перекрытия
    total_needed = autumn_spring_deficit + winter_deficit # 10530
    real_grid_pay = total_needed - summer_surplus # Остаток, за который платим (6690 кВт)
    
    total_light_bill = real_grid_pay * GRID_TARIFF
    total_year_profit_uah = (monthly_rev_uah * 12) - total_light_bill

    text = (
        f"💰 **ФИНАНСОВОЕ САЛЬДО (Логика перекрытия):**\n\n"
        f"☀️ **Лето:** Доход чистый, свет 0 грн. Накоплено {summer_surplus} кВт·ч.\n"
        f"🍂🌻 **Осень/Весна:** Тратим летний запас. Свет 0 грн, пока есть бонус.\n"
        f"❄️ **Зима:** Запас исчерпан. Начинаем платить по 4.32 грн.\n"
        f"--- \n"
        f"💸 **Затраты на свет за год:** {round(total_light_bill):,} ₴\n"
        f"*(Оплачено {real_grid_pay} кВт из {total_needed} дефицитных)*\n\n"
        f"🏆 **ИТОГОВЫЙ ПРОФИТ (Год):**\n"
        f"🔥 **{round(total_year_profit_uah):,} ₴**\n"
        f"💵 **${round(total_year_profit_uah/usd_r):,}**\n\n"
        f"Курс: {btc_p}$ | {usd_r}₴"
    )
    await message.answer(text)

@dp.message_handler(lambda m: "Сезонный отчет" in m.text)
async def seasonal_total(message: types.Message):
    text = (
        f"📊 **Баланс по периодам (кВт·ч):**\n\n"
        f"☀️ **ЛЕТО:** Пришло 11400 | Ушло 7560 | **+3840**\n"
        f"🍂🌻 **О/В:** Пришло 10800 | Ушло 15120 | **-4320**\n"
        f"❄️ **ЗИМА:** Пришло 1350 | Ушло 7560 | **-6210**"
    )
    await message.answer(text)

@dp.message_handler(lambda m: "Окупаемость S21" in m.text)
async def roi_live(message: types.Message):
    btc_p, usd_r = get_live_rates()
    roi_days = DEVICE_PRICE_USD / (DAILY_BTC_FLOW * btc_p)
    text = (
        f"🚀 **LIVE Окупаемость:**\n"
        f"• Год: ₿{round(DAILY_BTC_FLOW * 365, 5)}\n"
        f"• Срок: {round(roi_days)} дней\n"
        f"• Курс: {btc_p}$"
    )
    await message.answer(text)

@dp.message_handler(lambda m: "Годовой баланс" in m.text)
async def yearly(message: types.Message):
    await message.answer("📅 **Итог года:**\n🌞 СЭС: 32 000 кВт·ч\n⚡ S21: 30 660 кВт·ч\n🏆 Остаток: **+1340 кВт·ч**")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
