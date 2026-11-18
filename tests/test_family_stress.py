"""
Family tree / breeding eligibility stress test.

Self-contained benchmark for:
- NumPy-backed direct parent-child storage
- Multi-generational biological family-tree construction
- Lazy, depth-limited biological ancestor traversal
- Short-circuit breeding eligibility checks
- Query latency and Python-tracked memory

Default workload:
    1,000 founders
    1,000 births per generation
    9 birth generations
    10,000 total pawns
    50,000 breeding checks

Run:
    python family_stress_test.py

Optional:
    python family_stress_test.py --queries 100000 --max-depth 4
"""

from __future__ import annotations

import argparse
import random
import statistics
import time
import tracemalloc
from collections import deque

import numpy as np

from data.social.family_graph import FamilyGraph
from simulation.entity_systems.ancestry_system import AncestrySystem

family_g = FamilyGraph()
ancestry_system = AncestrySystem(None, family_g)


def generate_population(
    family: FamilyGraph,
    founder_count: int = 1000,
    births_per_generation: int = 1000,
    generations: int = 9,
    seed: int = 42,
) -> dict:
    """Create founder pawns followed by repeated generations of offspring.

    Every generated child receives two biological parents from the
    immediately preceding generation. Pairings are random and are not
    filtered through can_breed: this is a graph/performance stress test.
    """
    if founder_count < 2:
        raise ValueError("founder_count must be at least 2")
    if births_per_generation < 1:
        raise ValueError("births_per_generation must be at least 1")
    if generations < 0:
        raise ValueError("generations cannot be negative")

    rng = random.Random(seed)

    next_id = 0
    previous_generation = list(range(founder_count))
    next_id = founder_count

    parent_child_pairs = []
    sibling_pairs = []

    for _generation in range(generations):
        current_generation = []
        children_by_parent_pair = {}

        for _ in range(births_per_generation // 4):
            parent_a, parent_b = rng.sample(previous_generation, 2)

            for _ in range(4):
                child = next_id
                next_id += 1

                family.add_biological_parent(parent_a, child)
                family.add_biological_parent(parent_b, child)

                parent_child_pairs.append((parent_a, child))
                parent_child_pairs.append((parent_b, child))

                current_generation.append(child)

                parent_key = (
                    (parent_a, parent_b)
                    if parent_a < parent_b
                    else (parent_b, parent_a)
                )
                siblings = children_by_parent_pair.setdefault(parent_key, [])

                if siblings:
                    sibling_pairs.append((siblings[0], child))

                siblings.append(child)

        previous_generation = current_generation

    return {
        "pawn_count": next_id,
        "parent_child_pairs": parent_child_pairs,
        "sibling_pairs": sibling_pairs,
    }


def generate_queries(
    population: dict,
    query_count: int = 50_000,
    seed: int = 123,
) -> list[tuple[int, int]]:
    """Generate a repeatable mixture of close-relative and random queries."""
    rng = random.Random(seed)
    pawn_count = population["pawn_count"]

    parent_child = population["parent_child_pairs"]
    siblings = population["sibling_pairs"]

    queries = []

    for _ in range(query_count):
        roll = rng.random()

        if roll < 0.20 and parent_child:
            pair = rng.choice(parent_child)
        elif roll < 0.40 and siblings:
            pair = rng.choice(siblings)
        else:
            pair = tuple(rng.sample(range(pawn_count), 2))

        queries.append(pair)

    return queries


def percentile(sorted_values: list[int], fraction: float) -> int:
    if not sorted_values:
        return 0
    index = min(int((len(sorted_values) - 1) * fraction), len(sorted_values) - 1)
    return sorted_values[index]


def benchmark_family(
    founder_count: int = 1000,
    births_per_generation: int = 1000,
    generations: int = 9,
    query_count: int = 50_000,
    max_depth: int = 3,
    seed: int = 42,
) -> dict:
    print("\nBuilding family tree...")
    tracemalloc.start()
    memory_before, _ = tracemalloc.get_traced_memory()

    build_start = time.perf_counter()
    population = generate_population(
        family_g,
        founder_count=founder_count,
        births_per_generation=births_per_generation,
        generations=generations,
        seed=seed,
    )
    build_seconds = time.perf_counter() - build_start

    memory_current, memory_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"Pawn count:             {population['pawn_count']:,}")
    print(f"Birth generations:      {generations:,}")
    print(f"Parent-child edges:     {family_g.connection_count:,}")
    print(f"Tree construction:      {build_seconds:.4f} seconds")
    print(
        "Python-tracked memory: " f"{(memory_current - memory_before) / 1024**2:.2f} MB"
    )
    print("Python-tracked peak:   " f"{memory_peak / 1024**2:.2f} MB")
    print(
        "Note: tracemalloc reports Python-tracked allocations; "
        "it may not include all NumPy buffer memory."
    )

    print("\nPreparing breeding queries...")
    queries = generate_queries(
        population,
        query_count=query_count,
        seed=seed + 1,
    )

    # Warm-up calls are excluded from measurements.
    for pawn_a, pawn_b in queries[: min(100, len(queries))]:
        ancestry_system.can_breed(pawn_a, pawn_b, max_depth=max_depth)

    print(f"Running {len(queries):,} breeding checks (depth={max_depth})...")

    timings_ns = []
    prohibited = 0

    query_start = time.perf_counter()
    for pawn_a, pawn_b in queries:
        start_ns = time.perf_counter_ns()
        allowed = ancestry_system.can_breed(
            pawn_a,
            pawn_b,
            max_depth=max_depth,
        )
        timings_ns.append(time.perf_counter_ns() - start_ns)

        if not allowed:
            prohibited += 1

    total_query_seconds = time.perf_counter() - query_start
    timings_ns.sort()

    average_us = statistics.mean(timings_ns) / 1000 if timings_ns else 0
    median_us = statistics.median(timings_ns) / 1000 if timings_ns else 0
    p95_us = percentile(timings_ns, 0.95) / 1000
    p99_us = percentile(timings_ns, 0.99) / 1000
    queries_per_second = (
        len(queries) / total_query_seconds if total_query_seconds else 0
    )

    print("\n" + "-" * 48)
    print("BREEDING CHECK RESULTS")
    print("-" * 48)
    print(f"Total query time:       {total_query_seconds:.4f} seconds")
    print(f"Average latency:        {average_us:.2f} microseconds")
    print(f"Median latency:         {median_us:.2f} microseconds")
    print(f"95th percentile:        {p95_us:.2f} microseconds")
    print(f"99th percentile:        {p99_us:.2f} microseconds")
    print(f"Throughput:             {queries_per_second:,.0f} checks/second")
    print(f"Prohibited pairs:       {prohibited:,}")
    print(f"Allowed pairs:          {len(queries) - prohibited:,}")

    return {
        "pawns": population["pawn_count"],
        "edges": family_g.connection_count,
        "build_seconds": build_seconds,
        "query_seconds": total_query_seconds,
        "average_us": average_us,
        "median_us": median_us,
        "p95_us": p95_us,
        "p99_us": p99_us,
        "queries_per_second": queries_per_second,
        "prohibited": prohibited,
    }


def run_scaling_tests(query_count: int, max_depth: int) -> None:
    """Run the three population sizes used in the initial test plan."""
    configurations = [
        (100, 100, 4),  # 500 pawns
        (500, 500, 3),  # 2,000 pawns
        (1000, 1000, 9),  # 10,000 pawns
    ]

    results = []

    for founders, births, generations in configurations:
        expected_pawns = founders + births * generations

        print("\n" + "=" * 60)
        print(f"STRESS TEST: {expected_pawns:,} PAWNS")
        print("=" * 60)

        result = benchmark_family(
            founder_count=founders,
            births_per_generation=births,
            generations=generations,
            query_count=query_count,
            max_depth=max_depth,
        )
        results.append(result)

    print("\n\nSCALING SUMMARY")
    print("=" * 90)
    print(
        f"{'Pawns':>10} {'Edges':>10} {'Build (s)':>12} "
        f"{'Avg (us)':>12} {'P95 (us)':>12} {'Checks/s':>12}"
    )
    print("-" * 90)

    for result in results:
        print(
            f"{result['pawns']:>10,} "
            f"{result['edges']:>10,} "
            f"{result['build_seconds']:>12.4f} "
            f"{result['average_us']:>12.2f} "
            f"{result['p95_us']:>12.2f} "
            f"{result['queries_per_second']:>12,.0f}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Stress-test multi-generational family relationships."
    )
    parser.add_argument(
        "--queries",
        type=int,
        default=50_000,
        help="Breeding checks per population size (default: 50000)",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=3,
        help="Maximum biological ancestor depth per pawn (default: 3)",
    )
    parser.add_argument(
        "--single",
        action="store_true",
        help="Run only the 10,000-pawn default workload.",
    )

    args = parser.parse_args()

    if args.queries < 1:
        parser.error("--queries must be at least 1")
    if args.max_depth < 0:
        parser.error("--max-depth cannot be negative")

    print("FAMILY TREE / BREEDING STRESS TEST")
    print(f"Queries per workload: {args.queries:,}")
    print(f"Ancestor depth:       {args.max_depth}")

    if args.single:
        benchmark_family(
            founder_count=1000,
            births_per_generation=1000,
            generations=9,
            query_count=args.queries,
            max_depth=args.max_depth,
        )
    else:
        run_scaling_tests(
            query_count=args.queries,
            max_depth=args.max_depth,
        )


if __name__ == "__main__":
    main()
