import logging
import sys
from typing import List

import yaml

import radtext.utils
from radtext.neg import ngrex
from radtext.neg.constants import NEGATION, UNCERTAINTY, NegPattern, NegResult
from radtext.neg.ngrex import NgrexMatch, NgrexPattern


class NegNgrexPattern(NegPattern):
    def compile(self) -> NgrexPattern:
        return ngrex.compile(self.pattern_str)


class NegNgrexResult(NegResult):
    def __init__(self, category: str, matcher: NgrexMatch, pattern: NegNgrexPattern, *args):
        super(NegNgrexResult, self).__init__(category, matcher, pattern, *args)

    def get_span(self):
        graph = self.matchers[0].graph
        start = sys.maxsize
        end = -1
        for m in self.matchers:
            for n in m.groups():
                start = min(start, graph.nodes[n]['start'])
                end = max(end, graph.nodes[n]['end'])
        return start, end


def load_ngrex_yml(file, type: str) -> List[NegNgrexPattern]:
    """
    Read a pattern file in the yaml format
    """
    logger = logging.getLogger(__name__)
    with open(file) as fp:
        objs = yaml.load(fp, yaml.FullLoader)

    patterns = []
    if objs:
        for p in objs:
            try:
                patterns.append(NegNgrexPattern(p['id'], type, p['pattern']))
            except TypeError as e:
                logger.error('%s:%s: %s', file, p['id'], e)
    return patterns


class NegGrex:
    def __init__(self, negation_file, uncertainty_pre_neg_file, uncertainty_post_neg_file,
                 double_neg_file):
        self.negation_patterns = load_ngrex_yml(negation_file, NEGATION)
        self.uncertainty_pre_neg_patterns = load_ngrex_yml(uncertainty_pre_neg_file, UNCERTAINTY)
        self.uncertainty_post_neg_patterns = load_ngrex_yml(uncertainty_post_neg_file, UNCERTAINTY)
        self.double_neg_patterns = load_ngrex_yml(double_neg_file, UNCERTAINTY)
        # private
        self.__graph = None
        self.__start = None
        self.__end = None

    def setup(self, graph, ann):
        self.__graph = graph
        self.__start = ann.total_span.offset
        self.__end = ann.total_span.end

    def match_neg(self):
        for node in find_nodes(self.__graph, self.__start, self.__end):
            for p in self.negation_patterns:
                for m in p.pattern_obj.finditer(self.__graph):
                    nf = m.group('f')
                    if nf == node:
                        if 'k0' in m.groupindex:
                            nk = m.group('k0')
                            for p2 in self.double_neg_patterns:
                                for m2 in p2.pattern_obj.finditer(self.__graph):
                                    n2 = m2.group('f')
                                    if n2 == nk:
                                        return NegNgrexResult(UNCERTAINTY, m, p, m2, p2)
                        return NegNgrexResult(NEGATION, m, p)
        return None

    def match_uncertainty_pre_neg(self):
        for node in find_nodes(self.__graph, self.__start, self.__end):
            for p in self.uncertainty_pre_neg_patterns:
                for m in p.pattern_obj.finditer(self.__graph):
                    n0 = m.group(0)
                    if n0 == node:
                        return NegNgrexResult(UNCERTAINTY, m, p)
        return None

    def match_uncertainty_post_neg(self):
        for node in find_nodes(self.__graph, self.__start, self.__end):
            for p in self.uncertainty_post_neg_patterns:
                for m in p.pattern_obj.finditer(self.__graph):
                    n0 = m.group(0)
                    if n0 == node:
                        return NegNgrexResult(UNCERTAINTY, m, p)
        return None


def find_nodes(graph, begin, end):
    for node in graph.nodes():
        if radtext.utils.intersect((begin, end), (graph.nodes[node]['start'], graph.nodes[node]['end'])):
            yield node
