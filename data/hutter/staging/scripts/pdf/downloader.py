"""
Download functionality for Hutter Polyglot Bible PDFs using aria2.
"""

import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, Tuple

from scripts.pdf.constants import (
    BASE_URL,
    BOOK_NAMES,
    DEFAULT_CONNECTIONS_PER_FILE,
    DEFAULT_MAX_CONCURRENT,
    OUTPUT_NAMES,
)

logger = logging.getLogger(__name__)


def is_aria2_available() -> bool:
    """Check if aria2c is installed and available."""
    return shutil.which("aria2c") is not None


def get_aria2_install_instructions() -> str:
    """Return installation instructions for aria2."""
    return """
Error: aria2c is not installed!

Install aria2:
  macOS:         brew install aria2
  Ubuntu/Debian: sudo apt install aria2
  Windows:       choco install aria2
"""


def prepare_download_list(
    book_names: List[str],
    output_dir: str,
    force_redownload: bool = False,
    resume_existing: bool = False,
) -> Tuple[List[Tuple[str, str]], int]:
    """
    Prepare the list of files to download, filtering out existing files.

    Args:
        book_names: List of book names to download
        output_dir: Output directory
        force_redownload: Force re-download existing files
        resume_existing: Resume downloads of existing files

    Returns:
        Tuple of (files_to_download, skipped_count)
    """
    files_to_download = []
    skipped = 0

    for book_name in book_names:
        filename = BOOK_NAMES[book_name]
        output_name = OUTPUT_NAMES[book_name]
        file_path = os.path.join(output_dir, output_name)

        if os.path.exists(file_path) and not force_redownload and not resume_existing:
            if os.path.getsize(file_path) > 0:
                logger.info(f"Skipping {output_name} (already exists)")
                skipped += 1
                continue

        if os.path.exists(file_path) and force_redownload:
            logger.info(f"Deleting existing {output_name} for forced re-download")
            try:
                os.remove(file_path)
            except OSError as e:
                logger.warning(f"Could not delete {file_path}: {e}")
                continue
            logger.info(f"Starting forced re-download of {output_name}")

        elif os.path.exists(file_path) and resume_existing:
            if os.path.getsize(file_path) > 0:
                logger.info(f"Resuming download of {output_name} (existing file)")
            else:
                logger.info(f"Starting download of {output_name}")

        files_to_download.append((filename, output_name))

    return files_to_download, skipped


def create_aria2_input_file(
    files_to_download: List[Tuple[str, str]],
) -> str:
    """
    Create a temporary input file for aria2c.

    Args:
        files_to_download: List of (url_filename, output_name) tuples

    Returns:
        Path to the temporary input file
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for filename, output_name in files_to_download:
            url = BASE_URL + filename
            f.write(f"{url}\n")
            f.write(f"  out={output_name}\n")
        return f.name


def build_aria2_command(
    input_file: str,
    output_dir: str,
    connections_per_file: int,
    max_concurrent: int,
    force_redownload: bool,
) -> List[str]:
    """
    Build the aria2c command with optimized settings.

    Args:
        input_file: Path to aria2 input file
        output_dir: Output directory
        connections_per_file: Number of connections per file
        max_concurrent: Number of concurrent downloads
        force_redownload: Whether to allow overwriting existing files

    Returns:
        List of command arguments
    """
    return [
        "aria2c",
        "--input-file", input_file,
        "--dir", output_dir,
        "--max-connection-per-server", str(connections_per_file),
        "--split", str(connections_per_file),
        "--max-concurrent-downloads", str(max_concurrent),
        "--min-split-size", "1M",
        "--continue=true",
        "--auto-file-renaming=false",
        "--allow-overwrite=true" if force_redownload else "--allow-overwrite=false",
        "--console-log-level=notice",
        "--summary-interval=5",
        "--download-result=full",
        "--retry-wait=2",
        "--max-tries=5",
        "--timeout=60",
        "--connect-timeout=30",
        "--lowest-speed-limit=1K",
        "--max-file-not-found=3",
        "--remote-time=true",
        "--check-certificate=false",
    ]


def run_aria2_download(
    files_to_download: List[Tuple[str, str]],
    output_dir: str,
    skipped: int,
    connections_per_file: int = DEFAULT_CONNECTIONS_PER_FILE,
    max_concurrent: int = DEFAULT_MAX_CONCURRENT,
    force_redownload: bool = False,
) -> bool:
    """
    Execute aria2c to download files.

    Args:
        files_to_download: List of (url_filename, output_name) tuples
        output_dir: Output directory
        skipped: Number of files skipped (for logging)
        connections_per_file: Number of connections per file
        max_concurrent: Number of concurrent downloads
        force_redownload: Whether to allow overwriting

    Returns:
        True if all downloads succeeded, False otherwise
    """
    input_file = create_aria2_input_file(files_to_download)

    try:
        cmd = build_aria2_command(
            input_file=input_file,
            output_dir=output_dir,
            connections_per_file=connections_per_file,
            max_concurrent=max_concurrent,
            force_redownload=force_redownload,
        )

        logger.info(
            f"Starting aria2c with {connections_per_file} connections/file, "
            f"{max_concurrent} concurrent downloads"
        )
        logger.info(f"Output directory: {output_dir}")

        result = subprocess.run(cmd, capture_output=False)

        if result.returncode == 0:
            logger.info("All downloads completed successfully!")
            return True

        # Check which files were actually downloaded
        successful = skipped
        failed = []

        for _, output_name in files_to_download:
            file_path = os.path.join(output_dir, output_name)
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                successful += 1
            else:
                failed.append(output_name)

        if failed:
            logger.error(f"Failed downloads: {', '.join(failed)}")
            logger.info(f"Total: {successful} successful, {len(failed)} failed")
            return False

        logger.info(f"All downloads completed! ({successful} files)")
        return True

    finally:
        try:
            os.unlink(input_file)
        except OSError:
            pass


def download_books(
    book_names: List[str],
    output_dir: str,
    force_redownload: bool = False,
    resume_existing: bool = False,
    connections_per_file: int = DEFAULT_CONNECTIONS_PER_FILE,
    max_concurrent: int = DEFAULT_MAX_CONCURRENT,
) -> bool:
    """
    Download books using aria2c.

    Args:
        book_names: List of book names to download
        output_dir: Output directory
        force_redownload: Force re-download existing files
        resume_existing: Resume downloads of existing files
        connections_per_file: Number of connections per file
        max_concurrent: Number of concurrent downloads

    Returns:
        True if all downloads succeeded, False otherwise

    Raises:
        SystemExit: If aria2c is not available
    """
    if not is_aria2_available():
        print(get_aria2_install_instructions())
        raise SystemExit(1)

    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Prepare download list
    files_to_download, skipped = prepare_download_list(
        book_names=book_names,
        output_dir=output_dir,
        force_redownload=force_redownload,
        resume_existing=resume_existing,
    )

    if not files_to_download:
        logger.info("All requested files already exist!")
        return True

    action = "Resuming" if resume_existing else "Downloading"
    logger.info(f"{action} {len(files_to_download)} files (skipped {skipped} existing)")

    return run_aria2_download(
        files_to_download=files_to_download,
        output_dir=output_dir,
        skipped=skipped,
        connections_per_file=connections_per_file,
        max_concurrent=max_concurrent,
        force_redownload=force_redownload,
    )

