"""
utils/image_io.py
Image loading and saving utilities.
Uses PIL/Pillow for file I/O — the only dependency allowed outside NumPy
(Pillow is the standard for image file access in Python).
"""

import numpy as np
from PIL import Image


def load_image(path: str) -> np.ndarray:
    """
    Load an image from disk and return it as a NumPy uint8 array.

    - RGB images are returned with shape (H, W, 3).
    - RGBA images are converted to RGB (alpha discarded).
    - Grayscale images are returned with shape (H, W).
    - All values are uint8 in [0, 255].

    Parameters
    ----------
    path : str  absolute or relative path to the image file

    Returns
    -------
    np.ndarray  uint8
    """
    pil_img = Image.open(path)

    if pil_img.mode == 'RGBA':
        pil_img = pil_img.convert('RGB')
    elif pil_img.mode == 'L':
        pass  # keep grayscale
    elif pil_img.mode != 'RGB':
        pil_img = pil_img.convert('RGB')

    return np.array(pil_img, dtype=np.uint8)


def save_image(image: np.ndarray, path: str) -> None:
    """
    Save a NumPy uint8 array as an image file.

    The format is inferred from the file extension (PNG, JPEG, BMP, TIFF…).

    Parameters
    ----------
    image : np.ndarray  (H, W) or (H, W, 3), uint8
    path  : str         destination file path
    """
    pil_img = Image.fromarray(image)
    pil_img.save(path)


def numpy_to_qimage(image: np.ndarray):
    """
    Convert a NumPy uint8 array to a PySide6 QImage for display in the GUI.

    Parameters
    ----------
    image : np.ndarray  (H, W) grayscale or (H, W, 3) RGB

    Returns
    -------
    QImage
    """
    from PySide6.QtGui import QImage

    if image.ndim == 2:
        H, W = image.shape
        contiguous = np.ascontiguousarray(image)
        return QImage(contiguous.data, W, H, W, QImage.Format.Format_Grayscale8)
    else:
        H, W, C = image.shape
        if C == 3:
            rgb = np.ascontiguousarray(image)
            return QImage(rgb.data, W, H, W * 3, QImage.Format.Format_RGB888)
        raise ValueError(f"Unsupported image shape: {image.shape}")
