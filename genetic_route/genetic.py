import random
import numpy as np

from ag_params import AGParams
from ga_operators import order_crossover, mutate, roulette_selection, two_opt


class GeneticTSP:

    def __init__(self, dist_matrix, params: AGParams):
        self.dist_matrix = dist_matrix
        self.n_points = dist_matrix.shape[0]
        self.params = params
        self.elite_size = min(params.elite_size, max(1, params.pop_size // 2))

        finite_vals = dist_matrix[np.isfinite(dist_matrix)]
        max_real = finite_vals.max() if finite_vals.size > 0 else 1000.0
        self.blocked_penalty = max_real * self.n_points * 10

        if params.seed is not None:
            random.seed(params.seed)
            np.random.seed(params.seed)

        self.collection_indices = list(range(1, self.n_points - 1))

    def _create_individual(self):
        ind = self.collection_indices.copy()
        random.shuffle(ind)
        return ind

    def _fitness(self, individual):
        route = [0] + individual + [self.n_points - 1]
        total = 0.0
        for i in range(len(route) - 1):
            d = self.dist_matrix[route[i]][route[i + 1]]
            total += self.blocked_penalty if d == float("inf") else d
        return total

    def _rank(self, population):
        ranked = [(self._fitness(ind), ind) for ind in population]
        ranked.sort(key=lambda x: x[0])
        return ranked

    def _local_search(self, individual):
        if len(individual) < 2:
            return individual
        return two_opt(individual, self.dist_matrix, 0, self.n_points - 1, self.blocked_penalty)

    def _breed(self, selected):
        children = selected[:self.elite_size]
        pool = random.sample(selected, len(selected))
        for i in range(self.params.pop_size - self.elite_size):
            p1 = pool[i % len(pool)]
            p2 = pool[(i + 1) % len(pool)]
            child = order_crossover(p1, p2) if random.random() < self.params.crossover_rate else p1.copy()
            children.append(mutate(child, self.params.mutation_rate, self.params.mutation_type))
        return children

    def _count_blocked_legs(self, route):
        return sum(
            1 for i in range(len(route) - 1)
            if self.dist_matrix[route[i]][route[i + 1]] == float("inf")
        )

    def _log_result(self, best_dist, route, generations):
        blocked = self._count_blocked_legs(route)
        if blocked > 0:
            real = best_dist - blocked * self.blocked_penalty
            print(f"  [AG] Resultado final: {real:.1f} m ({real/1000:.2f} km) en {generations} generaciones")
            print(f"  [AG] ADVERTENCIA: {blocked} tramo(s) sin ruta por bloqueos.")
        else:
            print(f"  [AG] Resultado final: {best_dist:.1f} m ({best_dist/1000:.2f} km) "
                  f"en {generations} generaciones (sin tramos bloqueados)")

    def run(self, verbose=True):
        if not self.collection_indices:
            return [0, self.n_points - 1], 0.0, []

        population = [self._create_individual() for _ in range(self.params.pop_size)]
        history = []
        best_overall, best_overall_ind, stale = float("inf"), None, 0
        gen = 0

        for gen in range(self.params.generations):
            ranked = self._rank(population)
            best_dist, best_ind = ranked[0]

            improved_ind = self._local_search(best_ind)
            improved_dist = self._fitness(improved_ind)
            if improved_dist < best_dist:
                best_dist, best_ind = improved_dist, improved_ind
                population[population.index(ranked[0][1])] = improved_ind

            history.append(best_dist)

            if best_dist < best_overall - self.params.min_improvement:
                best_overall, best_overall_ind, stale = best_dist, best_ind, 0
            else:
                stale += 1

            if verbose and gen % self.params.log_interval == 0:
                print(f"  Generacion {gen:4d} | Mejor: {best_dist:.1f} m | Sin mejora: {stale}")

            if self.params.patience > 0 and stale >= self.params.patience:
                if verbose:
                    print(f"  [AG] Parada temprana en generacion {gen} ({self.params.patience} sin mejora)")
                break

            population = self._breed(roulette_selection(ranked, self.elite_size, self.params.pop_size))

        ranked = self._rank(population)
        best_dist, best_ind = ranked[0]
        if best_overall < best_dist and best_overall_ind is not None:
            best_dist, best_ind = best_overall, best_overall_ind

        final_ind = self._local_search(best_ind)
        final_dist = self._fitness(final_ind)
        if final_dist < best_dist:
            best_dist, best_ind = final_dist, final_ind

        best_route = [0] + best_ind + [self.n_points - 1]
        if verbose:
            self._log_result(best_dist, best_route, gen + 1)

        return best_route, best_dist, history
