"""
Разведочный скрипт: дёргаем API реестра НЦЭЛС напрямую (без браузера)
и смотрим, что приходит в ответе — какие поля есть, сколько записей.

Запускать локально:  python ndda_explore.py
Понадобится:          pip install requests
"""

import json
import requests

URL = "https://oldregister.ndda.kz/register-backend/RegisterService/list"

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "ru-KZ,ru-RU;q=0.9,ru;q=0.8,en-US;q=0.7,en;q=0.6",
    "content-type": "application/json",
    "origin": "https://oldregister.ndda.kz",
    "referer": "https://oldregister.ndda.kz/",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"
    ),
}

# regTypeId: пробуем 2 (предположительно медизделия). Если будет нужно
# сравнить с лекарствами — поменяй на 1 и запусти снова в отдельный файл.
PAYLOAD = {"regTypeId": 2, "regPeriod": 1}

OUTPUT_FILE = "ndda_raw.json"


def main():
    print(f"Отправляю запрос с payload: {PAYLOAD}")
    response = requests.post(URL, headers=HEADERS, json=PAYLOAD, timeout=120)
    print("Статус ответа:", response.status_code)
    response.raise_for_status()

    data = response.json()

    # Сохраняем сырые данные сразу на диск — дальше будем работать с файлом,
    # а не гонять запрос повторно.
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    print(f"Сырые данные сохранены в {OUTPUT_FILE}")

    # Разбираемся со структурой
    if isinstance(data, list):
        print(f"\nЭто список. Всего записей: {len(data)}")
        if data:
            print("Поля первой записи:")
            print(json.dumps(data[0], ensure_ascii=False, indent=2))

    elif isinstance(data, dict):
        print("\nЭто словарь. Ключи верхнего уровня:", list(data.keys()))
        for key, value in data.items():
            if isinstance(value, list):
                print(f"\n  Ключ '{key}': список из {len(value)} записей")
                if value:
                    print("  Поля первой записи:")
                    print(json.dumps(value[0], ensure_ascii=False, indent=2))
            else:
                print(f"\n  Ключ '{key}': {type(value).__name__} = {value!r}"[:300])

    else:
        print("Неожиданный тип ответа:", type(data))


if __name__ == "__main__":
    main()
