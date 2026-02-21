"""
Experimental framework for TSP metaheuristics comparison
"""

import time
import statistics
import json
import os
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np

from algorithms import (TSPInstance, HillClimbing, MultiStartHillClimbing,
                       SimulatedAnnealing, TabuSearch, GRASP)
from data_utils import load_standard_instances, nearest_neighbor_heuristic


class TSPExperiment:
    """Framework for running and analyzing TSP algorithm experiments."""

    def __init__(self, instances: Dict[str, TSPInstance], output_dir: str = "results"):
        self.instances = instances
        self.output_dir = output_dir
        self.results = {}
        os.makedirs(output_dir, exist_ok=True)

    def run_algorithm(self, algorithm_class, instance_name: str, instance: TSPInstance,
                     num_runs: int, max_evaluations: int, **kwargs) -> Dict:
        """
        Run an algorithm multiple times on an instance.

        Returns:
            Dictionary with statistics
        """
        costs = []
        times = []
        best_cost = float('inf')

        print(f"  Running {algorithm_class.__name__} on instance {instance_name}... ", end='', flush=True)

        for run in range(num_runs):
            solver = algorithm_class(instance)
            start_time = time.time()
            tour, cost = solver.solve(max_evaluations=max_evaluations, **kwargs)
            elapsed = time.time() - start_time

            costs.append(cost)
            times.append(elapsed)
            best_cost = min(best_cost, cost)

        stats = {
            'best': min(costs),
            'worst': max(costs),
            'mean': statistics.mean(costs),
            'stdev': statistics.stdev(costs) if len(costs) > 1 else 0,
            'time_mean': statistics.mean(times),
            'time_stdev': statistics.stdev(times) if len(times) > 1 else 0,
        }

        print(f"Best: {stats['best']:.2f}, Mean: {stats['mean']:.2f} ± {stats['stdev']:.2f}")

        return stats

    def run_comprehensive_experiment(self, num_runs: int = 30, max_evaluations: int = 10000):
        """
        Run comprehensive comparison of all algorithms.

        Args:
            num_runs: Number of runs per algorithm-instance pair
            max_evaluations: Maximum evaluations per run
        """
        algorithms = {
            'HC_Best_Swap': {
                'class': HillClimbing,
                'params': {'variant': 'best', 'neighborhood': 'swap'}
            },
            'HC_First_Swap': {
                'class': HillClimbing,
                'params': {'variant': 'first', 'neighborhood': 'swap'}
            },
            'HC_Best_2opt': {
                'class': HillClimbing,
                'params': {'variant': 'best', 'neighborhood': '2opt'}
            },
            'MultiStart_HC': {
                'class': MultiStartHillClimbing,
                'params': {'num_starts': 10, 'hc_variant': 'best', 'neighborhood': 'swap'}
            },
            'SA_Swap': {
                'class': SimulatedAnnealing,
                'params': {'T0': 100.0, 'alpha': 0.95, 'Tmin': 0.01, 'neighborhood': 'swap'}
            },
            'SA_2opt': {
                'class': SimulatedAnnealing,
                'params': {'T0': 100.0, 'alpha': 0.95, 'Tmin': 0.01, 'neighborhood': '2opt'}
            },
            'TabuSearch': {
                'class': TabuSearch,
                'params': {'tabu_size': 50, 'neighborhood': 'swap'}
            },
            'GRASP': {
                'class': GRASP,
                'params': {'num_iterations': 10, 'alpha': 0.3, 'neighborhood': 'swap'}
            },
        }

        # Run algorithms
        for algo_name, algo_config in algorithms.items():
            print(f"\n{'='*60}")
            print(f"Testing: {algo_name}")
            print(f"{'='*60}")

            self.results[algo_name] = {}

            for instance_name, instance in self.instances.items():
                print(f"Instance {instance_name} ({instance.n} cities):")
                stats = self.run_algorithm(
                    algo_config['class'],
                    instance_name,
                    instance,
                    num_runs=num_runs,
                    max_evaluations=max_evaluations,
                    **algo_config['params']
                )
                self.results[algo_name][instance_name] = stats

    def save_results(self, filename: str = "results.json"):
        """Save results to JSON file."""
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\nResults saved to {filepath}")

    def generate_summary_table(self) -> pd.DataFrame:
        """Generate summary table comparing all algorithms."""
        data = []

        for algo_name in sorted(self.results.keys()):
            for instance_name in sorted(self.results[algo_name].keys()):
                stats = self.results[algo_name][instance_name]
                data.append({
                    'Algorithm': algo_name,
                    'Instance': instance_name,
                    'Best': f"{stats['best']:.2f}",
                    'Mean': f"{stats['mean']:.2f}",
                    'Stdev': f"{stats['stdev']:.2f}",
                    'Time (s)': f"{stats['time_mean']:.3f}",
                })

        df = pd.DataFrame(data)
        return df

    def print_summary(self):
        """Print summary of results."""
        df = self.generate_summary_table()
        print("\n" + "="*90)
        print("SUMMARY OF RESULTS")
        print("="*90)
        print(df.to_string(index=False))
        print("="*90)

    def save_summary_to_csv(self, filename: str = "summary.csv"):
        """Save summary table to CSV."""
        df = self.generate_summary_table()
        filepath = os.path.join(self.output_dir, filename)
        df.to_csv(filepath, index=False)
        print(f"Summary saved to {filepath}")

    def generate_comparison_by_instance(self) -> Dict[str, pd.DataFrame]:
        """Generate comparison tables grouped by instance."""
        comparisons = {}

        for instance_name in sorted(next(iter(self.results.values())).keys()):
            data = []
            for algo_name in sorted(self.results.keys()):
                if instance_name in self.results[algo_name]:
                    stats = self.results[algo_name][instance_name]
                    data.append({
                        'Algorithm': algo_name,
                        'Best': f"{stats['best']:.2f}",
                        'Mean': f"{stats['mean']:.2f}",
                        'Stdev': f"{stats['stdev']:.2f}",
                        'Time (s)': f"{stats['time_mean']:.3f}",
                    })

            comparisons[f'Instance_{instance_name}'] = pd.DataFrame(data)

        return comparisons

    def print_instance_comparisons(self):
        """Print detailed comparisons for each instance."""
        comparisons = self.generate_comparison_by_instance()

        for instance_name, df in comparisons.items():
            print(f"\n{'='*80}")
            print(f"Detailed Results for {instance_name}")
            print(f"{'='*80}")
            print(df.to_string(index=False))

    def get_best_algorithm_per_instance(self) -> Dict[str, str]:
        """Return best algorithm for each instance."""
        best = {}

        for instance_name in sorted(next(iter(self.results.values())).keys()):
            best_algo = None
            best_mean = float('inf')

            for algo_name in sorted(self.results.keys()):
                if instance_name in self.results[algo_name]:
                    mean_cost = self.results[algo_name][instance_name]['mean']
                    if mean_cost < best_mean:
                        best_mean = mean_cost
                        best_algo = algo_name

            best[instance_name] = (best_algo, best_mean)

        return best


def run_quick_benchmark():
    """Run a quick benchmark with small number of runs for testing."""
    print("Loading instances...")
    instances = load_standard_instances()

    if not instances:
        print("Creating standard instances...")
        from data_utils import create_standard_instances
        instances = create_standard_instances()

    print(f"Loaded {len(instances)} instances\n")

    # Run with smaller budgets for quick testing
    experiment = TSPExperiment(instances)
    experiment.run_comprehensive_experiment(num_runs=5, max_evaluations=5000)

    # Print results
    experiment.print_summary()
    experiment.print_instance_comparisons()

    # Print best algorithms
    print("\n" + "="*60)
    print("BEST ALGORITHMS PER INSTANCE")
    print("="*60)
    for instance, (algo, cost) in experiment.get_best_algorithm_per_instance().items():
        print(f"Instance {instance}: {algo} (Mean cost: {cost:.2f})")

    # Save results
    experiment.save_results()
    experiment.save_summary_to_csv()


if __name__ == "__main__":
    run_quick_benchmark()
