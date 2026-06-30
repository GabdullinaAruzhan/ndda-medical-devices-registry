"""
Шаг 2: дотягиваем детальные карточки (включая класс риска) для каждого
изделия из ndda_raw.json, используя найденный endpoint MtMainGetById.

ВАЖНО: 14105 запросов — это много. Скрипт:
  - делает паузу между запросами (не долбит сервер слишком быстро)
  - сохраняет прогресс на диск каждые N штук, чтобы можно было прерваться
    и продолжить, не теряя уже скачанное
  - пропускает ID, которые уже скачаны

Перед полным прогоном — сначала тест на небольшом количестве
(см. TEST_LIMIT ниже), чтобы убедиться что всё работает и посмотреть,
как выглядит структура ответа с классом риска.
"""

import json
import time
import requests
from pathlib import Path

DETAIL_URL = "https://oldregister.ndda.kz/register-backend/RegisterService/MtMainGetById"

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "ru-KZ,ru-RU;q=0.9,ru;q=0.8,en-US;q=0.7,en;q=0.6",
    "referer": "https://oldregister.ndda.kz/",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"
    ),
}

SOURCE_FILE = "ndda_raw.json"
OUTPUT_FILE = "ndda_details.json"
PAUSE_SECONDS = 0.5      
SAVE_EVERY = 100         


# Когда убедишься, что всё работает — поставь None, чтобы скачать всё.
TEST_LIMIT = None


def load_ids():
    with open(SOURCE_FILE, encoding="utf-8") as f:
        data = json.load(f)
    return [item["id"] for item in data]


def load_existing_details():
    path = Path(OUTPUT_FILE)
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_details(details):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(details, f, ensure_ascii=False)


def fetch_one(item_id):
    response = requests.get(
        DETAIL_URL, headers=HEADERS, params={"Id": item_id}, timeout=30
    )
    response.raise_for_status()
    return response.json()


def main():
    all_ids = load_ids()
    if TEST_LIMIT:
        all_ids = all_ids[:TEST_LIMIT]

    details = load_existing_details()
    remaining = [i for i in all_ids if str(i) not in details]
    print(f"Всего ID: {len(all_ids)}, уже скачано: {len(details)}, осталось: {len(remaining)}")

    for n, item_id in enumerate(remaining, start=1):
        try:
            data = fetch_one(item_id)
            details[str(item_id)] = data
        except Exception as e:
            print(f"Ошибка для id={item_id}: {e}")
            details[str(item_id)] = {"error": str(e)}

        if n % SAVE_EVERY == 0 or n == len(remaining):
            save_details(details)
            print(f"Сохранено {n}/{len(remaining)} (всего в файле: {len(details)})")

        time.sleep(PAUSE_SECONDS)

    print("Готово.")
    # покажем структуру одной карточки, чтобы видеть, где класс риска
    sample = next((v for v in details.values() if "error" not in v), None)
    if sample:
        print("\nПример детальной карточки:")
        print(json.dumps(sample, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
