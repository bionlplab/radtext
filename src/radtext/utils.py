import logging
from typing import Tuple

from bioc import BioCPassage


def intersect(range1: Tuple[float, float], range2: Tuple[float, float]) -> bool:
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


def is_passage_empty(passage: BioCPassage) -> bool:
    return len(passage.text) == 0


def strip_passage(passage: BioCPassage) -> BioCPassage:
    start = 0
    while start < len(passage.text) and passage.text[start].isspace():
        start += 1

    end = len(passage.text)
    while end > start and passage.text[end - 1].isspace():
        end -= 1

    passage.offset += start
    logging.debug('before: %r' % passage.text)
    passage.text = passage.text[start:end]
    logging.debug('after:  %r' % passage.text)
    return passage