"""Detection methods for Hebrew text column extraction."""

import cv2
import logging
import numpy as np
from typing import Tuple, Optional, List, Callable
from .utils import (
    VERTICAL_WIDTH_RANGE,
    VERTICAL_MIN_HEIGHT,
    expand_vertical_range,
    split_wide_region,
    validate_column_width,
    reject_first_column,
)

logger = logging.getLogger(__name__)


def select_second_column(
    candidates: List[Tuple], sort_key: Callable, get_coords: Callable, image_width: int = None
) -> Optional[Tuple]:
    """
    Select the second column from left from a list of candidates.
    
    Args:
        candidates: List of candidate columns (format depends on detection method)
        sort_key: Function to extract sort key (typically x position)
        get_coords: Function to extract coordinates from candidate
        image_width: Image width for position validation (optional)
        
    Returns:
        Selected column coordinates or None if insufficient candidates
    """
    if len(candidates) < 2:
        logger.debug(
            "Found only %d column(s), need at least 2 to select second. Rejecting.",
            len(candidates),
        )
        return None
    
    # Sort by position (left to right)
    candidates.sort(key=sort_key)
    
    # Select second column from left (index 1)
    selected = candidates[1]
    coords = get_coords(selected)
    
    # Simple validation: if image_width provided, check if selected is too far right
    if image_width:
        x = coords[0] if isinstance(coords, tuple) else (coords[0] if isinstance(coords, (list, np.ndarray)) else coords)
        # Only reject if clearly too far right (>50% of page or >700px) - very conservative
        max_allowed_x = max(int(image_width * 0.50), 700)
        if x > max_allowed_x:
            logger.debug(
                "Index 1 column at x=%d is very far right (max=%d), may be third column.",
                x, max_allowed_x
            )
            # Still return it - let other validation handle it
    
    logger.debug(
        "Found %d columns, selecting second from left (x=%d)",
        len(candidates),
        coords[0] if isinstance(coords, tuple) else coords,
    )
    
    return coords


def find_main_box_from_contours(
    thresh: np.ndarray, margin: int = 20
) -> Optional[Tuple[int, int, int, int]]:
    """
    Find the main vertical column using contour analysis.
    
    Args:
        thresh: Binary image after thresholding.
        margin: Pixels to skip from borders to avoid noise.
        
    Returns:
        Bounding box (x, y, w, h) or None if not found.
    """
    height, width = thresh.shape[:2]
    if width <= 2 * margin or height <= 2 * margin:
        return None
    
    roi = thresh[margin : height - margin, margin : width - margin]
    
    # Morphological operations to connect text
    h_kernel_size = max(3, int(width * 0.015))
    v_kernel_size = max(8, int(height * 0.008))
    kernel_horizontal = cv2.getStructuringElement(cv2.MORPH_RECT, (h_kernel_size, 3))
    kernel_vertical = cv2.getStructuringElement(cv2.MORPH_RECT, (3, v_kernel_size))
    
    dilated_h = cv2.dilate(roi, kernel_horizontal, iterations=2)
    dilated = cv2.dilate(dilated_h, kernel_vertical, iterations=3)
    
    closing_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    dilated = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, closing_kernel, iterations=1)
    
    contours, _ = cv2.findContours(
        dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    
    candidate_boxes: List[Tuple[Tuple[int, int, int, int], float]] = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        x += margin
        y += margin
        
        # Width validation
        max_allowed_width = min(VERTICAL_WIDTH_RANGE[1] + 200, int(width * 0.6))
        width_ok = VERTICAL_WIDTH_RANGE[0] <= w <= max_allowed_width
        # Height validation
        height_ok = h >= max(VERTICAL_MIN_HEIGHT - 200, int(0.4 * height))
        # Position validation - allow wide range to find ALL columns
        center_x = x + w / 2
        x_ok = (
            x >= 0
            and x <= width * 0.8
            and center_x <= width * 0.8
        )
        # Aspect ratio validation
        aspect_ok = h / max(1, w) > 1.5
        
        if width_ok and height_ok and x_ok and aspect_ok:
            # Score by area and centrality
            area = w * h
            ideal_x = width * 0.3
            centrality_score = 1.0 / (1.0 + abs(center_x - ideal_x) / (width * 0.2))
            ideal_width = (VERTICAL_WIDTH_RANGE[0] + VERTICAL_WIDTH_RANGE[1]) / 2
            width_score = 1.0 / (1.0 + abs(w - ideal_width) / 200)
            score = area * centrality_score * width_score
            candidate_boxes.append(((x, y, w, h), score))
    
    if not candidate_boxes:
        return None
    
    # Select second column
    result = select_second_column(
        candidate_boxes,
        sort_key=lambda b: b[0][0],  # Sort by x
        get_coords=lambda b: b[0],  # Extract box coordinates
        image_width=width,
    )
    
    if result is None:
        return None
    
    x, y, w, h = result
    
    # Final validation
    if w < VERTICAL_WIDTH_RANGE[0]:
        logger.debug("Contour detection found box too narrow (w=%d), rejecting.", w)
        return None
    
    if reject_first_column(x, width):
        logger.debug(
            "Contour detection found column starting too close to left edge (x=%d), rejecting.",
            x,
        )
        return None
    
    # Expand vertical range
    box = expand_vertical_range((x, y, w, h), height)
    
    logger.debug(
        "Contour-based column: x=%d, y=%d, w=%d, h=%d",
        box[0],
        box[1],
        box[2],
        box[3],
    )
    return box


def find_main_box_with_hough(
    gray: np.ndarray, thresh: np.ndarray
) -> Optional[Tuple[int, int, int, int]]:
    """
    Fallback detection using Hough lines to locate vertical borders.
    
    Args:
        gray: Grayscale image.
        thresh: Thresholded image.
        
    Returns:
        Bounding box (x, y, w, h) or None.
    """
    height, width = gray.shape[:2]
    
    edges = cv2.Canny(thresh, 50, 150, apertureSize=3)
    
    # Detect vertical lines
    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi / 180,
        threshold=100,
        minLineLength=max(height // 4, 500),
        maxLineGap=50,
    )
    
    if lines is None:
        return None
    
    vertical_xs: List[int] = []
    horizontal_ys: List[int] = []
    
    for line in lines[:, 0, :]:
        x1, y1, x2, y2 = line
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        
        if dx < 15 and dy > 300:  # Vertical lines
            avg_x = (x1 + x2) / 2
            if 0 <= avg_x <= width * 0.8:
                vertical_xs.extend([x1, x2])
        
        if dy < 15 and dx > 300:  # Horizontal lines
            if 0 <= min(y1, y2) <= 700:  # TITLE_SCAN_HEIGHT + 300
                horizontal_ys.extend([y1, y2])
    
    if len(vertical_xs) < 2:
        return None
    
    # Filter and cluster x positions
    filtered_xs = [x for x in vertical_xs if 0 <= x <= width * 0.8]
    if len(filtered_xs) < 2:
        return None
    
    filtered_xs_sorted = sorted(filtered_xs)
    clusters: List[List[int]] = []
    if len(filtered_xs_sorted) == 0:
        return None
    
    current_cluster = [filtered_xs_sorted[0]]
    for x in filtered_xs_sorted[1:]:
        if x - current_cluster[-1] < 50:
            current_cluster.append(x)
        else:
            clusters.append(current_cluster)
            current_cluster = [x]
    clusters.append(current_cluster)
    
    # Retry with tighter clustering if needed
    if len(clusters) < 3 and len(filtered_xs_sorted) > 2:
        clusters = []
        current_cluster = [filtered_xs_sorted[0]]
        for x in filtered_xs_sorted[1:]:
            if x - current_cluster[-1] < 30:
                current_cluster.append(x)
            else:
                clusters.append(current_cluster)
                current_cluster = [x]
        clusters.append(current_cluster)
    
    # Find valid column pairs
    valid_columns: List[Tuple[int, int, float]] = []  # (left_x, right_x, score)
    
    for i in range(len(clusters) - 1):
        j = i + 1
        left_x = min(clusters[i])
        right_x = max(clusters[j])
        w = right_x - left_x
        
        if VERTICAL_WIDTH_RANGE[0] - 300 <= w <= VERTICAL_WIDTH_RANGE[1] + 400:
            center_x = (left_x + right_x) / 2
            ideal_x = width * 0.3
            centrality = 1.0 / (1.0 + abs(center_x - ideal_x) / (width * 0.2))
            
            if VERTICAL_WIDTH_RANGE[0] <= w <= VERTICAL_WIDTH_RANGE[1]:
                width_score = 1.0
            elif VERTICAL_WIDTH_RANGE[0] - 200 <= w < VERTICAL_WIDTH_RANGE[0]:
                width_score = 0.8
            elif VERTICAL_WIDTH_RANGE[1] < w <= VERTICAL_WIDTH_RANGE[1] + 300:
                width_score = 0.8
            else:
                width_score = 0.5
            
            position_penalty = 1.0
            if left_x < 50 and len(clusters) > 3:
                position_penalty = 0.3
            
            score = centrality * width_score * position_penalty
            valid_columns.append((left_x, right_x, score))
    
    if not valid_columns:
        left_x = min(filtered_xs)
        right_x = max(filtered_xs)
    else:
            # Select second column
            result = select_second_column(
                valid_columns,
                sort_key=lambda c: c[0],  # Sort by left_x
                get_coords=lambda c: (c[0], c[1]),  # Extract left_x, right_x
                image_width=width,
            )
            
            if result is None:
                return None
            
            left_x, right_x = result
            
            # Validate and adjust position if needed
            min_x_threshold = max(250, int(width * 0.15))
            if left_x < min_x_threshold:
                logger.debug(
                    "Hough detection: selected column starts too close to left (x=%d), checking for better option.",
                    left_x,
                )
                better_columns = [col for col in valid_columns if col[0] >= min_x_threshold]
                if better_columns:
                    better_columns.sort(key=lambda c: c[0])
                    left_x, right_x, _ = better_columns[0]
                    logger.debug("Hough detection: using better column (x=%d)", left_x)
                else:
                    # Adjust position
                    adjusted_x = max(400, int(width * 0.25))
                    w_current = right_x - left_x
                    w_adjusted = max(800, min(w_current, 1100))
                    right_x = adjusted_x + w_adjusted
                    left_x = adjusted_x
                    logger.debug(
                        "Hough detection: adjusted column position (x=%d, w=%d)", left_x, w_adjusted
                    )
    
    # Ensure reasonable width
    w_detected = right_x - left_x
    if w_detected < VERTICAL_WIDTH_RANGE[0] - 200:
        if left_x + VERTICAL_WIDTH_RANGE[0] <= width * 0.7:
            right_x = left_x + VERTICAL_WIDTH_RANGE[0]
        else:
            if w_detected < 600:
                logger.debug("Hough detection: column too narrow (w=%d), rejecting.", w_detected)
                return None
    
    if right_x - left_x > VERTICAL_WIDTH_RANGE[1] + 300:
        right_x = left_x + VERTICAL_WIDTH_RANGE[1] + 150
    
    # Find vertical extent
    y_min, y_max = 0, height - 1
    if horizontal_ys:
        y_min = max(0, min(horizontal_ys) - 20)
    
    # Refine vertical range
    mask = thresh[:, max(0, left_x - 10) : min(width, right_x + 10)]
    nz = cv2.findNonZero(mask)
    if nz is not None and len(nz) > 0:
        y_coords = nz[:, 0, 1]
        y_min_refined = max(0, int(np.min(y_coords) - 15))
        y_max_refined = min(height - 1, int(np.max(y_coords) + 15))
        y_min = min(y_min, y_min_refined)
        y_max = max(y_max, y_max_refined)
    
    if y_max - y_min < VERTICAL_MIN_HEIGHT - 200:
        y_max = min(height - 1, y_min + VERTICAL_MIN_HEIGHT)
    
    w_calculated = right_x - left_x
    
    # Expand width if too narrow
    if w_calculated < 800 and right_x < width * 0.9:
        max_expand_x = min(width * 0.9, left_x + 1100)
        w_expanded = max_expand_x - left_x
        if w_expanded >= 800:
            w_calculated = min(1100, w_expanded)
            right_x = left_x + w_calculated
    
    box = (
        max(0, left_x),
        max(0, y_min),
        min(width - max(0, left_x), right_x - left_x),
        max(0, y_max - y_min),
    )
    
    # Validate box
    x, y, w, h = box
    center_x = x + w / 2
    
    if center_x > width * 0.5:
        logger.debug("Hough detection found column too far right (center_x=%.1f), rejecting.", center_x)
        return None
    
    min_x_threshold = max(250, int(width * 0.15))
    max_x = max(int(width * 0.35), 600)
    
    if x < min_x_threshold:
        logger.debug(
            "Hough detection found column starting too close to left edge (x=%d), rejecting.",
            x,
        )
        return None
    
    if x > max_x:
        logger.debug("Hough detection found column at invalid x position (x=%d), rejecting.", x)
        return None
    
    if not validate_column_width(w, width):
        logger.debug("Hough detection found unreasonable width (w=%d), rejecting.", w)
        return None
    
    # Expand vertical range
    box = expand_vertical_range(box, height)
    
    # Final width expansion check
    x, y, w, h = box
    if w < 800 and x + w < width * 0.9:
        max_expand_x = min(width * 0.9, x + 1100)
        w_expanded = min(1100, max_expand_x - x)
        if w_expanded >= 800:
            w = w_expanded
    
    box = (x, y, w, h)
    
    logger.debug("Hough-based column: x=%d, y=%d, w=%d, h=%d", box[0], box[1], box[2], box[3])
    return box


def longest_run(array: np.ndarray, ratio: float = 0.02) -> Optional[Tuple[int, int, int]]:
    """Find the longest continuous run in an array above threshold."""
    if array.size == 0:
        return None
    max_val = array.max()
    if max_val == 0:
        return None
    threshold = max(1, ratio * float(max_val))
    indices = np.where(array > threshold)[0]
    if indices.size == 0:
        return None
    splits = np.where(np.diff(indices) > 1)[0]
    starts = [indices[0]]
    ends: List[int] = []
    for idx in splits:
        ends.append(indices[idx])
        starts.append(indices[idx + 1])
    ends.append(indices[-1])
    spans = [(s, e, e - s) for s, e in zip(starts, ends)]
    return max(spans, key=lambda t: t[2])


def find_main_box_from_projection(
    thresh: np.ndarray
) -> Optional[Tuple[int, int, int, int]]:
    """
    Fallback using horizontal/vertical projections to locate dense text bands.
    
    Args:
        thresh: Thresholded binary image.
        
    Returns:
        Bounding box (x, y, w, h) or None.
    """
    height, width = thresh.shape[:2]
    if height == 0 or width == 0:
        return None
    
    sum_x = thresh.sum(axis=0)
    sum_y = thresh.sum(axis=1)
    
    # Find all dense text regions (columns)
    all_columns: List[Tuple[int, int, int, float]] = []  # (x0, x1, w, score)
    search_end = int(width * 0.8)
    search_sum_x = sum_x[:search_end]
    
    x_span = None  # Initialize before loop
    
    # Try multiple thresholds to find all valid columns
    for threshold_ratio in [0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.035, 0.04, 0.045, 0.05]:
        if search_sum_x.size == 0:
            continue
        max_val = search_sum_x.max()
        if max_val == 0:
            continue
        threshold = max(1, threshold_ratio * float(max_val))
        indices = np.where(search_sum_x > threshold)[0]
        if indices.size == 0:
            continue
        
        splits = np.where(np.diff(indices) > 1)[0]
        starts = [indices[0]]
        ends = []
        for idx in splits:
            ends.append(indices[idx])
            starts.append(indices[idx + 1])
        ends.append(indices[-1])
        
        for start, end in zip(starts, ends):
            x0_cand = start
            x1_cand = end + 1
            w_cand = x1_cand - x0_cand
            
            min_col_width = max(300, VERTICAL_WIDTH_RANGE[0] - 400)
            max_col_width = min(VERTICAL_WIDTH_RANGE[1] + 500, int(width * 0.75))
            if min_col_width <= w_cand <= max_col_width:
                density = search_sum_x[x0_cand:x1_cand].sum()
                ideal_width = (VERTICAL_WIDTH_RANGE[0] + VERTICAL_WIDTH_RANGE[1]) / 2
                width_score = 1.0 / (1.0 + abs(w_cand - ideal_width) / 200)
                position_score = 1.0 if x0_cand > 50 else 0.7
                score = density * width_score * position_score
                all_columns.append((x0_cand, x1_cand, w_cand, score))
        
        # Remove overlapping columns
        filtered_columns = []
        if all_columns:
            all_columns.sort(key=lambda c: c[0])
            for col in all_columns:
                x0, x1, w, score = col
                overlap = False
                for existing in filtered_columns:
                    ex0, ex1 = existing[0], existing[1]
                    overlap_size = max(0, min(x1, ex1) - max(x0, ex0))
                    if overlap_size > min(w, ex1 - ex0) * 0.3:
                        overlap = True
                        if score > existing[3]:
                            filtered_columns.remove(existing)
                            filtered_columns.append(col)
                        break
                if not overlap:
                    filtered_columns.append(col)
        
        if filtered_columns:
            filtered_columns.sort(key=lambda c: c[0])
            
            # Select second column or handle single wide column
            if len(filtered_columns) < 2:
                logger.debug(
                    "Projection detection: found only %d column(s), need at least 2.",
                    len(filtered_columns),
                )
                if len(filtered_columns) == 1:
                    x0_single, x1_single, w_single, _ = filtered_columns[0]
                    if w_single > 1200:
                        logger.debug(
                            "Single column is very wide (w=%d), attempting to split.",
                            w_single,
                        )
                        split_x, w_second = split_wide_region(x0_single, x1_single, width)
                        x_span = (split_x, x1_single, w_second)
                        logger.debug(
                            "Projection detection: split wide column (x=%d, w=%d)",
                            split_x,
                            w_second,
                        )
                    else:
                        logger.debug("Single column is not wide enough to split. Rejecting.")
                        x_span = None
                else:
                    x_span = None
            else:
                # Use improved second column selection
                result = select_second_column(
                    filtered_columns,
                    sort_key=lambda c: c[0],  # Sort by x0
                    get_coords=lambda c: (c[0], c[1], c[2]),  # Extract (x0, x1, w)
                    image_width=width,
                )
                if result:
                    x0, x1, w = result if len(result) == 3 else (result[0], result[1], result[1] - result[0])
                    logger.debug(
                        "Projection detection: found %d columns, selected second (x=%d)",
                        len(filtered_columns),
                        x0,
                    )
                    x_span = (x0, x1, w)
                else:
                    # Fallback to index 1
                    x0, x1, w, _ = filtered_columns[1]
                    logger.debug(
                        "Projection detection: found %d columns, using index 1 (x=%d)",
                        len(filtered_columns),
                        x0,
                    )
                    x_span = (x0, x1, w)
            
            if x_span is not None:
                break
    
    # Fallback: sliding window approach
    if x_span is None:
        target_width = (VERTICAL_WIDTH_RANGE[0] + VERTICAL_WIDTH_RANGE[1]) // 2
        best_start = 0
        best_density = 0
        best_width = target_width
        
        for test_width in range(
            VERTICAL_WIDTH_RANGE[0], min(VERTICAL_WIDTH_RANGE[1] + 200, search_end), 25
        ):
            for start_idx in range(0, max(1, len(search_sum_x) - test_width + 1)):
                end_idx = start_idx + test_width
                if end_idx > len(search_sum_x):
                    continue
                window_density = search_sum_x[start_idx:end_idx].sum()
                left_bonus = 1.0 / (1.0 + start_idx / 150.0)
                width_bonus = 1.0 / (1.0 + abs(test_width - target_width) / 150.0)
                score = window_density * left_bonus * width_bonus
                if score > best_density:
                    best_density = score
                    best_start = start_idx
                    best_width = test_width
        
        if best_density > 0:
            x_span = (best_start, best_start + best_width, best_width)
        else:
            x_span = longest_run(search_sum_x, 0.02)
            if x_span is None:
                return None
            x0_long, x1_long, w_long = x_span
            if w_long > 1200:
                logger.debug("Longest run is very wide (w=%d), splitting.", w_long)
                split_x, w_second = split_wide_region(x0_long, x1_long, width)
                x_span = (split_x, x1_long, w_second)
    
    y_span = longest_run(sum_y, 0.02)
    if y_span is None:
        return None
    
    x0, x1, w_span = x_span if len(x_span) == 3 else (x_span[0], x_span[1], x_span[1] - x_span[0])
    y0, y1, _ = y_span
    
    w = int(x1 - x0)
    h = int(y1 - y0)
    if w <= 0 or h <= 0:
        return None
    
    # Split if too wide
    if w > 1200 or (w > 900 and x0 < 100):
        logger.debug("Detected region is too wide (w=%d, x=%d), splitting.", w, x0)
        split_x, w_second = split_wide_region(x0, x1, width)
        x0 = split_x
        w = min(w_second, 1100)
        x1 = x0 + w
    
    # Expand width if too narrow
    if w < VERTICAL_WIDTH_RANGE[0]:
        max_expand = min(VERTICAL_WIDTH_RANGE[0], search_end - x0)
        if max_expand >= VERTICAL_WIDTH_RANGE[0]:
            w = VERTICAL_WIDTH_RANGE[0]
            x1 = x0 + w
        else:
            if x0 > 100:  # VERTICAL_X_RANGE[0]
                new_x0 = max(0, 50)  # VERTICAL_X_RANGE[0] - 50
                if new_x0 + VERTICAL_WIDTH_RANGE[0] <= search_end:
                    x0 = new_x0
                    w = VERTICAL_WIDTH_RANGE[0]
                    x1 = x0 + w
                else:
                    logger.debug("Projection detection: cannot achieve minimum width, rejecting.")
                    return None
            else:
                logger.debug("Projection detection: width too narrow, rejecting.")
                return None
    
    # Expand vertical range
    box = expand_vertical_range((x0, y0, w, h), height)
    x0, y0, w, h = box
    
    # Handle overly wide regions
    max_allowed_width = min(VERTICAL_WIDTH_RANGE[1] + 200, int(width * 0.6))
    if w > max_allowed_width:
        search_end = min(int(width * 0.5), len(sum_x))
        search_sum_x = sum_x[:search_end]
        
        if search_sum_x.size > 0:
            target_width = (VERTICAL_WIDTH_RANGE[0] + VERTICAL_WIDTH_RANGE[1]) // 2
            best_start = 0
            best_density = 0
            best_width = target_width
            
            for test_width in range(
                VERTICAL_WIDTH_RANGE[0], min(max_allowed_width + 1, search_end), 50
            ):
                for start_idx in range(0, max(1, len(search_sum_x) - test_width + 1)):
                    end_idx = start_idx + test_width
                    if end_idx > len(search_sum_x):
                        continue
                    window_density = search_sum_x[start_idx:end_idx].sum()
                    left_bonus = 1.0 / (1.0 + start_idx / 100.0)
                    score = window_density * left_bonus
                    if score > best_density:
                        best_density = score
                        best_start = start_idx
                        best_width = test_width
            
            x0 = best_start
            x1 = best_start + best_width
            w = best_width
            
            if w < VERTICAL_WIDTH_RANGE[0]:
                    if x0 + VERTICAL_WIDTH_RANGE[0] <= search_end:
                        w = VERTICAL_WIDTH_RANGE[0]
                        x1 = x0 + w
                    else:
                        logger.debug("Projection detection: cannot achieve minimum width, rejecting.")
                        return None
    
    # Final width validation
    w = min(w, max_allowed_width)
    if w < VERTICAL_WIDTH_RANGE[0]:
        if x0 + VERTICAL_WIDTH_RANGE[0] <= width * 0.5:
            w = VERTICAL_WIDTH_RANGE[0]
            x1 = x0 + w
        else:
            logger.debug("Projection detection: cannot achieve minimum width, rejecting.")
            return None
    
    # Ensure coordinates are within bounds
    x0 = max(50, int(x0))
    y0 = max(0, int(y0))
    
    if x0 + w > width:
        x0 = max(0, width - w)
        w = width - x0
    
    if y0 + h > height:
        if h <= height:
            y0 = max(0, height - h)
        else:
            h = height - y0
    
    w = min(w, width - x0)
    h = min(h, height - y0)
    
    box = (x0, y0, w, h)
    
    # Final validation
    x, y, w, h = box
    center_x = x + w / 2
    
    max_allowed_width = min(VERTICAL_WIDTH_RANGE[1] + 200, int(width * 0.6))
    if w > max_allowed_width:
        logger.debug(
            "Projection-based detection found box too wide (w=%d), rejecting.", w
        )
        return None
    
    if center_x > width * 0.5:
        logger.debug("Projection-based detection found column too far right, rejecting.")
        return None
    
    if x > width * 0.4:
        logger.debug("Projection-based detection found column starting too far right, rejecting.")
        return None
    
    if w < VERTICAL_WIDTH_RANGE[0]:
        logger.debug("Projection-based detection found box too narrow (w=%d), rejecting.", w)
        return None
    
    if reject_first_column(x, width):
        logger.debug(
            "Projection-based detection found column starting too close to left edge, rejecting."
        )
        return None
    
    logger.debug(
        "Projection-based column: x=%d, y=%d, w=%d, h=%d",
        box[0],
        box[1],
        box[2],
        box[3],
    )
    return box
