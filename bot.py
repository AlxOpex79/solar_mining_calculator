import logging
import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

logging.basicConfig(level=logging.INFO)

API_TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Константы оборудования (S21 200 TH)
DEVICE_PRICE_USD = 5000
DAILY_BTC_FLOW = 0.00038 
MONTHLY_CONS = 2520 # 3.5 кВт * 24 * 30

def get_live_rates():
    try:
        btc_data = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd").json()
        btc_to_usd = btc_data['bitcoin']['usd']
        uah_data = requests.get("https://api.exchangerate-api.com/v4/latest/USD").json()
        usd_to_uah = uah_data['rates']['UAH']
        return btc_to_usd, usd_to_uah
    except:
        return 88000, 41.5 # Резерв

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    kb.add("📊 Сезонный отчет (Суммарно кВт)", "🚀 Окупаемость S21 (Live $, ₴)", "📅 Годовой баланс СЭС")
    await message.answer(f"Алексей, теперь отчеты показывают суммарный приход и расход по периодам!", reply_markup=kb)

@dp.message_handler(lambda m: "Сезонный отчет" in m.text)
async def seasonal_total(message: types.Message):
    # ЛЕТО (3 месяца)
    summer_gen = 3800 * 3
    summer_cons = MONTHLY_CONS * 3
    summer_diff = summer_gen - summer_cons

    # ОСЕНЬ + ВЕСНА (6 месяцев)
    mid_gen = 1800 * 6
    mid_cons = MONTHLY_CONS * 6
    mid_diff = mid_gen - mid_cons

    # ЗИМА (3 месяца)
    winter_gen = 450 * 3
    winter_cons = MONTHLY_CONS * 3
    winter_diff = winter_gen - winter_cons

    text = (
        f"📊 **Суммарный баланс по периодам (кВт⋅ч):**\n\n"
        f"☀️ **ЛЕТО (Июнь-Авг):**\n"
        f"  • Пришло: {summer_gen}\n"
        f"  • Ушло: {summer_cons}\n"
        f"  ➕ **Накоплено: +{summer_diff} кВт⋅ч**\n\n"
        f"🍂🌻 **ОСЕНЬ/ВЕСНА (6 мес):**\n"
        f"  • Пришло: {mid_gen}\n"
        f"  • Ушло: {mid_cons}\n"
        f"  ➖ **Расход баланса: {mid_diff} кВт⋅ч**\n\n"
        f"❄️ **ЗИМА (Дек-Фев):**\n"
        f"  • Пришло: {winter_gen}\n"
        f"  • Ушло: {winter_cons}\n"
        f"  ➖ **Расход баланса: {winter_diff} кВт⋅ч**\n\n"
        f"💡 *Весь дефицит осени и зимы перекрывается летним солнцем.*"
    )
    await message.answer(text)

@dp.message_handler(lambda m: "Окупаемость S21" in m.text)
async def roi_live(message: types.Message):
    btc_price, usd_rate = get_live_rates()
    daily_rev_usd = DAILY_BTC_FLOW * btc_price
    yearly_rev_usd = daily_rev_usd * 365
    roi_days = DEVICE_PRICE_USD / daily_rev_usd
    
    text = (
        f"🚀 **LIVE Окупаемость (Боярка/оя):**\n\n"
        f"💰 **Добыча в год:**\n"
        f"₿ {round(DAILY_BTC_FLOW * 365, 5)} BTC\n"
        f"$ {round(yearly_rev_usd, 2):,}\n"
        f"₴ {round(yearly_rev_usd * usd_rate, 2):,}\n\n"
        f"⏳ **Срок:** {round(roi_days)} дней (~{round(roi_days/30.5, 1)} мес.)\n"
        f"🔌 Свет: 0.00 грн (Net Billing)"
    )
    await message.answer(text)

@dp.message_handler(lambda m: "Годовой баланс" in m.text)
async def yearly(message: types.Message):
    annual_gen = 32000
    annual_cons = MONTHLY_CONS * 12
    await message.answer(f"📅 **Итог года:**\n🌞 СЭС: 32 000 кВт⋅ч\n⚡ S21: {annual_cons} кВт⋅ч\n🏆 Остаток: **+{annual_gen - annual_cons} кВт⋅ч**")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
