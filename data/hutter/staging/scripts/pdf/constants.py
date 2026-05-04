"""
Constants and book mappings for the Hutter Polyglot Bible PDF downloader.
"""

# Base URL for downloads (uses HTTPS with redirect to available server)
BASE_URL = "https://archive.org/download/hutter-polyglot/"

# Default directories
DEFAULT_OUTPUT_DIR = "data/source"
TEST_OUTPUT_DIR = "data/temp"

# PDF files available on the archive (URL-encoded names)
PDF_FILES = [
    "1-%20Matthew.pdf",
    "2-%20Mark.pdf",
    "3-%20Luke.pdf",
    "4-%20John.pdf",
    "5-%20Acts.pdf",
    "6-%20Romans.pdf",
    "7-%20First%20Corithians.pdf",
    "8-%20Second%20Corinthians.pdf",
    "9%20-%20Galations.pdf",
    "10%20-%20Ephesians.pdf",
    "11%20-%20Phillipians.pdf",
    "12%20-%20Colossians.pdf",
    "13%20-%201st%20Thessalonians.pdf",
    "14%20-%202nd%20Thessalonians.pdf",
    "15%20-%201st%20Timothy.pdf",
    "16%20-%202nd%20Timothy.pdf",
    "17%20-%20Titus.pdf",
    "18%20-%20Philemon.pdf",
    "19%20-%20Hebrews.pdf",
    "20%20-%20James.pdf",
    "21%20-%201st%20Peter.pdf",
    "22%20-%202nd%20Peter.pdf",
    "23%20-%201st%20John.pdf",
    "24%20-%202nd%20John.pdf",
    "25%20-%203rd%20John.pdf",
    "26%20-%20Jude.pdf",
    "27%20-%20Revelation%20-%20missing%20ch.%209%2017-21.pdf",
]

# Mapping from simple book names to URL-encoded filenames
BOOK_NAMES = {
    "matthew": "1-%20Matthew.pdf",
    "mark": "2-%20Mark.pdf",
    "luke": "3-%20Luke.pdf",
    "john": "4-%20John.pdf",
    "acts": "5-%20Acts.pdf",
    "romans": "6-%20Romans.pdf",
    "corinthians1": "7-%20First%20Corithians.pdf",
    "corinthians2": "8-%20Second%20Corinthians.pdf",
    "galatians": "9%20-%20Galations.pdf",
    "ephesians": "10%20-%20Ephesians.pdf",
    "philippians": "11%20-%20Phillipians.pdf",
    "colossians": "12%20-%20Colossians.pdf",
    "thessalonians1": "13%20-%201st%20Thessalonians.pdf",
    "thessalonians2": "14%20-%202nd%20Thessalonians.pdf",
    "timothy1": "15%20-%201st%20Timothy.pdf",
    "timothy2": "16%20-%202nd%20Timothy.pdf",
    "titus": "17%20-%20Titus.pdf",
    "philemon": "18%20-%20Philemon.pdf",
    "hebrews": "19%20-%20Hebrews.pdf",
    "james": "20%20-%20James.pdf",
    "peter1": "21%20-%201st%20Peter.pdf",
    "peter2": "22%20-%202nd%20Peter.pdf",
    "john1": "23%20-%201st%20John.pdf",
    "john2": "24%20-%202nd%20John.pdf",
    "john3": "25%20-%203rd%20John.pdf",
    "jude": "26%20-%20Jude.pdf",
    "revelation": "27%20-%20Revelation%20-%20missing%20ch.%209%2017-21.pdf",
}

# Clean output filenames for each book
OUTPUT_NAMES = {
    "matthew": "matthew.pdf",
    "mark": "mark.pdf",
    "luke": "luke.pdf",
    "john": "john.pdf",
    "acts": "acts.pdf",
    "romans": "romans.pdf",
    "corinthians1": "corinthians1.pdf",
    "corinthians2": "corinthians2.pdf",
    "galatians": "galatians.pdf",
    "ephesians": "ephesians.pdf",
    "philippians": "philippians.pdf",
    "colossians": "colossians.pdf",
    "thessalonians1": "thessalonians1.pdf",
    "thessalonians2": "thessalonians2.pdf",
    "timothy1": "timothy1.pdf",
    "timothy2": "timothy2.pdf",
    "titus": "titus.pdf",
    "philemon": "philemon.pdf",
    "hebrews": "hebrews.pdf",
    "james": "james.pdf",
    "peter1": "peter1.pdf",
    "peter2": "peter2.pdf",
    "john1": "john1.pdf",
    "john2": "john2.pdf",
    "john3": "john3.pdf",
    "jude": "jude.pdf",
    "revelation": "revelation.pdf",
}

# Default aria2 settings
DEFAULT_CONNECTIONS_PER_FILE = 16
DEFAULT_MAX_CONCURRENT = 5

