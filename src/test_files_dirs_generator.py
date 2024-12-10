import random
import string
from argparse import ArgumentParser
from pathlib import Path

from config import FILE_GENERATOR, INPUT_DIR


def generate_random_files(
    base_dir: Path, num_files: int, total_files_limit: int = None
) -> tuple[int, int]:
    """
    Генерує випадкові файли з різними розширеннями та без розширень у заданій теці.
    Повертає кількість створених файлів та їх загальний розмір.
    """
    if total_files_limit is not None and num_files > total_files_limit:
        num_files = total_files_limit

    total_size = 0
    files_created = 0
    base_dir.mkdir(parents=True, exist_ok=True)
    extensions = FILE_GENERATOR["EXTENSIONS"]
    no_extension_ratio = FILE_GENERATOR["NO_EXTENSION_RATIO"]

    num_no_ext_files = int(num_files * no_extension_ratio)
    for i in range(num_files):
        # Визначаємо, чи створювати файл без розширення
        if i < num_no_ext_files:
            ext = ""
        else:
            ext = random.choice(extensions)
        # Генеруємо випадкове ім'я файлу
        file_name = "".join(random.choices(string.ascii_letters + string.digits, k=8))
        if ext:
            file_name += f".{ext}"
        file_path = base_dir / file_name

        # Створюємо файл з випадковим вмістом
        random_text = "".join(
            random.choices(string.ascii_letters + string.digits + " ", k=1024)
        )
        file_path.write_text(random_text)
        file_size = len(random_text.encode())
        total_size += file_size
        files_created += 1

    return files_created, total_size


def create_chaotic_structure(
    base_dir: Path, depth: int = 3, total_files_limit: int = None
) -> tuple[int, int]:
    """
    Рекурсивно створює хаотичну структуру директорій з випадковими файлами.
    Повертає загальну кількість створених файлів та їх розмір.
    """
    if depth == 0 or (total_files_limit is not None and total_files_limit <= 0):
        return 0, 0

    total_files = 0
    total_size = 0

    num_files = min(random.randint(5, 15), total_files_limit or float("inf"))
    files_created, size = generate_random_files(base_dir, num_files, total_files_limit)
    total_files += files_created
    total_size += size

    if total_files_limit is not None:
        total_files_limit -= files_created

    for _ in range(random.randint(1, 3)):
        if total_files_limit is not None and total_files_limit <= 0:
            break
        subdir_files, subdir_size = create_chaotic_structure(
            base_dir / "".join(random.choices(string.ascii_letters, k=5)),
            depth - 1,
            total_files_limit,
        )
        total_files += subdir_files
        total_size += subdir_size
        if total_files_limit is not None:
            total_files_limit -= subdir_files

    return total_files, total_size


if __name__ == "__main__":
    parser = ArgumentParser(description="Генерація тестових файлів")
    parser.add_argument("--max-files", type=int, help="Максимальна кількість файлів")
    args = parser.parse_args()

    total_files, total_size = create_chaotic_structure(
        INPUT_DIR, total_files_limit=args.max_files
    )
    print(f"Створено файлів: {total_files}")
    print(f"Загальний розмір: {total_size / 1024:.2f} KB")
