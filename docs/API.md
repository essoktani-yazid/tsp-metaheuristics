# Référence API & Interfaces — tsp-metaheuristics

> Documentation technique exhaustive des points d'entrée en ligne de commande (CLI) et de l'API programmatique Python de **tsp-metaheuristics**.

Le projet propose deux niveaux d'interface :
1. **Interface CLI (Command-Line Endpoints) :** Automatisation des benchmarks, initialisation et génération de rapports graphiques.
2. **API Programmatique Python :** Modules, classes et méthodes utilisables directement dans des scripts d'optimisation ou pour étendre la suite d'algorithmes.

---

## 1. Interface Ligne de Commande (CLI Endpoints)

### 1.1. `run_experiment.py` — Exécution des Benchmarks

Point d'entrée principal pour exécuter une campagne expérimentale comparative sur toutes les métaheuristiques.

```bash
python run_experiment.py [--mode {full,quick}] [--runs RUNS] [--evals EVALS]
```

#### Arguments CLI

| Argument | Type | Valeur par défaut | Description |
| :--- | :--- | :--- | :--- |
| `--mode` | `string` | `full` | Mode d'exécution : `quick` (5 runs, 5000 évaluations) ou `full` (30 runs, 10000 évaluations). |
| `--runs` | `int` | `None` (auto selon mode) | Surcharge optionnelle du nombre de runs indépendants par algorithme et par instance. |
| `--evals` | `int` | `None` (auto selon mode) | Surcharge optionnelle du budget maximal d'évaluations par run. |

#### Fichiers produits

- `results/results_full.json` (ou `results_quick.json`) : Données numériques brutes hiérarchisées.
- `results/summary_full.csv` (ou `summary_quick.csv`) : Tableau récapitulatif avec métriques agrégées.

---

### 1.2. `init.py` — Initialisation & Test du Projet

Vérifie l'environnement, crée les trois instances de test standards et exécute un test unitaire rapide sur les algorithmes.

```bash
python init.py
```

#### Effets de bord

- Génère `data/instance_A.json` (20 villes, seed=42)
- Génère `data/instance_B.json` (50 villes, seed=43)
- Génère `data/instance_C.json` (80 villes, seed=44)
- Valide l'exécution de `HillClimbing` et `SimulatedAnnealing`.

---

### 1.3. `analyze.py` — Analyse Statistique & Génération Graphique

Traite les fichiers de résultats numériques pour générer les classements, les taux de victoire et exporter les tracés graphiques.

```bash
python analyze.py
```

#### Fichiers produits

- `docs/assets/comparison_instances.png` : Graphique à barres des coûts moyens par instance.
- `docs/assets/quality_vs_time.png` : Nuage de points qualité du tour versus temps de calcul.
- `docs/assets/heatmap.png` : Matrice thermique des performances des algorithmes par instance.

---

### 1.4. `examples.py` — Exemples Pratiques Guidés

Exécute 5 scénarios d'utilisation concrets (résolution unitaire, comparaison d'instances, benchmark, optimisation sur coordonnées personnalisées, et étude comparative Swap vs 2-opt).

```bash
python examples.py
```

---

## 2. API Programmatique Python

### 2.1. Module `algorithms`

Contient les classes de modélisation et l'ensemble des métaheuristiques.

#### Classe `TSPInstance`

Représente une instance du TSP avec ses coordonnées géométriques et sa matrice de distances euclidiennes précalculée.

```python
from algorithms import TSPInstance
import numpy as np

coords = np.array([[10, 20], [30, 40], [50, 10]])
instance = TSPInstance(cities=coords, name="Custom_Instance")
```

##### Attributs
- `cities` (`np.ndarray`) : Tableau de forme `(N, 2)` contenant les coordonnées $(x, y)$ des $N$ villes.
- `n` (`int`) : Nombre total de villes.
- `name` (`str`) : Identifiant textuel de l'instance.
- `distance_matrix` (`np.ndarray`) : Matrice carrée $(N, N)$ des distances euclidiennes.

##### Méthodes
- `evaluate_tour(tour: List[int]) -> float` : Calcule et retourne la distance euclidienne totale d'une tournée fermée. Complexité : $O(N)$.

---

#### Classe de Base `TSPSolver`

Classe mère pour toutes les métaheuristiques. Fournit les opérateurs de voisinage et le suivi du budget d'évaluations.

##### Méthodes internes utiles
- `_random_swap(tour: List[int]) -> List[int]` : Échange deux sommets choisis aléatoirement.
- `_2opt_swap(tour: List[int], i: int, j: int) -> List[int]` : Inverse le sous-tour entre les indices `i` et `j`.
- `_get_all_swap_neighbors(tour: List[int]) -> List[List[int]]` : Génère l'ensemble exhaustif des voisins Swap ($N(N-1)/2$).
- `_get_all_2opt_neighbors(tour: List[int]) -> List[List[int]]` : Génère l'ensemble exhaustif des voisins 2-opt.

---

#### Solveurs Implémentés

Tous les solveurs héritent de `TSPSolver` et exposent la méthode `.solve() -> Tuple[List[int], float]`.

##### 1. `HillClimbing`
```python
solver = HillClimbing(instance)
tour, cost = solver.solve(
    max_evaluations=10000, 
    variant="best",      # "best" (Best Improvement) ou "first" (First Improvement)
    neighborhood="2opt"  # "swap" ou "2opt"
)
```

##### 2. `MultiStartHillClimbing`
```python
solver = MultiStartHillClimbing(instance)
tour, cost = solver.solve(
    max_evaluations=10000, 
    num_starts=10,       # Nombre de redémarrages indépendants
    hc_variant="best",   # Variante HC interne
    neighborhood="swap"  # Opérateur de voisinage
)
```

##### 3. `SimulatedAnnealing`
```python
solver = SimulatedAnnealing(instance)
tour, cost = solver.solve(
    max_evaluations=10000,
    T0=100.0,            # Température initiale
    alpha=0.95,          # Coefficient de refroidissement géométrique (T = T * alpha)
    Tmin=0.01,           # Température plancher d'arrêt
    neighborhood="2opt"  # Opérateur de voisinage
)
```

##### 4. `TabuSearch`
```python
solver = TabuSearch(instance)
tour, cost = solver.solve(
    max_evaluations=10000,
    tabu_size=50,        # Taille maximale de la mémoire taboue (liste FIFO de mouvements)
    neighborhood="swap"  # Opérateur de voisinage
)
```

##### 5. `GRASP`
```python
solver = GRASP(instance)
tour, cost = solver.solve(
    max_evaluations=10000,
    num_iterations=10,   # Nombre d'itérations Construction + Recherche Locale
    alpha=0.3,           # Paramètre de restriction RCL (0 = pur glouton, 1 = pur aléatoire)
    neighborhood="swap"  # Voisinage pour la phase de recherche locale
)
```

---

### 2.2. Module `data_utils`

Gestion des instances et heuristique constructive de référence.

```python
import data_utils
```

| Fonction | Signature | Description |
| :--- | :--- | :--- |
| `generate_random_instance` | `(n: int, seed: int = None) -> TSPInstance` | Génère une instance de $n$ villes distribuées uniformément sur $[0, 100]^2$. |
| `load_instance_from_file` | `(filepath: str) -> TSPInstance` | Charge une instance depuis un fichier JSON. |
| `save_instance_to_file` | `(instance: TSPInstance, filepath: str) -> None` | Sauvegarde une instance au format JSON. |
| `create_standard_instances` | `() -> Dict[str, TSPInstance]` | Génère et écrit sur disque les instances A (20), B (50) et C (80). |
| `load_standard_instances` | `() -> Dict[str, TSPInstance]` | Charge les trois instances A, B et C depuis `data/`. |
| `nearest_neighbor_heuristic`| `(instance: TSPInstance, start_city: int = 0) -> Tuple[List[int], float]` | Heuristique constructive gloutonne du plus proche voisin. |

---

### 2.3. Module `experiment`

Orchestration et calcul statistique multi-runs.

#### Classe `TSPExperiment`

```python
from experiment import TSPExperiment

exp = TSPExperiment(instances=instances, output_dir="results")
exp.run_comprehensive_experiment(num_runs=30, max_evaluations=10000)
```

##### Méthodes principales

- `run_algorithm(algorithm_class, instance_name: str, instance: TSPInstance, num_runs: int, max_evaluations: int, **kwargs) -> Dict` : Exécute $N$ fois un algorithme sur une instance donnée et retourne le dictionnaire des statistiques (`best`, `worst`, `mean`, `stdev`, `time_mean`, `time_stdev`).
- `run_comprehensive_experiment(num_runs: int = 30, max_evaluations: int = 10000) -> None` : Exécute l'ensemble du protocole comparatif sur 8 configurations d'algorithmes et sur toutes les instances enregistrées.
- `save_results(filename: str = "results.json") -> None` : Sauvegarde les résultats bruts en JSON.
- `save_summary_to_csv(filename: str = "summary.csv") -> None` : Exporte le résumé tabulaire au format CSV.
- `get_best_algorithm_per_instance() -> Dict[str, Tuple[str, float]]` : Identifie l'algorithme vainqueur (coût moyen le plus bas) pour chaque instance.

---

### 2.4. Module `analyze`

Analyse approfondie et génération des graphiques.

#### Classe `TSPAnalyzer`

```python
from analyze import TSPAnalyzer

analyzer = TSPAnalyzer(results_file="results/results_quick.json")
```

##### Méthodes principales

- `plot_algorithm_comparison(instance_name: str, output_file: str = None)` : Génère un diagramme en barres avec barres d'erreur (écart-type) pour l'instance ciblée.
- `plot_instance_comparison(output_file: str = None)` : Génère une vue comparative côte-à-côte de toutes les instances.
- `plot_algorithm_quality_vs_time(output_file: str = None)` : Génère un diagramme de dispersion (scatter plot) mettant en regard le temps de calcul moyen et le coût moyen obtenu.
- `plot_heatmap(output_file: str = None)` : Produit une heatmap annotée des coûts moyens (Algorithmes $\times$ Instances).
- `get_algorithm_rankings() -> Dict[str, Dict[str, int]]` : Calcule le classement ordinal (de 1 à $K$) des algorithmes par instance.
- `calculate_win_statistics() -> Dict[str, int]` : Compte le nombre d'instances remportées (1ère position) par chaque algorithme.

---

## 3. Schémas de Données

### 3.1. Structure d'un Fichier Instance (`data/*.json`)

```json
{
  "name": "random_20",
  "cities": [
    [37.454, 95.071],
    [73.199, 59.865],
    [15.601, 15.599]
  ]
}
```

### 3.2. Structure des Résultats d'Expérience (`results/*.json`)

```json
{
  "HC_Best_2opt": {
    "A": {
      "best": 386.63,
      "worst": 490.12,
      "mean": 434.16,
      "stdev": 42.99,
      "time_mean": 0.024,
      "time_stdev": 0.003
    }
  }
}
```

### 3.3. Structure du Fichier Récapitulatif (`results/*.csv`)

```csv
Algorithm,Instance,Best,Mean,Stdev,Time (s)
HC_Best_2opt,A,386.63,434.16,42.99,0.024
GRASP,A,491.82,515.00,20.21,0.046
SA_2opt,A,494.55,567.18,47.60,0.003
```

---

## 4. Codes de Sortie & Gestion des Exceptions

| Exception / Statut | Cause Fréquente | Solution |
| :--- | :--- | :--- |
| `FileNotFoundError` | Le fichier d'instance ou de résultats JSON n'existe pas. | Exécuter `python init.py` ou `python run_experiment.py` au préalable. |
| `ValueError` | Coordonnées de villes non conformes (dimensions != `(N, 2)`). | Vérifier que les villes contiennent des paires $[x, y]$ valides. |
| `KeyError` | Tentative d'accès à une instance absente du dictionnaire. | Utiliser `load_standard_instances()` pour s'assurer de la présence des clés `'A'`, `'B'`, `'C'`. |
| `NotImplementedError`| Appel direct de la méthode `solve()` sur la classe abstraite `TSPSolver`. | Instancier une sous-classe concrète (`HillClimbing`, `SimulatedAnnealing`, etc.). |

---
[⬅ Retour au README principal](../README.md)
