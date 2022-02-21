import logging
from typing import List, Generator, Union
import networkx as nx
import bioc
import yaml

from radtext.utils import intersect
from radtext.models.neg import ngrex
from radtext.models.constants import UNCERTAINTY, NEGATION

from radtext.models.neg import semgraph
from cachetools import cached, LRUCache


class NegNgrexPattern:
    def __init__(self, id, pattern_str: str, pattern_obj):
        self.id = id
        self.pattern_str = pattern_str
        self.pattern_obj = pattern_obj

    @staticmethod
    def compile(id, pattern_str: str):
        pattern_obj = ngrex.compile(pattern_str)
        return NegNgrexPattern(id, pattern_str, pattern_obj)

    def __str__(self):
        return '[id=%s,pattern=%s]' % (self.id, self.pattern_str)


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
                patterns.append(NegNgrexPattern.compile(p['id'], p['pattern']))
            except TypeError as e:
                logger.error('%s:%s: %s', file, p['id'], e)
    return patterns


class NegGrexAssertion:
    def __init__(self, patterns: 'NegGrexPatterns', graph: nx.DiGraph, ann: bioc.BioCAnnotation):
        self.graph = graph  # type: nx.DiGraph
        self.ann = ann  # type: bioc.BioCAnnotation
        self.start = ann.total_span.offset  # type: int
        self.end = ann.total_span.end  # type: int
        self.patterns = patterns # type: NegGrexPatterns

    def assert_neg(self) -> bool:
        for node in find_nodes(self.graph, self.start, self.end):
            for p in self.patterns.negation_patterns:
                for m in p.pattern_obj.finditer(self.graph):
                    n0 = m.group(0)
                    if n0 == node:
                        self.ann.infons[NEGATION] = True
                        self.ann.infons['ngrex_neg_pattern_id'] = p.id
                        self.ann.infons['ngrex_neg_pattern_str'] = p.pattern_str
                        return True
        return False

    def assert_double_neg(self) -> bool:
        for node in find_nodes(self.graph, self.start, self.end):
            for p in self.patterns.double_negation_patterns:
                for m in p.pattern_obj.finditer(self.graph):
                    n0 = m.group(0)
                    if n0 == node:
                        self.ann.infons[UNCERTAINTY] = True
                        self.ann.infons['ngrex_double_neg_pattern_id'] = p.id
                        self.ann.infons['ngrex_double_neg_pattern_str'] = p.pattern_str
                        return True
        return False

    def assert_uncertainty_pre_neg(self) -> bool:
        for node in find_nodes(self.graph, self.start, self.end):
            for p in self.patterns.uncertainty_pre_neg_patterns:
                for m in p.pattern_obj.finditer(self.graph):
                    n0 = m.group(0)
                    if n0 == node:
                        self.ann.infons[UNCERTAINTY] = True
                        self.ann.infons['ngrex_uncertainty_pre_neg_pattern_id'] = p.id
                        self.ann.infons['ngrex_uncertainty_pre_neg_pattern_str'] = p.pattern_str
                        return True
        return False

    def assert_uncertainty_post_neg(self):
        for node in find_nodes(self.graph, self.start, self.end):
            for p in self.patterns.uncertainty_post_neg_patterns:
                for m in p.pattern_obj.finditer(self.graph):
                    n0 = m.group(0)
                    if n0 == node:
                        self.ann.infons[UNCERTAINTY] = True
                        self.ann.infons['ngrex_uncertainty_post_neg_pattern_id'] = p.id
                        self.ann.infons['ngrex_uncertainty_post_neg_pattern_str'] = p.pattern_str
                        return True
        return False


class NegGrexPatterns:
    def __init__(self):
        self.negation_patterns = []
        self.uncertainty_pre_neg_patterns = []
        self.uncertainty_post_neg_patterns = []
        self.double_negation_patterns = []

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
            self.negation_patterns.append(NegNgrexPattern.compile(obj['id'], obj['pattern']))
        for obj in objs['uncertainty_pre']:
            self.uncertainty_pre_neg_patterns.append(NegNgrexPattern.compile(obj['id'], obj['pattern']))
        for obj in objs['uncertainty_post']:
            self.uncertainty_post_neg_patterns.append(NegNgrexPattern.compile(obj['id'], obj['pattern']))
        if 'double_negation' in objs and objs['double_negation'] is not None:
            for obj in objs['double_negation']:
                self.double_negation_patterns.append(NegNgrexPattern.compile(obj['id'], obj['pattern']))

    def assert_(self, passage: bioc.BioCPassage, ann: bioc.BioCAnnotation, docid):
        offset = ann.total_span.offset
        sentence = find_sentence(passage, offset)
        if not sentence:
            raise ValueError('%s: cannot find sentence at %s' % (docid, offset))

        try:
            g = get_graph(sentence)
        except Exception as e:
            raise ValueError('%s:%s: Cannot parse graph: %s', docid, sentence.offset, e)

        return NegGrexAssertion(self, g, ann)

    def assert_graph_(self, graph: nx.DiGraph, ann: bioc.BioCAnnotation):
        return NegGrexAssertion(self, graph, ann)


@cached(cache=LRUCache(maxsize=64))
def get_graph(sentence):
    return semgraph.load(sentence)


def find_nodes(graph: nx.DiGraph, begin: int, end: int) -> Generator:
    """
    Find the nodes in the graph that are within [begin, end)
    """
    for node in graph.nodes():
        node_start = graph.nodes[node]['start']
        node_end = graph.nodes[node]['end']
        if intersect((begin, end), (node_start, node_end)):
            yield node


def find_sentence(passage: bioc.BioCPassage, offset: int) -> Union[bioc.BioCSentence, None]:
    for sentence in passage.sentences:
        if sentence.offset <= offset < sentence.offset + len(sentence.text):
            return sentence
    return None