import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

API_TOKEN = os.getenv('BOT_TOKEN')
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Данные для расчета
DEVICE_PRICE = 5000  # Цена S21 (можно менять)
DAILY_REVENUE_USD = 18.2  # Примерный доход S21 (200 TH) при текущем курсе и сложности
MONTHLY_REVENUE = DAILY_REVENUE_USD * 30.5

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["🚀 Расчет окупаемости S21", "📅 Годовой баланс СЭС", "☀️ Сезонные отчеты"]
    keyboard.add(*buttons)
    await message.answer(f"Алексей, порядок наведен! Теперь бот считает окупаемость с учетом Net Billing для Боярки (оя).", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == "🚀 Расчет окупаемости S21")
async def calculate_roi(message: types.Message):
    # При 30 кВт СЭС затраты на электричество перекрываются генерацией (Net Billing)
    # Поэтому считаем чистый доход без вычета за свет
    roi_days = DEVICE_PRICE / DAILY_REVENUE_USD
    roi_months = roi_days / 30.5
    
    text = (
        f"💎 **Окупаемость S21 (СЭС 30 кВт + Net Billing):**\n\n"
        f"💰 Стоимость аппарата: ${DEVICE_PRICE}\n"
        f"🔌 Цена за свет: 0.00 грн (перекрыто солнцем)\n"
        f"💵 Доход в месяц: ~${round(MONTHLY_REVENUE, 2)}\n"
        f"--- \n"
        f"⏳ Срок окупаемости: **{round(roi_days)} дней**\n"
        f"📊 В месяцах: **~{round(roi_months, 1)} мес.**\n\n"
        f"⚠️ *Для сравнения: на обычном тарифе (4.32 грн) срок составил бы ~20 месяцев.*"
    )
    await message.answer(text, parse_mode="Markdown")

@dp.message_handler(lambda message: message.text == "📅 Годовой баланс СЭС")
async def yearly_total(message: types.Message):
    # Данные для СЭС 30 кВт в Киевской обл.
    gen_year = 32000
    cons_year = 3.5 * 24 * 365 # Потребление одного S21 в год
    surplus = gen_year - cons_year
    
    text = (
        f"📅 **Годовой баланс (Боярка/оя):**\n\n"
        f"🌞 Генерация СЭС 30 кВт: {gen_year} кВт*ч\n"
        f"⚡ Расход S21: {round(cons_year)} кВт*ч\n"
        f"--- \n"
        f"📈 Излишек для дома: **+{round(surplus)} кВт*ч**\n"
        f"Этого излишка хватит на 2-3 кондиционера и весь свет в доме!"
    )
    await message.answer(text)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
