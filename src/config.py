import logging
from pathlib import Path


def validate_word_analysis_config(config):
    """Валідація налаштувань для аналізу слів."""
    assert isinstance(config["DEFAULT_URL"], str), "DEFAULT_URL має бути рядком"
    assert isinstance(
        config["DEFAULT_TOP_N"], int
    ), "DEFAULT_TOP_N має бути цілим числом"
    assert config["DEFAULT_TOP_N"] > 0, "DEFAULT_TOP_N має бути більше 0"
    assert isinstance(
        config["NUM_PROCESSES"], int
    ), "NUM_PROCESSES має бути цілим числом"
    assert config["NUM_PROCESSES"] > 0, "NUM_PROCESSES має бути більше 0"
    assert isinstance(config["CHUNK_SIZE"], int), "CHUNK_SIZE має бути цілим числом"
    assert config["CHUNK_SIZE"] > 0, "CHUNK_SIZE має бути більше 0"


def validate_file_generator_config(config):
    """Валідація налаштувань для генератора файлів."""
    assert isinstance(
        config["DEFAULT_EXTENSIONS"], list
    ), "DEFAULT_EXTENSIONS має бути списком"
    assert all(
        isinstance(ext, str) for ext in config["DEFAULT_EXTENSIONS"]
    ), "Всі розширення мають бути рядками"
    assert isinstance(
        config["MAX_FILE_SIZE_MB"], int
    ), "MAX_FILE_SIZE_MB має бути цілим числом"
    assert config["MAX_FILE_SIZE_MB"] > 0, "MAX_FILE_SIZE_MB має бути більше 0"
    assert isinstance(
        config["MIN_FILE_SIZE_BYTES"], int
    ), "MIN_FILE_SIZE_BYTES має бути цілим числом"
    assert config["MIN_FILE_SIZE_BYTES"] > 0, "MIN_FILE_SIZE_BYTES має бути більше 0"


def validate_file_sorter_config(config):
    """Валідація налаштувань для сортувальника файлів."""
    assert isinstance(
        config["MAX_RECURSION_DEPTH"], int
    ), "MAX_RECURSION_DEPTH має бути цілим числом"
    assert config["MAX_RECURSION_DEPTH"] > 0, "MAX_RECURСION_DEPTH має бути більше 0"
    assert isinstance(
        config["LOG_CONFIG"]["LEVEL"], str
    ), "LOG_CONFIG.LEVEL має бути рядком"
    assert config["LOG_CONFIG"]["LEVEL"] in [
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ], "Невірний рівень логування"


# Налаштування для word_frequency_analysis.py
WORD_ANALYSIS = {
    "DEFAULT_URL": "https://www.gutenberg.org/files/84/84-0.txt",
    "DEFAULT_TOP_N": 10,
    "NUM_PROCESSES": 4,
    "CHUNK_SIZE": 1000,
    "PLOT_CONFIG": {"FIGURE_SIZE": (10, 6), "BAR_COLOR": "skyblue", "ROTATION": 45},
}

# Налаштування для test_files_dirs_generator.py
FILE_GENERATOR = {
    "DEFAULT_EXTENSIONS": ["txt", "jpg", "png", "pdf", "docx", "csv", "json", "xml"],
    "DEFAULT_NUM_FILES": 100,
    "TEXT_FILE_CHUNK_SIZE": 100,
    "FILE_SIZE_RANGE": (1, 10),  # KB
    "DEFAULT_TEST_DIR": Path("test"),
    "MAX_FILE_SIZE_MB": 100,  # максимальний розмір файлу в MB
    "MIN_FILE_SIZE_BYTES": 1024,  # мінімальний розмір файлу в байтах
}

# Налаштування для async_file_sorter.py
FILE_SORTER = {
    "LOG_CONFIG": {
        "LEVEL": "INFO",
        "FORMAT": "%(asctime)s - %(levelname)s - %(message)s",
        "LOG_FILE": "file_sorter.log",
    },
    "DEFAULT_OUTPUT_DIR_PREFIX": "sorted_files_",
    "DATETIME_FORMAT": "%Y%m%d_%H%M%S",
    "MAX_RECURSION_DEPTH": 10,
    "PERFORMANCE_LOG_FILE": "performance.log",
}

# Валідація конфігурацій при імпорті
try:
    validate_word_analysis_config(WORD_ANALYSIS)
    validate_file_generator_config(FILE_GENERATOR)
    validate_file_sorter_config(FILE_SORTER)
except AssertionError as e:
    logging.critical(f"Помилка в конфігурації: {e}")
    raise
