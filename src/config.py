from pathlib import Path

# Налаштування аналізу слів
DEFAULT_URL = "https://gutenberg.net.au/ebooks01/0100021.txt"
MAX_WORDS_TO_DISPLAY = 10  # Максимальна кількість слів для відображення
MINIMUM_WORD_LENGTH = 3  # Мінімальна довжина слова для аналізу

# Налаштування обробки файлів
MAX_CONCURRENT_OPERATIONS = 5  # Ліміт семафору для асинхронних операцій
CHUNK_SIZE = 1024 * 1024  # Розмір частини для операцій з файлами (1MB)

# Базова конфігурація
BASE_DIR = Path(__file__).parent.parent
SCRIPT_DIR = BASE_DIR / "src"
LOG_DIR = SCRIPT_DIR / "logs"
OUTPUT_DIR = SCRIPT_DIR / "output"
INPUT_DIR = SCRIPT_DIR / "input"

# Налаштування логування
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"

# Налаштування мережі
REQUEST_TIMEOUT = 10  # Таймаут для запитів (секунди)
MAX_RETRIES = 3  # Максимальна кількість повторних спроб

# Налаштування генератора файлів
FILE_GENERATOR = {
    "MAX_FILE_SIZE_MB": 5,  # Максимальний розмір файлу в мегабайтах
    "MIN_FILE_SIZE_BYTES": 1024,  # Мінімальний розмір файлу в байтах (1KB)
    "TEXT_FILE_CHUNK_SIZE": 1024,  # Кількість байтів на запис у текстовий файл
    "EXTENSIONS": [
        "txt",
        "jpg",
        "png",
        "pdf",
        "docx",
        "csv",
        "json",
        "xml",
    ],
    "NO_EXTENSION_RATIO": 0.1,  # Відсоток файлів без розширення (10%)
}
