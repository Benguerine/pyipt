import numpy as np


def adjust_contrast_brightness(image: np.ndarray, alpha: float, beta: float) -> np.ndarray:

    result = alpha * image.astype(np.float64) + beta
    return np.clip(result, 0, 255).astype(np.uint8)


def histogram_equalization(image: np.ndarray) -> np.ndarray:
    

    if image.ndim != 2:
        raise ValueError("histogram_equalization expects a 2-D grayscale image.")

    hist = np.zeros(256, dtype=np.int64)
    for val in image.ravel():
        hist[val] += 1

    cdf = np.cumsum(hist)
    cdf_min = cdf[cdf > 0][0]
    total_pixels = image.size

    lut = np.zeros(256, dtype=np.uint8)
    denom = total_pixels - cdf_min
    if denom == 0:
        return image.copy()

    for k in range(256):
        lut[k] = round((cdf[k] - cdf_min) / denom * 255)

    return lut[image]


def otsu_threshold(image: np.ndarray) -> tuple[np.ndarray, int]:
    
    if image.ndim != 2:
        raise ValueError("otsu_threshold expects a 2-D grayscale image.")

    hist = np.zeros(256, dtype=np.float64)
    total = image.size
    for val in image.ravel():
        hist[val] += 1
    hist /= total  # normalise to probabilities

    best_thresh = 0
    best_var = -1.0

    for t in range(256):
        w0 = hist[:t+1].sum()
        w1 = hist[t+1:].sum()
        if w0 == 0 or w1 == 0:
            continue
        mu0 = (np.arange(t+1) * hist[:t+1]).sum() / w0
        mu1 = (np.arange(t+1, 256) * hist[t+1:]).sum() / w1
        between_var = w0 * w1 * (mu0 - mu1) ** 2
        if between_var > best_var:
            best_var = between_var
            best_thresh = t

    binary = np.where(image > best_thresh, np.uint8(255), np.uint8(0))
    return binary, best_thresh


def compute_histogram(image: np.ndarray) -> np.ndarray:

    if image.ndim == 3:
        gray = rgb_to_gray(image)
    else:
        gray = image
    hist = np.zeros(256, dtype=np.int64)
    for val in gray.ravel():
        hist[val] += 1
    return hist


def rgb_to_gray(image: np.ndarray) -> np.ndarray:

    if image.ndim == 2:
        return image
    r, g, b = image[:, :, 0], image[:, :, 1], image[:, :, 2]
    gray = 0.299 * r.astype(np.float64) + \
           0.587 * g.astype(np.float64) + \
           0.114 * b.astype(np.float64)
    return np.clip(gray, 0, 255).astype(np.uint8)
