"""
TSP Metaheuristics Implementation
Comparison of several algorithms for solving the Traveling Salesman Problem
"""

import random
import math
import time
import numpy as np
from typing import List, Tuple, Callable, Dict, Any


class TSPInstance:
    """Represents a TSP instance with cities and distance matrix."""

    def __init__(self, cities: np.ndarray, name: str = ""):
        """
        Initialize TSP instance.

        Args:
            cities: Array of shape (n, 2) with city coordinates
            name: Name of the instance
        """
        self.cities = cities
        self.n = len(cities)
        self.name = name
        self.distance_matrix = self._compute_distance_matrix()

    def _compute_distance_matrix(self) -> np.ndarray:
        """Compute Euclidean distance matrix."""
        dist = np.zeros((self.n, self.n))
        for i in range(self.n):
            for j in range(self.n):
                if i != j:
                    dist[i, j] = np.linalg.norm(self.cities[i] - self.cities[j])
        return dist

    def evaluate_tour(self, tour: List[int]) -> float:
        """
        Calculate total distance of a tour.

        Args:
            tour: List of city indices representing a tour

        Returns:
            Total distance of the tour
        """
        total = 0.0
        for i in range(len(tour)):
            current = tour[i]
            next_city = tour[(i + 1) % len(tour)]
            total += self.distance_matrix[current, next_city]
        return total


class TSPSolver:
    """Base class for TSP solvers."""

    def __init__(self, instance: TSPInstance):
        self.instance = instance
        self.best_solution = None
        self.best_cost = float('inf')
        self.evaluations = 0

    def _random_swap(self, tour: List[int]) -> List[int]:
        """Generate neighbor by swapping two random positions."""
        neighbor = tour.copy()
        i, j = random.sample(range(len(neighbor)), 2)
        neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
        return neighbor

    def _2opt_swap(self, tour: List[int], i: int, j: int) -> List[int]:
        """Generate 2-opt neighbor."""
        new_tour = tour[:i] + tour[i:j][::-1] + tour[j:]
        return new_tour

    def _get_all_swap_neighbors(self, tour: List[int]) -> List[List[int]]:
        """Generate all neighbors by swap moves."""
        neighbors = []
        n = len(tour)
        for i in range(n):
            for j in range(i + 1, n):
                neighbor = tour.copy()
                neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
                neighbors.append(neighbor)
        return neighbors

    def _get_all_2opt_neighbors(self, tour: List[int]) -> List[List[int]]:
        """Generate all neighbors by 2-opt moves."""
        neighbors = []
        n = len(tour)
        for i in range(1, n - 1):
            for j in range(i + 1, n):
                neighbor = self._2opt_swap(tour, i, j)
                neighbors.append(neighbor)
        return neighbors

    def _evaluate(self, tour: List[int]) -> float:
        """Evaluate tour and increment evaluation counter."""
        self.evaluations += 1
        return self.instance.evaluate_tour(tour)

    def _update_best(self, tour: List[int], cost: float):
        """Update best solution if current is better."""
        if cost < self.best_cost:
            self.best_cost = cost
            self.best_solution = tour.copy()

    def solve(self, **kwargs) -> Tuple[List[int], float]:
        """Solve method to be implemented by subclasses."""
        raise NotImplementedError


class HillClimbing(TSPSolver):
    """Hill Climbing algorithm with best and first improvement variants."""

    def __init__(self, instance: TSPInstance):
        super().__init__(instance)
        self.variant = "best"  # "best" or "first"

    def solve(self, max_evaluations: int = 10000, variant: str = "best",
              neighborhood: str = "swap") -> Tuple[List[int], float]:
        """
        Solve TSP using Hill Climbing.

        Args:
            max_evaluations: Maximum number of evaluations
            variant: "best" for best improvement, "first" for first improvement
            neighborhood: "swap" or "2opt"

        Returns:
            Best tour found and its cost
        """
        self.evaluations = 0
        self.variant = variant

        # Random initial solution
        current_tour = list(range(self.instance.n))
        random.shuffle(current_tour)
        current_cost = self._evaluate(current_tour)
        self._update_best(current_tour, current_cost)

        while self.evaluations < max_evaluations:
            # Generate neighbors
            if neighborhood == "2opt":
                neighbors = self._get_all_2opt_neighbors(current_tour)
            else:  # swap
                neighbors = self._get_all_swap_neighbors(current_tour)

            if variant == "best":
                # Best improvement: evaluate all neighbors
                best_neighbor = None
                best_neighbor_cost = current_cost

                for neighbor in neighbors:
                    if self.evaluations >= max_evaluations:
                        break
                    neighbor_cost = self._evaluate(neighbor)

                    if neighbor_cost < best_neighbor_cost:
                        best_neighbor_cost = neighbor_cost
                        best_neighbor = neighbor

                # If no improvement found, stop
                if best_neighbor is None:
                    break

                current_tour = best_neighbor
                current_cost = best_neighbor_cost
                self._update_best(current_tour, current_cost)

            else:  # first improvement
                # First improvement: stop at first improving neighbor
                improved = False
                for neighbor in neighbors:
                    if self.evaluations >= max_evaluations:
                        break
                    neighbor_cost = self._evaluate(neighbor)

                    if neighbor_cost < current_cost:
                        current_tour = neighbor
                        current_cost = neighbor_cost
                        self._update_best(current_tour, current_cost)
                        improved = True
                        break

                # If no improvement found, stop
                if not improved:
                    break

        return self.best_solution, self.best_cost


class MultiStartHillClimbing(TSPSolver):
    """Multi-start Hill Climbing algorithm."""

    def solve(self, max_evaluations: int = 10000, num_starts: int = 10,
              hc_variant: str = "best", neighborhood: str = "swap") -> Tuple[List[int], float]:
        """
        Solve TSP using Multi-Start Hill Climbing.

        Args:
            max_evaluations: Total evaluations budget
            num_starts: Number of random starts
            hc_variant: HC variant ("best" or "first")
            neighborhood: Neighborhood type ("swap" or "2opt")

        Returns:
            Best tour found and its cost
        """
        self.evaluations = 0
        evaluations_per_run = max_evaluations // num_starts

        for start in range(num_starts):
            if self.evaluations >= max_evaluations:
                break

            hc = HillClimbing(self.instance)
            tour, cost = hc.solve(
                max_evaluations=evaluations_per_run,
                variant=hc_variant,
                neighborhood=neighborhood
            )

            self.evaluations += hc.evaluations
            self._update_best(tour, cost)

        return self.best_solution, self.best_cost


class SimulatedAnnealing(TSPSolver):
    """Simulated Annealing algorithm."""

    def solve(self, max_evaluations: int = 10000, T0: float = 100.0,
              alpha: float = 0.95, Tmin: float = 0.01, neighborhood: str = "swap") -> Tuple[List[int], float]:
        """
        Solve TSP using Simulated Annealing.

        Args:
            max_evaluations: Maximum number of evaluations
            T0: Initial temperature
            alpha: Cooling rate
            Tmin: Minimum temperature
            neighborhood: Neighborhood type ("swap" or "2opt")

        Returns:
            Best tour found and its cost
        """
        self.evaluations = 0

        # Random initial solution
        current_tour = list(range(self.instance.n))
        random.shuffle(current_tour)
        current_cost = self._evaluate(current_tour)
        self._update_best(current_tour, current_cost)

        T = T0

        while self.evaluations < max_evaluations and T > Tmin:
            # Generate random neighbor
            if neighborhood == "2opt":
                # Random 2-opt move
                i = random.randint(1, self.instance.n - 2)
                j = random.randint(i + 1, self.instance.n - 1)
                neighbor = self._2opt_swap(current_tour, i, j)
            else:  # swap
                neighbor = self._random_swap(current_tour)

            neighbor_cost = self._evaluate(neighbor)
            delta = neighbor_cost - current_cost

            # Acceptance criterion
            if delta <= 0 or random.random() < math.exp(-delta / T):
                current_tour = neighbor
                current_cost = neighbor_cost
                self._update_best(current_tour, current_cost)

            # Cooling schedule
            T *= alpha

        return self.best_solution, self.best_cost


class TabuSearch(TSPSolver):
    """Tabu Search algorithm (bonus)."""

    def solve(self, max_evaluations: int = 10000, tabu_size: int = 50,
              neighborhood: str = "swap") -> Tuple[List[int], float]:
        """
        Solve TSP using Tabu Search.

        Args:
            max_evaluations: Maximum number of evaluations
            tabu_size: Size of tabu list
            neighborhood: Neighborhood type ("swap" or "2opt")

        Returns:
            Best tour found and its cost
        """
        self.evaluations = 0
        tabu_list = []

        # Random initial solution
        current_tour = list(range(self.instance.n))
        random.shuffle(current_tour)
        current_cost = self._evaluate(current_tour)
        self._update_best(current_tour, current_cost)

        while self.evaluations < max_evaluations:
            # Generate all neighbors
            if neighborhood == "2opt":
                neighbors = self._get_all_2opt_neighbors(current_tour)
            else:
                neighbors = self._get_all_swap_neighbors(current_tour)

            # Find best neighbor not in tabu list
            best_neighbor = None
            best_neighbor_cost = float('inf')
            best_move = None

            for neighbor in neighbors:
                if self.evaluations >= max_evaluations:
                    break

                # Create move signature
                move = tuple(sorted([i for i in range(len(current_tour))
                                   if current_tour[i] != neighbor[i]][:2]))

                neighbor_cost = self._evaluate(neighbor)

                # Allow tabu move if it improves best cost (aspiration criteria)
                if move not in tabu_list or neighbor_cost < self.best_cost:
                    if neighbor_cost < best_neighbor_cost:
                        best_neighbor_cost = neighbor_cost
                        best_neighbor = neighbor
                        best_move = move

            if best_neighbor is None:
                break

            current_tour = best_neighbor
            current_cost = best_neighbor_cost
            self._update_best(current_tour, current_cost)

            # Update tabu list
            if best_move:
                tabu_list.append(best_move)
                if len(tabu_list) > tabu_size:
                    tabu_list.pop(0)

        return self.best_solution, self.best_cost


class GRASP(TSPSolver):
    """GRASP (Greedy Randomized Adaptive Search Procedure) algorithm (bonus)."""

    def solve(self, max_evaluations: int = 10000, num_iterations: int = 10,
              alpha: float = 0.3, neighborhood: str = "swap") -> Tuple[List[int], float]:
        """
        Solve TSP using GRASP.

        Args:
            max_evaluations: Total evaluations budget
            num_iterations: Number of GRASP iterations
            alpha: Randomness parameter for RCL (0 < alpha <= 1)
            neighborhood: HC neighborhood type

        Returns:
            Best tour found and its cost
        """
        self.evaluations = 0
        evaluations_per_iter = max_evaluations // num_iterations

        for _ in range(num_iterations):
            if self.evaluations >= max_evaluations:
                break

            # Construction phase: greedy randomized nearest neighbor
            tour = self._greedy_randomized_construction(alpha)
            cost = self._evaluate(tour)
            self._update_best(tour, cost)

            # Local search phase
            hc = HillClimbing(self.instance)
            remaining_evals = max_evaluations - self.evaluations
            tour, cost = hc.solve(
                max_evaluations=min(evaluations_per_iter, remaining_evals),
                variant="best",
                neighborhood=neighborhood
            )
            self.evaluations += hc.evaluations
            self._update_best(tour, cost)

        return self.best_solution, self.best_cost

    def _greedy_randomized_construction(self, alpha: float) -> List[int]:
        """Construct solution using greedy randomized nearest neighbor."""
        n = self.instance.n
        unvisited = set(range(n))
        current = random.randint(0, n - 1)
        tour = [current]
        unvisited.remove(current)

        while unvisited:
            # Find nearest unvisited cities
            distances = [(city, self.instance.distance_matrix[current, city])
                        for city in unvisited]
            distances.sort(key=lambda x: x[1])

            # Create RCL (Restricted Candidate List)
            min_dist = distances[0][1]
            max_dist = distances[-1][1]
            threshold = min_dist + alpha * (max_dist - min_dist)
            rcl = [city for city, dist in distances if dist <= threshold]

            # Randomly select from RCL
            next_city = random.choice(rcl)
            tour.append(next_city)
            unvisited.remove(next_city)
            current = next_city

        return tour
