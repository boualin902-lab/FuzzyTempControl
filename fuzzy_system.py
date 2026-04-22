"""
fuzzy_system.py
===============
Système de Régulation de la Température par Logique Floue
Adapté pour un incubateur médical (contrôle température / vitesse ventilateur)
 
Auteurs : Adapté de HAMMEDI NOURHEN & BOUALI NADA — INTeK
"""
 
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
 
# ─────────────────────────────────────────────────────────────────────────────
# 1. DÉFINITION DES UNIVERS DE DISCOURS
# ─────────────────────────────────────────────────────────────────────────────
 
# Température externe : 0 à 50 °C
externe = np.arange(0, 51, 0.5)
 
# Température cutanée (interne) : 34 à 41 °C
interne = np.arange(34, 41.1, 0.1)
 
# Puissance du chauffage / ventilateur : 0 à 100 %
puiss = np.arange(0, 101, 1)
 
 
def build_fuzzy_system(defuzz_method='centroid', use_gaussian=False):
    """
    Construit et retourne le système flou complet.
 
    Paramètres
    ----------
    defuzz_method : str
        Méthode de défuzzification : 'centroid', 'mom', 'bisector', 'som', 'lom'
    use_gaussian : bool
        Si True, utilise des fonctions d'appartenance gaussiennes (section 7 du TP)
 
    Retourne
    --------
    sim : ctrl.ControlSystemSimulation
    T_externe, T_interne, puissance : Antecedent / Consequent
    """
 
    # ── Variables linguistiques ───────────────────────────────────────────────
    T_externe = ctrl.Antecedent(externe, 'temperature_externe')
    T_interne = ctrl.Antecedent(interne,  'temperature_cutanee')
    puissance = ctrl.Consequent(puiss,    'puissance', defuzzify_method=defuzz_method)
 
    # ── Fonctions d'appartenance ──────────────────────────────────────────────
    if use_gaussian:
        # Section 7 : fonctions gaussiennes (plus souples, système plus stable)
        T_externe['froid']  = fuzz.gaussmf(externe, mean=5,  sigma=10)
        T_externe['chaud']  = fuzz.gaussmf(externe, mean=35, sigma=10)
 
        T_interne['hypothermie'] = fuzz.gaussmf(interne, mean=34.5, sigma=0.6)
        T_interne['normal']      = fuzz.gaussmf(interne, mean=37.0, sigma=0.5)
        T_interne['fievre']      = fuzz.gaussmf(interne, mean=39.5, sigma=0.7)
 
        puissance['Faible']   = fuzz.gaussmf(puiss, mean=20,  sigma=10)
        puissance['Moyenne']  = fuzz.gaussmf(puiss, mean=55,  sigma=12)
        puissance['Maximale'] = fuzz.gaussmf(puiss, mean=85,  sigma=10)
 
    else:
        # Section 1-2 : fonctions trapézoïdales / triangulaires (originales du TP)
        T_externe['froid']  = fuzz.trapmf(externe, [0,  3, 12, 15])
        T_externe['chaud']  = fuzz.trapmf(externe, [20, 25, 45, 50])
 
        T_interne['hypothermie'] = fuzz.trapmf(interne, [34,   34.5, 36,   36.5])
        T_interne['normal']      = fuzz.trapmf(interne, [36,   36.5, 37.5, 38  ])
        T_interne['fievre']      = fuzz.trapmf(interne, [37.5, 38,   40.5, 41  ])
 
        puissance['Faible']   = fuzz.trimf(puiss, [0,  20, 40 ])
        puissance['Moyenne']  = fuzz.trimf(puiss, [35, 55, 75 ])
        puissance['Maximale'] = fuzz.trimf(puiss, [70, 85, 100])
 
    # ── Règles d'inférence (section 3) ───────────────────────────────────────
    rule1 = ctrl.Rule(T_externe['froid'] & T_interne['hypothermie'], puissance['Maximale'])
    rule2 = ctrl.Rule(T_externe['froid'] & T_interne['normal'],      puissance['Moyenne'])
    rule3 = ctrl.Rule(T_externe['froid'] & T_interne['fievre'],      puissance['Faible'])
    rule4 = ctrl.Rule(T_externe['chaud'] & T_interne['hypothermie'], puissance['Moyenne'])
    rule5 = ctrl.Rule(T_externe['chaud'] & T_interne['normal'],      puissance['Faible'])
    rule6 = ctrl.Rule(T_externe['chaud'] & T_interne['fievre'],      puissance['Faible'])
 
    # ── Système de contrôle (section 4) ──────────────────────────────────────
    systeme = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6])
    sim = ctrl.ControlSystemSimulation(systeme)
 
    return sim, T_externe, T_interne, puissance
 
 
def build_partial_system(rules_to_remove=None, defuzz_method='centroid'):
    """
    Section 8 : Système avec règles supprimées.
 
    Paramètres
    ----------
    rules_to_remove : list[int]
        Indices des règles à supprimer (1 à 6). Ex: [2, 4]
    """
    if rules_to_remove is None:
        rules_to_remove = []
 
    T_externe = ctrl.Antecedent(externe, 'temperature_externe')
    T_interne = ctrl.Antecedent(interne,  'temperature_cutanee')
    puissance = ctrl.Consequent(puiss,    'puissance', defuzzify_method=defuzz_method)
 
    T_externe['froid']  = fuzz.trapmf(externe, [0,  3, 12, 15])
    T_externe['chaud']  = fuzz.trapmf(externe, [20, 25, 45, 50])
    T_interne['hypothermie'] = fuzz.trapmf(interne, [34,   34.5, 36,   36.5])
    T_interne['normal']      = fuzz.trapmf(interne, [36,   36.5, 37.5, 38  ])
    T_interne['fievre']      = fuzz.trapmf(interne, [37.5, 38,   40.5, 41  ])
    puissance['Faible']   = fuzz.trimf(puiss, [0,  20, 40 ])
    puissance['Moyenne']  = fuzz.trimf(puiss, [35, 55, 75 ])
    puissance['Maximale'] = fuzz.trimf(puiss, [70, 85, 100])
 
    all_rules = [
        ctrl.Rule(T_externe['froid'] & T_interne['hypothermie'], puissance['Maximale']),
        ctrl.Rule(T_externe['froid'] & T_interne['normal'],      puissance['Moyenne']),
        ctrl.Rule(T_externe['froid'] & T_interne['fievre'],      puissance['Faible']),
        ctrl.Rule(T_externe['chaud'] & T_interne['hypothermie'], puissance['Moyenne']),
        ctrl.Rule(T_externe['chaud'] & T_interne['normal'],      puissance['Faible']),
        ctrl.Rule(T_externe['chaud'] & T_interne['fievre'],      puissance['Faible']),
    ]
 
    active_rules = [r for i, r in enumerate(all_rules, 1) if i not in rules_to_remove]
    print(f"  → Règles actives : {[i for i in range(1,7) if i not in rules_to_remove]}")
 
    systeme = ctrl.ControlSystem(active_rules)
    sim = ctrl.ControlSystemSimulation(systeme)
    return sim, T_externe, T_interne, puissance
 
 
# ─────────────────────────────────────────────────────────────────────────────
# 2. TRAÇAGE DES FONCTIONS D'APPARTENANCE
# ─────────────────────────────────────────────────────────────────────────────
 
def plot_membership_functions(T_externe, T_interne, puissance,
                               title_suffix='', save_path=None):
    """Trace les 3 graphiques de fonctions d'appartenance."""
    fig, axes = plt.subplots(3, 1, figsize=(10, 9))
    fig.suptitle(f'Fonctions d\'appartenance — {title_suffix}', fontsize=14, fontweight='bold')
 
    colors = {'froid': '#3A86FF', 'chaud': '#FF6B6B',
              'hypothermie': '#06D6A0', 'normal': '#FFD166', 'fievre': '#EF476F',
              'Faible': '#118AB2', 'Moyenne': '#FF9F1C', 'Maximale': '#2EC4B6'}
 
    # Température externe
    ax = axes[0]
    for label, color in [('froid', colors['froid']), ('chaud', colors['chaud'])]:
        ax.plot(externe, T_externe[label].mf, label=label, color=color, linewidth=2)
    ax.set_title('Température externe (°C)', fontsize=11)
    ax.set_xlabel('Température'); ax.set_ylabel("Degré d'appartenance")
    ax.legend(); ax.set_ylim(-0.05, 1.1); ax.grid(alpha=0.3)
 
    # Température cutanée
    ax = axes[1]
    for label in ['hypothermie', 'normal', 'fievre']:
        ax.plot(interne, T_interne[label].mf, label=label, color=colors[label], linewidth=2)
    ax.set_title('Température cutanée (°C)', fontsize=11)
    ax.set_xlabel('Température'); ax.set_ylabel("Degré d'appartenance")
    ax.legend(); ax.set_ylim(-0.05, 1.1); ax.grid(alpha=0.3)
 
    # Puissance
    ax = axes[2]
    for label in ['Faible', 'Moyenne', 'Maximale']:
        ax.plot(puiss, puissance[label].mf, label=label, color=colors[label], linewidth=2)
    ax.set_title('Puissance du chauffage (%)', fontsize=11)
    ax.set_xlabel('Puissance'); ax.set_ylabel("Degré d'appartenance")
    ax.legend(); ax.set_ylim(-0.05, 1.1); ax.grid(alpha=0.3)
 
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"  Figure sauvegardée : {save_path}")
    return fig
 
 
# ─────────────────────────────────────────────────────────────────────────────
# 3. TESTS ET SIMULATIONS
# ─────────────────────────────────────────────────────────────────────────────
 
TESTS = [
    (10, 35,   "Froid + Hypothermie"),
    (10, 37,   "Froid + Normal"),
    (25, 39,   "Chaud + Fièvre"),
]
 
def run_tests(sim, tests=None, label=''):
    """Lance les cas de test et affiche les résultats."""
    if tests is None:
        tests = TESTS
    print(f"\n{'═'*55}")
    print(f"  Résultats — {label}")
    print(f"{'═'*55}")
    results = []
    for Te, Ti, desc in tests:
        try:
            sim.input['temperature_externe']  = Te
            sim.input['temperature_cutanee'] = Ti
            sim.compute()
            p = sim.output['puissance']
            print(f"  T_ext={Te:>3}°C  T_int={Ti:.1f}°C  →  Puissance = {p:.2f}%   [{desc}]")
            results.append((Te, Ti, p, desc))
        except Exception as e:
            print(f"  T_ext={Te}°C T_int={Ti}°C → ERREUR ({e})")
            results.append((Te, Ti, None, desc))
    return results
 
 
# ─────────────────────────────────────────────────────────────────────────────
# 4. COMPARAISON MOM vs CENTROID
# ─────────────────────────────────────────────────────────────────────────────
 
def compare_defuzz_methods():
    """Section 6 : compare MOM et Centroid sur les mêmes entrées."""
    print("\n" + "═"*55)
    print("  Comparaison des méthodes de défuzzification")
    print("═"*55)
 
    tests_comp = [(10, 35), (10, 37), (25, 39)]
    methods = [('centroid', 'Centre de Gravité'), ('mom', 'Moyenne des Maxima (MOM)')]
 
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    fig.suptitle('Comparaison Centroid vs MOM', fontsize=13, fontweight='bold')
 
    for ax, (method, name) in zip(axes, methods):
        sim, _, _, _ = build_fuzzy_system(defuzz_method=method)
        res = []
        print(f"\n  ── {name} ──")
        for Te, Ti in tests_comp:
            try:
                sim.input['temperature_externe']  = Te
                sim.input['temperature_cutanee'] = Ti
                sim.compute()
                p = sim.output['puissance']
                print(f"    T_ext={Te}°C  T_int={Ti}°C  →  {p:.2f}%")
                res.append(p)
            except Exception as e:
                print(f"    T_ext={Te}°C  T_int={Ti}°C  →  ERREUR ({e}), ignoré")
                res.append(0)
 
        labels = [f"({te}°C,{ti}°C)" for te, ti in tests_comp]
        bars = ax.bar(labels, res, color=['#3A86FF', '#FF6B6B', '#06D6A0'], edgecolor='white', linewidth=1.5)
        ax.set_title(name, fontsize=11)
        ax.set_ylabel('Puissance (%)'); ax.set_ylim(0, 110)
        ax.grid(axis='y', alpha=0.3)
        for bar, v in zip(bars, res):
            ax.text(bar.get_x() + bar.get_width()/2, v + 1.5, f'{v:.1f}%',
                    ha='center', va='bottom', fontsize=9, fontweight='bold')
 
    plt.tight_layout()
    plt.savefig('figures/comparison_defuzz.png', dpi=150, bbox_inches='tight')
    print("\n  Figure sauvegardée : figures/comparison_defuzz.png")
    return fig
 
 
if __name__ == '__main__':
    import os; os.makedirs('figures', exist_ok=True)
 
    # ── Section 1-2 : Fonctions d'appartenance originales ────────────────────
    print("\n[1-2] Tracé des fonctions d'appartenance (trapézoidales)")
    sim, T_ext, T_int, puis = build_fuzzy_system()
    plot_membership_functions(T_ext, T_int, puis,
                               title_suffix='Fonctions trapézoidales',
                               save_path='figures/membership_trapezoidal.png')
 
    # ── Section 3-5 : Tests du système ───────────────────────────────────────
    print("\n[3-5] Règles d'inférence + Tests")
    run_tests(sim, label='Système complet (Centroid)')
 
    # ── Section 6 : Comparaison MOM vs Centroid ───────────────────────────────
    compare_defuzz_methods()
 
    # ── Section 7 : Fonctions gaussiennes ────────────────────────────────────
    print("\n[7] Fonctions d'appartenance gaussiennes")
    sim_g, T_ext_g, T_int_g, puis_g = build_fuzzy_system(use_gaussian=True)
    plot_membership_functions(T_ext_g, T_int_g, puis_g,
                               title_suffix='Fonctions gaussiennes',
                               save_path='figures/membership_gaussian.png')
    run_tests(sim_g, label='Système Gaussien (Centroid)')
 
    # ── Section 8 : Règles supprimées ────────────────────────────────────────
    print("\n[8] Suppression de règles — Cas 1 (règles 2 et 4)")
    sim_p1, *_ = build_partial_system(rules_to_remove=[2, 4])
    run_tests(sim_p1, label='Règles supprimées : 2 & 4')
 
    print("\n[8] Suppression de règles — Cas 2 (règles 3 et 5)")
    sim_p2, *_ = build_partial_system(rules_to_remove=[3, 5])
    run_tests(sim_p2, label='Règles supprimées : 3 & 5')
 
    plt.show()
    print("\n✅ Tous les modules exécutés avec succès.")