import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

API_TOKEN = os.getenv('BOT_TOKEN')
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Константы для Боярки (оя)
SOLAR_CAPACITY = 30  # кВт
MINER_CONSUMPTION_MONTH = 2520  # кВт*ч в месяц (S21 ~3.5 кВт * 24 * 30)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["☀️ Лето", "🍂 Осень/Весна", "❄️ Зима", "📅 Отчет за год"]
    keyboard.add(*buttons)
    await message.answer(f"Алексей, выберите период для анализа СЭС 30 кВт и Net Billing:", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == "☀️ Лето")
async def summer_stats(message: types.Message):
    gen = 3800 # Средняя генерация в июне
    balance = gen - MINER_CONSUMPTION_MONTH
    text = (
        f"☀️ **ЛЕТО (Июнь-Август):**\n"
        f"📊 Генерация: {gen} кВт*ч\n"
        f"⚡ Потребление S21: {MINER_CONSUMPTION_MONTH} кВт*ч\n"
        f"--- \n"
        f"💰 **В копилку Net Billing: +{balance} кВт*ч**\n"
        f"Счет за свет: 0 грн. Ты работаешь в плюс!"
    )
    await message.answer(text)

@dp.message_handler(lambda message: message.text == "❄️ Зима")
async def winter_stats(message: types.Message):
    gen = 450 # Средняя генерация в декабре
    deficit = MINER_CONSUMPTION_MONTH - gen
    text = (
        f"❄️ **ЗИМА (Декабрь-Февраль):**\n"
        f"📊 Генерация: {gen} кВт*ч\n"
        f"⚡ Потребление S21: {MINER_CONSUMPTION_MONTH} кВт*ч\n"
        f"--- \n"
        f"📉 **Дефицит: -{deficit} кВт*ч**\n"
        f"Покрывается за счет летних накоплений в Net Billing."
    )
    await message.answer(text)

@dp.message_handler(lambda message: message.text == "📅 Отчет за год")
async def yearly_report(message: types.Message):
    annual_gen = 32000 # Пример для 30 кВт в нашем регионе
    annual_cons = MINER_CONSUMPTION_MONTH * 12
    final_balance = annual_gen - annual_cons
    
    text = (
        f"📅 **ГОДОВОЙ ПРОГНОЗ (Боярка/оя):**\n"
        f"🌞 Всего генерации: {annual_gen} кВт*ч\n"
        f"🔌 Всего расход S21: {annual_cons} кВт*ч\n"
        f"--- \n"
        f"🏆 **Итог года: {final_balance} кВт*ч в вашу пользу!**\n\n"
        f"Вы полностью перекрываете майнинг солнцем и еще остается на дом."
    )
    await message.answer(text)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
