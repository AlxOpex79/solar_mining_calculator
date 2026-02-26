import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

API_TOKEN = os.getenv('BOT_TOKEN')
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["☀️ Баланс СЭС 30 кВт", "💰 Доходность майнинга", "📊 Настройки"]
    keyboard.add(*buttons)
    await message.answer(f"Алексей, система 30 кВт в Боярке (оя) готова к расчету!", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == "☀️ Баланс СЭС 30 кВт")
async def solar_30kw_balance(message: types.Message):
    solar_power = 26.0  # Реальный пик летом для 30-ки
    miner_power = 3.5   # Потребление S21
    house_avg = 1.5     # Дом с кондиционерами
    
    surplus = solar_power - miner_power - house_avg
    green_tariff_price = 0.16 # Примерная ставка Евро/кВт (нужно уточнять по договору)
    hourly_profit = surplus * green_tariff_price

    text = (
        f"☀️ **СЭС 30 кВт (Летний пик):**\n\n"
        f"📡 Генерация: {solar_power} кВт\n"
        f"⚡ Майнер S21: -{miner_power} кВт\n"
        f"🏠 Потребление дома: -{house_avg} кВт\n"
        f"--- \n"
        f"📈 **Свободный остаток: {round(surplus, 2)} кВт**\n"
        f"💶 Потенциал продажи: ~{round(hourly_profit, 2)} € в час"
    )
    await message.answer(text, parse_mode="Markdown")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
