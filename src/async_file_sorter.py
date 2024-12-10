import asyncio
import logging
import shutil
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path
from typing import List, Set

from colorama import Fore, Style, init

from config import LOG_DIR, LOG_FORMAT, LOG_LEVEL, MAX_CONCURRENT_OPERATIONS, SCRIPT_DIR

# Ініціалізація кольорів
init(autoreset=True)

# Отримуємо шлях до теки скрипту
# SCRIPT_DIR = Path(__file__).parent

# Налаштування логування
# LOG_DIR = SCRIPT_DIR / "logs"
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
        "info": Fore.GREEN,
        "warning": Fore.YELLOW,
        "error": Fore.RED,
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
    file_path: Path, output_folder: Path, semaphore: asyncio.Semaphore
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
            # Ім'я файлу виділено Cyan, повідомлення залишається Green
            log_console(
                f"Файл успішно скопійовано: {Fore.CYAN}{file_path.name}", "info"
            )
        except Exception as e:
            log_console(f"Помилка при копіюванні {file_path.name}: {e}", "error")


# Функція для створення підпапок (не асинхронна)
def create_subfolders(output_folder: Path, extensions: Set[str]) -> None:
    """Створює підпапки для кожного розширення."""
    for ext in extensions:
        subfolder = output_folder / (ext if ext else "NO_EXTENSION")
        subfolder.mkdir(parents=True, exist_ok=True)


# Асинхронна функція для читання файлів та їх копіювання
async def read_and_sort_files(source_folder: Path, output_folder: Path) -> None:
    """Зчитує та сортує файли з використанням асинхронної обробки."""
    extensions: Set[str] = set()
    tasks: List[asyncio.Task] = []
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_OPERATIONS)

    for file_path in source_folder.rglob("*"):
        if file_path.is_file():
            extensions.add(file_path.suffix[1:])
            task = asyncio.create_task(copy_file(file_path, output_folder, semaphore))
            tasks.append(task)

    if tasks:
        await asyncio.gather(*tasks)
    # Викликаємо функцію без await, оскільки вона не асинхронна
    create_subfolders(output_folder, extensions)


# Головна функція
async def main(source_folder: str, output_folder: str) -> None:
    """Головна функція, яка виконує сортування файлів."""
    source_path = SCRIPT_DIR / source_folder
    output_path = SCRIPT_DIR / output_folder  # Тека output створюється в теці скрипту

    if not source_path.exists():
        log_console(f"Початкова тека '{source_path}' не існує.", "error")
        return

    # Виведення інформації та підтвердження
    print(f"{Fore.YELLOW}Тека для сортування: {source_path}")
    print(f"{Fore.YELLOW}Тека для збереження результатів: {output_path}")
    confirm = input(f"{Fore.YELLOW}Бажаєте продовжити? (y/n): ").strip().lower()
    if confirm != "y":
        log_console("Сортування скасовано користувачем.", "warning")
        return

    output_path.mkdir(parents=True, exist_ok=True)
    # Виводимо шлях до файлу логування, в��ділений жовтим кольором
    print(f"{Fore.YELLOW}Шлях до файлу логування: {log_filename}")
    log_console("Сортування розпочато.", "info")

    await read_and_sort_files(source_path, output_path)
    log_console("Сортування завершено.", "info")

    print(f"{Fore.YELLOW}Шлях до файлу логування: {log_filename}")


# Парсер аргументів командного рядка
if __name__ == "__main__":
    parser = ArgumentParser(description="Асинхронне сортування файлів за розширенням.")
    parser.add_argument(
        "--source",
        type=str,
        default="input",
        help="Папка з файлами для сортування (за замовчуванням 'input').",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=f"output/sorted_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        help="Папка для збереження відсортованих файлів.",
    )

    args = parser.parse_args()

    asyncio.run(main(args.source, args.output))
