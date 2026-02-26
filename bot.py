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
GRID_TARIFF = 4.32

# Генерация СЭС в месяц (кВт)
GEN_SUMMER = 3800
GEN_MID = 1800
GEN_WINTER = 450

# Потребление в месяц (кВт)
CONS_1_ASIC = 2520
CONS_2_ASIC = 5040

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
    kb.add("📊 Сезонный баланс (1 vs 2 ASIC)", "🚀 Окупаемость", "💰 Чистая прибыль", "🏗️ Детализация затрат")
    await message.answer(f"Алексей, расчеты по 1 и 2 асикам добавлены во все разделы!", reply_markup=kb)

@dp.message_handler(lambda m: "Сезонный баланс" in m.text)
async def seasonal_comparison(message: types.Message):
    def get_info(gen, cons):
        diff = gen - cons
        money = diff * GRID_TARIFF
        return diff, money

    text = "📊 **СРАВНЕНИЕ БАЛАНСА (в месяц):**\n\n"
    
    for name, gen in [("☀️ ЛЕТО", GEN_SUMMER), ("🍂🌻 ОСЕНЬ/ВЕСНА", GEN_MID), ("❄️ ЗИМА", GEN_WINTER)]:
        d1, m1 = get_info(gen, CONS_1_ASIC)
        d2, m2 = get_info(gen, CONS_2_ASIC)
        text += (
            f"📍 **{name}:** (Ген: {gen} кВт)\n"
            f"🔹 *1 ASIC:* Сальдо {d1} кВт ({round(m1):,} ₴)\n"
            f"🔸 *2 ASIC:* Сальдо {d2} кВт ({round(m2):,} ₴)\n"
            f"--------------------------\n"
        )
    await message.answer(text)

@dp.message_handler(lambda m: "Окупаемость" in m.text)
async def roi_detail(message: types.Message):
    btc_p, usd_r = get_live_data()
    
    # Расчет для 1 ASIC
    inv1 = SES_PRICE + POWER_UP_PRICE + ASIC_PRICE
    prof1 = (0.00038 * 365 * btc_p) - ((6690 * GRID_TARIFF) / usd_r)
    mo1 = (inv1 / prof1) * 12
    
    # Расчет для 2 ASIC
    inv2 = SES_PRICE + POWER_UP_PRICE + (ASIC_PRICE * 2)
    prof2 = (0.00076 * 365 * btc_p) - ((28480 * GRID_TARIFF) / usd_r)
    mo2 = (inv2 / prof2) * 12

    text = (
        f"🚀 **ОКУПАЕМОСТЬ (Курс: ${btc_p:,}):**\n\n"
        f"💎 **ВАРИАНТ '1 ASIC':**\n"
        f"• Инвестиции: ${inv1:,}\n"
        f"• Срок: **{round(mo1, 1)} мес.** ({round(mo1/12, 1)} г.)\n\n"
        f"🔥 **ВАРИАНТ '2 ASIC':**\n"
        f"• Инвестиции: ${inv2:,}\n"
        f"• Срок: **{round(mo2, 1)} мес.** ({round(mo2/12, 1)} г.)\n"
    )
    await message.answer(text)

@dp.message_handler(lambda m: "Чистая прибыль" in m.text)
async def profit_detail(message: types.Message):
    btc_p, usd_r = get_live_data()
    p1_usd = (0.00038 * 365 * btc_p) - ((6690 * GRID_TARIFF) / usd_r)
    p2_usd = (0.00076 * 365 * btc_p) - ((28480 * GRID_TARIFF) / usd_r)
    
    text = (
        f"💰 **ЧИСТАЯ ПРИБЫЛЬ (в год):**\n"
        f"*(На сегодняшний день, курс {usd_r} ₴)*\n\n"
        f"💎 **С 1 АСИКОМ:**\n"
        f"• ${round(p1_usd):,} / {round(p1_usd * usd_r):,} ₴\n\n"
        f"🔥 **С 2 АСИКАМИ:**\n"
        f"• ${round(p2_usd):,} / {round(p2_usd * usd_r):,} ₴\n"
    )
    await message.answer(text)

@dp.message_handler(lambda m: "Детализация затрат" in m.text)
async def costs_info(message: types.Message):
    text = (
        f"🏗️ **ЗАТРАТЫ:**\n"
        f"• СЭС 30 кВт: $16,000\n"
        f"• Ввод 30 кВт: $2,000\n"
        f"• ASIC S21 (1 шт): $5,000\n\n"
        f"✅ Итого (1 ASIC): **$23,000**\n"
        f"✅ Итого (2 ASIC): **$28,000**"
    )
    await message.answer(text)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
