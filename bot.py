import logging
import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

logging.basicConfig(level=logging.INFO)

API_TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- ИСХОДНЫЕ ДАННЫЕ ---
SES_PRICE = 16000
POWER_UP_PRICE = 2000
ASIC_PRICE = 5000
GRID_TARIFF = 4.32

# Генерация СЭС в месяц по сезонам (кВт)
GEN_SUMMER = 3800
GEN_MID = 1800
GEN_WINTER = 450

# Потребление (кВт/мес)
CONS_1_ASIC = 2520
CONS_2_ASIC = 5040

def get_live_data():
    try:
        btc_p = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd").json()['bitcoin']['usd']
        usd_r = requests.get("https://api.exchangerate-api.com/v4/latest/USD").json()['rates']['UAH']
        return btc_p, usd_r
    except:
        return 67000, 43.0

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    kb.add("📊 Сезонный баланс (Детально)", "🚀 Окупаемость (1 vs 2 ASIC)", "💰 Чистая прибыль (Финансы)", "🏗️ Детализация затрат")
    await message.answer(f"Алексей, правки внесены! Боярка (оя) переходит на детальный расчет.", reply_markup=kb)

@dp.message_handler(lambda m: "Сезонный баланс" in m.text)
async def seasonal_detailed(message: types.Message):
    # Расчет для 2-х асиков
    s_bal = GEN_SUMMER - CONS_2_ASIC
    m_bal = GEN_MID - CONS_2_ASIC
    w_bal = GEN_WINTER - CONS_2_ASIC
    
    text = (
        f"📊 **СЕЗОННЫЙ БАЛАНС (на 2 ASIC):**\n\n"
        f"☀️ **ЛЕТО (в мес):**\n"
        f"• Сгенерировано: {GEN_SUMMER} кВт\n"
        f"• Потреблено: {CONS_2_ASIC} кВт\n"
        f"• Сальдо: {s_bal} кВт ({round(s_bal * GRID_TARIFF)} ₴)\n\n"
        f"🍂🌻 **ОСЕНЬ/ВЕСНА (в мес):**\n"
        f"• Сгенерировано: {GEN_MID} кВт\n"
        f"• Потреблено: {CONS_2_ASIC} кВт\n"
        f"• Сальдо: {m_bal} кВт ({round(m_bal * GRID_TARIFF)} ₴)\n\n"
        f"❄️ **ЗИМА (в мес):**\n"
        f"• Сгенерировано: {GEN_WINTER} кВт\n"
        f"• Потреблено: {CONS_2_ASIC} кВт\n"
        f"• Сальдо: {w_bal} кВт ({round(w_bal * GRID_TARIFF)} ₴)\n"
    )
    await message.answer(text)

@dp.message_handler(lambda m: "Окупаемость" in m.text)
async def roi_compare(message: types.Message):
    btc_p, usd_r = get_live_data()
    
    # 1 ASIC
    inv1 = SES_PRICE + POWER_UP_PRICE + ASIC_PRICE
    prof1 = (0.00038 * 365 * btc_p) - ((6690 * GRID_TARIFF) / usd_r)
    m1 = (inv1 / prof1) * 12
    
    # 2 ASIC
    inv2 = SES_PRICE + POWER_UP_PRICE + (ASIC_PRICE * 2)
    prof2 = (0.00076 * 365 * btc_p) - ((28480 * GRID_TARIFF) / usd_r)
    m2 = (inv2 / prof2) * 12

    text = (
        f"🚀 **ОКУПАЕМОСТЬ (при курсе ${btc_p:,}):**\n\n"
        f"💎 **С 1 АСИКОМ:**\n"
        f"• Срок: **{round(m1, 1)} мес.** ({round(m1/12, 1)} г.)\n\n"
        f"🔥 **С 2 АСИКАМИ:**\n"
        f"• Срок: **{round(m2, 1)} мес.** ({round(m2/12, 1)} г.)\n"
        f"--- \n"
        f"💡 *Разница наглядна: больше вложений, но быстрее возврат.*"
    )
    await message.answer(text)

@dp.message_handler(lambda m: "Чистая прибыль" in m.text)
async def finance_live(message: types.Message):
    btc_p, usd_r = get_live_data()
    prof2_usd = (0.00076 * 365 * btc_p) - ((28480 * GRID_TARIFF) / usd_r)
    
    text = (
        f"💰 **ФИНАНСЫ (на сегодняшний день):**\n\n"
        f"При актуальном курсе BTC **${btc_p:,}** и USD **{usd_r} ₴**,\n"
        f"ваша чистая прибыль с 2-х асиков составит:\n\n"
        f"💵 **${round(prof2_usd):,} в год**\n"
        f"💸 **{round(prof2_usd * usd_r):,} ₴ в год**\n\n"
        f"*(Учтены все расходы на доплату за свет)*"
    )
    await message.answer(text)

@dp.message_handler(lambda m: "Детализация затрат" in m.text)
async def cost_det(message: types.Message):
    total = SES_PRICE + POWER_UP_PRICE + (ASIC_PRICE * 2)
    await message.answer(f"🏗️ **ЗАТРАТЫ БИЗНЕС:**\n• СЭС: $16,000\n• Ввод 30кВт: $2,000\n• 2xS21: $10,000\n---\nИТОГО: **${total:,}**")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
