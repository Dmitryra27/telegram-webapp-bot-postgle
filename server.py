import asyncio
from flask import Flask, request, Response, send_from_directory
from ai_utils import generate_text
from db_utils import can_use_bot
import os

from db_utils import can_use_bot
from main import main
from payments import handle_stripe_webhook

app = Flask(__name__, template_folder='templates', static_folder='static')


@app.route('/')
def home():
    html = open('index.html', encoding='utf-8').read()
    return Response(html, content_type='text/html; charset=utf-8')


@app.route('/<path:path>')
def catch_all(path):
    #return app.send_static_file(path)
    return send_from_directory('static', path)

@app.route('/stripe/webhook', methods=['POST'])
async def stripe_webhook():
    result, code = await handle_stripe_webhook(request)
    return result, code


@app.route('/success')
def success():
    user_id = request.args.get('user_id')
    session_id = request.args.get('session_id')

    if user_id and session_id:
        return f"<h1>Спасибо за покупку, пользователь {user_id}!</h1>"
    else:
        return "<h1>Оплата прошла успешно, но данные пользователя не получены.</h1>"


@app.route('/api/generate')
def generate():
    prompt = request.args.get('prompt')
    user_id = request.args.get('user_id', 'default')
    if not prompt:
        return "Нет запроса", 400
    if not can_use_bot(user_id):
        return "Подписка закончилась", 402

    try:
        result = generate_text(prompt, user_id)
        return f"<p>{result}</p>"
    except Exception as e:
        return f"<p>Ошибка: {str(e)}</p>", 500


@app.route('/subscribe')
def subscribe():
    return """
    <h1>💳 Подписка недоступна</h1>
    <p>Подписка закончилась. Пожалуйста, оплатите подписку.</p>
    """
    # return redirect(" https://your-stripe-checkout-link.com ")


#if __name__ == '__main__':
#    app.run(host='0.0.0.0', port=8080)
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(
        main(),
        loop.run_in_executor(None, app.run, '0.0.0.0', 8080)
    ))
