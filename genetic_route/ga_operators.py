import random
import numpy as np


def order_crossover(parent1, parent2):
    size = len(parent1)
    a, b = sorted(random.sample(range(size), 2))
    child = [None] * size
    child[a:b] = parent1[a:b]
    fill = [g for g in parent2 if g not in child[a:b]]
    j = 0
    for i in range(size):
        if child[i] is None:
            child[i] = fill[j]
            j += 1
    return child


def mutate_swap(individual, rate):
    ind = individual.copy()
    for i in range(len(ind)):
        if random.random() < rate:
            j = random.randint(0, len(ind) - 1)
            ind[i], ind[j] = ind[j], ind[i]
    return ind


def mutate_inversion(individual, rate):
    ind = individual.copy()
    if len(ind) >= 2 and random.random() < rate:
        a, b = sorted(random.sample(range(len(ind)), 2))
        ind[a:b + 1] = reversed(ind[a:b + 1])
    return ind


def mutate(individual, rate, mutation_type):
    if len(individual) < 2:
        return individual.copy()
    if mutation_type == "inversion":
        return mutate_inversion(individual, rate)
    return mutate_swap(individual, rate)


def roulette_selection(ranked, elite_size, pop_size):
    selected = [ind for _, ind in ranked[:elite_size]]
    weights = [1.0 / (i + 1) for i in range(len(ranked))]
    total_w = sum(weights)
    probs = [w / total_w for w in weights]
    pool = [ind for _, ind in ranked]
    n_select = pop_size - elite_size
    indices = np.random.choice(len(pool), size=n_select, replace=True, p=probs)
    selected += [pool[i] for i in indices]
    return selected


def two_opt(individual, dist_matrix, start_idx, end_idx, blocked_penalty):
    def leg(a, b):
        d = dist_matrix[a][b]
        return blocked_penalty if d == float("inf") else d

    route = [start_idx] + list(individual) + [end_idx]
    improved = True
    while improved:
        improved = False
        for i in range(1, len(route) - 2):
            for j in range(i + 1, len(route) - 1):
                a, b = route[i - 1], route[i]
                c, d = route[j], route[j + 1]
                before = leg(a, b) + leg(c, d)
                after = leg(a, c) + leg(b, d)
                if after < before - 1e-9:
                    route[i:j + 1] = reversed(route[i:j + 1])
                    improved = True
    return route[1:-1]
