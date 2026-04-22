```
███████╗██╗   ██╗███████╗███████╗██╗   ██╗    ████████╗███████╗███╗   ███╗██████╗
██╔════╝██║   ██║╚══███╔╝╚══███╔╝╚██╗ ██╔╝    ╚══██╔══╝██╔════╝████╗ ████║██╔══██╗
█████╗  ██║   ██║  ███╔╝   ███╔╝  ╚████╔╝        ██║   █████╗  ██╔████╔██║██████╔╝
██╔══╝  ██║   ██║ ███╔╝   ███╔╝    ╚██╔╝         ██║   ██╔══╝  ██║╚██╔╝██║██╔═══╝
██║     ╚██████╔╝███████╗███████╗   ██║          ██║   ███████╗██║ ╚═╝ ██║██║
╚═╝      ╚═════╝ ╚══════╝╚══════╝   ╚═╝          ╚═╝   ╚══════╝╚═╝     ╚═╝╚═╝
          Fuzzy Temperature Controller — Incubateur Médical
```

# 🌡 FuzzyTempControl

> **Système de Régulation de la Température par Logique Floue**  
> Incubateur Médical — TP 02 — INTeK (Institut National des Technologies et des Sciences du Kef)

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)](https://python.org)
[![scikit-fuzzy](https://img.shields.io/badge/scikit--fuzzy-0.4.2-orange)](https://pypi.org/project/scikit-fuzzy/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![INTeK](https://img.shields.io/badge/INTeK-Génie%20Biomédical-purple)](https://www.intek.ens.tn)

---

## 📋 Description

Ce projet implémente un **contrôleur flou** (Fuzzy Logic Controller) pour réguler la puissance de chauffage d'un **incubateur médical néonatal**. Le système prend en compte deux entrées :

- 🌡 **Température externe** (ambiance, 0–50 °C)  
- 🩺 **Température cutanée** du nourrisson (34–41 °C)

Et calcule en sortie :

- 🔥 **Puissance du chauffage** (0–100 %)

---

## 🗂 Structure du projet

```
FuzzyTempControl/
│
├── 📓 main.ipynb          # Notebook Jupyter complet (toutes les sections du TP)
├── 🐍 fuzzy_system.py     # Module principal : système flou, tests, graphiques
├── 🖥  interface.py        # Interface graphique Tkinter interactive
├── 📄 requirements.txt    # Dépendances Python
├── 📘 README.md           # Ce fichier
│
└── 📁 figures/            # Graphiques générés automatiquement
    ├── membership_trapezoidal.png
    ├── membership_gaussian.png
    └── comparison_defuzz.png
```

---

## ⚙️ Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/votre-utilisateur/FuzzyTempControl.git
cd FuzzyTempControl
```

### 2. Créer un environnement virtuel (recommandé)

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

---

## 🚀 Exécution

### Notebook Jupyter (toutes les étapes du TP)
```bash
jupyter notebook main.ipynb
```

### Script Python principal (tests + graphiques automatiques)
```bash
python fuzzy_system.py
```

### Interface graphique Tkinter
```bash
python interface.py
```

---

## 📐 Architecture du système flou

### Variables d'entrée

| Variable | Plage | Termes linguistiques |
|---|---|---|
| Température externe | [0, 50] °C | *froid*, *chaud* |
| Température cutanée | [34, 41] °C | *hypothermie*, *normal*, *fièvre* |

### Variable de sortie

| Variable | Plage | Termes linguistiques |
|---|---|---|
| Puissance chauffage | [0, 100] % | *Faible*, *Moyenne*, *Maximale* |

### Règles d'inférence

```
R1: SI froid ET hypothermie  →  Maximale
R2: SI froid ET normal       →  Moyenne
R3: SI froid ET fièvre       →  Faible
R4: SI chaud ET hypothermie  →  Moyenne
R5: SI chaud ET normal       →  Faible
R6: SI chaud ET fièvre       →  Faible
```

---

## 🧪 Exemples de résultats

| T\_externe | T\_cutanée | Puissance (Centroid) | Puissance (MOM) |
|---|---|---|---|
| 10 °C | 35 °C | 84.82 % | 85.00 % |
| 15 °C | 37 °C | 50.00 % | 50.00 % |
| 25 °C | 39 °C | 20.00 % | 20.00 % |

---

## 📊 Contenu du TP

| Section | Description |
|---|---|
| 1–2 | Définition des univers et tracé des fonctions d'appartenance |
| 3 | Implémentation des 6 règles d'inférence |
| 4–5 | Construction et test du système (méthode Centroid) |
| 6 | Comparaison MOM vs Centre de Gravité |
| 7 | Modification des fonctions (gaussiennes vs trapézoidales) |
| 8 | Impact de la suppression de règles |
| 9 | Interface graphique Tkinter |

---

## 🛠 Technologies utilisées

- **Python 3.9+**
- **scikit-fuzzy** — moteur de logique floue
- **NumPy** — calculs numériques
- **Matplotlib** — visualisations
- **Tkinter** — interface graphique native

---

## 👩‍🎓 Auteurs

**HAMMEDI NOURHEN** & **BOUALI NADA**  
Filière : Génie Biomédical  
Institut National des Technologies et des Sciences du Kef (INTeK)  
Université de Jendouba — République Tunisienne

---

## 📄 Licence

Ce projet est distribué sous licence **MIT**.  
Voir le fichier [LICENSE](LICENSE) pour plus de détails.
