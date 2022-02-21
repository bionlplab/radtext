from typing import List

from bioc import BioCAnnotation, BioCPassage

from radtext.core import BioCProcessor
from radtext.models.constants import UNCERTAINTY, NEGATION


def extend_anns(annotations: List[BioCAnnotation]):
    """Mark all annotations in [begin:end] as type"""
    annotations = sorted(annotations, key=lambda a: (a.total_span.offset, -a.total_span.end))

    for i in range(len(annotations)):
        ai = annotations[i]
        ai_loc = ai.total_span
        if not (NEGATION in ai.infons or UNCERTAINTY in ai.infons):
            continue
        for j in range(i + 1, len(annotations)):
            aj = annotations[j]
            if NEGATION in aj.infons or UNCERTAINTY in aj.infons:
                continue
            aj_loc = aj.total_span
            if ai_loc.offset <= aj_loc.offset and aj_loc.end <= ai_loc.end:
                if NEGATION in ai.infons:
                    aj.infons[NEGATION] = ai.infons[NEGATION]
                if UNCERTAINTY in ai.infons:
                    aj.infons[UNCERTAINTY] = ai.infons[UNCERTAINTY]
                for k in ai.infons.keys():
                    if k in (NEGATION, UNCERTAINTY) or 'pattern_id' in k or 'pattern_str' in k:
                        aj.infons[k] = ai.infons[k]


class NegCleanUp(BioCProcessor):
    def __init__(self, sort_anns: bool = False, extend_anns: bool = True):
        """
        Args:
            sort_anns: sort annotations by its location
            extend_anns: if A covers B, B has the same type as A.
        """
        super(NegCleanUp, self).__init__()
        self.sort_anns = sort_anns
        self.extend_anns = extend_anns

    def process_passage(self, passage: BioCPassage, docid: str = None) -> BioCPassage:
        del passage.sentences[:]

        if self.extend_anns:
            extend_anns(passage.annotations)

        if self.sort_anns:
            anns = passage.annotations
            anns = sorted(anns, key=lambda a: (a.total_span.offset, a.total_span.end))
            for i, ann in enumerate(anns):
                ann.id = str(i)
            passage.annotations = anns
        return passage