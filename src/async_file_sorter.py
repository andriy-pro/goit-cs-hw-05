import argparse
import asyncio
import datetime
import logging
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Set

from aiopath import AsyncPath

from config import FILE_SORTER

# Покращене налаштування логування
logging.basicConfig(
    level=getattr(logging, FILE_SORTER["LOG_CONFIG"]["LEVEL"]),
    format=FILE_SORTER["LOG_CONFIG"]["FORMAT"],
    handlers=[
        logging.FileHandler(FILE_SORTER["LOG_CONFIG"]["LOG_FILE"]),
        logging.StreamHandler(sys.stdout),
    ],
)


class RecursionDepthExceeded(Exception):
    """Виняток, що виникає при надмірній глибині рекурсії."""


class FileOperationError(Exception):
    """Виняток, пов'язаний з операціями над файлами."""


def get_script_dir() -> Path:
    """Повертає теку, де знаходиться скрипт."""
    return Path(__file__).parent.resolve()


async def create_default_output_folder() -> AsyncPath:
    """
    Створює дефолтну папку в теці 'output' з датою й часом.
    """
    script_dir = get_script_dir()
    timestamp = datetime.datetime.now().strftime(FILE_SORTER["DATETIME_FORMAT"])
    folder_name = f"{FILE_SORTER['DEFAULT_OUTPUT_DIR_PREFIX']}{timestamp}"

    output_base = script_dir / "output"
    output_base.mkdir(parents=True, exist_ok=True)

    folder = AsyncPath(output_base / folder_name)
    await folder.mkdir(parents=True, exist_ok=True)
    return folder


def parse_args():
    """
    Парсинг аргументів командного рядка з значеннями за замовчуванням.
    """
    parser = argparse.ArgumentParser(
        description="Асинхронне сортування файлів за розширенням."
    )
    script_dir = get_script_dir()
    default_source = script_dir / "input" / "test"
    parser.add_argument(
        "source_folder",
        type=str,
        nargs="?",
        default=str(default_source),
        help="Шлях до вихідної папки (за замовчуванням: input/test/ у теці скрипта).",
    )
    parser.add_argument(
        "--output_folder",
        type=str,
        help="Шлях до цільової папки (за замовчуванням: output/sorted_files_<timestamp> у теці скрипта).",
    )
    return parser.parse_args()


class TimingContext:
    """Контекстний менеджер для вимірювання часу виконання операцій."""

    def __init__(self, operation_name: str, level: str = "DEBUG"):
        self.operation_name = operation_name
        self.level = level
        self.start_time = None

    async def __aenter__(self):
        self.start_time = time.time()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        getattr(logging, self.level.lower())(
            f"Час виконання {self.operation_name}: {duration:.4f} секунд"
        )
        if self.operation_name == "всього скрипту":
            # Записуємо метрики продуктивності
            with open(FILE_SORTER["PERFORMANCE_LOG_FILE"], "a") as f:
                f.write(f"{datetime.datetime.now()}, {duration:.2f}\n")


async def copy_file(file: AsyncPath, output_folder: AsyncPath):
    """Асинхронне копіювання файлу з розширеною обробкою помилок та логуванням часу."""
    async with TimingContext(f"копіювання {file}"):
        try:
            if not await file.exists():
                raise FileNotFoundError(f"Файл не існує: {file}")

            # Перевірка доступу до файлу
            if not os.access(str(file), os.R_OK):
                raise PermissionError(f"Немає доступу до читання файлу: {file}")

            # Перевірка вільного місця
            stat = await file.stat()
            free_space = shutil.disk_usage(str(output_folder))[2]
            if stat.st_size > free_space:
                raise OSError(f"Недостатньо місця для копіювання файлу: {file}")

            ext = file.suffix.lstrip(".").lower() or "no_extension"
            target_dir = output_folder / ext
            await target_dir.mkdir(parents=True, exist_ok=True)

            await asyncio.to_thread(
                shutil.copy2, str(file), str(target_dir / file.name)
            )
            logging.info(f"Файл {file} скопійовано до {target_dir}.")

        except Exception as e:
            error_msg = f"Помилка при копіюванні {file}: {e}"
            logging.error(error_msg)
            raise FileOperationError(error_msg) from e


async def read_folder(
    source_folder: AsyncPath,
    output_folder: AsyncPath,
    depth: int = 0,
    processed_dirs: Set[str] = None,
):
    """
    Рекурсивне читання папки з контролем глибини та обробкою файлів.
    """
    if processed_dirs is None:
        processed_dirs = set()

    if depth > FILE_SORTER["MAX_RECURSION_DEPTH"]:
        raise RecursionDepthExceeded(
            f"Перевищено максимальну глибину рекурсії: {depth}"
        )

    real_path = str(await source_folder.resolve())
    if real_path in processed_dirs:
        logging.warning(f"Виявлено циклічне посилання: {source_folder}")
        return

    processed_dirs.add(real_path)
    tasks = []

    try:
        async for item in source_folder.iterdir():
            if await item.is_symlink():
                logging.info(f"Пропуск символічного посилання: {item}")
                continue
            if await item.is_dir():
                tasks.append(
                    read_folder(item, output_folder, depth + 1, processed_dirs)
                )
            else:
                tasks.append(copy_file(item, output_folder))
    except Exception as e:
        logging.error(f"Помилка при читанні директорії {source_folder}: {e}")
        raise

    await asyncio.gather(*tasks)


def print_directory_tree(directory: Path, indent=""):
    """
    Виводить структуру директорій (синхронна функція, оскільки лише вивід).
    """
    for item in sorted(directory.iterdir()):
        if item.is_dir():
            print(f"{indent}📁 {item.name}")
            print_directory_tree(item, indent + "    ")
        else:
            print(f"{indent}📄 {item.name}")


async def main():
    async with TimingContext("всього скрипту", level="INFO"):
        try:
            args = parse_args()
            script_dir = get_script_dir()

            # Setup input directory
            input_dir = script_dir / "input"
            test_dir = input_dir / "test"
            input_dir.mkdir(parents=True, exist_ok=True)
            test_dir.mkdir(parents=True, exist_ok=True)

            # Setup source directory
            source_path = Path(args.source_folder)
            if not source_path.is_absolute():
                source_path = script_dir / source_path
            source_path = source_path.resolve()

            if not source_path.exists():
                source_path.mkdir(parents=True, exist_ok=True)
                logging.info(f"Created source directory: {source_path}")

            if not source_path.is_dir():
                logging.error(f"Source path is not a directory: {source_path}")
                return 1

            source_folder = AsyncPath(str(source_path))
            logging.info(f"Using source folder: {source_folder}")

            # Setup output directory
            if args.output_folder:
                output_path = Path(args.output_folder)
                if not output_path.is_absolute():
                    output_path = script_dir / output_path
                output_path = output_path.resolve()
                output_path.mkdir(parents=True, exist_ok=True)
                output_folder = AsyncPath(str(output_path))
            else:
                output_folder = await create_default_output_folder()

            logging.info(f"Using output folder: {output_folder}")

            # Print initial structure
            print("\nStructure before sorting:")
            if source_path.exists():  # Check again as it might have been just created
                print_directory_tree(source_path)
            else:
                print("Source directory is empty")

            # Perform sorting
            try:
                async with TimingContext("sorting files"):
                    await read_folder(source_folder, output_folder)

                # Print final structure
                print("\nStructure after sorting:")
                output_path = Path(str(output_folder))
                if output_path.exists() and any(output_path.iterdir()):
                    print_directory_tree(output_path)
                else:
                    print("No files were sorted")

                return 0

            except RecursionDepthExceeded as e:
                logging.error(f"Maximum recursion depth exceeded: {e}")
                return 1
            except FileOperationError as e:
                logging.error(f"File operation error: {e}")
                return 1
            except Exception as e:
                logging.error(f"Error during sorting: {e}")
                return 1

        except Exception as e:
            logging.error(f"Unexpected error in main: {e}", exc_info=True)
            return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logging.critical(f"Critical error: {e}", exc_info=True)
        sys.exit(1)
