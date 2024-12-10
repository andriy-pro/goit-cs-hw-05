import logging
import os
from argparse import ArgumentParser
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import List

import matplotlib.pyplot as plt
import requests
from colorama import Fore, init
from requests.exceptions import RequestException

from config import (
    DEFAULT_URL,
    LOG_DIR,
    LOG_FORMAT,
    LOG_LEVEL,
    MAX_WORDS_TO_DISPLAY,
    MINIMUM_WORD_LENGTH,
    REQUEST_TIMEOUT,
    SCRIPT_DIR,
)

# Ініціалізація кольорів
init(autoreset=True)

# Налаштування логування
os.makedirs(LOG_DIR, exist_ok=True)
log_filename = os.path.join(
    LOG_DIR, f"word_frequency_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
)
logging.basicConfig(
    filename=str(log_filename),
    level=LOG_LEVEL,
    format=LOG_FORMAT,
)


# Функція для отримання тексту з URL
def fetch_text(url: str) -> str:
    """Отримує текстовий вміст з вказаної URL-адреси з обробкою помилок."""
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.text
    except RequestException as e:
        logging.error(f"Не вдалося отримати текст: {e}")
        raise


def preprocess_text(text: str) -> List[str]:
    """Попередньо обробляє текст: перетворює в нижній регістр та вилучає пунктуацію."""
    import re

    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text.split()


# Функція для аналізу частоти слів
def analyze_frequency(text: str) -> Counter:
    """Аналізує частоту слів у попередньо обробленому тексті."""
    words = preprocess_text(text)
    # Фільтруємо слова за мінімальною довжиною
    filtered_words = [word for word in words if len(word) >= MINIMUM_WORD_LENGTH]
    word_counts = Counter(filtered_words)
    logging.info(
        f"Проаналізовано {len(filtered_words)} слів (мін. довжина: {MINIMUM_WORD_LENGTH})"
    )
    logging.info(f"Топ слів: {word_counts.most_common(10)}")
    return word_counts


# Функція для візуалізації результатів
def visualize_top_words(word_counts, top_n=MAX_WORDS_TO_DISPLAY):
    """Візуалізує топ слів за частотою у вигляді графіків."""
    top_words = word_counts.most_common(top_n)
    words, counts = zip(*top_words)

    bar_image_path = SCRIPT_DIR / "word_frequency_bar.png"
    pie_image_path = SCRIPT_DIR / "word_frequency_pie.png"

    plt.bar(words, counts, color="blue")
    plt.title("Топ слів за частотою")
    plt.xlabel("Слова")
    plt.ylabel("Частота")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(bar_image_path)
    plt.show()

    plt.pie(counts, labels=words, autopct="%1.1f%%")
    plt.title("Розподіл слів за частотою")
    plt.savefig(pie_image_path)
    plt.show()


# Основна функція
def main(url, top_n):
    print(f"{Fore.CYAN}Завантаження тексту з: {Fore.YELLOW}{url}")
    confirm = input(f"{Fore.GREEN}Бажаєте продовжити? (y/n) [Y]: ").strip().lower()
    if confirm == "" or confirm == "y":
        confirm = "y"
    if confirm != "y":
        print(f"{Fore.RED}Операцію скасовано користувачем.")
        logging.info("Операцію скасовано користувачем.")
        return

    logging.info(f"Отримуємо текст з {url}")
    text = fetch_text(url)

    logging.info("Аналізуємо частоту слів...")
    with ThreadPoolExecutor() as executor:
        word_counts = executor.submit(analyze_frequency, text).result()

    logging.info("Візуалізація результатів...")
    visualize_top_words(word_counts, top_n)
    print(
        f"{Fore.GREEN}Графіки збережено як {Fore.YELLOW}'word_frequency_bar.png' {Fore.GREEN}та {Fore.YELLOW}'word_frequency_pie.png'"
    )


# Парсер аргументів командного рядка
if __name__ == "__main__":
    parser = ArgumentParser(description="Аналіз частоти слів у тексті за URL.")
    parser.add_argument(
        "--url",
        type=str,
        default=DEFAULT_URL,
        help=f"URL-адреса тексту для аналізу (за замовчуванням {DEFAULT_URL}).",
    )
    parser.add_argument(
        "--top_n",
        type=int,
        default=MAX_WORDS_TO_DISPLAY,
        help=f"Кількість слів для відображення (за замовчуванням {MAX_WORDS_TO_DISPLAY}).",
    )

    args = parser.parse_args()

    try:
        main(args.url, args.top_n)
    except Exception as e:
        logging.error(f"Сталася помилка: {e}")
        print(f"{Fore.RED}Помилка: {e}")
