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
    # Делаем кнопки четкими и понятными
    keyboard.add("📊 Сезонные отчеты")
    keyboard.add("🚀 Расчет окупаемости S21")
    keyboard.add("📅 Годовой баланс СЭС")
    await message.answer(f"Алексей, порядок наведен! Теперь все кнопки в Боярке (оя) работают.", reply_markup=keyboard)

# Этот фильтр поймает кнопку, даже если там будет другой смайлик
@dp.message_handler(lambda message: "Сезонные отчеты" in message.text)
async def seasonal_report(message: types.Message):
    text = (
        f"📊 **Сезонные отчеты (СЭС 30 кВт + Net Billing):**\n\n"
        f"☀️ **Лето:** Генерация ~3800 кВт*ч/мес.\n"
        f"💰 В копилку Net Billing: +1280 кВт*ч.\n\n"
        f"🍂 **Осень/Весна:** Генерация ~1800 кВт*ч/мес.\n"
        f"🔌 Берем из накоплений: -720 кВт*ч.\n\n"
        f"❄️ **Зима:** Генерация ~450 кВт*ч/мес.\n"
        f"⚠️ Тратим летний депозит: -2070 кВт*ч."
    )
    await message.answer(text)

@dp.message_handler(lambda message: "Расчет окупаемости" in message.text)
async def calculate_roi(message: types.Message):
    # Твой расчет: $5000 / $18.2 в день (без учета света)
    days = 275 
    text = (
        f"🚀 **Окупаемость S21 (Максимальная эффективность):**\n\n"
        f"💰 Стоимость: $5000\n"
        f"⚡ Свет: 0.00 грн (СЭС перекрывает годовой расход)\n"
        f"--- \n"
        f"⏳ Срок окупаемости: **{days} дней** (~9.0 мес.)\n\n"
        f"Чистый профит: майнер работает только на твой карман!"
    )
    await message.answer(text)

@dp.message_handler(lambda message: "Годовой баланс" in message.text)
async def yearly_total(message: types.Message):
    text = (
        f"📅 **Годовой итог (Боярка/оя):**\n"
        f"🌞 Генерация СЭС: 32 000 кВт*ч\n"
        f"⚡ Расход S21: 30 660 кВт*ч\n"
        f"--- \n"
        f"🏆 Остаток на дом: **+1340 кВт*ч**\n"
        f"Система полностью автономна по балансу!"
    )
    await message.answer(text)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
