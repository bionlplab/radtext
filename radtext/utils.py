from typing import Tuple


def intersect(range1: Tuple[int, int], range2: Tuple[int, int]) -> bool:
    """
    Args:
        range1: [begin, end)
        range2: [begin, end)
    """
    if range1[0] <= range2[0] < range1[1]:
        return True
    elif range1[0] < range2[1] <= range1[1]:
        return True
    elif range2[0] <= range1[0] < range2[1]:
        return True
    elif range2[0] < range1[1] <= range2[1]:
        return True
    return False


def contains(func, iterable):
    """
    Return true if one element of iterable for which function returns true.
    """
    if func is None:
        func = bool
    for x in iterable:
        if func(x):
            return True
    return False