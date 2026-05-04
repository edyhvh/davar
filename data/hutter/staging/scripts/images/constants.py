"""
Constants and configuration for the PDF to Images converter.
"""

# Available books (New Testament)
AVAILABLE_BOOKS = [
    "matthew",
    "mark",
    "luke",
    "john",
    "acts",
    "romans",
    "corinthians1",
    "corinthians2",
    "galatians",
    "ephesians",
    "philippians",
    "colossians",
    "thessalonians1",
    "thessalonians2",
    "timothy1",
    "timothy2",
    "titus",
    "philemon",
    "hebrews",
    "james",
    "peter1",
    "peter2",
    "john1",
    "john2",
    "john3",
    "jude",
    "revelation",
]

# Default directories
DEFAULT_OUTPUT_DIR = "data/images/raw_images"
TEST_OUTPUT_DIR = "data/temp"
PDF_SOURCE_DIR = "data/source"

# Performance tracking file
PERF_STATS_FILE = "data/.conversion_stats.json"

# Default conversion settings
DEFAULT_DPI = 300
DEFAULT_BATCH_SIZE = 10
DEFAULT_IMAGE_FORMAT = "PNG"

# Supported image formats
SUPPORTED_FORMATS = ["PNG", "JPEG", "TIFF", "BMP"]

