"""Improved logging system for Hebrew text extraction."""

import logging
from typing import Optional
from contextlib import contextmanager


class ImageLogger:
    """Context manager for organized per-image logging."""

    def __init__(self, image_name: str, logger: logging.Logger):
        self.image_name = image_name
        self.logger = logger
        self.detection_methods_tried = []
        self.warnings = []
        self.success = False
        self.method_used = None
        self.box = None

    def __enter__(self):
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"Processing: {self.image_name}")
        self.logger.info(f"{'='*60}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:  # Only show summary if no exception occurred
            if self.success:
                self.logger.info(f"✓ Success: {self.image_name}")
                if self.method_used:
                    self.logger.info(f"  Method: {self.method_used}")
                if self.box:
                    x, y, w, h = self.box
                    self.logger.info(f"  Box: x={x}, y={y}, w={w}, h={h}")
            else:
                self.logger.warning(f"✗ Failed: {self.image_name}")
                if self.warnings:
                    for warning in self.warnings:
                        self.logger.warning(f"  {warning}")
            self.logger.info("")
        return False  # Don't suppress exceptions

    def log_detection_attempt(self, method: str, success: bool, details: Optional[str] = None):
        """Log a detection method attempt."""
        status = "✓" if success else "✗"
        msg = f"  {status} {method}"
        if details:
            msg += f": {details}"
        self.logger.debug(msg)
        self.detection_methods_tried.append((method, success))
        if success:
            self.method_used = method

    def log_warning(self, message: str):
        """Log a warning message."""
        self.warnings.append(message)
        self.logger.warning(f"  ⚠ {message}")

    def log_info(self, message: str):
        """Log an info message."""
        self.logger.info(f"  ℹ {message}")

    def set_success(self, box: Optional[tuple] = None, method: Optional[str] = None):
        """Mark processing as successful."""
        self.success = True
        self.box = box
        if method:
            self.method_used = method


def setup_logging(verbose: bool = False) -> logging.Logger:
    """
    Setup logging configuration.
    
    Args:
        verbose: If True, show DEBUG messages
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger("hebrew_extractor")
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create console handler
    handler = logging.StreamHandler()
    
    # Set level
    level = logging.DEBUG if verbose else logging.INFO
    logger.setLevel(level)
    handler.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    logger.propagate = False
    
    return logger


def log_summary(logger: logging.Logger, successful: int, total: int, skipped: int = 0):
    """
    Log a summary of processing results.
    
    Args:
        logger: Logger instance
        successful: Number of successfully processed images
        total: Total number of images
        skipped: Number of skipped images
    """
    logger.info("")
    logger.info("="*60)
    logger.info("PROCESSING SUMMARY")
    logger.info("="*60)
    logger.info(f"Total images:     {total}")
    logger.info(f"Successfully processed: {successful} ({successful/total*100:.1f}%)")
    if skipped > 0:
        logger.info(f"Skipped:          {skipped}")
    failed = total - successful - skipped
    if failed > 0:
        logger.info(f"Failed:           {failed}")
    logger.info("="*60)






