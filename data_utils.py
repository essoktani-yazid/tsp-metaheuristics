"""
Data generation and utilities for TSP instances
"""

import numpy as np
import json
import os
from typing import List, Tuple
from algorithms import TSPInstance


def generate_random_instance(n: int, seed: int = None) -> TSPInstance:
    """
    Generate a random TSP instance.

    Args:
        n: Number of cities
        seed: Random seed for reproducibility

    Returns:
        TSPInstance object
    """
    if seed is not None:
        np.random.seed(seed)

    cities = np.random.uniform(0, 100, size=(n, 2))
    return TSPInstance(cities, name=f"random_{n}")


def load_instance_from_file(filepath: str) -> TSPInstance:
    """
    Load TSP instance from JSON file.

    File format:
    {
        "name": "instance_name",
        "cities": [[x1, y1], [x2, y2], ...]
    }
    """
    with open(filepath, 'r') as f:
        data = json.load(f)

    cities = np.array(data['cities'])
    return TSPInstance(cities, name=data.get('name', 'loaded_instance'))


def save_instance_to_file(instance: TSPInstance, filepath: str):
    """Save TSP instance to JSON file."""
    data = {
        'name': instance.name,
        'cities': instance.cities.tolist()
    }

    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def create_standard_instances():
    """Create three standard instances (A, B, C) for the project."""
    instances = {
        'A': generate_random_instance(20, seed=42),
        'B': generate_random_instance(50, seed=43),
        'C': generate_random_instance(80, seed=44)
    }

    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(data_dir, exist_ok=True)

    for name, instance in instances.items():
        filepath = os.path.join(data_dir, f'instance_{name}.json')
        save_instance_to_file(instance, filepath)
        print(f"Created instance {name}: {filepath}")

    return instances


def load_standard_instances() -> dict:
    """Load the three standard instances."""
    instances = {}
    data_dir = os.path.join(os.path.dirname(__file__), 'data')

    for name in ['A', 'B', 'C']:
        filepath = os.path.join(data_dir, f'instance_{name}.json')
        if os.path.exists(filepath):
            instances[name] = load_instance_from_file(filepath)
        else:
            print(f"Warning: Instance {name} not found at {filepath}")

    return instances


def nearest_neighbor_heuristic(instance: TSPInstance, start_city: int = 0) -> Tuple[List[int], float]:
    """
    Nearest Neighbor heuristic for initial solution.

    Args:
        instance: TSP instance
        start_city: Starting city

    Returns:
        Tour and its cost
    """
    unvisited = set(range(instance.n))
    current = start_city
    tour = [current]
    unvisited.remove(current)

    while unvisited:
        nearest = min(unvisited,
                     key=lambda city: instance.distance_matrix[current, city])
        tour.append(nearest)
        unvisited.remove(nearest)
        current = nearest

    cost = instance.evaluate_tour(tour)
    return tour, cost


if __name__ == "__main__":
    # Create standard instances
    create_standard_instances()

    # Test loading
    print("\nLoading instances...")
    instances = load_standard_instances()
    for name, inst in instances.items():
        print(f"Instance {name}: {inst.n} cities")

    # Test nearest neighbor heuristic
    print("\nTesting Nearest Neighbor heuristic...")
    if 'A' in instances:
        tour, cost = nearest_neighbor_heuristic(instances['A'])
        print(f"Instance A - NN tour cost: {cost:.2f}")
