import argparse
import gc
import random
import time
import tracemalloc
import numpy as np

from data.social.relationship_graph import RelationshipGraph
from simulation.simulation import Simulation


def benchmark_time(function, iterations):
    """Return average operation time in microseconds."""

    gc.collect()

    start = time.perf_counter()

    for _ in range(iterations):
        function()

    elapsed = time.perf_counter() - start

    return (elapsed / iterations) * 1_000_000


def run_benchmark(pawn_count, density=0.10, seed=42):
    print(f"\n{'=' * 65}")
    print(f"Benchmark: {pawn_count:,} pawns")
    print(f"{'=' * 65}")

    rng = random.Random(seed)

    # --------------------------------------------------
    # 1. Create pawns
    # --------------------------------------------------

    simulation = Simulation()

    start = time.perf_counter()

    for _ in range(pawn_count):
        simulation.spawn_entity("base.cat")

    pawn_creation_time = time.perf_counter() - start

    print(f"Pawn creation: {pawn_creation_time:.4f}s")

    # --------------------------------------------------
    # 2. Create relationships
    # --------------------------------------------------

    store = simulation.relationships

    possible_pairs = pawn_count * (pawn_count - 1) // 2
    target_pairs = int(possible_pairs * density)

    print(f"Target relationships: {target_pairs:,}")

    tracemalloc.start()
    gc.collect()

    start = time.perf_counter()

    while store.relationship_count < target_pairs:
        a = rng.randrange(pawn_count)
        b = rng.randrange(pawn_count)

        if a == b:
            continue

        store.get_or_create_index(a, b)

    creation_time = time.perf_counter() - start

    current_memory, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"Relationship creation: {creation_time:.4f}s")
    print(f"Creation throughput: " f"{target_pairs / creation_time:,.0f} pairs/sec")

    print(f"Tracked memory: {current_memory / 1024 / 1024:.2f} MB")

    print(f"Peak tracked memory: {peak_memory / 1024 / 1024:.2f} MB")

    # --------------------------------------------------
    # 3. Prepare existing relationships for testing
    # --------------------------------------------------

    endpoints = store.endpoints[: store.count]

    # Select random existing pairs
    sample_count = min(100_000, target_pairs)

    sample_indices = rng.sample(range(target_pairs), sample_count)

    sample_pairs = [
        (int(endpoints[i, 0]), int(endpoints[i, 1])) for i in sample_indices
    ]

    # --------------------------------------------------
    # 4. Lookup benchmark
    # --------------------------------------------------

    lookup_rng = random.Random(seed + 1)
    lookup_pairs = [
        sample_pairs[lookup_rng.randrange(sample_count)] for _ in range(100_000)
    ]

    lookup_position = 0

    def lookup_test():
        nonlocal lookup_position

        a, b = lookup_pairs[lookup_position]
        lookup_position += 1

        if lookup_position == len(lookup_pairs):
            lookup_position = 0

        store.get_metrics(a, b)

    lookup_time = benchmark_time(lookup_test, 100_000)

    print(f"Lookup: {lookup_time:.3f} us/op")

    # --------------------------------------------------
    # 5. Modification benchmark
    # --------------------------------------------------

    modification_rng = random.Random(seed + 2)

    modification_pairs = [
        sample_pairs[modification_rng.randrange(sample_count)] for _ in range(100_000)
    ]

    modification_position = 0

    def modification_test():
        nonlocal modification_position

        a, b = modification_pairs[modification_position]
        modification_position += 1

        if modification_position == len(modification_pairs):
            modification_position = 0

        store.adjust_metric(a, b, RelationshipGraph.LIKE, 1)

    modification_time = benchmark_time(modification_test, 100_000)

    print(f"Modification: {modification_time:.3f} us/op")

    # --------------------------------------------------
    # 6. Pawn relationship retrieval
    # --------------------------------------------------

    pawn_samples = [rng.randrange(pawn_count) for _ in range(1000)]

    retrieval_position = 0

    def retrieval_test():
        nonlocal retrieval_position

        pawn = pawn_samples[retrieval_position]
        retrieval_position += 1

        if retrieval_position == len(pawn_samples):
            retrieval_position = 0

        # Consume the iterator so we measure actual iteration
        sum(1 for _ in store.iter_for_pawn(pawn))

    retrieval_time = benchmark_time(retrieval_test, 1000)

    print(f"Pawn retrieval: {retrieval_time:.3f} us/op")

    # --------------------------------------------------
    # 7. Results
    # --------------------------------------------------

    print("\n--- Summary ---")

    print(f"Pawns: {pawn_count:,}")
    print(f"Relationships: {store.relationship_count:,}")
    print(f"Density: {density * 100:.1f}%")
    print(f"Creation: {creation_time:.3f}s")
    print(f"Lookup: {lookup_time:.3f} us/op")
    print(f"Modification: {modification_time:.3f} us/op")
    print(f"Retrieval: {retrieval_time:.3f} us/op")

    print(f"Tracked memory: {current_memory / 1024 / 1024:.2f} MB")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--sizes", nargs="+", type=int, default=[500, 1000, 2000])

    parser.add_argument("--density", type=float, default=0.10)

    args = parser.parse_args()

    for size in args.sizes:
        run_benchmark(size, args.density)


if __name__ == "__main__":
    main()
