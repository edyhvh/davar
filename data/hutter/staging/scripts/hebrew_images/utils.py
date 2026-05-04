"""Shared utilities and constants for Hebrew text extraction."""

import cv2
import numpy as np
from typing import Tuple

# Expected geometry for the central Hebrew column
VERTICAL_WIDTH_RANGE = (800, 1200)
VERTICAL_MIN_HEIGHT = 2000
VERTICAL_X_RANGE = (100, 300)
TITLE_SCAN_HEIGHT = 400
TITLE_MIN_HEIGHT = 25
TITLE_MAX_HEIGHT = 220


def get_fallback_coords(width: int, height: int) -> dict:
    """Get fallback coordinates based on image dimensions."""
    # Estimate second column position: typically 25-30% from left
    x = int(width * 0.28)  # ~28% from left
    # Width: typically 700-1100px, use ~40% of page width or 700px minimum
    w = max(700, min(1100, int(width * 0.4)))
    return {
        "x": x,
        "y": 0,  # CRITICAL: Start from top to preserve enumeration
        "w": w,
        "h": height,  # Full height
    }


def expand_vertical_range(
    box: Tuple[int, int, int, int], height: int
) -> Tuple[int, int, int, int]:
    """
    Expand vertical range to preserve enumeration at top.
    
    CRITICAL: ALWAYS start from very top (y=0 or small margin <50px) to preserve
    enumeration/verse numbers. Ignore the detected y position - we need the full
    column from top.
    
    Args:
        box: Bounding box (x, y, w, h)
        height: Image height
        
    Returns:
        Updated bounding box with expanded vertical range
    """
    x, y, w, h = box
    
    # Start from top, max 50px margin (2% of height)
    y0_start = max(0, min(50, int(height * 0.02)))
    # Extend to near bottom (93% of page to ensure we capture all text)
    y1_end = min(height - 1, int(height * 0.93))
    h_expanded = y1_end - y0_start
    
    # Ensure we capture enough height (at least 85% of page for full text)
    min_height = int(height * 0.85)
    if h_expanded < min_height:
        # Expand downward if possible
        y1_end = min(height - 1, y0_start + min_height)
        h_expanded = y1_end - y0_start
    
    return (x, y0_start, w, h_expanded)


def split_wide_region(
    x0: int, x1: int, width: int
) -> Tuple[int, int]:
    """
    Split a wide region to extract the second column.
    
    CRITICAL: Second column typically starts around 400-500px from left edge.
    If the wide region starts very close to left (x0 < 100), it likely includes
    first column.
    
    Args:
        x0: Left edge of wide region
        x1: Right edge of wide region
        width: Image width
        
    Returns:
        Tuple of (new_x0, new_w) for second column
    """
    w_original = x1 - x0
    
    # Determine split point based on starting position
    if x0 < 100:
        # Wide region starting near left edge - second column starts around 400-500px
        split_x = max(400, int(width * 0.25))
    else:
        # Region starts further right - use proportional split
        split_x = max(x0 + 400, int(x0 + w_original * 0.3))
    
    # Ensure the second column has sufficient width (at least 800px)
    w_second = x1 - split_x
    if w_second < 800:
        # Adjust split point to ensure minimum width
        split_x = max(x0, x1 - 1100)  # Ensure at least 1100px width
        # But don't go too far left (second column should start >= 400px)
        split_x = max(400, split_x)
        w_second = x1 - split_x
    
    # Cap width at reasonable maximum
    w_final = min(w_second, 1100)
    
    return (split_x, w_final)


def validate_column_width(w: int, width: int) -> bool:
    """Validate that column width is within reasonable bounds."""
    max_allowed_width = min(VERTICAL_WIDTH_RANGE[1] + 200, int(width * 0.6))
    min_allowed_width = max(600, VERTICAL_WIDTH_RANGE[0] - 200)
    return min_allowed_width <= w <= max_allowed_width


def reject_first_column(x: int, width: int) -> bool:
    """
    Check if column starts too close to left edge (likely first column).
    
    Args:
        x: X position of column start
        width: Image width
        
    Returns:
        True if column should be rejected (starts too close to left)
    """
    min_x_threshold = max(50, int(width * 0.05))
    return x < min_x_threshold
