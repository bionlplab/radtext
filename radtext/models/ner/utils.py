from itertools import permutations
from typing import List, Set

from intervaltree import IntervalTree
from nltk.corpus import stopwords

from radtext.utils import intersect


class NERMatch:
    def __init__(self):
        # concept id
        self.concept_id = None  # type: str | None
        # character start position of the extracted term
        self.start = None       # type: int | None
        # character end position of the extracted term
        self.end = None         # type: int | None
        self.pattern = None
        self.concept = None     # type: str | None
        self.text = None        # type: str | None

    def __str__(self):
        return 'NERMatch[concept_id=%s,start=%s,end=%s,text=%s,pattern=%s,concept=%s]' \
            % (self.concept_id, self.start, self.end, self.text, self.pattern, self.concept)


def remove_duplicates(matches: List[NERMatch]) -> List[NERMatch]:
    s = {(m.start, m.end, m.concept_id): m for m in matches}
    return sorted(s.values(), key=lambda m: (m.start, m.end))


def longest_matching2(matches: List[NERMatch]) -> List[NERMatch]:
    results = []
    for i, mi in enumerate(matches):
        # print(mi.start, mi.end, mi.text)
        enclosed = False
        for j, mj in enumerate(matches):
            if i == j:
                continue
            if (mj.start < mi.start and mi.end <= mj.end) or (mj.start <= mi.start and mi.end < mj.end):
                # print(mj.start, mj.end, mj.text)
                # print(mi.start, mi.end, mi.text)
                # print('Remove', mi.start, mi.end, mi.text)
                enclosed = True
                break
        if not enclosed:
            results.append(mi)
    return results


def longest_matching(matches: List[NERMatch]) -> List[NERMatch]:
    tree = IntervalTree()
    for m in matches:
        tree[m.start:m.end] = m

    nodes = list(tree)
    for n1, n2 in permutations(nodes, 2):
        if n2.begin <= n1.begin <= n1.end <= n2.end:
            if n1 in tree:
                tree.remove(n1)

    results = [v.data for v in sorted(tree)]
    return results


def remove_excludes(includes: List[NERMatch], excludes: List[NERMatch]) -> List[NERMatch]:
    results = []
    for mi in includes:
        overlapped = False
        for mj in excludes:
            if intersect((mi.start, mi.end), (mj.start, mj.end)) and mi.concept_id == mj.concept_id:
                overlapped = True
                break
        if not overlapped:
            results.append(mi)
    return results


def filter_number(matches: List[NERMatch]) -> List[NERMatch]:
    results = []
    for m in matches:
        try:
            float(m.text)
        except:
            results.append(m)
    return results


def filter_stop_words(matches: List[NERMatch], stop_words: Set) -> List[NERMatch]:
    return [a for a in matches if a.text not in stop_words]


STOP_WORDS = set(stopwords.words('english'))