from pathlib import Path

# Base configuration
BASE_DIR = Path(__file__).parent.parent
SCRIPT_DIR = BASE_DIR / "src"
LOG_DIR = SCRIPT_DIR / "logs"
OUTPUT_DIR = SCRIPT_DIR / "output"
INPUT_DIR = SCRIPT_DIR / "input"

# Logging configuration
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"

# File processing configuration
MAX_CONCURRENT_OPERATIONS = 5  # Semaphore limit for async operations
CHUNK_SIZE = 1024 * 1024  # 1MB chunks for file operations

# Word analysis configuration
MAX_WORDS_TO_DISPLAY = 10
MINIMUM_WORD_LENGTH = 3
DEFAULT_URL = "https://gutenberg.net.au/ebooks01/0100021.txt"

# Network configuration
REQUEST_TIMEOUT = 10  # seconds
MAX_RETRIES = 3

# File generator configuration
FILE_GENERATOR = {
    "MAX_FILE_SIZE_MB": 5,
    "MIN_FILE_SIZE_BYTES": 1024,  # 1KB
    "TEXT_FILE_CHUNK_SIZE": 1024,  # bytes per write
    "EXTENSIONS": ["txt", "jpg", "png", "pdf", "docx", "csv", "json", "xml"],
    "NO_EXTENSION_RATIO": 0.1,  # 10% of files without extensions
}
