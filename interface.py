"""
interface.py
============
Interface graphique Tkinter pour le Système de Régulation Floue
de la Température (Incubateur Médical)

Auteurs : Adapté de HAMMEDI NOURHEN & BOUALI NADA — INTeK
"""

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# ─────────────────────────────────────────────────────────────────────────────
# Construction du système flou (importé depuis fuzzy_system si disponible)
# ─────────────────────────────────────────────────────────────────────────────

externe = np.arange(0, 51, 0.5)
interne = np.arange(34, 41.1, 0.1)
puiss   = np.arange(0, 101, 1)


def _make_system(defuzz='centroid', gaussian=False):
    T_ext = ctrl.Antecedent(externe, 'temperature_externe')
    T_int = ctrl.Antecedent(interne,  'temperature_cutanee')
    puis  = ctrl.Consequent(puiss,    'puissance', defuzzify_method=defuzz)

    if gaussian:
        T_ext['froid']  = fuzz.gaussmf(externe, 5,  10)
        T_ext['chaud']  = fuzz.gaussmf(externe, 35, 10)
        T_int['hypothermie'] = fuzz.gaussmf(interne, 34.5, 0.6)
        T_int['normal']      = fuzz.gaussmf(interne, 37.0, 0.5)
        T_int['fievre']      = fuzz.gaussmf(interne, 39.5, 0.7)
        puis['Faible']   = fuzz.gaussmf(puiss, 20, 10)
        puis['Moyenne']  = fuzz.gaussmf(puiss, 55, 12)
        puis['Maximale'] = fuzz.gaussmf(puiss, 85, 10)
    else:
        T_ext['froid']  = fuzz.trapmf(externe, [0,  3, 12, 15])
        T_ext['chaud']  = fuzz.trapmf(externe, [20, 25, 45, 50])
        T_int['hypothermie'] = fuzz.trapmf(interne, [34, 34.5, 36, 36.5])
        T_int['normal']      = fuzz.trapmf(interne, [36, 36.5, 37.5, 38])
        T_int['fievre']      = fuzz.trapmf(interne, [37.5, 38, 40.5, 41])
        puis['Faible']   = fuzz.trimf(puiss, [0,  20, 40])
        puis['Moyenne']  = fuzz.trimf(puiss, [35, 55, 75])
        puis['Maximale'] = fuzz.trimf(puiss, [70, 85, 100])

    rules = [
        ctrl.Rule(T_ext['froid'] & T_int['hypothermie'], puis['Maximale']),
        ctrl.Rule(T_ext['froid'] & T_int['normal'],      puis['Moyenne']),
        ctrl.Rule(T_ext['froid'] & T_int['fievre'],      puis['Faible']),
        ctrl.Rule(T_ext['chaud'] & T_int['hypothermie'], puis['Moyenne']),
        ctrl.Rule(T_ext['chaud'] & T_int['normal'],      puis['Faible']),
        ctrl.Rule(T_ext['chaud'] & T_int['fievre'],      puis['Faible']),
    ]
    system = ctrl.ControlSystem(rules)
    return ctrl.ControlSystemSimulation(system), puis


# ─────────────────────────────────────────────────────────────────────────────
# APPLICATION TKINTER
# ─────────────────────────────────────────────────────────────────────────────

DARK_BG    = "#1E1E2E"
CARD_BG    = "#2A2A3E"
ACCENT     = "#7C3AED"
ACCENT2    = "#06D6A0"
TEXT_LIGHT = "#E2E8F0"
TEXT_DIM   = "#94A3B8"
WARNING    = "#F59E0B"
DANGER     = "#EF4444"


class FuzzyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🌡 Régulation Floue — Incubateur Médical | INTeK")
        self.geometry("1100x750")
        self.configure(bg=DARK_BG)
        self.resizable(True, True)
        self._build_ui()

    # ── Interface ─────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        header = tk.Frame(self, bg=ACCENT, pady=14)
        header.pack(fill='x')
        tk.Label(header, text="⚕  Système de Régulation Floue du Chauffage",
                 font=("Helvetica", 17, "bold"), bg=ACCENT, fg="white").pack()
        tk.Label(header, text="Incubateur Médical — INTeK Kef  •  Logique Floue (skfuzzy)",
                 font=("Helvetica", 9), bg=ACCENT, fg="#DDD6FE").pack()

        # Main layout
        main = tk.Frame(self, bg=DARK_BG)
        main.pack(fill='both', expand=True, padx=16, pady=12)

        left  = tk.Frame(main, bg=DARK_BG, width=290)
        right = tk.Frame(main, bg=DARK_BG)
        left.pack(side='left', fill='y', padx=(0, 14))
        right.pack(side='left', fill='both', expand=True)
        left.pack_propagate(False)

        self._build_controls(left)
        self._build_chart(right)

    def _label(self, parent, text, font_size=10, bold=False, color=TEXT_LIGHT, pady=4):
        fw = "bold" if bold else "normal"
        tk.Label(parent, text=text, font=("Helvetica", font_size, fw),
                 bg=CARD_BG if parent._name != '.' else DARK_BG,
                 fg=color).pack(anchor='w', pady=(pady, 0), padx=10)

    def _build_controls(self, parent):
        card = tk.Frame(parent, bg=CARD_BG, bd=0, relief='flat',
                        highlightbackground=ACCENT, highlightthickness=1)
        card.pack(fill='x', pady=(0, 12))

        tk.Label(card, text="⚙  Paramètres d'entrée", font=("Helvetica", 11, "bold"),
                 bg=ACCENT, fg="white", pady=7).pack(fill='x')

        # Température externe
        tk.Label(card, text="Température externe (°C)",
                 font=("Helvetica", 10), bg=CARD_BG, fg=TEXT_DIM).pack(anchor='w', padx=12, pady=(10,0))
        self.var_ext = tk.DoubleVar(value=10.0)
        frm_e = tk.Frame(card, bg=CARD_BG); frm_e.pack(fill='x', padx=12)
        self.sl_ext = ttk.Scale(frm_e, from_=0, to=50, variable=self.var_ext,
                                orient='horizontal', command=self._on_slider)
        self.sl_ext.pack(side='left', fill='x', expand=True)
        self.lbl_ext = tk.Label(frm_e, text="10.0", width=5,
                                 font=("Courier", 10, "bold"), bg=CARD_BG, fg=ACCENT2)
        self.lbl_ext.pack(side='left', padx=(6,0))

        # Température cutanée
        tk.Label(card, text="Température cutanée (°C)",
                 font=("Helvetica", 10), bg=CARD_BG, fg=TEXT_DIM).pack(anchor='w', padx=12, pady=(8,0))
        self.var_int = tk.DoubleVar(value=35.0)
        frm_i = tk.Frame(card, bg=CARD_BG); frm_i.pack(fill='x', padx=12)
        self.sl_int = ttk.Scale(frm_i, from_=34, to=41, variable=self.var_int,
                                orient='horizontal', command=self._on_slider)
        self.sl_int.pack(side='left', fill='x', expand=True)
        self.lbl_int = tk.Label(frm_i, text="35.0", width=5,
                                 font=("Courier", 10, "bold"), bg=CARD_BG, fg=ACCENT2)
        self.lbl_int.pack(side='left', padx=(6,0))

        # Options
        sep = tk.Frame(card, bg=ACCENT, height=1); sep.pack(fill='x', padx=10, pady=10)

        tk.Label(card, text="Méthode de défuzzification",
                 font=("Helvetica", 10), bg=CARD_BG, fg=TEXT_DIM).pack(anchor='w', padx=12)
        self.defuzz_var = tk.StringVar(value='centroid')
        combo = ttk.Combobox(card, textvariable=self.defuzz_var,
                             values=['centroid', 'mom', 'bisector', 'som', 'lom'],
                             state='readonly', width=18)
        combo.pack(anchor='w', padx=12, pady=4)

        self.gaussian_var = tk.BooleanVar(value=False)
        tk.Checkbutton(card, text="Fonctions gaussiennes",
                       variable=self.gaussian_var,
                       font=("Helvetica", 10), bg=CARD_BG, fg=TEXT_LIGHT,
                       selectcolor=DARK_BG, activebackground=CARD_BG).pack(anchor='w', padx=12)

        # Bouton calculer
        btn = tk.Button(card, text="▶  Calculer", command=self._calculate,
                        font=("Helvetica", 12, "bold"),
                        bg=ACCENT, fg="white", relief='flat',
                        activebackground="#6D28D9", activeforeground="white",
                        cursor="hand2", pady=8)
        btn.pack(fill='x', padx=12, pady=12)

        # Résultat
        self.result_frame = tk.Frame(card, bg=CARD_BG)
        self.result_frame.pack(fill='x', padx=12, pady=(0, 12))
        self.result_lbl = tk.Label(self.result_frame,
                                   text="Puissance calculée : —",
                                   font=("Helvetica", 14, "bold"),
                                   bg=CARD_BG, fg=ACCENT2)
        self.result_lbl.pack()
        self.status_lbl = tk.Label(self.result_frame, text="",
                                   font=("Helvetica", 9), bg=CARD_BG, fg=WARNING)
        self.status_lbl.pack()

        # Batch tests card
        card2 = tk.Frame(parent, bg=CARD_BG, bd=0, relief='flat',
                         highlightbackground="#374151", highlightthickness=1)
        card2.pack(fill='x', pady=(0, 12))
        tk.Label(card2, text="🧪  Tests rapides", font=("Helvetica", 10, "bold"),
                 bg="#374151", fg=TEXT_LIGHT, pady=5).pack(fill='x')

        tests = [(10, 35, "Froid+Hypo"), (15, 37, "Froid+Normal"), (25, 39, "Chaud+Fièvre")]
        for te, ti, name in tests:
            f = tk.Frame(card2, bg=CARD_BG); f.pack(fill='x', padx=10, pady=2)
            tk.Button(f, text=f"{name}  ({te}°/{ti}°)",
                      command=lambda a=te, b=ti: self._quick_test(a, b),
                      font=("Helvetica", 9), bg="#374151", fg=TEXT_LIGHT,
                      relief='flat', cursor="hand2", padx=6, pady=3).pack(side='left')

        tk.Frame(card2, bg=CARD_BG, height=6).pack()

    def _build_chart(self, parent):
        tk.Label(parent, text="Degré d'appartenance — Puissance du chauffage",
                 font=("Helvetica", 11, "bold"), bg=DARK_BG, fg=TEXT_LIGHT).pack(pady=(0, 6))

        self.fig, self.ax = plt.subplots(figsize=(7, 4))
        self.fig.patch.set_facecolor('#1E1E2E')
        self.ax.set_facecolor('#2A2A3E')
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        self._draw_empty_chart()

    def _draw_empty_chart(self):
        self.ax.clear()
        self.ax.set_facecolor('#2A2A3E')
        for spine in self.ax.spines.values():
            spine.set_edgecolor('#475569')
        self.ax.tick_params(colors=TEXT_DIM)
        self.ax.set_xlabel('Puissance (%)', color=TEXT_DIM)
        self.ax.set_ylabel("Degré d'appartenance", color=TEXT_DIM)
        self.ax.plot(puiss, np.zeros_like(puiss), alpha=0)
        self.ax.set_ylim(-0.05, 1.1)
        self.ax.text(50, 0.5, "Appuyer sur ▶ Calculer",
                     ha='center', va='center', color='#475569',
                     fontsize=12, fontstyle='italic')
        self.canvas.draw()

    # ── Logique ───────────────────────────────────────────────────────────────
    def _on_slider(self, _=None):
        self.lbl_ext.config(text=f"{self.var_ext.get():.1f}")
        self.lbl_int.config(text=f"{self.var_int.get():.1f}")

    def _quick_test(self, te, ti):
        self.var_ext.set(te)
        self.var_int.set(ti)
        self.lbl_ext.config(text=f"{te:.1f}")
        self.lbl_int.config(text=f"{ti:.1f}")
        self._calculate()

    def _calculate(self):
        Te = self.var_ext.get()
        Ti = self.var_int.get()
        method  = self.defuzz_var.get()
        gauss   = self.gaussian_var.get()

        try:
            sim, puis_var = _make_system(defuzz=method, gaussian=gauss)
            sim.input['temperature_externe']  = Te
            sim.input['temperature_cutanee'] = Ti
            sim.compute()
            p = sim.output['puissance']

            self.result_lbl.config(text=f"Puissance calculée : {p:.2f} %")

            # Couleur selon la puissance
            if p > 70:
                color = DANGER
                status = "🔴 Chauffage maximal activé"
            elif p > 40:
                color = WARNING
                status = "🟡 Puissance modérée"
            else:
                color = ACCENT2
                status = "🟢 Puissance faible"
            self.result_lbl.config(fg=color)
            self.status_lbl.config(text=status)

            self._draw_chart(p, puis_var)

        except Exception as e:
            messagebox.showerror("Erreur de calcul", str(e))

    def _draw_chart(self, result_value, puis_var):
        self.ax.clear()
        self.ax.set_facecolor('#2A2A3E')
        for spine in self.ax.spines.values():
            spine.set_edgecolor('#475569')
        self.ax.tick_params(colors=TEXT_DIM)
        self.ax.set_xlabel('Puissance (%)', color=TEXT_DIM)
        self.ax.set_ylabel("Degré d'appartenance", color=TEXT_DIM)

        palette = {'Faible': '#3A86FF', 'Moyenne': '#FF9F1C', 'Maximale': '#06D6A0'}
        for label, color in palette.items():
            mf = puis_var[label].mf
            self.ax.plot(puiss, mf, label=label, color=color, linewidth=2.2)
            self.ax.fill_between(puiss, mf, alpha=0.12, color=color)

        self.ax.axvline(x=result_value, color='#F8FAFC', linewidth=2,
                        linestyle='--', label=f'{result_value:.2f} %')
        self.ax.set_ylim(-0.05, 1.15)
        self.ax.set_xlim(0, 100)
        self.ax.legend(facecolor='#374151', edgecolor='#475569',
                       labelcolor=TEXT_LIGHT, fontsize=9)
        self.ax.set_title(f"Résultat : {result_value:.2f}%", color=TEXT_LIGHT, fontsize=10)
        self.canvas.draw()


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app = FuzzyApp()
    app.mainloop()
