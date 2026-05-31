from PySide6.QtWidgets import QLabel, QSizePolicy, QScrollArea, QWidget, QVBoxLayout
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor, QCursor
from PySide6.QtCore import Signal, Qt, QPoint, QRect


class _Canvas(QLabel):
    """Internal label that handles mouse events and draws overlays."""

    line_drawn = Signal(int, int, int, int)         # x0,y0,x1,y1 in image coords
    points_picked = Signal(int, int, int, int)       # x0,y0,x1,y1 in image coords

    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)

        self._mode = "normal"
        self._start: QPoint | None = None
        self._end:   QPoint | None = None
        self._base_pixmap: QPixmap | None = None

  

    def set_pixmap(self, pixmap: QPixmap):
        self._base_pixmap = pixmap
        self._start = None
        self._end = None
        self._render()

    def set_mode(self, mode: str):
        self._mode = mode
        self._start = None
        self._end = None
        if mode != "normal":
            self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
        else:
            self.unsetCursor()
        if self._base_pixmap:
            self._render()

   

    def mousePressEvent(self, event):
        if self._mode in ("draw_line", "pick_two_points"):
            self._start = event.position().toPoint()
            self._end = None

    def mouseMoveEvent(self, event):
        if self._mode in ("draw_line", "pick_two_points") and self._start:
            self._end = event.position().toPoint()
            self._render()

    def mouseReleaseEvent(self, event):
        if self._mode in ("draw_line",) and self._start:
            self._end = event.position().toPoint()
            self._render()
            ix0, iy0 = self._widget_to_image(self._start)
            ix1, iy1 = self._widget_to_image(self._end)
            self.line_drawn.emit(ix0, iy0, ix1, iy1)

        elif self._mode == "pick_two_points":
            if self._start is None:
                self._start = event.position().toPoint()
            else:
                self._end = event.position().toPoint()
                self._render()
                ix0, iy0 = self._widget_to_image(self._start)
                ix1, iy1 = self._widget_to_image(self._end)
                self.points_picked.emit(ix0, iy0, ix1, iy1)
                self._start = None
                self._end = None

   

    def _render(self):
        if self._base_pixmap is None:
            return
        scaled = self._base_pixmap.scaled(
            self.width(), self.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        if self._start and self._end:
            copy = scaled.copy()
            painter = QPainter(copy)
            pen = QPen(QColor(0, 200, 100), 2, Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            painter.drawLine(self._start, self._end)
            # Draw endpoint circles
            painter.setBrush(QColor(0, 200, 100))
            painter.drawEllipse(self._start, 4, 4)
            painter.drawEllipse(self._end, 4, 4)
            painter.end()
            super().setPixmap(copy)
        else:
            super().setPixmap(scaled)

    def resizeEvent(self, event):
        self._render()
        super().resizeEvent(event)

    def _widget_to_image(self, point: QPoint) -> tuple[int, int]:
        """Convert widget coordinates → image pixel coordinates."""
        if self._base_pixmap is None:
            return point.x(), point.y()
        iw, ih = self._base_pixmap.width(), self._base_pixmap.height()
        ww, wh = self.width(), self.height()
        scale = min(ww / iw, wh / ih)
        # offset to center the scaled image
        ox = (ww - iw * scale) / 2
        oy = (wh - ih * scale) / 2
        ix = int((point.x() - ox) / scale)
        iy = int((point.y() - oy) / scale)
        ix = max(0, min(iw - 1, ix))
        iy = max(0, min(ih - 1, iy))
        return ix, iy


class ImageCanvas(QWidget):
    """Public-facing canvas widget wrapping _Canvas in a scroll area."""

    line_drawn    = Signal(int, int, int, int)
    points_picked = Signal(int, int, int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._canvas = _Canvas()
        self._canvas.line_drawn.connect(self.line_drawn)
        self._canvas.points_picked.connect(self.points_picked)

        self._scroll = QScrollArea()
        self._scroll.setWidget(self._canvas)
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet("background-color: #2d3748;")
        layout.addWidget(self._scroll)

    def set_image(self, pixmap: QPixmap):
        self._canvas.set_pixmap(pixmap)
        # Resize canvas to fill scroll area
        self._canvas.setMinimumSize(pixmap.size())

    def set_mode(self, mode: str):
        self._canvas.set_mode(mode)
