
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,
    QLabel, QScrollArea, QFrame, QSizePolicy
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont


class CategorySection(QWidget):
   

    tool_selected = Signal(str)

    def __init__(self, title: str, tools: list[tuple[str, str]], parent=None):
      
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 4)
        layout.setSpacing(2)

        # Category header button (acts as toggle)
        self._collapsed = False
        header = QPushButton(f"▾  {title}")
        header.setCheckable(False)
        header.setStyleSheet("""
            QPushButton {
                background-color: #2d3748;
                color: #e2e8f0;
                font-weight: bold;
                font-size: 12px;
                padding: 6px 8px;
                text-align: left;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #4a5568; }
        """)
        header.clicked.connect(self._toggle)
        layout.addWidget(header)
        self._header = header

        # Container for tool buttons
        self._body = QWidget()
        body_layout = QVBoxLayout(self._body)
        body_layout.setContentsMargins(8, 0, 0, 0)
        body_layout.setSpacing(2)

        for tool_id, label in tools:
            btn = QPushButton(label)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1a202c;
                    color: #a0aec0;
                    font-size: 11px;
                    padding: 5px 8px;
                    text-align: left;
                    border: none;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #2d3748;
                    color: #e2e8f0;
                }
                QPushButton:pressed { background-color: #4299e1; color: white; }
            """)
            btn.clicked.connect(lambda checked, tid=tool_id: self.tool_selected.emit(tid))
            body_layout.addWidget(btn)

        layout.addWidget(self._body)

    def _toggle(self):
        self._collapsed = not self._collapsed
        self._body.setVisible(not self._collapsed)
        symbol = "▸" if self._collapsed else "▾"
        text = self._header.text()
        self._header.setText(symbol + text[1:])


class Sidebar(QWidget):
    """Left panel containing all tool category sections."""

    tool_selected = Signal(str)

    
    CATEGORIES = [
        ("Point-to-point", [
            ("contrast_brightness", "Contraste / Luminosité"),
            ("hist_equalisation",   "Égalisation d'histogramme"),
            ("otsu_threshold",      "Seuillage d'Otsu"),
        ]),
        ("Filtres Spatiaux", [
            ("mean_filter",         "Filtre Moyenneur"),
            ("gaussian_filter",     "Filtre Gaussien"),
            ("median_filter",       "Filtre Médian"),
            ("sobel_filter",        "Détection Sobel"),
            ("prewitt_filter",      "Détection Prewitt"),
            ("laplacian_filter",    "Laplacien"),
            ("unsharp_masking",     "Unsharp Masking"),
        ]),
        ("Morphologie", [
            ("erosion",   "Érosion"),
            ("dilation",  "Dilatation"),
            ("opening",   "Ouverture"),
            ("closing",   "Fermeture"),
            ("skeleton",  "Squelette (Zhang-Suen)"),
        ]),
        ("Analyse", [
            ("line_profile",      "Profil de ligne"),
            ("measure_distance",  "Mesure de distance"),
        ]),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(200)
        self.setStyleSheet("background-color: #1a202c;")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(4, 4, 4, 4)
        outer.setSpacing(0)

        # Title
        title = QLabel("🔧  Outils")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "color: #e2e8f0; font-size: 14px; font-weight: bold; padding: 8px 0;"
        )
        outer.addWidget(title)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #4a5568;")
        outer.addWidget(sep)

        # Scroll area for all categories
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: #1a202c; }")

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 4, 0, 4)
        container_layout.setSpacing(6)

        for category_title, tools in self.CATEGORIES:
            section = CategorySection(category_title, tools)
            section.tool_selected.connect(self.tool_selected)
            container_layout.addWidget(section)

        container_layout.addStretch()
        scroll.setWidget(container)
        outer.addWidget(scroll)
