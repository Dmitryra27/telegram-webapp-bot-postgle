import os
import requests
from dotenv import load_dotenv

load_dotenv()

FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")
IAM_TOKEN = os.getenv("YANDEX_API_KEY")

# Хранилище истории диалогов
user_histories = {}

def generate_text(prompt: str, user_id: str) -> str:
    # Добавляем новый запрос в историю
    if user_id not in user_histories:
        user_histories[user_id] = []
    user_histories[user_id].append({"role": "user", "text": prompt})

    headers = {
        "Authorization": f"API-KEY {IAM_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "modelUri": f"gpt://{FOLDER_ID}/yandexgpt",
        "completionOptions": {
            "temperature": 0.6,
            "maxTokenCount": 1000
        },
        "messages": user_histories[user_id]
    }

    response = requests.post(
        "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
        headers=headers,
        json=data
    )

    if response.status_code == 200:
        result = response.json()['result']['alternatives'][0]['message']['text']
        user_histories[user_id].append({"role": "assistant", "text": result})
        return result
    else:
        return f"Ошибка YandexGPT: {response.status_code}, {response.text}"
