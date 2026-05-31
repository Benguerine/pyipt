
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSlider, QPushButton,
    QDoubleSpinBox, QSpinBox, QComboBox, QFrame, QScrollArea
)
from PySide6.QtCore import Signal, Qt


class ParamPanel(QWidget):
    

    
    apply_requested = Signal(str, dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(230)
        self.setStyleSheet("background-color: #1a202c; color: #e2e8f0;")

        self._tool_id: str = ""
        self._widgets: dict = {}

        outer = QVBoxLayout(self)
        outer.setContentsMargins(6, 6, 6, 6)
        outer.setSpacing(4)

        self._title_label = QLabel("Paramètres")
        self._title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title_label.setStyleSheet(
            "font-size: 14px; font-weight: bold; padding: 8px 0;"
        )
        outer.addWidget(self._title_label)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #4a5568;")
        outer.addWidget(sep)

        # Scrollable content area
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet("QScrollArea { border: none; background: #1a202c; }")

        self._content = QWidget()
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(4, 4, 4, 4)
        self._content_layout.setSpacing(10)
        self._content_layout.addStretch()

        self._scroll.setWidget(self._content)
        outer.addWidget(self._scroll, stretch=1)

        self._apply_btn = QPushButton("▶  Appliquer")
        self._apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #3182ce;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover { background-color: #2b6cb0; }
            QPushButton:pressed { background-color: #2c5282; }
        """)
        self._apply_btn.clicked.connect(self._on_apply)
        outer.addWidget(self._apply_btn)

        self._show_placeholder()

   

    def set_tool(self, tool_id: str):
        self._tool_id = tool_id
        self._clear_content()
        self._widgets = {}
        builder = _PARAM_BUILDERS.get(tool_id)
        if builder:
            self._title_label.setText(f"⚙  {_TOOL_LABELS.get(tool_id, tool_id)}")
            builder(self._content_layout, self._widgets)
        else:
            self._title_label.setText("Paramètres")
            self._show_placeholder()
        self._content_layout.addStretch()

    

    def _clear_content(self):
        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _show_placeholder(self):
        lbl = QLabel("Sélectionnez un outil\ndans la barre latérale.")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("color: #718096; font-size: 12px;")
        lbl.setWordWrap(True)
        self._content_layout.addWidget(lbl)

    def _on_apply(self):
        if not self._tool_id:
            return
        params = {}
        for key, widget in self._widgets.items():
            if isinstance(widget, (QSlider, QSpinBox)):
                params[key] = widget.value()
            elif isinstance(widget, QDoubleSpinBox):
                params[key] = widget.value()
            elif isinstance(widget, QComboBox):
                params[key] = int(widget.currentText().split("×")[0])
        self.apply_requested.emit(self._tool_id, params)




def _label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet("color: #a0aec0; font-size: 11px;")
    return lbl


def _kernel_combo(layout, widgets, key="kernel_size"):
    layout.addWidget(_label("Taille du noyau :"))
    combo = QComboBox()
    combo.addItems(["3×3", "5×5", "7×7"])
    combo.setStyleSheet(
        "background-color: #2d3748; color: #e2e8f0; padding: 4px; border-radius: 3px;"
    )
    layout.addWidget(combo)
    widgets[key] = combo


def _sigma_spin(layout, widgets, key="sigma"):
    layout.addWidget(_label("Sigma (écart-type) :"))
    spin = QDoubleSpinBox()
    spin.setRange(0.1, 10.0)
    spin.setSingleStep(0.1)
    spin.setValue(1.0)
    spin.setStyleSheet(
        "background-color: #2d3748; color: #e2e8f0; padding: 4px; border-radius: 3px;"
    )
    layout.addWidget(spin)
    widgets[key] = spin


def _se_size_combo(layout, widgets):
    layout.addWidget(_label("Taille de l'élément structurant :"))
    combo = QComboBox()
    combo.addItems(["3×3", "5×5", "7×7"])
    combo.setStyleSheet(
        "background-color: #2d3748; color: #e2e8f0; padding: 4px; border-radius: 3px;"
    )
    layout.addWidget(combo)
    widgets["se_size"] = combo




def _build_contrast_brightness(layout, widgets):
    layout.addWidget(_label("Alpha (contraste) :"))
    alpha = QDoubleSpinBox()
    alpha.setRange(0.0, 5.0)
    alpha.setSingleStep(0.1)
    alpha.setValue(1.0)
    alpha.setStyleSheet(
        "background-color: #2d3748; color: #e2e8f0; padding: 4px; border-radius: 3px;"
    )
    layout.addWidget(alpha)
    widgets["alpha"] = alpha

    layout.addWidget(_label("Beta (luminosité) :"))
    beta = QSpinBox()
    beta.setRange(-255, 255)
    beta.setValue(0)
    beta.setStyleSheet(
        "background-color: #2d3748; color: #e2e8f0; padding: 4px; border-radius: 3px;"
    )
    layout.addWidget(beta)
    widgets["beta"] = beta


def _build_mean_filter(layout, widgets):
    _kernel_combo(layout, widgets)


def _build_gaussian_filter(layout, widgets):
    _kernel_combo(layout, widgets)
    _sigma_spin(layout, widgets)


def _build_median_filter(layout, widgets):
    _kernel_combo(layout, widgets)


def _build_unsharp(layout, widgets):
    _kernel_combo(layout, widgets)
    _sigma_spin(layout, widgets)
    layout.addWidget(_label("Intensité (amount) :"))
    amount = QDoubleSpinBox()
    amount.setRange(0.1, 5.0)
    amount.setSingleStep(0.1)
    amount.setValue(1.5)
    amount.setStyleSheet(
        "background-color: #2d3748; color: #e2e8f0; padding: 4px; border-radius: 3px;"
    )
    layout.addWidget(amount)
    widgets["amount"] = amount


def _build_morphology(layout, widgets):
    _se_size_combo(layout, widgets)


def _build_no_params(layout, widgets):
    lbl = QLabel("Aucun paramètre.\nCliquez 'Appliquer'.")
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setStyleSheet("color: #718096; font-size: 12px;")
    lbl.setWordWrap(True)
    layout.addWidget(lbl)




_PARAM_BUILDERS = {
    "contrast_brightness": _build_contrast_brightness,
    "hist_equalisation":   _build_no_params,
    "otsu_threshold":      _build_no_params,
    "mean_filter":         _build_mean_filter,
    "gaussian_filter":     _build_gaussian_filter,
    "median_filter":       _build_median_filter,
    "sobel_filter":        _build_no_params,
    "prewitt_filter":      _build_no_params,
    "laplacian_filter":    _build_no_params,
    "unsharp_masking":     _build_unsharp,
    "erosion":             _build_morphology,
    "dilation":            _build_morphology,
    "opening":             _build_morphology,
    "closing":             _build_morphology,
    "skeleton":            _build_no_params,
    "line_profile":        _build_no_params,
    "measure_distance":    _build_no_params,
}

_TOOL_LABELS = {
    "contrast_brightness": "Contraste / Luminosité",
    "hist_equalisation":   "Égalisation d'histogramme",
    "otsu_threshold":      "Seuillage d'Otsu",
    "mean_filter":         "Filtre Moyenneur",
    "gaussian_filter":     "Filtre Gaussien",
    "median_filter":       "Filtre Médian",
    "sobel_filter":        "Sobel",
    "prewitt_filter":      "Prewitt",
    "laplacian_filter":    "Laplacien",
    "unsharp_masking":     "Unsharp Masking",
    "erosion":             "Érosion",
    "dilation":            "Dilatation",
    "opening":             "Ouverture",
    "closing":             "Fermeture",
    "skeleton":            "Squelette (Zhang-Suen)",
    "line_profile":        "Profil de ligne",
    "measure_distance":    "Mesure de distance",
}
