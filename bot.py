import logging
import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

logging.basicConfig(level=logging.INFO)

API_TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- ДАННЫЕ ПРОЕКТА ---
SES_PRICE = 16000          # СЭС 30 кВт
POWER_UP_PRICE = 2000      # Ввод 30 кВт
ASIC_PRICE_ONE = 5000      # За 1 шт S21
TOTAL_INV_TWO = SES_PRICE + POWER_UP_PRICE + (ASIC_PRICE_ONE * 2)

DAILY_BTC_ONE = 0.00038
DAILY_BTC_TWO = 0.00076
GRID_TARIFF = 4.32

def get_live_data():
    try:
        btc_r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd", timeout=10).json()
        btc_p = btc_r['bitcoin']['usd']
        uah_r = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=10).json()
        usd_rate = uah_r['rates']['UAH']
        return btc_p, usd_rate
    except:
        return 90000, 41.5

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    kb.add("🚀 Окупаемость: БИЗНЕС (2 ASIC)", "💰 Финансы (Сальдо 1 vs 2 ASIC)", "🏗️ Детализация затрат", "📊 Сезонный баланс кВт")
    await message.answer("Алексей, система обновлена! Все данные LIVE.", reply_markup=kb)

@dp.message_handler(lambda m: "Детализация затрат" in m.text)
async def costs_detail(message: types.Message):
    btc_p, usd_r = get_live_data()
    total_uah = TOTAL_INV_TWO * usd_r
    text = (
        f"🏗️ **ЗАТРАТЫ (Курс {usd_r} ₴):**\n\n"
        f"• СЭС 30 кВт: ${SES_PRICE:,}\n"
        f"• Ввод 30 кВт: ${POWER_UP_PRICE:,}\n"
        f"• 2 × S21: ${ASIC_PRICE_ONE * 2:,}\n"
        f"--- \n"
        f"💰 **ИТОГО: ${TOTAL_INV_TWO:,} / {round(total_uah):,}-₴**"
    )
    await message.answer(text)

@dp.message_handler(lambda m: "Окупаемость: БИЗНЕС" in m.text)
async def roi_two_asics(message: types.Message):
    btc_p, usd_r = get_live_data()
    annual_rev_usd = DAILY_BTC_TWO * 365 * btc_p
    light_cost_usd = (28480 * GRID_TARIFF) / usd_r
    net_profit_usd = annual_rev_usd - light_cost_usd
    roi_months = (TOTAL_INV_TWO / net_profit_usd) * 12
    
    text = (
        f"🚀 **ОКУПАЕМОСТЬ (2 ASIC):**\n"
        f"📈 Курс BTC: ${btc_p:,}\n"
        f"💵 Чистый профит/год: ${round(net_profit_usd):,}\n"
        f"--- \n"
        f"⏳ **СРОК: {round(roi_months, 1)} мес.**"
    )
    await message.answer(text)

@dp.message_handler(lambda m: "Финансы" in m.text)
async def finance_compare(message: types.Message):
    btc_p, usd_r = get_live_data()
    prof_1_usd = (DAILY_BTC_ONE * 365 * btc_p) - ((6690 * GRID_TARIFF) / usd_r)
    prof_2_usd = (DAILY_BTC_TWO * 365 * btc_p) - ((28480 * GRID_TARIFF) / usd_r)
    text = (
        f"💰 **ПРИБЫЛЬ В ГОД (Чистыми):**\n"
        f"💎 1 ASIC: ${round(prof_1_usd):,}\n"
        f"🔥 2 ASIC: ${round(prof_2_usd):,}\n"
        f"📈 Курс: {btc_p}$ | {usd_r}₴"
    )
    await message.answer(text)

@dp.message_handler(lambda m: "Сезонный баланс" in m.text)
async def seasonal_kwh(message: types.Message):
    await message.answer("📊 **1 ASIC:** Лето +3840, О/В -4320, Зима -6210.\n💡 2 ASIC: Дефицит -28,480 кВт·ч/год.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
