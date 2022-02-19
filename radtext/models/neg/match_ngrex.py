import logging
import sys
from typing import List, Generator
import networkx as nx
import bioc
import yaml

from radtext.utils import intersect
from radtext.models.neg import ngrex
from radtext.models.neg.constants import NEGATION, UNCERTAINTY
from radtext.models.neg.ngrex import NgrexPattern


class NegNgrexPattern:
    def __init__(self, id, pattern_str: str):
        self.id = id
        self.pattern_str = pattern_str
        self.pattern_obj = self.compile()

    def __str__(self):
        return '[id=%s,pattern=%s]' % (self.id, self.pattern_str)

    def compile(self) -> NgrexPattern:
        return ngrex.compile(self.pattern_str)


def load_ngrex_yml(file) -> List[NegNgrexPattern]:
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
                patterns.append(NegNgrexPattern(p['id'], p['pattern']))
            except TypeError as e:
                logger.error('%s:%s: %s', file, p['id'], e)
    return patterns


class NegGrex:
    def __init__(self):
        self.negation_patterns = []
        self.uncertainty_pre_neg_patterns = []
        self.uncertainty_post_neg_patterns = []
        self.double_negation_patterns = []
        # private
        self._graph = None  # type: nx.DiGraph or None
        self._start = None  # type: int or None
        self._end = None  # type: int or None
        self._ann = None  # type: bioc.BioCAnnotation or None

    def load_yml(self,
                 negation_file,
                 uncertainty_pre_neg_file,
                 uncertainty_post_neg_file,
                 double_neg_file):
        self.negation_patterns = load_ngrex_yml(negation_file)
        self.uncertainty_pre_neg_patterns = load_ngrex_yml(uncertainty_pre_neg_file)
        self.uncertainty_post_neg_patterns = load_ngrex_yml(uncertainty_post_neg_file)
        self.double_negation_patterns = load_ngrex_yml(double_neg_file)

    def load_yml2(self, pattern_file):
        with open(pattern_file) as fp:
            objs = yaml.load(fp, yaml.FullLoader)
        for obj in objs['negation']:
            self.negation_patterns.append(NegNgrexPattern(obj['id'], obj['pattern']))
        for obj in objs['uncertainty_pre']:
            self.uncertainty_pre_neg_patterns.append(NegNgrexPattern(obj['id'], obj['pattern']))
        for obj in objs['uncertainty_post']:
            self.uncertainty_post_neg_patterns.append(NegNgrexPattern(obj['id'], obj['pattern']))
        if 'double_negation' in objs and objs['double_negation'] is not None:
            for obj in objs['double_negation']:
                self.double_negation_patterns.append(NegNgrexPattern(obj['id'], obj['pattern']))

    def setup(self, graph: nx.DiGraph, ann: bioc.BioCAnnotation):
        self._graph = graph
        self._start = ann.total_span.offset
        self._end = ann.total_span.end
        self._ann = ann

    def match_neg(self) -> bool:
        for node in find_nodes(self._graph, self._start, self._end):
            for p in self.negation_patterns:
                for m in p.pattern_obj.finditer(self._graph):
                    n0 = m.group(0)
                    if n0 == node:
                        self._ann.infons[NEGATION] = 'True'
                        self._ann.infons['ngrex_neg_pattern_id'] = p.id
                        self._ann.infons['ngrex_neg_pattern_str'] = p.pattern_str
                        return True
        return False

    def match_double_neg(self) -> bool:
        for node in find_nodes(self._graph, self._start, self._end):
            for p in self.double_negation_patterns:
                for m in p.pattern_obj.finditer(self._graph):
                    n0 = m.group(0)
                    if n0 == node:
                        self._ann.infons[UNCERTAINTY] = 'True'
                        self._ann.infons['ngrex_double_neg_pattern_id'] = p.id
                        self._ann.infons['ngrex_double_neg_pattern_str'] = p.pattern_str
                        return True
        return False

    def match_uncertainty_pre_neg(self) -> bool:
        for node in find_nodes(self._graph, self._start, self._end):
            for p in self.uncertainty_pre_neg_patterns:
                for m in p.pattern_obj.finditer(self._graph):
                    n0 = m.group(0)
                    if n0 == node:
                        self._ann.infons[UNCERTAINTY] = 'True'
                        self._ann.infons['ngrex_uncertainty_pre_neg_pattern_id'] = p.id
                        self._ann.infons['ngrex_uncertainty_pre_neg_pattern_str'] = p.pattern_str
                        return True
        return False

    def match_uncertainty_post_neg(self):
        for node in find_nodes(self._graph, self._start, self._end):
            for p in self.uncertainty_post_neg_patterns:
                for m in p.pattern_obj.finditer(self._graph):
                    n0 = m.group(0)
                    if n0 == node:
                        self._ann.infons[UNCERTAINTY] = 'True'
                        self._ann.infons['ngrex_uncertainty_post_neg_pattern_id'] = p.id
                        self._ann.infons['ngrex_uncertainty_post_neg_pattern_str'] = p.pattern_str
                        return True
        return False


def find_nodes(graph: nx.DiGraph, begin: int, end: int) -> Generator:
    """
    Find the nodes in the graph that are within [begin, end)
    """
    for node in graph.nodes():
        node_start = graph.nodes[node]['start']
        node_end = graph.nodes[node]['end']
        if intersect((begin, end), (node_start, node_end)):
            yield node
