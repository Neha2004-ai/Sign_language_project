import cv2
import numpy as np
from typing import Tuple, Optional

class ImagePreprocessor:
    """
    Image preprocessing and normalization for raw webcam frames and dataset images.
    """
    
    @staticmethod
    def resize_and_normalize(image: np.ndarray, target_size: Tuple[int, int] = (128, 128)) -> np.ndarray:
        """Resizes image to target resolution and normalizes pixel values to [0, 1]."""
        resized = cv2.resize(image, target_size, interpolation=cv2.INTER_AREA)
        normalized = resized.astype(np.float32) / 255.0
        return normalized

    @staticmethod
    def apply_skin_mask(image: np.ndarray) -> np.ndarray:
        """Segments skin color in HSV color space to suppress background clutter."""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        mask = cv2.inRange(hsv, lower_skin, upper_skin)
        result = cv2.bitwise_and(image, image, mask=mask)
        return result
