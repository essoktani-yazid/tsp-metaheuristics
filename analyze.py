"""
Advanced analysis and visualization utilities for TSP experiments
Optional: Use matplotlib for enhanced visualizations
"""

import json
import os
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt


class TSPAnalyzer:
    """Advanced analysis tools for TSP experiments."""

    def __init__(self, results_file: str = "results/results_full.json"):
        """Load and analyze results from JSON file."""
        if os.path.exists(results_file):
            with open(results_file, 'r') as f:
                self.results = json.load(f)
        else:
            self.results = {}
        self.output_dir = os.path.dirname(results_file)

    def plot_algorithm_comparison(self, instance_name: str, output_file: str = None):
        """
        Plot mean costs for all algorithms on a given instance.

        Args:
            instance_name: Name of the instance (e.g., 'A', 'B', 'C')
            output_file: Output file path (optional)
        """
        if not self.results:
            print("No results loaded")
            return

        algorithms = []
        means = []
        stdevs = []

        for algo_name in sorted(self.results.keys()):
            if instance_name in self.results[algo_name]:
                stats = self.results[algo_name][instance_name]
                algorithms.append(algo_name)
                means.append(stats['mean'])
                stdevs.append(stats['stdev'])

        if not algorithms:
            print(f"No results for instance {instance_name}")
            return

        plt.figure(figsize=(12, 6))
        x_pos = np.arange(len(algorithms))
        plt.bar(x_pos, means, yerr=stdevs, capsize=5, alpha=0.7, color='steelblue')
        plt.xlabel('Algorithm', fontsize=12)
        plt.ylabel('Mean Tour Cost', fontsize=12)
        plt.title(f'Algorithm Comparison - Instance {instance_name}', fontsize=14)
        plt.xticks(x_pos, algorithms, rotation=45, ha='right')
        plt.tight_layout()

        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"Saved plot to {output_file}")
        else:
            plt.savefig(os.path.join(self.output_dir, f'comparison_{instance_name}.png'),
                       dpi=300, bbox_inches='tight')
            plt.close()

    def plot_instance_comparison(self, output_file: str = None):
        """
        Plot mean costs across all instances for all algorithms.
        """
        if not self.results:
            print("No results loaded")
            return

        instances = sorted(set(
            inst for algo in self.results.values()
            for inst in algo.keys()
        ))

        fig, axes = plt.subplots(1, len(instances), figsize=(5*len(instances), 5))
        if len(instances) == 1:
            axes = [axes]

        for idx, instance_name in enumerate(instances):
            algorithms = []
            means = []

            for algo_name in sorted(self.results.keys()):
                if instance_name in self.results[algo_name]:
                    stats = self.results[algo_name][instance_name]
                    algorithms.append(algo_name)
                    means.append(stats['mean'])

            x_pos = np.arange(len(algorithms))
            axes[idx].bar(x_pos, means, alpha=0.7, color='steelblue')
            axes[idx].set_xlabel('Algorithm', fontsize=10)
            axes[idx].set_ylabel('Mean Cost', fontsize=10)
            axes[idx].set_title(f'Instance {instance_name}', fontsize=12)
            axes[idx].set_xticks(x_pos)
            axes[idx].set_xticklabels(algorithms, rotation=45, ha='right', fontsize=9)

        plt.tight_layout()

        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"Saved plot to {output_file}")
        else:
            plt.savefig(os.path.join(self.output_dir, 'comparison_all_instances.png'),
                       dpi=300, bbox_inches='tight')
        plt.close()

    def plot_algorithm_quality_vs_time(self, output_file: str = None):
        """
        Create scatter plot: quality (mean cost) vs time for all algorithms.
        """
        if not self.results:
            print("No results loaded")
            return

        algorithms = sorted(self.results.keys())
        instances = sorted(set(
            inst for algo in self.results.values()
            for inst in algo.keys()
        ))

        fig, axes = plt.subplots(1, len(instances), figsize=(6*len(instances), 5))
        if len(instances) == 1:
            axes = [axes]

        for idx, instance_name in enumerate(instances):
            times = []
            costs = []
            labels = []

            for algo_name in algorithms:
                if instance_name in self.results[algo_name]:
                    stats = self.results[algo_name][instance_name]
                    times.append(stats['time_mean'])
                    costs.append(stats['mean'])
                    labels.append(algo_name)

            scatter = axes[idx].scatter(times, costs, s=200, alpha=0.6, c=range(len(labels)), cmap='tab10')

            for i, label in enumerate(labels):
                axes[idx].annotate(label, (times[i], costs[i]), fontsize=8, ha='center')

            axes[idx].set_xlabel('Time (seconds)', fontsize=10)
            axes[idx].set_ylabel('Mean Cost', fontsize=10)
            axes[idx].set_title(f'Instance {instance_name}', fontsize=12)
            axes[idx].grid(True, alpha=0.3)

        plt.suptitle('Algorithm Quality vs Computation Time', fontsize=14, y=1.02)
        plt.tight_layout()

        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"Saved plot to {output_file}")
        else:
            plt.savefig(os.path.join(self.output_dir, 'quality_vs_time.png'),
                       dpi=300, bbox_inches='tight')
        plt.close()

    def generate_summary_statistics(self) -> pd.DataFrame:
        """Generate summary statistics for all algorithms."""
        data = []

        for algo_name in sorted(self.results.keys()):
            for instance_name in sorted(self.results[algo_name].keys()):
                stats = self.results[algo_name][instance_name]
                data.append({
                    'Algorithm': algo_name,
                    'Instance': instance_name,
                    'Best': f"{stats['best']:.2f}",
                    'Worst': f"{stats['worst']:.2f}",
                    'Mean': f"{stats['mean']:.2f}",
                    'Stdev': f"{stats['stdev']:.2f}",
                    'Time(s)': f"{stats['time_mean']:.3f}",
                })

        df = pd.DataFrame(data)
        return df

    def get_algorithm_rankings(self) -> Dict[str, Dict[str, int]]:
        """
        Rank algorithms by mean cost for each instance.

        Returns:
            Dictionary with instance names and algorithm rankings
        """
        instances = sorted(set(
            inst for algo in self.results.values()
            for inst in algo.keys()
        ))

        rankings = {}
        for instance_name in instances:
            costs = []
            for algo_name in self.results.keys():
                if instance_name in self.results[algo_name]:
                    stats = self.results[algo_name][instance_name]
                    costs.append((algo_name, stats['mean']))

            costs.sort(key=lambda x: x[1])
            rankings[instance_name] = {algo: rank+1 for rank, (algo, cost) in enumerate(costs)}

        return rankings

    def print_rankings_summary(self):
        """Print algorithm rankings for each instance."""
        rankings = self.get_algorithm_rankings()

        print("\n" + "="*80)
        print("ALGORITHM RANKINGS")
        print("="*80)

        for instance_name in sorted(rankings.keys()):
            print(f"\nInstance {instance_name}:")
            ranked = sorted(rankings[instance_name].items(), key=lambda x: x[1])
            for algo, rank in ranked:
                stats = self.results[algo][instance_name]
                print(f"  {rank}. {algo:20s} - Mean: {stats['mean']:8.2f}, "
                      f"Time: {stats['time_mean']:7.3f}s")

    def calculate_win_statistics(self) -> Dict[str, int]:
        """
        Calculate how many times each algorithm ranks first.

        Returns:
            Dictionary with win counts
        """
        rankings = self.get_algorithm_rankings()
        wins = {}

        for instance in rankings.values():
            for algo, rank in instance.items():
                if rank == 1:
                    wins[algo] = wins.get(algo, 0) + 1

        return dict(sorted(wins.items(), key=lambda x: x[1], reverse=True))

    def generate_heatmap_data(self) -> Tuple[np.ndarray, List, List]:
        """
        Generate data for algorithm x instance heatmap of mean costs.

        Returns:
            Matrix of mean costs, algorithm names, instance names
        """
        algorithms = sorted(self.results.keys())
        instances = sorted(set(
            inst for algo in self.results.values()
            for inst in algo.keys()
        ))

        matrix = np.zeros((len(algorithms), len(instances)))

        for i, algo_name in enumerate(algorithms):
            for j, instance_name in enumerate(instances):
                if instance_name in self.results[algo_name]:
                    matrix[i, j] = self.results[algo_name][instance_name]['mean']
                else:
                    matrix[i, j] = np.nan

        return matrix, algorithms, instances

    def plot_heatmap(self, output_file: str = None):
        """Plot heatmap of mean costs across algorithms and instances."""
        if not self.results:
            print("No results loaded")
            return

        matrix, algorithms, instances = self.generate_heatmap_data()

        plt.figure(figsize=(8, 10))
        im = plt.imshow(matrix, cmap='YlOrRd', aspect='auto')

        plt.xticks(np.arange(len(instances)), instances)
        plt.yticks(np.arange(len(algorithms)), algorithms)

        plt.xlabel('Instance', fontsize=12)
        plt.ylabel('Algorithm', fontsize=12)
        plt.title('Mean Tour Cost Heatmap', fontsize=14)

        # Add colorbar
        cbar = plt.colorbar(im)
        cbar.set_label('Mean Cost', fontsize=10)

        # Add text annotations
        for i in range(len(algorithms)):
            for j in range(len(instances)):
                if not np.isnan(matrix[i, j]):
                    text = plt.text(j, i, f'{matrix[i, j]:.0f}',
                                  ha="center", va="center", color="black", fontsize=9)

        plt.tight_layout()

        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"Saved heatmap to {output_file}")
        else:
            plt.savefig(os.path.join(self.output_dir, 'heatmap.png'),
                       dpi=300, bbox_inches='tight')
        plt.close()


def generate_analysis_report(results_file: str = "results/results_full.json"):
    """Generate complete analysis report with visualizations."""
    analyzer = TSPAnalyzer(results_file)

    print("\n" + "="*80)
    print("GENERATING ANALYSIS REPORT")
    print("="*80)

    # Generate visualizations
    print("\nGenerating visualizations...")

    instances = sorted(set(
        inst for algo in analyzer.results.values()
        for inst in algo.keys()
    ))

    for instance in instances:
        print(f"  • Generating comparison plot for Instance {instance}...")
        analyzer.plot_algorithm_comparison(instance)

    print("  • Generating overall instance comparison...")
    analyzer.plot_instance_comparison()

    print("  • Generating quality vs time plot...")
    analyzer.plot_algorithm_quality_vs_time()

    print("  • Generating heatmap...")
    analyzer.plot_heatmap()

    # Generate statistics
    print("\nGenerating statistics...")
    analyzer.print_rankings_summary()

    # Win statistics
    print("\n" + "="*80)
    print("ALGORITHM WIN STATISTICS")
    print("="*80)
    wins = analyzer.calculate_win_statistics()
    if wins:
        for algo, count in wins.items():
            print(f"  {algo}: {count} first place(s)")
    else:
        print("  No wins recorded")

    print("\n" + "="*80)
    print("Analysis report generated successfully!")
    print(f"Visualizations saved to: {analyzer.output_dir}/")
    print("="*80)


if __name__ == "__main__":
    # Run analysis if results exist
    if os.path.exists("results/results_full.json"):
        generate_analysis_report()
    elif os.path.exists("results/results.json"):
        generate_analysis_report("results/results.json")
    else:
        print("No results file found. Run experiments first!")
