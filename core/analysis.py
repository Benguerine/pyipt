import numpy as np
from core.point_transforms import rgb_to_gray, compute_histogram


def get_histogram_data(image: np.ndarray) -> tuple[np.ndarray, np.ndarray]:

    hist = compute_histogram(image)
    bins = np.arange(256, dtype=np.int32)
    return bins, hist


def get_rgb_histogram_data(image: np.ndarray) -> dict[str, np.ndarray]:

    if image.ndim == 2:
        gray_hist = compute_histogram(image)
        return {'r': gray_hist, 'g': gray_hist, 'b': gray_hist}

    result = {}
    for idx, name in enumerate(['r', 'g', 'b']):
        channel = image[:, :, idx]
        hist = np.zeros(256, dtype=np.int64)
        for val in channel.ravel():
            hist[val] += 1
        result[name] = hist
    return result



def line_profile(image: np.ndarray,
                 x0: int, y0: int,
                 x1: int, y1: int) -> tuple[np.ndarray, np.ndarray]:

    if image.ndim == 3:
        gray = rgb_to_gray(image)
    else:
        gray = image

    num_samples = int(np.hypot(x1 - x0, y1 - y0)) + 1
    if num_samples < 2:
        return np.array([0.0]), np.array([float(gray[y0, x0])])

    cols = np.linspace(x0, x1, num_samples).astype(np.float64)
    rows = np.linspace(y0, y1, num_samples).astype(np.float64)

    H, W = gray.shape
    cols_int = np.clip(np.round(cols).astype(int), 0, W - 1)
    rows_int = np.clip(np.round(rows).astype(int), 0, H - 1)

    intensities = gray[rows_int, cols_int].astype(np.float64)
    positions = np.linspace(0.0, np.hypot(x1 - x0, y1 - y0), num_samples)

    return positions, intensities



def pixel_distance(x0: int, y0: int, x1: int, y1: int) -> float:

    return float(np.hypot(x1 - x0, y1 - y0))
