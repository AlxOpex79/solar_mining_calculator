import logging
import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

logging.basicConfig(level=logging.INFO)

API_TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- КОНСТАНТЫ ---
SES_PRICE = 16000
POWER_UP_PRICE = 2000
ASIC_PRICE = 5000
BASE_TARIFF = 4.32
NIGHT_TARIFF_AVG = 3.60 # (16ч*4.32 + 8ч*2.16)/24

# Дефицит кВт в год (уже посчитанный ранее)
DEFICIT_1_ASIC = 6690
DEFICIT_2_ASIC = 28480

def get_live_data():
    try:
        btc_p = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd", timeout=5).json()['bitcoin']['usd']
        usd_r = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5).json()['rates']['UAH']
        return btc_p, usd_r
    except:
        return 65000, 43.5

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    kb.add("📊 Сезонный баланс (1 vs 2 ASIC)", "🚀 Окупаемость", "💰 Чистая прибыль", "🌙 Ночной тариф (Экономия)", "🏗️ Детализация затрат")
    await message.answer(f"Алексей, добавила отдельную вкладку для расчета ночного тарифа!", reply_markup=kb)

@dp.message_handler(lambda m: "Ночной тариф" in m.text)
async def night_mode(message: types.Message):
    btc_p, usd_r = get_live_data()
    
    # Расчет затрат для 2-х асиков (самый важный случай)
    cost_base = (DEFICIT_2_ASIC * BASE_TARIFF) / usd_r
    cost_night = (DEFICIT_2_ASIC * NIGHT_TARIFF_AVG) / usd_r
    saving_usd = cost_base - cost_night
    
    text = (
        f"🌙 **ВЫГОДА НОЧНОГО ТАРИФА (на 2 ASIC):**\n\n"
        f"📉 **Средний тариф:** {NIGHT_TARIFF_AVG} ₴/кВт\n"
        f"*(вместо обычных {BASE_TARIFF} ₴)*\n\n"
        f"💰 **Экономия на свете:**\n"
        f"• В год: **${round(saving_usd):,}** ({round(saving_usd * usd_r):,} ₴)\n\n"
        f"🚀 **Влияние на окупаемость:**\n"
        f"Ночной тариф сокращает срок возврата инвестиций примерно на **1.5 - 2 месяца** за счет снижения операционных расходов."
    )
    await message.answer(text)

@dp.message_handler(lambda m: "Сезонный баланс" in m.text)
async def seasonal_comparison(message: types.Message):
    # Здесь оставляем базовый тариф 4.32 для наглядности "худшего сценария"
    text = "📊 **СЕЗОННЫЙ БАЛАНС (Тариф 4.32 ₴):**\n\n"
    for name, gen in [("☀️ ЛЕТО", 3800), ("🍂🌻 ОСЕНЬ/ВЕСНА", 1800), ("❄️ ЗИМА", 450)]:
        d1 = gen - 2520
        d2 = gen - 5040
        text += (
            f"📍 **{name}:**\n"
            f"🔹 *1 ASIC:* {d1} кВт ({round(d1 * BASE_TARIFF):,} ₴)\n"
            f"🔸 *2 ASIC:* {d2} кВт ({round(d2 * BASE_TARIFF):,} ₴)\n"
            f"--------------------------\n"
        )
    await message.answer(text)

@dp.message_handler(lambda m: "Окупаемость" in m.text)
async def roi_detail(message: types.Message):
    btc_p, usd_r = get_live_data()
    inv1 = SES_PRICE + POWER_UP_PRICE + ASIC_PRICE
    prof1 = (0.00038 * 365 * btc_p) - ((DEFICIT_1_ASIC * BASE_TARIFF) / usd_r)
    inv2 = SES_PRICE + POWER_UP_PRICE + (ASIC_PRICE * 2)
    prof2 = (0.00076 * 365 * btc_p) - ((DEFICIT_2_ASIC * BASE_TARIFF) / usd_r)

    text = (
        f"🚀 **ОКУПАЕМОСТЬ (Базовая):**\n\n"
        f"💎 **1 ASIC:** **{round((inv1/prof1)*12, 1)} мес.**\n"
        f"🔥 **2 ASIC:** **{round((inv2/prof2)*12, 1)} мес.**\n\n"
        f"*Для учета экономии нажми кнопку 'Ночной тариф'*."
    )
    await message.answer(text)

@dp.message_handler(lambda m: "Чистая прибыль" in m.text)
async def profit_detail(message: types.Message):
    btc_p, usd_r = get_live_data()
    p2_usd = (0.00076 * 365 * btc_p) - ((DEFICIT_2_ASIC * BASE_TARIFF) / usd_r)
    await message.answer(f"💰 **ПРИБЫЛЬ (2 ASIC):**\nЧистыми в год: **${round(p2_usd):,}**\n({round(p2_usd * usd_r):,} ₴)")

@dp.message_handler(lambda m: "Детализация затрат" in m.text)
async def costs_info(message: types.Message):
    await message.answer(f"🏗️ **ЗАТРАТЫ БИЗНЕС:**\nСЭС + Ввод + 2xS21 = **$28,000**")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
