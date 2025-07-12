import os
import requests
from dotenv import load_dotenv

load_dotenv()

FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")
API_KEY = os.getenv("YANDEX_API_KEY")

def generate_text(prompt: str) -> str:
    headers = {
        "Authorization": f"Api-Key {API_KEY}",
        "Content-Type": "application/json",
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
