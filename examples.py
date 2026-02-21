"""
Quick Start Guide - Simple examples for getting started with the TSP Project
"""

# ============================================================================
# QUICK START EXAMPLES
# ============================================================================

# Example 1: Generate instances and test basic algorithms
# ============================================================================
print("=" * 70)
print("EXAMPLE 1: Basic Algorithm Testing")
print("=" * 70)

from data_utils import generate_random_instance
from algorithms import HillClimbing, SimulatedAnnealing, TabuSearch

# Create a small instance
instance = generate_random_instance(n=30, seed=42)
print(f"Created TSP instance with {instance.n} cities")

# Run Hill Climbing
print("\n1. Hill Climbing (Best Improvement):")
hc = HillClimbing(instance)
tour_hc, cost_hc = hc.solve(max_evaluations=5000, variant='best', neighborhood='swap')
print(f"   Tour cost: {cost_hc:.2f}")
print(f"   Evaluations: {hc.evaluations}")

# Run Simulated Annealing
print("\n2. Simulated Annealing:")
sa = SimulatedAnnealing(instance)
tour_sa, cost_sa = sa.solve(max_evaluations=5000, T0=100.0, alpha=0.95, Tmin=0.01)
print(f"   Tour cost: {cost_sa:.2f}")
print(f"   Evaluations: {sa.evaluations}")

# Run Tabu Search
print("\n3. Tabu Search:")
ts = TabuSearch(instance)
tour_ts, cost_ts = ts.solve(max_evaluations=5000, tabu_size=50)
print(f"   Tour cost: {cost_ts:.2f}")
print(f"   Evaluations: {ts.evaluations}")

print("\n" + "=" * 70)


# Example 2: Load standard instances and run quick comparison
# ============================================================================
print("\nEXAMPLE 2: Standard Instances Comparison")
print("=" * 70)

from data_utils import load_standard_instances
from algorithms import HillClimbing, MultiStartHillClimbing, SimulatedAnnealing

# Load the three standard instances
instances = load_standard_instances()

for name, inst in sorted(instances.items()):
    print(f"\nInstance {name} ({inst.n} cities):")

    # Hill Climbing
    hc = HillClimbing(inst)
    _, cost_hc = hc.solve(max_evaluations=2000, variant='best')
    print(f"  HC Best:       {cost_hc:.2f}")

    # Multi-Start Hill Climbing
    mshc = MultiStartHillClimbing(inst)
    _, cost_mshc = mshc.solve(max_evaluations=2000, num_starts=5)
    print(f"  Multi-Start HC: {cost_mshc:.2f}")

    # Simulated Annealing
    sa = SimulatedAnnealing(inst)
    _, cost_sa = sa.solve(max_evaluations=2000)
    print(f"  Simulated Ann:  {cost_sa:.2f}")

print("\n" + "=" * 70)


# Example 3: Run full experiment with result analysis
# ============================================================================
print("\nEXAMPLE 3: Full Experiment with Analysis")
print("=" * 70)

from experiment import TSPExperiment
from data_utils import load_standard_instances

instances = load_standard_instances()

# Create experiment
exp = TSPExperiment(instances)

# Run with 10 runs and 5000 evaluations per run
print("Running experiments with 10 runs, 5000 evaluations per run...")
exp.run_comprehensive_experiment(num_runs=10, max_evaluations=5000)

# Print results
print("\nResults Summary:")
print("-" * 70)
exp.print_summary()

# Get best algorithms
print("\nBest Algorithms by Instance:")
print("-" * 70)
for inst_name, (algo, cost) in exp.get_best_algorithm_per_instance().items():
    print(f"Instance {inst_name}: {algo} (mean cost: {cost:.2f})")

# Save results
exp.save_results('results_example.json')
exp.save_summary_to_csv('summary_example.csv')
print("\nResults saved to results/ directory")

print("\n" + "=" * 70)


# Example 4: Create custom instance and optimize
# ============================================================================
print("\nEXAMPLE 4: Custom Instance Optimization")
print("=" * 70)

import numpy as np
from algorithms import TSPInstance, HillClimbing, SimulatedAnnealing, GRASP

# Create a custom instance with specific coordinates
cities = np.array([
    [10, 20],
    [30, 40],
    [50, 10],
    [70, 30],
    [85, 60],
])

instance = TSPInstance(cities, name="Custom_5_cities")
print(f"Created instance: {instance.name} with {instance.n} cities")

# Optimize with different algorithms
algorithms = {
    'HC': HillClimbing(instance),
    'SA': SimulatedAnnealing(instance),
    'GRASP': GRASP(instance),
}

print("\nOptimization results:")
for name, algo in algorithms.items():
    tour, cost = algo.solve(max_evaluations=1000)
    print(f"  {name:6s}: cost = {cost:7.2f}, tour = {tour}")

print("\n" + "=" * 70)


# Example 5: Analyze neighborhood effects
# ============================================================================
print("\nEXAMPLE 5: Neighborhood Comparison (Swap vs 2-opt)")
print("=" * 70)

from data_utils import load_standard_instances
from algorithms import HillClimbing

instances = load_standard_instances()
if 'A' in instances:
    inst = instances['A']
    print(f"Testing on Instance A ({inst.n} cities)")
    print(f"Budget: 5000 evaluations\n")

    # Swap neighborhood
    hc_swap = HillClimbing(inst)
    _, cost_swap = hc_swap.solve(max_evaluations=5000, variant='best', neighborhood='swap')
    print(f"Swap neighborhood:   {cost_swap:.2f}")

    # 2-opt neighborhood
    hc_2opt = HillClimbing(inst)
    _, cost_2opt = hc_2opt.solve(max_evaluations=5000, variant='best', neighborhood='2opt')
    print(f"2-opt neighborhood:  {cost_2opt:.2f}")

    improvement = ((cost_swap - cost_2opt) / cost_swap) * 100
    print(f"\n2-opt improvement: {improvement:.1f}%")

print("\n" + "=" * 70)
print("All examples completed!")
print("=" * 70)
