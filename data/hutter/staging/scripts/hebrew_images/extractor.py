"""Main Hebrew text extractor class and processing logic."""

import cv2
import logging
import numpy as np
from pathlib import Path
from tqdm import tqdm
from typing import Tuple, Optional

from .detection import (
    find_main_box_from_contours,
    find_main_box_with_hough,
    find_main_box_from_projection,
)
from .utils import (
    get_fallback_coords,
    VERTICAL_WIDTH_RANGE,
    TITLE_SCAN_HEIGHT,
    TITLE_MIN_HEIGHT,
    TITLE_MAX_HEIGHT,
    split_wide_region,
    validate_column_width,
    reject_first_column,
)
from .validation import (
    fix_wrong_column_detection,
    fix_right_edge_expansion,
    fix_corinthians2_000068,
)
from .logger import ImageLogger, log_summary

logger = logging.getLogger(__name__)


class HebrewTextExtractor:
    """Class to handle dynamic Hebrew text extraction from images."""

    def __init__(self, input_dir: Path, output_dir: Path):
        """
        Initialize the extractor.

        Args:
            input_dir: Directory containing input images
            output_dir: Directory to save cropped images
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        # Special handling for john1: skip 000006.png and 000008.png,
        # and from 000009.png onwards, process only odd-numbered images
        self.is_john1 = "john1" in str(input_dir).lower()
        
        # Specific problematic images that need special left edge fix
        self.problematic_images = {
            'matthew': ['000006.png', '000012.png', '000240.png', '000274.png'],
            'mark': ['000012.png', '000024.png', '000026.png', '000068.png', '000098.png', 
                    '000128.png', '000154.png', '000160.png', '000162.png', '000166.png', 
                    '000178.png', '000180.png', '000182.png'],
            'luke': ['000010.png', '000042.png', '000102.png', '000130.png', '000226.png', 
                    '000256.png', '000258.png'],
            'john': ['000142.png'],
            'acts': ['000010.png', '000258.png', '000268.png', '000280.png'],
            'revelation': ['000122.png'],
            'corinthians1': ['000016.png', '000030.png', '000118.png'],
            'galatians': ['000004.png'],
            'peter2': ['000002.png'],
            'timothy1': ['000020.png'],
            'timothy2': ['000006.png']
        }

    def _is_problematic_image(self, image_path: Path) -> bool:
        """
        Check if an image is in the list of problematic images that need special fix.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            True if image needs special fix, False otherwise
        """
        image_name = image_path.name
        book_name = self.input_dir.name.lower()
        
        if book_name in self.problematic_images:
            return image_name in self.problematic_images[book_name]
        
        return False

    def _is_corinthians2_000068(self, image_path: Path) -> bool:
        """
        Check if this is the specific corinthians2/000068.png image that needs special fix.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            True if this is corinthians2/000068.png, False otherwise
        """
        is_corinthians2 = "corinthians2" in str(self.input_dir).lower()
        return is_corinthians2 and image_path.name == "000068.png"

    def _split_wide_region(self, x: int, w: int, width: int) -> Tuple[int, int]:
        """
        Split a wide region to extract the second column.
        
        Args:
            x: Current x position
            w: Current width
            width: Image width
            
        Returns:
            Tuple of (new_x, new_w) for second column
        """
        if x < 150:
            new_x = max(400, int(width * 0.25))
        else:
            new_x = max(x + 400, int(x + w * 0.3))
        new_w = min(1100, width - new_x)
        return new_x, new_w

    def _adjust_height(self, h: int, height: int) -> int:
        """
        Adjust height to cover most of the page (85-95%).
        
        Args:
            h: Current height
            height: Image height
            
        Returns:
            Adjusted height
        """
        min_height = int(height * 0.85)
        return max(min_height, min(h, height))

    def _preprocess(self, image: cv2.Mat) -> Tuple[np.ndarray, np.ndarray]:
        """
        Convert image to grayscale and adaptive-thresholded binary mask.

        Args:
            image: Source BGR image.

        Returns:
            Tuple of (gray image, thresholded image).
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.adaptiveThreshold(
            blurred,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            31,
            12,
        )
        return gray, thresh

    def _check_text_beyond_left(self, thresh: np.ndarray, x: int, check_width: int = 100) -> Tuple[bool, float]:
        """
        Check if there's significant text beyond the left edge of the box.
        
        Args:
            thresh: Thresholded binary image
            x: Current x position
            check_width: Width of region to check before x
            
        Returns:
            Tuple of (has_text, density)
        """
        height = thresh.shape[0]
        check_start = max(0, x - check_width)
        check_end = x
        
        if check_end <= check_start:
            return False, 0.0
        
        beyond_region = thresh[:, check_start:check_end]
        if beyond_region.size == 0:
            return False, 0.0
        
        density = np.sum(beyond_region > 0) / beyond_region.size
        has_text = density > 0.05
        
        return has_text, density

    def _check_text_beyond_bottom(self, thresh: np.ndarray, box: Tuple[int, int, int, int], check_height: int = 100) -> Tuple[bool, float]:
        """
        Check if there's significant text beyond the bottom edge of the box.
        
        Args:
            thresh: Thresholded binary image
            box: Current bounding box (x, y, w, h)
            check_height: Height of region to check after bottom
            
        Returns:
            Tuple of (has_text, density)
        """
        x, y, w, h = box
        height, width = thresh.shape[:2]
        
        check_start = min(y + h, height - 1)
        check_end = min(y + h + check_height, height)
        
        if check_end <= check_start:
            return False, 0.0
        
        beyond_region = thresh[check_start:check_end, x:x+w]
        if beyond_region.size == 0:
            return False, 0.0
        
        density = np.sum(beyond_region > 0) / beyond_region.size
        has_text = density > 0.05
        
        return has_text, density

    def _check_first_column_density(self, thresh: np.ndarray, x_start: int, check_width: int = 200) -> Tuple[bool, float, float]:
        """
        Check if there's significant text density that might be first column.
        
        Args:
            thresh: Thresholded binary image
            x_start: X position to check from
            check_width: Width of region to check before x_start
            
        Returns:
            Tuple of (is_first_column, density, uniformity)
        """
        height = thresh.shape[0]
        check_start = max(0, x_start - check_width)
        check_end = x_start
        
        if check_end <= check_start:
            return False, 0.0, 0.0
        
        region = thresh[:, check_start:check_end]
        if region.size == 0:
            return False, 0.0, 0.0
        
        density = np.sum(region > 0) / region.size
        
        # Check uniformity (column structure)
        vertical_projection = region.sum(axis=1)
        if vertical_projection.max() > 0:
            mean_density = vertical_projection.mean()
            std_density = vertical_projection.std()
            uniformity = 1 - (std_density / (mean_density + 1))
        else:
            uniformity = 0.0
        
        # More sensitive detection: density >15% OR (density >10% AND high uniformity)
        has_first_column = density > 0.15 or (density > 0.10 and uniformity > 0.3)
        
        return has_first_column, density, uniformity

    def _check_central_column_completeness(self, thresh: np.ndarray, box: Tuple[int, int, int, int]) -> bool:
        """
        Check if the central column is captured completely.
        
        Args:
            thresh: Thresholded binary image
            box: Bounding box (x, y, w, h)
            
        Returns:
            True if column appears complete (text starts close to left edge of box)
        """
        x, y, w, h = box
        height, width = thresh.shape[:2]
        
        # Check first 30px of the box for text density
        roi_x = max(0, x)
        roi_y = max(0, y)
        roi_w = min(30, w, width - roi_x)
        roi_h = min(h, height - roi_y)
        
        if roi_w <= 0 or roi_h <= 0:
            return False
        
        left_edge_region = thresh[roi_y:roi_y+roi_h, roi_x:roi_x+roi_w]
        if left_edge_region.size == 0:
            return False
        
        density = np.sum(left_edge_region > 0) / left_edge_region.size
        
        # If high density at left edge of box, column is likely complete
        return density > 0.15

    def _analyze_box_for_first_column_specific(
        self, thresh: np.ndarray, box: Tuple[int, int, int, int]
    ) -> Tuple[bool, int, float]:
        """
        Analyze if box contains first column content (for specific problematic images).
        
        Returns:
            (has_first_col, recommended_left_x, left_region_density)
        """
        x, y, w, h = box
        height, width = thresh.shape[:2]
        
        # Heuristic: If x < 250px and width > 1000px, likely capturing first column
        if x < 250 and w > 1000:
            left_region = thresh[y:y+h, x:min(x+150, x+w)]
            if left_region.size > 0:
                left_density = np.sum(left_region > 0) / left_region.size
                if left_density > 0.15:
                    # Find Hebrew column start (typically 300-450px)
                    for check_x in range(300, min(450, width - 800), 20):
                        check_region = thresh[y:y+h, check_x:check_x+100]
                        if check_region.size > 0:
                            check_density = np.sum(check_region > 0) / check_region.size
                            if 0.10 < check_density < 0.30:  # Hebrew column density
                                return True, check_x, left_density
                    return True, 350, left_density
        
        # Check high density in left region
        check_width = min(150, w)
        left_region = thresh[y:y+h, x:x+check_width]
        if left_region.size > 0:
            density = np.sum(left_region > 0) / left_region.size
            if density > 0.25:
                before_start = max(0, x - 100)
                before_region = thresh[y:y+h, before_start:x]
                if before_region.size > 0:
                    before_density = np.sum(before_region > 0) / before_region.size
                    if before_density > 0.10:
                        for check_x in range(max(300, x), min(x + 200, width), 20):
                            check_region = thresh[y:y+h, check_x:check_x+80]
                            if check_region.size > 0:
                                check_density = np.sum(check_region > 0) / check_region.size
                                if 0.12 < check_density < 0.30:
                                    return True, check_x, density
                        return True, max(300, x + 100), density
        
        return False, x, 0.0

    def _find_text_left_boundary_specific(
        self, thresh: np.ndarray, current_x: int, search_width: int = 150
    ) -> int:
        """
        Find the actual left boundary of Hebrew text column (for specific problematic images).
        
        Args:
            thresh: Thresholded binary image
            current_x: Current x position
            search_width: Width to search before current_x
            
        Returns:
            Safe x position
        """
        height = thresh.shape[0]
        search_start = max(0, current_x - search_width)
        search_end = current_x
        
        if search_end <= search_start:
            return current_x
        
        search_region = thresh[:, search_start:search_end]
        if search_region.size == 0:
            return current_x
        
        projection = search_region.sum(axis=0)
        if projection.size == 0 or projection.max() == 0:
            return current_x
        
        # Find where Hebrew text starts
        threshold = projection.max() * 0.15
        text_start_idx = None
        for i in range(len(projection) - 1, -1, -1):
            if projection[i] > threshold:
                text_start_idx = i
                break
        
        if text_start_idx is None:
            return current_x
        
        text_start_abs = search_start + text_start_idx
        return max(0, text_start_abs - 30)

    def _apply_specific_problematic_fix(
        self, box: Tuple[int, int, int, int], thresh: np.ndarray, image_shape: Tuple[int, int, int]
    ) -> Tuple[int, int, int, int]:
        """
        Apply specific fix for problematic images that have left edge issues.
        
        This fix:
        1. Detects if original box contains first column
        2. Adjusts x position to avoid first column
        3. Finds actual Hebrew text boundary
        4. Applies adaptive bottom padding
        
        Args:
            box: Current bounding box (x, y, w, h)
            thresh: Thresholded binary image
            image_shape: Image shape (height, width, channels)
            
        Returns:
            Updated bounding box
        """
        x, y, w, h = box
        img_h, img_w = image_shape[:2]
        
        # Check if original box contains first column
        has_first_col, adjusted_x, left_density = self._analyze_box_for_first_column_specific(
            thresh, (x, y, w, h)
        )
        
        if has_first_col:
            logger.debug(
                f"First column detected in problematic image (density={left_density:.2%}), "
                f"adjusting x from {x} to {adjusted_x}"
            )
            x = adjusted_x
            w = min(img_w - x, w - (adjusted_x - x))  # Adjust width (move right, reduce width)
        
        # Find actual Hebrew text boundary
        safe_x = self._find_text_left_boundary_specific(thresh, x, search_width=150)
        expand_amount = x - safe_x
        
        # Limit expansion to avoid capturing first column
        max_expansion = 80
        if expand_amount > max_expansion:
            safe_x = max(0, x - max_expansion)
            expand_amount = max_expansion
        
        # Apply bottom padding (same as conservative fix)
        has_text_beyond_bottom, density_beyond_bottom = self._check_text_beyond_bottom(
            thresh, (x, y, w, h), check_height=100
        )
        
        if has_text_beyond_bottom:
            if density_beyond_bottom > 0.15:
                bottom_expand = 120
            elif density_beyond_bottom > 0.10:
                bottom_expand = 100
            else:
                bottom_expand = 80
            new_h = min(img_h - y, h + bottom_expand)
        else:
            new_h = min(img_h - y, h + 100)
        
        new_w = min(img_w - safe_x, w + expand_amount)
        
        return (safe_x, y, new_w, new_h)

    def _apply_specific_fixes(
        self, box: Tuple[int, int, int, int], thresh: np.ndarray, image_shape: Tuple[int, int, int], image_path: Path
    ) -> Tuple[int, int, int, int]:
        """
        Apply specific fixes for special cases.
        Executes BEFORE general adjustments to preserve original coordinates.
        
        Args:
            box: Current bounding box (x, y, w, h)
            thresh: Thresholded binary image
            image_shape: Image shape (height, width, channels)
            image_path: Path to the image file
            
        Returns:
            Updated bounding box
        """
        x, y, w, h = box
        img_h, img_w = image_shape[:2]
        
        # Fix for corinthians2/000068.png
        if self._is_corinthians2_000068(image_path):
            return fix_corinthians2_000068(box, img_w)
        
        # Fix for problematic images (must run BEFORE split check)
        if self._is_problematic_image(image_path):
            logger.debug(f"Applying specific fix for problematic image: {image_path.name}")
            return self._apply_specific_problematic_fix(box, thresh, image_shape)
        
        return box

    def _apply_general_adjustments(
        self, box: Tuple[int, int, int, int], thresh: np.ndarray, image_shape: Tuple[int, int, int], image_path: Path
    ) -> Tuple[int, int, int, int]:
        """
        Apply general adjustments (split check, padding, etc.).
        Executes AFTER specific fixes.
        
        Args:
            box: Current bounding box (x, y, w, h)
            thresh: Thresholded binary image
            image_shape: Image shape (height, width, channels)
            image_path: Path to the image file
            
        Returns:
            Updated bounding box
        """
        x, y, w, h = box
        img_h, img_w = image_shape[:2]
        
        # Validate and clamp basic coordinates
        x = max(0, min(x, img_w - 1))
        y = 0  # CRITICAL: Always start from top to preserve enumeration
        w = max(1, min(w, img_w - x))
        
        # Split check (only if NOT problematic - problematic images already fixed)
        if not self._is_problematic_image(image_path):
            if w > 900 or (w > 800 and x < 150):
                logger.debug(
                    "Final box is too wide (w=%d, x=%d), splitting.",
                    w,
                    x,
                )
                x, w = self._split_wide_region(x, w, img_w)
        
        # Adjust height
        h = self._adjust_height(h, img_h)
        
        # Apply adaptive padding
        if self._is_problematic_image(image_path):
            # Problematic images already have their specific fix applied
            # Just ensure coordinates are valid
            pass
        else:
            # Apply conservative adaptive padding for normal images
            box = self._apply_conservative_adaptive_padding((x, y, w, h), thresh, image_shape)
            x, y, w, h = box
        
        # Apply standard right padding (40px) to ensure adequate margin
        w = min(img_w - x, w + 40)
        
        return (x, y, w, h)

    def _apply_conservative_adaptive_padding(
        self, box: Tuple[int, int, int, int], thresh: np.ndarray, image_shape: Tuple[int, int, int]
    ) -> Tuple[int, int, int, int]:
        """
        Apply conservative adaptive padding to avoid cutting text and minimize first column capture.
        
        This function:
        1. Applies minimal left expansion (max 50px) only when needed
        2. Checks if central column is complete before expanding
        3. Detects first column and avoids capturing it
        4. Applies adaptive bottom padding when text extends beyond
        
        Args:
            box: Current bounding box (x, y, w, h)
            thresh: Thresholded binary image
            image_shape: Image shape (height, width, channels)
            
        Returns:
            Updated bounding box with conservative adaptive padding
        """
        x, y, w, h = box
        img_h, img_w = image_shape[:2]
        
        # Check if central column is complete
        column_complete = self._check_central_column_completeness(thresh, (x, y, w, h))
        
        # LEFT EDGE: Very conservative expansion
        has_text_beyond, density_beyond = self._check_text_beyond_left(thresh, x, check_width=100)
        
        if has_text_beyond and not column_complete:
            # Only expand if column incomplete AND text beyond
            if density_beyond > 0.15:
                expand_amount = 50  # Max expansion
            elif density_beyond > 0.10:
                expand_amount = 40
            else:
                expand_amount = 30
            
            # Check for first column with improved detection
            potential_x = max(0, x - expand_amount)
            has_first_col, first_col_density, uniformity = self._check_first_column_density(
                thresh, potential_x, check_width=200
            )
            
            if has_first_col:
                # First column detected - minimal expansion
                expand_amount = 20
                potential_x = max(0, x - expand_amount)
                has_first_col, _, _ = self._check_first_column_density(
                    thresh, potential_x, check_width=200
                )
                if has_first_col:
                    new_x = x  # Don't expand
                    new_w = w
                else:
                    new_x = potential_x
                    new_w = min(img_w - new_x, w + expand_amount)
            else:
                new_x = potential_x
                new_w = min(img_w - new_x, w + expand_amount)
        elif has_text_beyond and column_complete:
            # Column complete - minimal expansion only
            expand_amount = 20
            potential_x = max(0, x - expand_amount)
            has_first_col, _, _ = self._check_first_column_density(thresh, potential_x, check_width=200)
            if not has_first_col:
                new_x = potential_x
                new_w = min(img_w - new_x, w + expand_amount)
            else:
                new_x = x  # Don't expand
                new_w = w
        else:
            # Minimal padding
            expand_amount = 20
            potential_x = max(0, x - expand_amount)
            has_first_col, _, _ = self._check_first_column_density(thresh, potential_x, check_width=200)
            if not has_first_col:
                new_x = potential_x
                new_w = min(img_w - new_x, w + expand_amount)
            else:
                new_x = x
                new_w = w
        
        # BOTTOM EDGE: Adaptive padding
        has_text_beyond_bottom, density_beyond_bottom = self._check_text_beyond_bottom(
            thresh, (x, y, w, h), check_height=100
        )
        
        if has_text_beyond_bottom:
            # Calculate how much to expand based on density
            if density_beyond_bottom > 0.15:
                bottom_expand = 120  # More aggressive for high density
            elif density_beyond_bottom > 0.10:
                bottom_expand = 100
            else:
                bottom_expand = 80
            new_h = min(img_h - y, h + bottom_expand)
        else:
            # Standard bottom padding
            new_h = min(img_h - y, h + 100)
        
        return (new_x, y, new_w, new_h)

    def _is_box_reasonable(
        self, box: Tuple[int, int, int, int], image_shape: Tuple[int, int, int]
    ) -> bool:
        """
        Validate whether a detected box matches expected geometry.

        Args:
            box: Bounding box tuple (x, y, w, h).
            image_shape: Shape of the original image.

        Returns:
            True if the box fits expected constraints, False otherwise.
        """
        x, y, w, h = box
        img_h, img_w = image_shape[:2]

        max_allowed_width = min(VERTICAL_WIDTH_RANGE[1] + 200, int(img_w * 0.6))
        min_allowed_width = max(600, VERTICAL_WIDTH_RANGE[0] - 200)
        width_ok = min_allowed_width <= w <= max_allowed_width

        min_height_required = max(int(img_h * 0.4), 1500)
        height_ok = h >= min_height_required

        within_bounds = (
            x >= 0 and y >= 0 and x + w <= img_w and y + h <= img_h
        )

        center_x = x + w / 2
        max_x_percent = int(img_w * 0.35)
        max_x_absolute = 600
        max_x = max(max_x_percent, max_x_absolute)
        position_ok = (
            center_x <= img_w * 0.50
            and x <= max_x
            and x >= 50
        )

        return width_ok and height_ok and within_bounds and position_ok

    def _detect_title_region(
        self, thresh: np.ndarray, box: Tuple[int, int, int, int]
    ) -> Optional[Tuple[int, int, int, int]]:
        """
        Detect the horizontal title region near the top of the main column.

        Args:
            thresh: Thresholded binary image.
            box: Bounding box (x, y, w, h) of the main column.

        Returns:
            Bounding box of the detected title or None.
        """
        x, y, w, h = box
        if h <= 0 or w <= 0:
            return None

        scan_height = min(TITLE_SCAN_HEIGHT, h)
        roi = thresh[y : y + scan_height, x : x + w]
        if roi.size == 0:
            return None

        # Emphasize horizontal structures
        horiz_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 3))
        closed = cv2.morphologyEx(roi, cv2.MORPH_CLOSE, horiz_kernel, iterations=2)

        contours, _ = cv2.findContours(
            closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        candidates: list = []
        for cnt in contours:
            tx, ty, tw, th = cv2.boundingRect(cnt)
            width_ok = tw >= int(0.5 * w)
            height_ok = TITLE_MIN_HEIGHT <= th <= TITLE_MAX_HEIGHT
            top_ok = ty <= scan_height
            if width_ok and height_ok and top_ok:
                candidates.append((tx, ty, tw, th))

        if not candidates:
            return None

        title_box = min(candidates, key=lambda b: b[1])  # top-most
        abs_box = (x + title_box[0], y + title_box[1], title_box[2], title_box[3])
        logger.info(
            "Detected title region: x=%d, y=%d, w=%d, h=%d",
            abs_box[0],
            abs_box[1],
            abs_box[2],
            abs_box[3],
        )
        return abs_box

    def detect_hebrew_column(self, image: cv2.Mat, img_logger: Optional[ImageLogger] = None) -> Tuple[Tuple[int, int, int, int], str]:
        """
        Dynamically detect the Hebrew text column using contours and line detection.

        Args:
            image: OpenCV image matrix
            img_logger: Optional ImageLogger for organized logging

        Returns:
            Tuple of ((x, y, w, h), method_used) where method_used is the detection method name
        """
        height, width = image.shape[:2]
        if height == 0 or width == 0:
            fallback = get_fallback_coords(width, height)
            return (
                (
                    fallback["x"],
                    fallback["y"],
                    fallback["w"],
                    fallback["h"],
                ),
                "fallback",
            )

        gray, thresh = self._preprocess(image)

        # Try detection methods in order
        box = find_main_box_from_contours(thresh)
        method_used = "contour"
        if box is None:
            logger.debug("Contour detection failed; trying Hough lines.")
            box = find_main_box_with_hough(gray, thresh)
            if box is not None:
                method_used = "hough"
        if box is None:
            logger.debug("Hough detection failed; trying projection-based search.")
            box = find_main_box_from_projection(thresh)
            if box is not None:
                method_used = "projection"

        if box is None:
            logger.debug("All detection methods failed; using fallback coordinates.")
            fallback = get_fallback_coords(width, height)
            return (
                (
                    fallback["x"],
                    fallback["y"],
                    fallback["w"],
                    fallback["h"],
                ),
                "fallback",
            )

        # Validate and refine if needed
        if not self._is_box_reasonable(box, image.shape):
            logger.debug("Detected box out of expected range; refining with projection.")
            refined_box = find_main_box_from_projection(thresh)
            if refined_box is not None and self._is_box_reasonable(
                refined_box, image.shape
            ):
                box = refined_box
                method_used = "projection"

        # Additional validation: ensure x is reasonable
        x, y, w, h = box
        max_x_percent = int(width * 0.35)
        max_x_absolute = 600
        max_x = max(max_x_percent, max_x_absolute)
        if x > max_x:
            logger.debug("Box starts too far right (x=%d), trying projection.", x)
            refined_box = find_main_box_from_projection(thresh)
            if refined_box is not None and self._is_box_reasonable(
                refined_box, image.shape
            ):
                box = refined_box
                method_used = "projection"
            else:
                if img_logger:
                    img_logger.log_warning("All detection methods failed validation")
                fallback = get_fallback_coords(width, height)
                return (
                    (
                        fallback["x"],
                        fallback["y"],
                        fallback["w"],
                        fallback["h"],
                    ),
                    "fallback",
                )

        if not self._is_box_reasonable(box, image.shape):
            if img_logger:
                img_logger.log_warning("Detected box failed validation")
            fallback = get_fallback_coords(width, height)
            return (
                (
                    fallback["x"],
                    fallback["y"],
                    fallback["w"],
                    fallback["h"],
                ),
                "fallback",
            )

        # Detect and include title region
        title_box = self._detect_title_region(thresh, box)
        if title_box:
            tx, ty, tw, th = title_box
            x, y, w, h = box
            new_x = min(x, tx)
            # CRITICAL: Always keep y=0 to preserve enumeration/title at top
            new_y = 0
            new_w = max(x + w, tx + tw) - new_x
            new_h = max(y + h, ty + th) - new_y
            box = (new_x, new_y, new_w, new_h)
        else:
            # CRITICAL: Ensure y=0 even if no title detected
            x, y, w, h = box
            box = (x, 0, w, h)

        # Final check: split if too wide or starts too close to left
        x, y, w, h = box
        if w > 900 or (w > 800 and x < 150):
            logger.debug(
                "Final box is too wide (w=%d, x=%d), splitting to get second column.",
                w,
                x,
            )
            if x < 150:
                new_x = max(400, int(width * 0.25))
            else:
                new_x = max(x + 400, int(x + w * 0.3))
            x = new_x
            w = min(1100, width - x)
            box = (x, y, w, h)
            if img_logger:
                img_logger.log_info(f"Split wide region: x={x}, w={w}")

        # Apply general fixes for common problems
        # Fix 1: Wrong column detection (column too far right)
        box = fix_wrong_column_detection(thresh, box, width)
        
        # Fix 2: Right edge expansion (text too close to edge)
        box = fix_right_edge_expansion(thresh, box, width)

        logger.debug(
            "Final bounding box: x=%d, y=%d, w=%d, h=%d", box[0], box[1], box[2], box[3]
        )
        return box, method_used

    def _is_image_blank(self, image: np.ndarray) -> bool:
        """
        Check if an image is blank or has very little content.

        Args:
            image: BGR image

        Returns:
            True if image appears to be blank
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        std = np.std(gray)
        return std < 15

    def _should_process_image(self, image_number: int, img_logger: Optional[ImageLogger] = None) -> Tuple[bool, Optional[str]]:
        """
        Determine if an image should be processed based on special rules.

        Args:
            image_number: Image number from filename
            img_logger: Optional ImageLogger for organized logging

        Returns:
            Tuple of (should_process, skip_reason)
        """
        # Special handling for john1
        if self.is_john1:
            # Skip specific images
            if image_number in [6, 8]:
                reason = "not part of manuscript for john1"
                if img_logger:
                    img_logger.log_info(f"Skipped: {reason}")
                return False, reason
            # From 000009.png onwards, process only odd-numbered images
            if image_number >= 9:
                if image_number % 2 == 0:
                    reason = "john1: only odd from 000009 onwards"
                    if img_logger:
                        img_logger.log_info(f"Skipped: {reason}")
                    return False, reason
            # For images before 000009, process only even-numbered
            elif image_number % 2 == 1:
                reason = "typically no Hebrew text"
                if img_logger:
                    img_logger.log_info(f"Skipped: {reason}")
                return False, reason
        else:
            # Normal behavior: skip odd-numbered images
            if image_number % 2 == 1:
                reason = "typically no Hebrew text"
                if img_logger:
                    img_logger.log_info(f"Skipped: {reason}")
                return False, reason

        return True, None

    def process_single_image(self, image_path: Path, use_logger: bool = True) -> bool:
        """
        Process a single image: load, detect, crop, and save.

        Args:
            image_path: Path to the input image
            use_logger: Whether to use ImageLogger for organized output

        Returns:
            True if successful, False otherwise
        """
        image_logger = None
        if use_logger:
            image_logger = ImageLogger(image_path.name, logger)
            image_logger.__enter__()

        try:
            image_number = int(image_path.stem)

            # Check if image should be processed
            should_process, skip_reason = self._should_process_image(image_number, image_logger)
            if not should_process:
                if image_logger:
                    image_logger.__exit__(None, None, None)
                return False

            # Read the image
            image = cv2.imread(str(image_path))
            if image is None:
                logger.error(f"Failed to load image: {image_path}")
                if image_logger:
                    image_logger.log_warning("Failed to load image")
                    image_logger.__exit__(None, None, None)
                return False

            # Check if image is blank
            if self._is_image_blank(image):
                if image_logger:
                    image_logger.log_info("Skipped: blank image")
                    image_logger.__exit__(None, None, None)
                return False

            height, width = image.shape[:2]

            # Detect bounding box
            (x, y, w, h), method_used = self.detect_hebrew_column(image, image_logger)

            # Preprocess once (for both specific fixes and general adjustments)
            gray, thresh = self._preprocess(image)

            # Apply specific fixes FIRST (BEFORE split check)
            # This preserves original coordinates for problematic images
            (x, y, w, h) = self._apply_specific_fixes(
                (x, y, w, h), thresh, image.shape, image_path
            )

            # Apply general adjustments AFTER specific fixes
            # This includes split check (only for non-problematic images), height adjustment, and padding
            (x, y, w, h) = self._apply_general_adjustments(
                (x, y, w, h), thresh, image.shape, image_path
            )

            # Crop
            cropped = image[y : y + h, x : x + w]

            # Create output path
            output_filename = image_path.name
            output_path = self.output_dir / output_filename
            self.output_dir.mkdir(parents=True, exist_ok=True)

            # Save
            success = cv2.imwrite(str(output_path), cropped)
            if not success:
                logger.error(f"Failed to save cropped image: {output_path}")
                if image_logger:
                    image_logger.log_warning("Failed to save cropped image")
                    image_logger.__exit__(None, None, None)
                return False

            if image_logger:
                image_logger.set_success(box=(x, y, w, h), method=method_used)
                image_logger.__exit__(None, None, None)
            else:
                logger.info(
                    f"Saved cropped image to {output_path} (Box: {x},{y},{w},{h})"
                )
            return True

        except Exception as e:
            logger.error(f"Error processing {image_path}: {e}")
            if image_logger:
                image_logger.log_warning(f"Error: {e}")
                image_logger.__exit__(None, None, None)
            return False

    def process_all_images(self) -> Tuple[int, int]:
        """
        Process all images in the input directory.

        Returns:
            Tuple of (successful_count, total_count)
        """
        if not self.input_dir.exists():
            logger.error(f"Input directory not found: {self.input_dir}")
            return 0, 0

        image_files = []
        for ext in ["*.png", "*.jpg", "*.jpeg", "*.tiff", "*.bmp"]:
            image_files.extend(self.input_dir.glob(ext))
        # Case insensitive search
        for ext in ["*.PNG", "*.JPG", "*.JPEG"]:
            image_files.extend(self.input_dir.glob(ext))

        image_files = sorted(list(set(image_files)))  # Remove duplicates and sort

        if not image_files:
            logger.warning(f"No image files found in {self.input_dir}")
            return 0, 0

        logger.info(f"Found {len(image_files)} images to process in {self.input_dir}")

        successful = 0
        skipped = 0
        with tqdm(total=len(image_files), desc="Processing images", ncols=80) as pbar:
            for image_path in image_files:
                result = self.process_single_image(image_path, use_logger=True)
                if result:
                    successful += 1
                else:
                    # Check if it was skipped (not an error)
                    try:
                        image_number = int(image_path.stem)
                        should_process, _ = self._should_process_image(image_number)
                        if not should_process:
                            skipped += 1
                        elif self._is_image_blank(cv2.imread(str(image_path))):
                            skipped += 1
                    except:
                        pass
                pbar.update(1)

        log_summary(logger, successful, len(image_files), skipped)
        return successful, len(image_files)
