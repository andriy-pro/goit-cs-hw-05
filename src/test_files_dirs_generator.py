import logging
import random
import string
from pathlib import Path

from config import FILE_GENERATOR, INPUT_DIR, SCRIPT_DIR

# Отримуємо шлях до теки скрипту
SCRIPT_DIR = Path(__file__).parent

# Шлях до папки input
INPUT_DIR = SCRIPT_DIR / "input"
INPUT_DIR.mkdir(parents=True, exist_ok=True)


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


def generate_test_files(
    base_dir, num_files=100, extensions=None, no_extension_ratio=None
):
    """
    Створює тестові файли з випадковими розширеннями та вмістом, деякі без розширень.

    :param base_dir: Основна теки для збереження файлів.
    :param num_files: Кількість файлів для створення.
    :param extensions: Список можливих розширень файлів.
    :param no_extension_ratio: Частка файлів без розширень (0.0 - 1.0).
    """
    if extensions is None:
        extensions = FILE_GENERATOR["EXTENSIONS"]
    if no_extension_ratio is None:
        no_extension_ratio = FILE_GENERATOR["NO_EXTENSION_RATIO"]

    base_dir.mkdir(parents=True, exist_ok=True)
    num_no_ext_files = int(num_files * no_extension_ratio)

    for i in range(num_files):
        # Визначаємо, чи створювати файл без розширення
        if i < num_no_ext_files:
            ext = ""
        else:
            ext = random.choice(extensions)
        file_name = f"file_{i + 1}"
        if ext:
            file_name += f".{ext}"
        file_path = base_dir / file_name

        # Створюємо файл
        if ext in ["txt", "csv", "json", "xml"] or ext == "":
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


def generate_files(num_files: int):
    """Генерує випадкові файли в теці input."""
    for _ in range(num_files):
        filename = (
            "".join(random.choices(string.ascii_letters + string.digits, k=8)) + ".txt"
        )
        filepath = INPUT_DIR / filename
        with open(filepath, "w") as f:
            f.write("Test content")


if __name__ == "__main__":
    # Основна теки для тестування
    test_dir = INPUT_DIR

    # Генеруємо файли у теці `test`
    generate_test_files(test_dir, num_files=50)

    # Додаємо підпапки
    create_test_environment(test_dir)

    generate_files(10)
    print(f"Згенеровано файли у теці: {INPUT_DIR}")
    print(f"Тестові файли успішно створено у теці: {test_dir.resolve()}")
