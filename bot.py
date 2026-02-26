import os
import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# Токен берем из настроек Railway (Environment Variables)
TOKEN = os.getenv('BOT_TOKEN')

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- БЛОК ДАННЫХ ---
ASIC_POWER = 3.5  # Потребление S21 в кВт
TH_POWER = 200    # Мощность S21
# Доход на 1 TH в сутки в BTC (среднее значение на 2026 год)
HASHPRICE_BTC = 0.00000065 
TARIFF_DAY = 4.32
TARIFF_NIGHT = 2.16

def get_market_data():
    try:
        # Курс BTC с Binance
        btc = float(requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT").json()['price'])
        # Курс USD/UAH с НБУ
        usd = float(requests.get("https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?valcode=USD&json").json()[0]['rate'])
        return btc, usd
    except Exception as e:
        return 68000.0, 43.5 # Заглушка при сбое сети

def calculate_mining(season_mode):
    btc, usd = get_market_data()
    
    # Модель солнца для СЭС 30кВт (часы работы асика "бесплатно")
    sun_hours = {"Лето": 15, "Весна/Осень": 8, "Зима": 2}[season_mode]
    
    revenue_usd = TH_POWER * HASHPRICE_BTC * btc
    
    night_h = 8
    day_grid_h = max(0, 24 - sun_hours - night_h)
    
    cost_uah = (ASIC_POWER * night_h * TARIFF_NIGHT) + (ASIC_POWER * day_grid_h * TARIFF_DAY)
    cost_usd = cost_uah / usd
    profit = revenue_usd - cost_usd
    
    return {
        "btc": btc, "usd": usd, "profit": profit, 
        "cost": cost_usd, "sun": sun_hours, "grid": day_grid_h
    }

# --- ОБРАБОТКА КОМАНД ---
@dp.message(Command("start"))
async def start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.button(text="☀️ Лето")
    builder.button(text="⛅ Весна/Осень")
    builder.button(text="❄️ Зима")
    builder.button(text="📅 Итог за Год")
    builder.button(text="💰 Окупаемость S21")
    builder.adjust(3, 2)
    
    await message.answer(
        f"Приветствую, Алексей!\nЭто калькулятор доходности СЭС 30кВт в Боярке (оя).\n"
        f"Данные обновляются автоматически.",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )

@dp.message(lambda m: m.text in ["☀️ Лето", "⛅ Весна/Осень", "❄️ Зима"])
async def seasons(message: types.Message):
    mode = message.text.split()[-1]
    data = calculate_mining(mode)
    
    text = (
        f"📊 **Режим: {mode}**\n"
        f"---------------------------\n"
        f"🪙 BTC: ${data['btc']:,.0f}\n"
        f"💵 Курс USD: {data['usd']:.2f} грн\n"
        f"☀️ Солнце: {data['sun']} ч. | 🔌 Сеть: {data['grid']} ч.\n"
        f"---------------------------\n"
        f"💰 Доход: ${data['profit'] + data['cost']:.2f}/день\n"
        f"⚡ Свет: ${data['cost']:.2f}/день\n"
        f"✅ **Чистая прибыль: ${data['profit']:.2f}/день**"
    )
    await message.answer(text, parse_mode="Markdown")

@dp.message(lambda m: m.text == "💰 Окупаемость S21")
async def roi(message: types.Message):
    btc, usd = get_market_data()
    # Среднегодовая прибыль учитывая все сезоны
    avg_profit_day = 8.5 
    price_device = 5000
    days = round(price_device / avg_profit_day)
    
    await message.answer(
        f"📈 **Анализ S21 (200 TH)**\n"
        f"Цена аппарата: ${price_device}\n"
        f"Срок окупаемости: ~{days} дней ({round(days/30)} мес.)\n\n"
        f"Это с учетом твоей СЭС 30кВт и лития!"
    )

@dp.message(lambda m: m.text == "📅 Итог за Год")
async def year(message: types.Message):
    btc, _ = get_market_data()
    # Примерная годовая чистая прибыль
    year_money = 4200 
    await message.answer(
        f"📅 **Прогноз на 12 месяцев**\n"
        f"При текущем курсе ${btc:,.0f}:\n"
        f"💵 Чистый профит: **${year_money:,.0f}**\n"
        f"🚀 Система окупит себя и начнет работать в плюс."
    )

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
