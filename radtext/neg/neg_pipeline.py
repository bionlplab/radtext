import logging
from typing import Union

import tqdm
from bioc import BioCPassage, BioCSentence

from radtext.core import BioCProcessor
from radtext.neg import semgraph
from radtext.neg.constants import NegResult
from radtext.neg.match_ngrex import NegGrex
from radtext.neg.match_regex import NegRegex


def mark_ann(ann, match: NegResult):
    ann.infons[match.category] = 'True'
    ann.infons['negbio_pattern_id'] = match.id
    ann.infons['negbio_pattern_str'] = match.pattern_strs
    return ann


def create_graph(sentence: BioCSentence, docid):
    try:
        g = semgraph.load(sentence)
        return g
    except Exception as e:
        raise ValueError('%s:%s: Cannot parse graph: %s', docid, sentence.offset, e)


def find_sentence(passage: BioCPassage, offset: int) -> Union[BioCSentence, None]:
    for sentence in passage.sentences:
        if sentence.offset <= offset < sentence.offset + len(sentence.text):
            return sentence
    return None


class BioCNeg(BioCProcessor):
    def __init__(self, regex_actor: NegRegex, ngrex_actor: NegGrex, verbose=False):
        self.regex_actor = regex_actor
        self.ngrex_actor = ngrex_actor
        self.graph_cache = {}
        self.verbose = verbose

    def process_passage(self, passage: BioCPassage, docid: str = None) -> BioCPassage:
        self.graph_cache.clear()
        for ann in tqdm.tqdm(passage.annotations, disable=not self.verbose):
            self.regex_actor.setup(passage, ann)

            # uncertain pre neg
            matchobj = self.regex_actor.match_uncertainty_pre_neg()
            if matchobj:
                mark_ann(ann, matchobj)
                continue

            # graph
            try:
                g = self.get_graph(passage, ann, docid)
            except Exception as e:
                logging.error('%s', e)
                continue
            self.ngrex_actor.setup(g, ann)

            matchobj = self.ngrex_actor.match_uncertainty_pre_neg()
            if matchobj:
                mark_ann(ann, matchobj)
                continue
            # neg
            matchobj = self.regex_actor.match_neg()
            if matchobj:
                mark_ann(ann, matchobj)
                continue
            matchobj = self.ngrex_actor.match_neg()
            if matchobj:
                mark_ann(ann, matchobj)
                continue
            # uncertain post neg
            matchobj = self.regex_actor.match_uncertainty_post_neg()
            if matchobj:
                mark_ann(ann, matchobj)
                continue
            matchobj = self.ngrex_actor.match_uncertainty_post_neg()
            if matchobj:
                mark_ann(ann, matchobj)
                continue

        return passage

    def get_graph(self, passage, ann, docid):
        offset = ann.total_span.offset

        sentence = find_sentence(passage, offset)
        # logging.debug("find_sentence: %.4fs" % (time.time() - start_time))

        if not sentence:
            raise ValueError('%s: cannot find sentence at %s' % (docid, offset))

        k = (docid, sentence.offset)
        if k in self.graph_cache:
            g = self.graph_cache[k]
        else:
            g = create_graph(sentence, docid)
            # if docid == 'CXR2837':
            #     print(g)
            # logging.debug("create_graph: %.4fs" % (time.time() - start_time))
            self.graph_cache[k] = g

        if not g:
            raise ValueError('%s:%s: cannot find graph in sentence' % (docid, sentence.offset))
        return g
