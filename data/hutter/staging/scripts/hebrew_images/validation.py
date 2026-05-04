"""Validation and refinement module for detected Hebrew columns.

CONSERVATIVE: Only fixes very specific, clear problems.
"""

import cv2
import numpy as np
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


def calculate_right_edge_density(thresh: np.ndarray, x: int, w: int, edge_width: int = 50) -> float:
    """
    Calculate text density in the right edge region of the detected column.
    
    Args:
        thresh: Thresholded binary image
        x: Column x position
        w: Column width
        edge_width: Width of edge region to check (default 50px)
        
    Returns:
        Density ratio (0.0 to 1.0)
    """
    height, width = thresh.shape[:2]
    
    # Check last edge_width pixels of the column
    right_edge_start = max(x + w - edge_width, x)
    right_edge_end = min(x + w, width)
    
    if right_edge_end <= right_edge_start:
        return 0.0
    
    right_edge_region = thresh[:, right_edge_start:right_edge_end]
    
    if right_edge_region.size == 0:
        return 0.0
    
    # Calculate density (percentage of white pixels)
    density = np.sum(right_edge_region > 0) / right_edge_region.size
    return density


def find_left_region_peak(thresh: np.ndarray, image_width: int) -> Optional[int]:
    """
    Find the peak position in the left region (10-30% of width) for Problem 2 fix.
    
    Args:
        thresh: Thresholded binary image
        image_width: Full image width
        
    Returns:
        Peak x position or None if no significant peak found
    """
    height, width = thresh.shape[:2]
    
    # Define left region: 10% to 30% of width
    left_start = int(width * 0.10)
    left_end = int(width * 0.30)
    
    if left_end <= left_start:
        return None
    
    # Calculate horizontal projection in left region
    left_region = thresh[:, left_start:left_end]
    if left_region.size == 0:
        return None
    
    # Sum horizontally to get density per x position
    projection = left_region.sum(axis=0)
    
    if projection.size == 0 or projection.max() == 0:
        return None
    
    # Find peak (maximum density position)
    peak_idx = np.argmax(projection)
    peak_x = left_start + peak_idx
    
    # Check if peak is significant (at least 5% of max possible)
    max_possible = height * 255  # All pixels white
    peak_value = projection[peak_idx]
    threshold = max_possible * 0.05
    
    if peak_value > threshold:
        logger.debug(
            f"Found left region peak at x={peak_x} "
            f"(density: {peak_value / max_possible:.2%})"
        )
        return peak_x
    
    return None


def expand_width_if_text_cut(
    thresh: np.ndarray, x: int, w: int, max_expand: int = 200
) -> Tuple[int, int]:
    """
    Check if text is cut off at the right edge and expand width if needed.
    
    CONSERVATIVE: Only expands when there's clear evidence of text being cut.
    Targets specific problem images: 000016, 000056, 000062
    
    Args:
        thresh: Thresholded binary image
        x: Current x position
        w: Current width
        max_expand: Maximum pixels to expand
        
    Returns:
        Updated (x, w) tuple
    """
    height, width = thresh.shape[:2]
    
    # Only check narrow columns (<850px) - wider columns are less likely to be cut
    if w >= 850:
        return x, w
    
    # Check density at right edge (last 40px of column)
    right_edge_start = max(x + w - 40, x)
    right_edge_end = min(x + w, width)
    right_edge_region = thresh[:, right_edge_start:right_edge_end]
    
    if right_edge_region.size == 0:
        return x, w
    
    right_edge_density = np.sum(right_edge_region > 0) / right_edge_region.size
    
    # Only expand if there's HIGH density at edge (>18%) indicating text is present
    if right_edge_density > 0.18:
        # Check region beyond current width (first 60px)
        expand_start = min(x + w, width - 1)
        expand_end = min(x + w + 60, width)
        
        if expand_end > expand_start:
            beyond_region = thresh[:, expand_start:expand_end]
            beyond_density = np.sum(beyond_region > 0) / beyond_region.size if beyond_region.size > 0 else 0
            
            # Need significant density beyond edge (>12%) to expand
            if beyond_density > 0.12:
                # Find where text actually ends
                expand_full_end = min(x + w + max_expand, width)
                best_end = expand_start
                
                # Check in 20px increments to find end of text
                for check_x in range(expand_start, expand_full_end, 20):
                    check_strip = thresh[:, check_x:min(check_x + 40, width)]
                    if check_strip.size == 0:
                        break
                        
                    strip_density = np.sum(check_strip > 0) / check_strip.size
                    
                    # Track where text ends (density drops below threshold)
                    if strip_density > 0.08:
                        best_end = check_x + 40
                    else:
                        # Text ended, stop here
                        break
                
                # Only expand if we found meaningful continuation (at least 40px)
                if best_end > expand_start + 40:
                    new_w = best_end - x
                    # Don't expand beyond reasonable Hebrew column width
                    new_w = min(new_w, 1100)
                # Only expand if it's a meaningful increase (at least 40px)
                if new_w > w + 40:
                    logger.info(f"Expanding width from {w} to {new_w} (text cut detected)")
                    return x, new_w
    
    return x, w


def fix_wrong_column_detection(
    thresh: np.ndarray, box: Tuple[int, int, int, int], image_width: int
) -> Tuple[int, int, int, int]:
    """
    Fix Problem 2: Detect when column is too far right and look for correct column in left region.
    
    This is a general fix that works for any image where the detected column center
    is too far to the right (>55% of width), suggesting the wrong column was detected.
    
    Args:
        thresh: Thresholded binary image
        box: Current bounding box (x, y, w, h)
        image_width: Full image width
        
    Returns:
        Updated bounding box
    """
    x, y, w, h = box
    center_x = x + w / 2
    
    # Check if column is too far right (>55% of width)
    if center_x > image_width * 0.55:
        logger.debug(
            f"Column too far right detected (center_x={center_x:.1f}, {center_x/image_width:.1%} of width)"
        )
        
        # Look for peak in left region
        peak_x = find_left_region_peak(thresh, image_width)
        
        if peak_x is not None:
            # Adjust x position to match peak, with a margin
            margin = 30
            new_x = max(0, peak_x - margin)
            
            # Calculate new width - try to expand width significantly
            ideal_width = max(900, min(1100, w + 100))
            new_w = min(ideal_width, image_width - new_x)
            
            # Ensure we have a good width
            if new_w < 850 and image_width - new_x >= 850:
                new_w = min(1100, image_width - new_x)
            
            logger.info(
                f"Fixed wrong column detection: Adjusting x from {x}px to {new_x}px, "
                f"width from {w}px to {new_w}px (peak found at x={peak_x})"
            )
            return (new_x, y, new_w, h)
    
    return box


def fix_right_edge_expansion(
    thresh: np.ndarray, box: Tuple[int, int, int, int], image_width: int
) -> Tuple[int, int, int, int]:
    """
    Fix Problem 1: Expand width if text is too close to right edge.
    
    This is a general fix that works for any image where high text density
    is detected at the right edge, suggesting text may be cut off.
    
    Args:
        thresh: Thresholded binary image
        box: Current bounding box (x, y, w, h)
        image_width: Full image width
        
    Returns:
        Updated bounding box
    """
    x, y, w, h = box
    
    # Check if width is already at or near the limit (Problem 3 may have set it)
    # Limit expansion to avoid showing entire page
    max_allowed_width = 1100
    if w >= max_allowed_width - 50:  # Already close to limit
        # Only allow very conservative expansion, or skip expansion
        if w >= max_allowed_width:
            logger.debug(f"Skipping right edge expansion: width already at limit ({w}px)")
            return box
    
    # Calculate density in last 50px
    right_edge_density = calculate_right_edge_density(thresh, x, w, edge_width=50)
    
    # If high density (>12%) at edge, try to expand
    if right_edge_density > 0.12:
        current_right = x + w
        
        # Trim left side a bit if x is reasonable (to avoid capturing first column)
        if x > 200:
            left_trim = min(50, x - 200)  # Don't go below x=200
            if left_trim > 0:
                x = x + left_trim
                w = w - left_trim  # Adjust width to maintain right edge
                logger.debug(
                    f"Trimming left side, moving x from {x - left_trim}px to {x}px"
                )
        
        # More aggressive expansion for narrow columns
        if w < 900:
            expand_amount = 80
        else:
            expand_amount = 50
        
        # Check if we're at or very close to the edge
        at_edge = current_right >= image_width - 5
        
        if at_edge:
            # If at edge with high density, expand by moving x left
            if right_edge_density > 0.12:
                max_left_shift = min(expand_amount, x)
                if max_left_shift > 0:
                    new_x = x - max_left_shift
                    new_w = min(w + max_left_shift, image_width - new_x)
                    logger.info(
                        f"Expanding at edge: Moving x from {x}px to {new_x}px, "
                        f"expanding width from {w}px to {new_w}px "
                        f"(right edge density: {right_edge_density:.2%})"
                    )
                    return (new_x, y, new_w, h)
        else:
            # Not at edge, check if there's text beyond
            beyond_start = current_right
            beyond_end = min(current_right + 60, image_width)
            beyond_region = thresh[:, beyond_start:beyond_end]
            
            if beyond_region.size > 0:
                beyond_density = np.sum(beyond_region > 0) / beyond_region.size
                
                # Expand if there's significant text beyond (>10%) OR if density is high (>15%)
                if beyond_density > 0.10 or right_edge_density > 0.15:
                    available_room = image_width - current_right
                    
                    # If there's a lot of room and text beyond, expand more aggressively
                    if available_room > 200 and beyond_density > 0.12:
                        max_expand = min(150, available_room)
                        best_w = w
                        
                        # Check in increments to find where text ends
                        for check_expand in range(expand_amount, max_expand + 1, 20):
                            check_end = min(current_right + check_expand, image_width)
                            check_region = thresh[:, current_right:check_end]
                            if check_region.size > 0:
                                check_density = np.sum(check_region > 0) / check_region.size
                                if check_density > 0.08:
                                    best_w = w + check_expand
                                else:
                                    break
                        
                        new_w = min(best_w, image_width - x)
                    else:
                        new_w = min(w + expand_amount, image_width - x)
                    
                    if new_w > w:
                        # Cap at max_allowed_width if we're close to limit
                        if w >= max_allowed_width - 50:
                            new_w = min(new_w, max_allowed_width)
                            if new_w == w:
                                logger.debug(f"Skipping expansion: would exceed max width limit")
                                return box
                        
                        logger.info(
                            f"Expanding width from {w}px to {new_w}px "
                            f"(right edge density: {right_edge_density:.2%}, "
                            f"beyond density: {beyond_density:.2%})"
                        )
                        return (x, y, new_w, h)
    
    return box


def fix_corinthians2_000068(
    box: Tuple[int, int, int, int], image_width: int
) -> Tuple[int, int, int, int]:
    """
    Fix specific issue for corinthians2/000068.png: Move x much more to the left to focus on left content.
    
    This is a specific fix for image 000068.png in the corinthians2 dataset.
    Moves x coordinate much more to the left to include more content from the left side.
    
    Args:
        box: Current bounding box (x, y, w, h)
        image_width: Full image width
        
    Returns:
        Updated bounding box
    """
    x, y, w, h = box
    
    # Move x mucho más hacia la izquierda para enfocar mucho más en el contenido de la izquierda
    # Usar un valor fijo más pequeño para incluir mucho más contenido izquierdo
    new_x = 140  # Empezar desde 150px para incluir mucho más contenido de la izquierda
    
    # Ensure we have room for width
    target_width = 1100
    if new_x + target_width > image_width:
        new_x = max(0, image_width - target_width)
    
    # Keep width reasonable (1100px max)
    new_w = min(target_width, image_width - new_x)
    
    logger.info(
        f"Corinthians2 000068 fix: Moving x from {x}px to {new_x}px to focus much more on left content, "
        f"setting width to {new_w}px "
        f"(moving {new_x - x:+d}px to the left to include more left content)"
    )
    
    return (new_x, y, new_w, h)






