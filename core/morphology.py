
import numpy as np



def square_se(size: int = 3) -> np.ndarray:
    """Return a square (all-ones) structuring element of given size."""
    return np.ones((size, size), dtype=np.uint8)


def _binarize(image: np.ndarray, threshold: int = 128) -> np.ndarray:
    """Ensure the image is a binary uint8 array with values 0 and 1."""
    if image.max() > 1:
        return (image >= threshold).astype(np.uint8)
    return image.astype(np.uint8)


def _to_display(binary: np.ndarray) -> np.ndarray:
    """Convert binary {0,1} back to display {0,255}."""
    return (binary * 255).astype(np.uint8)




def erosion(image: np.ndarray, se: np.ndarray = None) -> np.ndarray:

    if se is None:
        se = square_se(3)
    binary = _binarize(image)
    kH, kW = se.shape
    pH, pW = kH // 2, kW // 2
    padded = np.pad(binary, ((pH, pH), (pW, pW)), mode='constant', constant_values=0)
    H, W = binary.shape
    out = np.zeros((H, W), dtype=np.uint8)

    se_positions = np.argwhere(se == 1)
    for i in range(H):
        for j in range(W):
            fits = all(padded[i + di, j + dj] == 1 for di, dj in se_positions)
            out[i, j] = 1 if fits else 0

    return _to_display(out)



def dilation(image: np.ndarray, se: np.ndarray = None) -> np.ndarray:

    if se is None:
        se = square_se(3)
    binary = _binarize(image)
    kH, kW = se.shape
    pH, pW = kH // 2, kW // 2
    padded = np.pad(binary, ((pH, pH), (pW, pW)), mode='constant', constant_values=0)
    H, W = binary.shape
    out = np.zeros((H, W), dtype=np.uint8)

    se_positions = np.argwhere(se == 1)
    for i in range(H):
        for j in range(W):
            hit = any(padded[i + di, j + dj] == 1 for di, dj in se_positions)
            out[i, j] = 1 if hit else 0

    return _to_display(out)



def opening(image: np.ndarray, se: np.ndarray = None) -> np.ndarray:

    if se is None:
        se = square_se(3)
    eroded = erosion(image, se)
    return dilation(eroded, se)


def closing(image: np.ndarray, se: np.ndarray = None) -> np.ndarray:
    """
    Morphological closing = dilation followed by erosion.
    Fills small holes in binary objects.
    """
    if se is None:
        se = square_se(3)
    dilated = dilation(image, se)
    return erosion(dilated, se)



def _zhang_suen_pass(binary: np.ndarray, pass_num: int) -> tuple[np.ndarray, bool]:

    H, W = binary.shape
    to_delete = np.zeros((H, W), dtype=bool)

    for i in range(1, H - 1):
        for j in range(1, W - 1):
            if binary[i, j] != 1:
                continue
            p2, p3 = binary[i-1, j],   binary[i-1, j+1]
            p4, p5 = binary[i,   j+1], binary[i+1, j+1]
            p6, p7 = binary[i+1, j],   binary[i+1, j-1]
            p8, p9 = binary[i,   j-1], binary[i-1, j-1]

            neighbours = [p2, p3, p4, p5, p6, p7, p8, p9]
            B = sum(neighbours)
            if B < 2 or B > 6:
                continue

            A = sum(1 for k in range(8) if neighbours[k] == 0 and neighbours[(k+1) % 8] == 1)
            if A != 1:
                continue

            if pass_num == 1:
                c = (p2 * p4 * p6 == 0)
                d = (p4 * p6 * p8 == 0)
            else:
                c = (p2 * p4 * p8 == 0)
                d = (p2 * p6 * p8 == 0)

            if c and d:
                to_delete[i, j] = True

    changed = to_delete.any()
    binary[to_delete] = 0
    return binary, changed


def skeleton_zhang_suen(image: np.ndarray) -> np.ndarray:

    binary = _binarize(image).copy()

    changed = True
    while changed:
        binary, c1 = _zhang_suen_pass(binary, pass_num=1)
        binary, c2 = _zhang_suen_pass(binary, pass_num=2)
        changed = c1 or c2

    return _to_display(binary)
