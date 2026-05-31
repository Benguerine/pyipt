

import numpy as np




def convolve2d(image: np.ndarray, kernel: np.ndarray) -> np.ndarray:

    if image.ndim == 3:
        channels = [convolve2d(image[:, :, c], kernel) for c in range(image.shape[2])]
        return np.stack(channels, axis=2)

    img = image.astype(np.float64)
    kH, kW = kernel.shape
    pH, pW = kH // 2, kW // 2
    padded = np.pad(img, ((pH, pH), (pW, pW)), mode='edge')
    H, W = img.shape
    out = np.zeros((H, W), dtype=np.float64)

    for i in range(H):
        for j in range(W):
            region = padded[i:i + kH, j:j + kW]
            out[i, j] = np.sum(region * kernel)

    return out


def _to_uint8(arr: np.ndarray) -> np.ndarray:
    """Clip to [0, 255] and cast to uint8."""
    return np.clip(arr, 0, 255).astype(np.uint8)




def mean_filter(image: np.ndarray, kernel_size: int = 3) -> np.ndarray:

    k = np.ones((kernel_size, kernel_size), dtype=np.float64) / (kernel_size ** 2)
    return _to_uint8(convolve2d(image, k))


def gaussian_kernel(size: int, sigma: float) -> np.ndarray:

    ax = np.arange(-(size // 2), size // 2 + 1, dtype=np.float64)
    xx, yy = np.meshgrid(ax, ax)
    k = np.exp(-(xx ** 2 + yy ** 2) / (2 * sigma ** 2))
    return k / k.sum()


def gaussian_filter(image: np.ndarray, kernel_size: int = 3, sigma: float = 1.0) -> np.ndarray:

    k = gaussian_kernel(kernel_size, sigma)
    return _to_uint8(convolve2d(image, k))


def median_filter(image: np.ndarray, kernel_size: int = 3) -> np.ndarray:

    if image.ndim == 3:
        channels = [median_filter(image[:, :, c], kernel_size) for c in range(image.shape[2])]
        return np.stack(channels, axis=2)

    img = image.astype(np.float64)
    pH = kernel_size // 2
    padded = np.pad(img, pH, mode='edge')
    H, W = img.shape
    out = np.zeros((H, W), dtype=np.float64)

    for i in range(H):
        for j in range(W):
            region = padded[i:i + kernel_size, j:j + kernel_size]
            out[i, j] = np.median(region)

    return _to_uint8(out)




# Sobel kernels
SOBEL_X = np.array([[-1, 0, 1],
                    [-2, 0, 2],
                    [-1, 0, 1]], dtype=np.float64)

SOBEL_Y = np.array([[-1, -2, -1],
                    [ 0,  0,  0],
                    [ 1,  2,  1]], dtype=np.float64)

# Prewitt kernels
PREWITT_X = np.array([[-1, 0, 1],
                      [-1, 0, 1],
                      [-1, 0, 1]], dtype=np.float64)

PREWITT_Y = np.array([[-1, -1, -1],
                      [ 0,  0,  0],
                      [ 1,  1,  1]], dtype=np.float64)

# Laplacian kernel
LAPLACIAN = np.array([[ 0,  1,  0],
                      [ 1, -4,  1],
                      [ 0,  1,  0]], dtype=np.float64)


def _to_gray_if_needed(image: np.ndarray) -> np.ndarray:
    """Convert to grayscale for edge detectors that need a single channel."""
    if image.ndim == 3:
        from core.point_transforms import rgb_to_gray
        return rgb_to_gray(image)
    return image


def sobel_filter(image: np.ndarray) -> np.ndarray:

    gray = _to_gray_if_needed(image).astype(np.float64)
    gx = convolve2d(gray, SOBEL_X)
    gy = convolve2d(gray, SOBEL_Y)
    magnitude = np.sqrt(gx ** 2 + gy ** 2)
    magnitude = magnitude / magnitude.max() * 255 if magnitude.max() > 0 else magnitude
    return _to_uint8(magnitude)


def prewitt_filter(image: np.ndarray) -> np.ndarray:
    """Prewitt edge detection (same structure as Sobel)."""
    gray = _to_gray_if_needed(image).astype(np.float64)
    gx = convolve2d(gray, PREWITT_X)
    gy = convolve2d(gray, PREWITT_Y)
    magnitude = np.sqrt(gx ** 2 + gy ** 2)
    magnitude = magnitude / magnitude.max() * 255 if magnitude.max() > 0 else magnitude
    return _to_uint8(magnitude)


def laplacian_filter(image: np.ndarray) -> np.ndarray:

    gray = _to_gray_if_needed(image).astype(np.float64)
    lap = convolve2d(gray, LAPLACIAN)
    lap_shifted = lap + 128
    return _to_uint8(lap_shifted)




def unsharp_masking(image: np.ndarray, kernel_size: int = 3,
                    sigma: float = 1.0, amount: float = 1.5) -> np.ndarray:

    blurred = gaussian_filter(image, kernel_size, sigma).astype(np.float64)
    img_f = image.astype(np.float64)
    sharpened = img_f + amount * (img_f - blurred)
    return _to_uint8(sharpened)
