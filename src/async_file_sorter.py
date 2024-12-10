import asyncio
import logging
import shutil
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path
from time import time
from typing import List, Set

from colorama import Fore, init

from config import LOG_DIR, LOG_FORMAT, LOG_LEVEL, MAX_CONCURRENT_OPERATIONS, SCRIPT_DIR

# Ініціалізація кольорів
init(autoreset=True)
CYAN = Fore.CYAN
YELLOW = Fore.YELLOW
GREEN = Fore.GREEN
RED = Fore.RED

LOG_DIR.mkdir(parents=True, exist_ok=True)
log_filename = (
    LOG_DIR / f"async_file_sorter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
)
logging.basicConfig(
    filename=str(log_filename),
    level=LOG_LEVEL,
    format=LOG_FORMAT,
)


# Функція для виведення повідомлень у консоль
def log_console(message, level="info"):
    """Виводить повідомлення в консоль та записує в лог без кольорових кодів."""
    color_map = {
        "info": GREEN,
        "warning": YELLOW,
        "error": RED,
    }
    color = color_map.get(level, Fore.WHITE)
    # Видаляємо кольорові коди з повідомлення перед записом у лог
    log_message = remove_color_codes(message)
    print(color + message)
    logging.log(getattr(logging, level.upper(), logging.INFO), log_message)


def remove_color_codes(text):
    """Видаляє ANSI-коди кольорів з тексту."""
    import re

    ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
    return ansi_escape.sub("", text)


# Асинхронна функція для копіювання файлу
async def copy_file(
    file_path: Path,
    output_folder: Path,
    semaphore: asyncio.Semaphore,
    source_folder: Path,
) -> None:
    """Копіює файл з контролем конкурентності та обробкою помилок."""
    async with semaphore:
        try:
            extension = file_path.suffix[1:]
            destination_folder = output_folder / (
                extension if extension else "NO_EXTENSION"
            )
            destination_path = destination_folder / file_path.name
            destination_folder.mkdir(parents=True, exist_ok=True)
            await asyncio.to_thread(shutil.copy, str(file_path), str(destination_path))
            relative_path = file_path.relative_to(source_folder)
            log_console(f"Скопійовано: {YELLOW}{relative_path}", "info")
            logging.info(f"Скопійовано файл з '{file_path}' до '{destination_path}'")
        except Exception as e:
            log_console(f"Помилка при копіюванні {file_path.name}: {e}", "error")


# Функція для створення підтек (не асинхронна)
def create_subfolders(output_folder: Path, extensions: Set[str]) -> None:
    """Створює підтеки для кожного розширення."""
    for ext in extensions:
        subfolder = output_folder / (ext if ext else "NO_EXTENSION")
        subfolder.mkdir(parents=True, exist_ok=True)


# Асинхронна функція для читання файлів та їх копіювання
async def read_and_sort_files(
    source_folder: Path, output_folder: Path
) -> tuple[int, float]:
    """Зчитує та сортує файли з використанням асинхронної обробки."""
    start_time = time()
    extensions: Set[str] = set()
    tasks: List[asyncio.Task] = []
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_OPERATIONS)
    file_count = 0

    # Перевіряємо існування та доступність вхідної теки
    if not source_folder.exists():
        raise FileNotFoundError(f"Тека '{source_folder}' не існує")
    if not source_folder.is_dir():
        raise NotADirectoryError(f"'{source_folder}' не є текою")

    for file_path in source_folder.rglob("*"):
        if file_path.is_file():
            file_count += 1
            extensions.add(file_path.suffix[1:])
            task = asyncio.create_task(
                copy_file(file_path, output_folder, semaphore, source_folder)
            )
            tasks.append(task)

    if tasks:
        await asyncio.gather(*tasks)
    create_subfolders(output_folder, extensions)

    execution_time = time() - start_time
    return file_count, execution_time


def parse_args():
    """Обробка аргументів командного рядка."""
    parser = ArgumentParser(description="Асинхронне сортування файлів за розширенням.")
    parser.add_argument(
        "--source",
        type=str,
        default="input",
        help="Тека з файлами для сортування (за замовчуванням 'input').",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=f"output/sorted_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        help="Тека для збереження відсортованих файлів.",
    )
    return parser.parse_args()


# Головна функція
async def main(source_folder: str, output_folder: str) -> None:
    """Головна функція, яка виконує сортування файлів."""
    source_path = SCRIPT_DIR / source_folder
    output_path = SCRIPT_DIR / output_folder  # Тека output створюється в теці скрипту

    if not source_path.exists():
        log_console(f"Початкова тека '{source_path}' не існує.", "error")
        return

    # Виведення інформації та підтвердження
    print(f"{CYAN}Тека для сортування: {YELLOW}{source_path}")
    print(f"{CYAN}Тека для збереження результатів: {YELLOW}{output_path}")
    print(f"{CYAN}Шлях до файлу логування: {YELLOW}{log_filename}")
    confirm = input(f"{GREEN}Бажаєте продовжити? (y/n) [Y]: ").strip().lower()
    if confirm == "" or confirm == "y":
        confirm = "y"
    if confirm != "y":
        log_console("Сортування скасовано користувачем.", "warning")
        return

    output_path.mkdir(parents=True, exist_ok=True)
    # Виводимо шлях до файлу логування, виділений жовтим кольором
    log_console("Сортування розпочато.", "info")

    try:
        file_count, execution_time = await read_and_sort_files(source_path, output_path)
        log_console(f"Сортування завершено. Оброблено файлів: {file_count}", "info")
        log_console(f"Час виконання: {execution_time:.2f} секунд", "info")
    except (FileNotFoundError, NotADirectoryError) as e:
        log_console(f"Помилка: {e}", "error")
        return

    print(f"{CYAN}Шлях до файлу логування: {YELLOW}{log_filename}")


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(main(args.source, args.output))
