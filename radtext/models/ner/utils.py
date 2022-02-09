from typing import List


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


def remove_duplicates(matches: List[NERMatch]) -> List[NERMatch]:
    s = {(m.start, m.end, m.concept_id): m for m in matches}
    return sorted(s.values(), key=lambda m: (m.start, m.end))


def longest_matching(matches: List[NERMatch]) -> List[NERMatch]:
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