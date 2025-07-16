from aiogram import Bot
import os
import stripe

# Загрузка Stripe Secret Key из переменных окружения
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

# Проверка наличия ключа
if not STRIPE_SECRET_KEY:
    print("⚠️ STRIPE_SECRET_KEY не найден. Функция оплаты через Stripe отключена.")

stripe.api_key = STRIPE_SECRET_KEY

def is_stripe_configured():
    return bool(STRIPE_SECRET_KEY)

def create_stripe_checkout_session(user_id: str, price_usd_cents: int = 999):
    """
    Создаёт Stripe Checkout Session и возвращает URL.
    """
    if not is_stripe_configured():
        return None

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": "AI Pro Subscription"},
                    "unit_amount": price_usd_cents,
                },
                "quantity": 1,
            }],
            mode="subscription" if price_usd_cents != 999 else "payment",
            success_url=f"https://your-webapp.up.railway.app/success?session_id={{CHECKOUT_SESSION_ID}}&user_id={user_id}",
            cancel_url=" https://your-webapp.up.railway.app/cancel",
        )
        return session.url
    except Exception as e:
        print(f"Ошибка при создании сессии Stripe: {e}")
        return None

async def handle_stripe_webhook(request):
    """
    Обработка webhook событий от Stripe
    """
    payload = await request.get_json()
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        # Неверный payload
        return {"error": "Invalid payload"}, 400
    except stripe.error.SignatureVerificationError:
        # Неверная подпись
        return {"error": "Invalid signature"}, 400

    # Обработка события
    if event.type == "checkout.session.completed":
        session = event.data.object
        user_id = session.metadata.get("user_id")
        if user_id:
            print(f"Пользователь {user_id} успешно оплатил подписку")
            from db_utils import update_subscription
            update_subscription(user_id, days=30)

    return {"success": True}, 200

async def send_stars_payment(bot: Bot, user_id: str, stars: int = 10):
    """
    Отправляет звёзды через Telegram Stars (если доступно)
    """
    try:
        await bot.send_stars_transaction(user_id=user_id, stars=stars)
        return True
    except Exception as e:
        print(f"Ошибка при отправке звёзд: {e}")
        return False
