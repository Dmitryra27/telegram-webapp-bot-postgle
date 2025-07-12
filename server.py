from flask import Flask, request, Response
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# === YandexGPT API ===
FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")
IAM_TOKEN = os.getenv("YANDEX_API_KEY")

def generate_text(prompt: str) -> str:
    headers = {
        "Authorization": f"API-KEY {IAM_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "modelUri": f"gpt://{FOLDER_ID}/yandexgpt",
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
            "maxTokenCount": 1000
        },
        "messages": [
            {
                "role": "user",
                "text": prompt
            }
        ]
    }

    response = requests.post(
        "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
        headers=headers,
        json=data
    )

    if response.status_code == 200:
        return response.json()['result']['alternatives'][0]['message']['text']
    else:
        return f"Ошибка YandexGPT: {response.status_code}, {response.text}"

# === Flask Routes ===
@app.route('/')
def home():
    html = open('index.html', encoding='utf-8').read()
    return Response(html, content_type='text/html; charset=utf-8')

@app.route('/api/generate')
def generate():
    prompt = request.args.get('prompt')
    if not prompt:
        return "Нет запроса", 400
    try:
        result = generate_text(prompt)
        return f"<p>{result}</p>"
    except Exception as e:
        return f"<p>Ошибка сервера: {str(e)}</p>", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
