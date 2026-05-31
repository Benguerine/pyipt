
import numpy as np
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QSplitter,
    QLabel, QFileDialog, QMessageBox, QStatusBar
)
from PySide6.QtGui import QAction, QPixmap
from PySide6.QtCore import Qt

from ui.sidebar import Sidebar
from ui.image_canvas import ImageCanvas
from ui.param_panel import ParamPanel
from ui.histogram_widget import HistogramWidget
from utils.image_io import load_image, save_image, numpy_to_qimage


class MainWindow(QMainWindow):
    """Main application window — the "Studio"."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Custom-IPT — Image Processing Studio")
        self.resize(1280, 800)

        self._original_image: np.ndarray | None = None   # image loaded from disk
        self._current_image: np.ndarray | None = None    # image after last operation

        self._build_menu()
        self._build_central_widget()
        self._build_status_bar()

  

    def _build_menu(self):
        menu_bar = self.menuBar()
        fichier_menu = menu_bar.addMenu("Fichier")

        action_open = QAction("Ouvrir…", self)
        action_open.setShortcut("Ctrl+O")
        action_open.triggered.connect(self._on_open)

        action_save = QAction("Enregistrer sous…", self)
        action_save.setShortcut("Ctrl+Shift+S")
        action_save.triggered.connect(self._on_save)

        action_reset = QAction("Reset", self)
        action_reset.setShortcut("Ctrl+R")
        action_reset.triggered.connect(self._on_reset)

        action_quit = QAction("Quitter", self)
        action_quit.setShortcut("Ctrl+Q")
        action_quit.triggered.connect(self.close)

        fichier_menu.addAction(action_open)
        fichier_menu.addAction(action_save)
        fichier_menu.addSeparator()
        fichier_menu.addAction(action_reset)
        fichier_menu.addSeparator()
        fichier_menu.addAction(action_quit)

    def _build_central_widget(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left sidebar — tool categories
        self.sidebar = Sidebar()
        self.sidebar.tool_selected.connect(self._on_tool_selected)
        splitter.addWidget(self.sidebar)

        # Centre — image canvas + histogram below
        centre_widget = QWidget()
        centre_layout = __import__('PySide6.QtWidgets', fromlist=['QVBoxLayout']).QVBoxLayout(centre_widget)
        centre_layout.setContentsMargins(4, 4, 4, 4)

        self.canvas = ImageCanvas()
        self.canvas.line_drawn.connect(self._on_line_drawn)
        self.canvas.points_picked.connect(self._on_points_picked)
        centre_layout.addWidget(self.canvas, stretch=3)

        self.histogram_widget = HistogramWidget()
        centre_layout.addWidget(self.histogram_widget, stretch=1)

        splitter.addWidget(centre_widget)

        # Right — parameter panel
        self.param_panel = ParamPanel()
        self.param_panel.apply_requested.connect(self._on_apply)
        splitter.addWidget(self.param_panel)

        splitter.setStretchFactor(0, 0)   
        splitter.setStretchFactor(1, 3)   
        splitter.setStretchFactor(2, 0)   

        layout.addWidget(splitter)

    def _build_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Bienvenue dans Custom-IPT. Ouvrez une image pour commencer.")

    

    def _on_open(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Ouvrir une image", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff *.tif)"
        )
        if not path:
            return
        try:
            img = load_image(path)
            self._original_image = img
            self._current_image = img.copy()
            self._display_image(img)
            self._update_histogram(img)
            self.status_bar.showMessage(
                f"Image chargée : {path}  —  "
                f"{img.shape[1]}×{img.shape[0]} pixels"
            )
        except Exception as exc:
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir l'image :\n{exc}")

    def _on_save(self):
        if self._current_image is None:
            QMessageBox.information(self, "Aucune image", "Aucune image à enregistrer.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer sous", "",
            "PNG (*.png);;JPEG (*.jpg *.jpeg);;BMP (*.bmp)"
        )
        if not path:
            return
        try:
            save_image(self._current_image, path)
            self.status_bar.showMessage(f"Image enregistrée : {path}")
        except Exception as exc:
            QMessageBox.critical(self, "Erreur", f"Impossible d'enregistrer :\n{exc}")

    def _on_reset(self):
        if self._original_image is None:
            return
        self._current_image = self._original_image.copy()
        self._display_image(self._current_image)
        self._update_histogram(self._current_image)
        self.status_bar.showMessage("Image réinitialisée.")

   

    def _on_tool_selected(self, tool_id: str):
        """Called when the user clicks a tool button in the sidebar."""
        self.param_panel.set_tool(tool_id)
        # Set canvas interaction mode for analysis tools
        if tool_id == "line_profile":
            self.canvas.set_mode("draw_line")
            self.status_bar.showMessage("Tracez une ligne sur l'image pour voir le profil d'intensité.")
        elif tool_id == "measure_distance":
            self.canvas.set_mode("pick_two_points")
            self.status_bar.showMessage("Cliquez deux points pour mesurer la distance en pixels.")
        else:
            self.canvas.set_mode("normal")

    def _on_apply(self, tool_id: str, params: dict):
        """Called when the user clicks 'Appliquer' in the parameter panel."""
        if self._current_image is None:
            QMessageBox.information(self, "Aucune image", "Ouvrez d'abord une image.")
            return
        try:
            result = self._run_tool(tool_id, params)
            if result is not None:
                self._current_image = result
                self._display_image(result)
                self._update_histogram(result)
                self.status_bar.showMessage(f"Opération '{tool_id}' appliquée avec succès.")
        except Exception as exc:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du traitement :\n{exc}")

    def _run_tool(self, tool_id: str, params: dict) -> np.ndarray | None:
        """Dispatch tool_id to the correct core function."""
        img = self._current_image

        
        if tool_id == "contrast_brightness":
            from core.point_transforms import adjust_contrast_brightness
            return adjust_contrast_brightness(img, params["alpha"], params["beta"])

        if tool_id == "hist_equalisation":
            from core.point_transforms import histogram_equalization, rgb_to_gray
            gray = rgb_to_gray(img) if img.ndim == 3 else img
            return histogram_equalization(gray)

        if tool_id == "otsu_threshold":
            from core.point_transforms import otsu_threshold, rgb_to_gray
            gray = rgb_to_gray(img) if img.ndim == 3 else img
            binary, thresh = otsu_threshold(gray)
            self.status_bar.showMessage(f"Seuil d'Otsu calculé : {thresh}")
            return binary

        
        if tool_id == "mean_filter":
            from core.spatial_filters import mean_filter
            return mean_filter(img, params["kernel_size"])

        if tool_id == "gaussian_filter":
            from core.spatial_filters import gaussian_filter
            return gaussian_filter(img, params["kernel_size"], params.get("sigma", 1.0))

        if tool_id == "median_filter":
            from core.spatial_filters import median_filter
            return median_filter(img, params["kernel_size"])

        if tool_id == "sobel_filter":
            from core.spatial_filters import sobel_filter
            return sobel_filter(img)

        if tool_id == "prewitt_filter":
            from core.spatial_filters import prewitt_filter
            return prewitt_filter(img)

        if tool_id == "laplacian_filter":
            from core.spatial_filters import laplacian_filter
            return laplacian_filter(img)

        if tool_id == "unsharp_masking":
            from core.spatial_filters import unsharp_masking
            return unsharp_masking(img, params["kernel_size"],
                                   params.get("sigma", 1.0),
                                   params.get("amount", 1.5))

        
        if tool_id == "erosion":
            from core.morphology import erosion, square_se
            from core.point_transforms import rgb_to_gray
            gray = rgb_to_gray(img) if img.ndim == 3 else img
            return erosion(gray, square_se(params.get("se_size", 3)))

        if tool_id == "dilation":
            from core.morphology import dilation, square_se
            from core.point_transforms import rgb_to_gray
            gray = rgb_to_gray(img) if img.ndim == 3 else img
            return dilation(gray, square_se(params.get("se_size", 3)))

        if tool_id == "opening":
            from core.morphology import opening, square_se
            from core.point_transforms import rgb_to_gray
            gray = rgb_to_gray(img) if img.ndim == 3 else img
            return opening(gray, square_se(params.get("se_size", 3)))

        if tool_id == "closing":
            from core.morphology import closing, square_se
            from core.point_transforms import rgb_to_gray
            gray = rgb_to_gray(img) if img.ndim == 3 else img
            return closing(gray, square_se(params.get("se_size", 3)))

        if tool_id == "skeleton":
            from core.morphology import skeleton_zhang_suen
            from core.point_transforms import rgb_to_gray
            gray = rgb_to_gray(img) if img.ndim == 3 else img
            return skeleton_zhang_suen(gray)

        return None

   

    def _on_line_drawn(self, x0, y0, x1, y1):
        """Called when the user draws a line on the canvas (line profile tool)."""
        if self._current_image is None:
            return
        from core.analysis import line_profile
        positions, intensities = line_profile(self._current_image, x0, y0, x1, y1)
        self.histogram_widget.plot_line_profile(positions, intensities)
        self.canvas.set_mode("normal")
        self.status_bar.showMessage(
            f"Profil de ligne : {len(positions)} points, "
            f"intensité min={intensities.min():.0f}  max={intensities.max():.0f}"
        )

    def _on_points_picked(self, x0, y0, x1, y1):
        """Called when the user picks two points (distance tool)."""
        from core.analysis import pixel_distance
        dist = pixel_distance(x0, y0, x1, y1)
        self.status_bar.showMessage(
            f"Distance entre ({x0},{y0}) et ({x1},{y1}) = {dist:.2f} pixels"
        )
        self.canvas.set_mode("normal")

    

    def _display_image(self, image: np.ndarray):
        qimg = numpy_to_qimage(image)
        self.canvas.set_image(QPixmap.fromImage(qimg))

    def _update_histogram(self, image: np.ndarray):
        from core.analysis import get_histogram_data
        bins, counts = get_histogram_data(image)
        self.histogram_widget.plot_histogram(bins, counts)
