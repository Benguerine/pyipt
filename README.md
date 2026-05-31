# Custom-IPT — Image Processing Toolbox

**Mini-Projet en Traitement d'Image — Ingénieur 4 IA**  
Département Informatique

---

## Description

Custom-IPT est une bibliothèque de traitement d'image codée **from scratch**
(algorithmes implémentés uniquement avec NumPy) et intégrée dans une interface
graphique interactive développée avec **PySide6** et **Matplotlib**.

L'objectif est de simuler un "Mini-Matlab IPT" ou un "Photoshop simplifié".

---

## Structure du projet

```
custom_ipt/
├── main.py                   # Point d'entrée de l'application
├── requirements.txt          # Dépendances Python
│
├── core/                     # Modules techniques (algorithmes)
│   ├── point_transforms.py   # Module A : Transformations ponctuelles
│   ├── spatial_filters.py    # Module B : Filtrage spatial (convolution 2D)
│   ├── morphology.py         # Module C : Morphologie mathématique
│   └── analysis.py           # Module 3 : Outils d'analyse
│
├── ui/                       # Interface graphique (PySide6)
│   ├── main_window.py        # Fenêtre principale (le "Studio")
│   ├── sidebar.py            # Barre latérale d'outils
│   ├── image_canvas.py       # Panneau d'affichage de l'image
│   ├── param_panel.py        # Panneau de paramètres dynamique
│   └── histogram_widget.py   # Histogramme & profil de ligne (Matplotlib)
│
└── utils/
    └── image_io.py           # Chargement / sauvegarde d'images (Pillow)
```

---

## Fonctionnalités implémentées

### Interface graphique (le "Studio")
- **Menu Fichier** : Ouvrir, Enregistrer sous, Reset
- **Barre latérale** : outils classés par catégorie (Point-to-point, Filtres, Morphologie, Analyse)
- **Panneau de paramètres** : curseurs/sliders qui apparaissent selon l'outil sélectionné
  (taille du noyau 3×3 / 5×5 / 7×7, sigma, alpha, beta…)
- **Histogramme en temps réel** : mis à jour après chaque opération

### Module A — Transformations Ponctuelles
| Outil | Description |
|---|---|
| Contraste / Luminosité | Formule linéaire g(x,y) = α·f(x,y) + β |
| Égalisation d'histogramme | CDF cumulé pour redistribuer les niveaux de gris |
| Seuillage d'Otsu | Maximisation de la variance inter-classes |

### Module B — Filtrage Spatial (Convolution 2D from scratch)
| Outil | Description |
|---|---|
| Filtre Moyenneur | Noyau uniforme 1/N² |
| Filtre Gaussien | Noyau gaussien normalisé |
| Filtre Médian | Médiane du voisinage (non linéaire) |
| Détection Sobel | Gradient Gx + Gy |
| Détection Prewitt | Idem avec noyaux Prewitt |
| Laplacien | Dérivée seconde pour contours |
| Unsharp Masking | Accentuation des détails : original + amount×(original − flou) |

### Module C — Morphologie Mathématique
| Outil | Description |
|---|---|
| Érosion | Un pixel est 1 si tout le voisinage SE est 1 |
| Dilatation | Un pixel est 1 si au moins un voisinage SE est 1 |
| Ouverture | Érosion puis Dilatation |
| Fermeture | Dilatation puis Érosion |
| Squelette | Algorithme de Zhang-Suen (thinning itératif) |

### Outils d'Analyse
| Outil | Description |
|---|---|
| Histogramme en temps réel | Affiché et mis à jour après chaque filtre |
| Profil de ligne | Tracer une ligne → graphe d'intensités le long de la ligne |
| Mesure de distance | Cliquer deux points → distance en pixels (formule euclidienne) |

---

## Installation et lancement

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Lancer l'application
python main.py
```

> **Python ≥ 3.10** requis (pour la syntaxe `X | None` dans les annotations).

---

## Notes techniques

- Tous les algorithmes de traitement sont dans `core/` et n'utilisent **que NumPy**.
- Aucun appel à `cv2.blur()`, `cv2.erode()`, `skimage.*` etc. pour les algorithmes.
- Pillow est utilisé uniquement pour la lecture/écriture des fichiers image.
- Matplotlib est utilisé uniquement pour l'affichage des graphiques.
- La convolution 2D générique `convolve2d()` dans `spatial_filters.py` est la
  base de tous les filtres linéaires.
