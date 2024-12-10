import string
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool

import matplotlib.pyplot as plt
import requests

from config import WORD_ANALYSIS


# Завантаження тексту з URL
def fetch_text(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching text: {e}")
        return None


# Обробка тексту
def preprocess_text(text):
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    return text.split()


# Map функція
def map_words(words):
    # Додамо обробку помилок
    try:
        word_counts = defaultdict(int)
        for word in words:
            if word.strip():  # Перевіряємо, чи слово не пусте
                word_counts[word] += 1
        return word_counts
    except Exception as e:
        print(f"Помилка в map_words: {e}")
        return defaultdict(int)


# Reduce функція
def reduce_counts(counts_list):
    total_counts = defaultdict(int)
    for counts in counts_list:
        for word, count in counts.items():
            total_counts[word] += count
    return total_counts


# Візуалізація
def visualize_top_words(word_counts, top_n=10):
    top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    words, counts = zip(*top_words)

    plt.figure(figsize=(10, 6))
    plt.bar(words, counts, color="skyblue")
    plt.title(f"Top {top_n} Words by Frequency")
    plt.xlabel("Words")
    plt.ylabel("Frequency")
    plt.xticks(rotation=45)
    plt.show()


# Головна функція
def main(
    url=WORD_ANALYSIS["DEFAULT_URL"],
    top_n=WORD_ANALYSIS["DEFAULT_TOP_N"],
    use_multiprocessing=False,
):
    # Використовуємо налаштування з конфігу
    if use_multiprocessing:
        chunk_size = WORD_ANALYSIS["CHUNK_SIZE"]
        num_chunks = WORD_ANALYSIS["NUM_PROCESSES"]
    text = fetch_text(url)
    if not text:
        return

    words = preprocess_text(text)

    if use_multiprocessing:
        num_chunks = 4
        chunk_size = len(words) // num_chunks
        chunks = [words[i : i + chunk_size] for i in range(0, len(words), chunk_size)]

        with Pool(num_chunks) as pool:
            map_results = pool.map(map_words, chunks)

        word_counts = reduce_counts(map_results)
    else:
        with ThreadPoolExecutor() as executor:
            mapped_values = list(executor.map(map_words, [words]))
            word_counts = reduce_counts(mapped_values)

    visualize_top_words(word_counts, top_n)


if __name__ == "__main__":
    url = "https://www.gutenberg.org/files/84/84-0.txt"
    main(url, top_n=10, use_multiprocessing=True)
