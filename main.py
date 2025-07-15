
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from ai_utils import generate_text
from db_utils import can_use_bot, update_subscription
from payments import is_stripe_configured, create_stripe_checkout_session, send_stars_payment

import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(F.text == "/start")
async def start(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="💬 Открыть AI-чат", web_app=WebAppInfo(url=WEBAPP_URL)),
        InlineKeyboardButton(text="💳 Оплатить подписку", callback_data="subscribe")
    ]])
    await message.answer("Добро пожаловать! Используйте WebApp или отправьте сообщение.", reply_markup=keyboard)


@dp.message()
async def handle_message(message: Message):
    user_id = str(message.from_user.id)

    if not can_use_bot(user_id):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="💳 Оплатить подписку", url=create_stripe_checkout_session(user_id))
        ]])
        await message.reply("Подписка закончилась. Оплатите подписку, чтобы продолжить использовать бота.",
                            reply_markup=keyboard)
        return

    reply = generate_text(message.text, user_id)
    await message.answer(reply)


@dp.callback_query(F.data == "subscribe")
async def subscribe(query):
    user_id = str(query.from_user.id)
    if await send_stars_payment(query.bot, user_id, stars=10):
        update_subscription(user_id, days=30)
        await query.message.answer("Вы успешно оформили подписку на 30 дней.")
    else:
        await query.message.answer("Ошибка при оплате.")


@dp.message(F.text == "/subscribe")
async def cmd_subscribe(message: Message):
    if not is_stripe_configured():
        await message.answer("❌ Оплата временно недоступна: администратор не указал Stripe Secret Key.")
        #return

    user_id = str(message.from_user.id)
    url = create_stripe_checkout_session(user_id, price_usd_cents=999)  # 9.99 USD

    if url:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="💳 Оплатить подписку", url=url)
        ]])
        await message.answer("Нажмите кнопку ниже, чтобы оформить подписку.", reply_markup=keyboard)
    else:
        await message.answer("⚠️ Не удалось создать ссылку для оплаты.")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
