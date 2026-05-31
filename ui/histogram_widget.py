import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt


class HistogramWidget(QWidget):


    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(160)
        self.setMaximumHeight(220)
        self.setStyleSheet("background-color: #1a202c;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(2)

        # Toolbar: mode label + switch button
        toolbar = QHBoxLayout()
        self._mode_label = QLabel("Histogramme")
        self._mode_label.setStyleSheet("color: #a0aec0; font-size: 11px;")
        toolbar.addWidget(self._mode_label)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        # Matplotlib figure
        self._fig = Figure(figsize=(5, 1.5), dpi=90, facecolor="#1a202c")
        self._ax = self._fig.add_subplot(111)
        self._ax.set_facecolor("#2d3748")
        self._fig.tight_layout(pad=0.5)

        self._canvas = FigureCanvas(self._fig)
        self._canvas.setStyleSheet("background-color: #1a202c;")
        layout.addWidget(self._canvas)

        self._draw_empty("Ouvrez une image pour voir l'histogramme.")

  

    def plot_histogram(self, bins: np.ndarray, counts: np.ndarray):
        """Update the figure with an intensity histogram."""
        self._mode_label.setText("Histogramme d'intensité")
        ax = self._ax
        ax.cla()
        ax.set_facecolor("#2d3748")
        ax.bar(bins, counts, color="#4299e1", width=1.0, alpha=0.85)
        ax.set_xlim(0, 255)
        ax.set_xlabel("Intensité", color="#a0aec0", fontsize=8)
        ax.set_ylabel("Pixels", color="#a0aec0", fontsize=8)
        ax.tick_params(colors="#718096", labelsize=7)
        for spine in ax.spines.values():
            spine.set_edgecolor("#4a5568")
        self._fig.tight_layout(pad=0.4)
        self._canvas.draw()

    def plot_line_profile(self, positions: np.ndarray, intensities: np.ndarray):
        """Update the figure with a line intensity profile."""
        self._mode_label.setText("Profil de ligne (intensité le long de la ligne tracée)")
        ax = self._ax
        ax.cla()
        ax.set_facecolor("#2d3748")
        ax.plot(positions, intensities, color="#68d391", linewidth=1.2)
        ax.fill_between(positions, intensities, alpha=0.25, color="#68d391")
        ax.set_xlabel("Distance (pixels)", color="#a0aec0", fontsize=8)
        ax.set_ylabel("Intensité", color="#a0aec0", fontsize=8)
        ax.tick_params(colors="#718096", labelsize=7)
        for spine in ax.spines.values():
            spine.set_edgecolor("#4a5568")
        self._fig.tight_layout(pad=0.4)
        self._canvas.draw()

    

    def _draw_empty(self, message: str):
        self._ax.cla()
        self._ax.set_facecolor("#2d3748")
        self._ax.text(
            0.5, 0.5, message,
            transform=self._ax.transAxes,
            ha="center", va="center",
            color="#718096", fontsize=9
        )
        self._ax.set_xticks([])
        self._ax.set_yticks([])
        for spine in self._ax.spines.values():
            spine.set_edgecolor("#4a5568")
        self._canvas.draw()
