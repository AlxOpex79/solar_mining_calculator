import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

logging.basicConfig(level=logging.INFO)

API_TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Данные для Боярки (оя)
DEVICE_PRICE = 5000
DAILY_BTC = 0.00038
BTC_PRICE = 85000

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    kb.add("📊 Сезонный отчет (кВт)", "🚀 Окупаемость S21 + BTC", "📅 Годовой баланс СЭС")
    await message.answer("Алексей, система обновлена и готова!", reply_markup=kb)

@dp.message_handler(lambda m: "Сезонный отчет" in m.text)
async def seasonal(message: types.Message):
    text = (
        "📊 **Баланс кВт⋅ч (СЭС 30 кВт vs S21):**\n\n"
        "☀️ Лето: **+1280** кВт⋅ч/мес (в копилку)\n"
        "🍂 Осень/Весна: **-720** кВт⋅ч/мес (из копилки)\n"
        "❄️ Зима: **-2070** кВт⋅ч/мес (тратим накопленное)\n\n"
        "Годовой баланс в Боярке (оя) остается положительным!"
    )
    await message.answer(text, parse_mode="Markdown")

@dp.message_handler(lambda m: "Окупаемость S21" in m.text)
async def roi(message: types.Message):
    yearly_btc = DAILY_BTC * 365
    yearly_usd = yearly_btc * BTC_PRICE
    roi_days = DEVICE_PRICE / (DAILY_BTC * BTC_PRICE)
    
    text = (
        f"🚀 **Результаты за год:**\n\n"
        f"₿ Накопишь: **{round(yearly_btc, 5)} BTC**\n"
        f"💵 В долларах: ${round(yearly_usd)}\n"
        f"🔌 Свет: 0.00 грн (Net Billing)\n"
        f"--- \n"
        f"⏳ Окупаемость: **{round(roi_days)} дней**"
    )
    await message.answer(text, parse_mode="Markdown")

@dp.message_handler(lambda m: "Годовой баланс" in m.text)
async def yearly(message: types.Message):
    text = (
        "📅 **Итог года:**\n"
        "🌞 СЭС выдаст: 32 000 кВт⋅ч\n"
        "⚡ S21 съест: 30 660 кВт⋅ч\n"
        f"🏆 Остаток: **+1340 кВт⋅ч** для дома!"
    )
    await message.answer(text)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
