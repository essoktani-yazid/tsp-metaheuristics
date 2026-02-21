"""
Full experiment runner with rigorous settings
Run this script to conduct comprehensive experiments
"""

import sys
import os
import time
import json

# Add project directory to path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

from experiment import TSPExperiment
from data_utils import load_standard_instances, create_standard_instances


def run_full_experiment():
    """Run comprehensive experiments with rigorous settings."""

    print("="*80)
    print("COMPREHENSIVE TSP METAHEURISTICS EXPERIMENT")
    print("="*80)

    # Load instances
    print("\n[1] Loading instances...")
    instances = load_standard_instances()

    if not instances:
        print("    Creating standard instances...")
        instances = create_standard_instances()

    print(f"    Loaded {len(instances)} instances:")
    for name, inst in instances.items():
        print(f"      Instance {name}: {inst.n} cities")

    # Configure experiment
    print("\n[2] Configuring experiment...")
    num_runs = 30  # Number of independent runs
    max_evals = 10000  # Maximum evaluations per run

    print(f"    Runs per algorithm-instance: {num_runs}")
    print(f"    Max evaluations per run: {max_evals}")

    # Run experiment
    print("\n[3] Running experiments...")
    print("    (This may take several minutes)")
    print("-"*80)

    start_time = time.time()
    experiment = TSPExperiment(instances)
    experiment.run_comprehensive_experiment(num_runs=num_runs, max_evaluations=max_evals)
    elapsed_time = time.time() - start_time

    print("\n" + "-"*80)
    print(f"    Experiments completed in {elapsed_time:.1f} seconds")

    # Analysis
    print("\n[4] Analyzing results...")
    print("-"*80)

    # Print summary
    experiment.print_summary()

    # Detailed comparisons
    print("\n[5] Detailed Results by Instance")
    print("-"*80)
    experiment.print_instance_comparisons()

    # Best algorithms
    print("\n[6] Best Algorithms Summary")
    print("-"*80)
    best = experiment.get_best_algorithm_per_instance()
    for instance, (algo, cost) in sorted(best.items()):
        print(f"    Instance {instance} ({experiment.instances[instance].n} cities):")
        print(f"      Best algorithm: {algo}")
        print(f"      Mean cost: {cost:.2f}")

    # Save results
    print("\n[7] Saving results...")
    print("-"*80)
    experiment.save_results('results_full.json')
    experiment.save_summary_to_csv('summary_full.csv')
    print(f"    Results saved in: {experiment.output_dir}/")

    # Print completion message
    print("\n" + "="*80)
    print("EXPERIMENT COMPLETED SUCCESSFULLY")
    print("="*80)
    print("\nGenerated files:")
    print(f"  • {experiment.output_dir}/results_full.json - Full numerical results")
    print(f"  • {experiment.output_dir}/summary_full.csv - Summary table")
    print("\nTotal execution time: {:.1f} seconds".format(elapsed_time))
    print("="*80)


def run_quick_comparison():
    """Run a quick comparison for testing (fewer runs, smaller budget)."""

    print("="*80)
    print("QUICK TSP METAHEURISTICS COMPARISON")
    print("="*80)

    # Load instances
    print("\n[1] Loading instances...")
    instances = load_standard_instances()

    if not instances:
        print("    Creating standard instances...")
        instances = create_standard_instances()

    print(f"    Loaded {len(instances)} instances")

    # Configure for quick run
    num_runs = 5
    max_evals = 5000

    print(f"    Runs per algorithm-instance: {num_runs}")
    print(f"    Max evaluations per run: {max_evals}")

    # Run experiment
    print("\n[2] Running experiments...")
    print("-"*80)

    start_time = time.time()
    experiment = TSPExperiment(instances)
    experiment.run_comprehensive_experiment(num_runs=num_runs, max_evaluations=max_evals)
    elapsed_time = time.time() - start_time

    # Print results
    print("\n" + "-"*80)
    experiment.print_summary()
    print("-"*80)

    print(f"\nCompleted in {elapsed_time:.1f} seconds")

    # Save results
    experiment.save_results('results_quick.json')
    experiment.save_summary_to_csv('summary_quick.csv')

    print("\nResults saved in results/ directory")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='TSP Metaheuristics Experiment Runner')
    parser.add_argument('--mode', choices=['full', 'quick'], default='full',
                       help='Execution mode: full experiment or quick test')
    parser.add_argument('--runs', type=int, default=None,
                       help='Override number of runs')
    parser.add_argument('--evals', type=int, default=None,
                       help='Override max evaluations per run')

    args = parser.parse_args()

    if args.mode == 'quick':
        run_quick_comparison()
    else:
        run_full_experiment()
