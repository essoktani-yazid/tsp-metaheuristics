"""
Initialize project: Generate instances and run quick test
"""

import sys
import os

# Add project directory to path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

from data_utils import create_standard_instances, load_standard_instances
from algorithms import HillClimbing, SimulatedAnnealing
import time


def main():
    print("="*70)
    print("TSP METAHEURISTICS PROJECT - INITIALIZATION")
    print("="*70)

    # Step 1: Create instances
    print("\n[1] Creating standard instances...")
    try:
        instances = create_standard_instances()
        print(f"✓ Successfully created {len(instances)} instances")
    except Exception as e:
        print(f"✗ Error creating instances: {e}")
        return False

    # Step 2: Load instances
    print("\n[2] Loading instances...")
    try:
        instances = load_standard_instances()
        if not instances:
            print("✗ No instances found")
            return False
        for name, inst in instances.items():
            print(f"  ✓ Instance {name}: {inst.n} cities")
    except Exception as e:
        print(f"✗ Error loading instances: {e}")
        return False

    # Step 3: Test algorithms
    print("\n[3] Running quick algorithm tests...")
    print("-" * 70)

    try:
        instance = instances['A']
        max_evals = 1000

        print(f"\nTesting on Instance A ({instance.n} cities, max {max_evals} evals):\n")

        # Hill Climbing - Best Improvement
        print("  Hill Climbing (Best Improvement)...", end='', flush=True)
        start = time.time()
        hc = HillClimbing(instance)
        tour, cost = hc.solve(max_evaluations=max_evals, variant='best', neighborhood='swap')
        elapsed = time.time() - start
        print(f" Cost: {cost:.2f}, Time: {elapsed:.3f}s")

        # Hill Climbing - First Improvement
        print("  Hill Climbing (First Improvement)...", end='', flush=True)
        start = time.time()
        hc = HillClimbing(instance)
        tour, cost = hc.solve(max_evaluations=max_evals, variant='first', neighborhood='swap')
        elapsed = time.time() - start
        print(f" Cost: {cost:.2f}, Time: {elapsed:.3f}s")

        # Simulated Annealing
        print("  Simulated Annealing...", end='', flush=True)
        start = time.time()
        sa = SimulatedAnnealing(instance)
        tour, cost = sa.solve(max_evaluations=max_evals, T0=100.0, alpha=0.95)
        elapsed = time.time() - start
        print(f" Cost: {cost:.2f}, Time: {elapsed:.3f}s")

        print("\n✓ All algorithms working correctly!")

    except Exception as e:
        print(f"\n✗ Error during algorithm testing: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Step 4: Summary
    print("\n" + "="*70)
    print("INITIALIZATION COMPLETE")
    print("="*70)
    print("\nNext steps:")
    print("  1. Review the instances in: data/")
    print("  2. Run experiments: python experiment.py")
    print("  3. Create a custom script for full experiments")
    print("  4. See README.md for detailed documentation")
    print("="*70)

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
