import os
import random
import string
from pathlib import Path

from config import FILE_GENERATOR


def create_random_text_file(file_path, size_kb):
    """Створює текстовий файл з контролем розміру"""
    max_size_bytes = FILE_GENERATOR["MAX_FILE_SIZE_MB"] * 1024 * 1024
    target_size_bytes = size_kb * 1024

    if target_size_bytes > max_size_bytes:
        raise ValueError(
            f"Розмір файлу перевищує ліміт: {size_kb}KB > {FILE_GENERATOR['MAX_FILE_SIZE_MB']}MB"
        )

    if target_size_bytes < FILE_GENERATOR["MIN_FILE_SIZE_BYTES"]:
        raise ValueError(f"Розмір файлу занадто малий: {size_kb}KB")

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            written_bytes = 0
            chunk_size = FILE_GENERATOR["TEXT_FILE_CHUNK_SIZE"]

            while written_bytes < target_size_bytes:
                random_text = "".join(
                    random.choices(
                        string.ascii_letters + string.digits + " ", k=chunk_size
                    )
                )
                f.write(random_text + "\n")
                written_bytes = f.tell()

                if written_bytes > max_size_bytes:
                    logging.warning(f"Файл {file_path} досяг максимального розміру")
                    break

    except IOError as e:
        logging.error(f"Помилка при створенні файлу {file_path}: {e}")
        raise


def generate_test_files(base_dir, num_files=100, extensions=None):
    """
    Створює тестові файли з випадковими розширеннями та вмістом.

    :param base_dir: Основна теки для збереження файлів.
    :param num_files: Кількість файлів для створення.
    :param extensions: Список можливих розширень файлів.
    """
    if extensions is None:
        extensions = ["txt", "jpg", "png", "pdf", "docx", "csv", "json", "xml"]

    base_dir.mkdir(parents=True, exist_ok=True)

    for i in range(num_files):
        ext = random.choice(extensions)
        file_name = f"file_{i + 1}.{ext}"
        file_path = base_dir / file_name

        if ext == "txt" or ext == "csv" or ext == "json" or ext == "xml":
            # Створюємо текстові файли з випадковим розміром (1-10 KB)
            create_random_text_file(file_path, random.randint(1, 10))
        else:
            # Створюємо порожні файли для інших розширень
            file_path.touch()


def create_test_environment(base_dir):
    """
    Створює структуру директорій для тестування.

    :param base_dir: Основна теки для тестування.
    """
    subfolders = ["subfolder1", "subfolder2/subsubfolder1", "subfolder3"]
    for folder in subfolders:
        generate_test_files(base_dir / folder, num_files=random.randint(10, 20))


if __name__ == "__main__":
    # Основна теки для тестування
    test_dir = Path("test")

    # Генеруємо файли у теці `test`
    generate_test_files(test_dir, num_files=50)

    # Додаємо підпапки
    create_test_environment(test_dir)

    print(f"Тестові файли успішно створено у теці: {test_dir.resolve()}")
