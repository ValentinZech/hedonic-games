import sys
from itertools import chain, combinations


def print_strerr(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(1, len(s)+1))


def all_partitions(collection):
    if len(collection) == 1:
        yield [set(collection)]
        return

    first_elem = collection[0]
    for subpartition in all_partitions(collection[1:]):
        # insert first_elem in each of the subpartition's subsets
        for i, subset in enumerate(subpartition):
            yield subpartition[:i] + [subset.union({first_elem})] + subpartition[i + 1:]
        # put first_elem in its own subset
        yield [{first_elem}] + subpartition
