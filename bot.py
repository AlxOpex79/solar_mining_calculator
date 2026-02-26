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
ASIC_PRICE_UNIT = 5000
BATTERY_PRICE_UNIT = 1200
BASE_TARIFF = 4.32
AVG_NIGHT_TARIFF = 3.60  # Средневзвешенный (16ч день/8ч ночь)

# Технические параметры (кВт/мес)
GEN = {"summer": 3800, "mid": 1800, "winter": 450}
CONS_1 = 2520
CONS_2 = 5040

# Экономия от АКБ в месяц (4 часа работы от солнца/батарей вместо сети вечером)
# 4ч * 3.5кВт * 30 дней = 420 кВт/мес экономии покупной энергии
BATTERY_SAVING_KWH = 420 

def get_live_data():
    try:
        btc_p = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd", timeout=5).json()['bitcoin']['usd']
        uah_r = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5).json()['rates']['UAH']
        return btc_p, uah_r
    except:
        return 65000, 42.0

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    kb.add("💰 Финансы (Детальный расчет)", "🚀 Окупаемость (1 vs 2 ASIC)", "🏗️ Затраты и Оборудование")
    await message.answer(f"Алексей, система Боярка (оя) обновлена! Учтены АКБ и сезонная прибыль.", reply_markup=kb)

@dp.message_handler(lambda m: "Финансы" in m.text)
async def finance_detailed(message: types.Message):
    btc_p, usd_r = get_live_data()
    
    def calculate_results(num_asics, tariff):
        cons = CONS_1 if num_asics == 1 else CONS_2
        # Экономия от батарей (420 кВт на каждый асик)
        bat_save = BATTERY_SAVING_KWH * num_asics
        
        results = {}
        total_profit_usd = 0
        for season, g_val in GEN.items():
            income = (0.00038 * num_asics * 30.5 * btc_p)
            # Расход: (Потребление - Генерация - Спасенные батареей кВт) * Тариф
            # Если генерация + батарея > потребления, расход = 0
            deficit = max(0, cons - g_val - bat_save)
            expense = (deficit * tariff) / usd_r
            saldo = income - expense
            results[season] = {"inc": income, "exp": expense, "sal": saldo}
            total_profit_usd += saldo * 4 if season == "mid" else saldo * 4 # Упрощенно по 4 мес
        return results, total_profit_usd

    res1, total1 = calculate_results(1, BASE_TARIFF)
    res2, total2 = calculate_results(2, BASE_TARIFF)
    _, total2_night = calculate_results(2, AVG_NIGHT_TARIFF)

    text = (
        f"📋 **ФИНАНСОВЫЙ ОТЧЕТ**\n"
        f"*(По состоянию на сегодня: BTC ${btc_p:,}, USD {usd_r} ₴)*\n\n"
        f"💎 **ВАРИАНТ 1 ASIC (+1 АКБ):**\n"
        f"• Лето: +${round(res1['summer']['sal']):,} | О/В: +${round(res1['mid']['sal']):,} | Зима: +${round(res1['winter']['sal']):,}\n"
        f"✅ **ИТОГО ЗА ГОД: ${round(total1):,} ({round(total1*usd_r):,} ₴)**\n\n"
        f"🔥 **ВАРИАНТ 2 ASIC (+2 АКБ):**\n"
        f"• Лето: +${round(res2['summer']['sal']):,} | О/В: +${round(res2['mid']['sal']):,} | Зима: +${round(res2['winter']['sal']):,}\n"
        f"✅ **ИТОГО ЗА ГОД: ${round(total2):,} ({round(total2*usd_r):,} ₴)**\n\n"
        f"📈 **ИТОГОВАЯ РАЗНИЦА:** +${round(total2 - total1):,} / год\n"
        f"--------------------------\n"
        f"🌙 **С НОЧНЫМ ТАРИФОМ (2 ASIC):**\n"
        f"💰 Прибыль вырастет до: **${round(total2_night):,}**\n"
        f"*(Экономия: +${round(total2_night - total2):,} в год)*"
    )
    await message.answer(text)

@dp.message_handler(lambda m: "Окупаемость" in m.text)
async def roi_view(message: types.Message):
    btc_p, usd_r = get_live_data()
    # Инвестиции
    inv1 = SES_PRICE + POWER_UP_PRICE + ASIC_PRICE_UNIT + BATTERY_PRICE_UNIT
    inv2 = SES_PRICE + POWER_UP_PRICE + (ASIC_PRICE_UNIT * 2) + (BATTERY_PRICE_UNIT * 2)
    
    # Годовая прибыль (базовая)
    _, prof1 = (0.00038 * 365 * btc_p) - (6690 * BASE_TARIFF / usd_r), 1 # Упрощенная логика для краткости
    # Используем точный расчет из функции выше
    def get_annual(n, t):
        p = 0
        for s, g in GEN.items():
            d = max(0, (CONS_1 if n==1 else CONS_2) - g - (BATTERY_SAVING_KWH * n))
            p += (0.00038 * n * 30.5 * btc_p) - (d * t / usd_r)
        return p * 4 # (Лето 4 + О/В 4 + Зима 4)
    
    p1, p2 = get_annual(1, BASE_TARIFF), get_annual(2, BASE_TARIFF)
    
    text = (
        f"🚀 **ОКУПАЕМОСТЬ (при курсе ${btc_p:,}):**\n\n"
        f"💎 **1 ASIC + 1 АКБ:**\n"
        f"• Срок: **{round((inv1/p1)*12, 1)} мес.** ({round(inv1/p1, 1)} лет)\n\n"
        f"🔥 **2 ASIC + 2 АКБ:**\n"
        f"• Срок: **{round((inv2/p2)*12, 1)} мес.** ({round(inv2/p2, 1)} лет)\n"
    )
    await message.answer(text)

@dp.message_handler(lambda m: "Затраты" in m.text)
async def cost_view(message: types.Message):
    text = (
        f"🏗️ **ОБОРУДОВАНИЕ И ЦЕНЫ:**\n"
        f"• СЭС 30 кВт: $16,000\n"
        f"• Ввод мощностей: $2,000\n"
        f"• ASIC S21: $5,000/шт\n"
        f"• АКБ (4 часа): $1,200/шт\n\n"
        f"✅ **Всего (1 ASIC): $24,200**\n"
        f"✅ **Всего (2 ASIC): $30,400**"
    )
    await message.answer(text)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
