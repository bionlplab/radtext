import logging
from os import PathLike
from pathlib import Path
from typing import Dict, List, Generator, Tuple, Union

import networkx as nx
import pandas as pd
import tqdm
from spacy.matcher import PhraseMatcher

from radtext.models.ner.ner_spacy import NerSpacyPhraseMatchers


def get_class_id(url: str) -> str:
    """http://www.radlex.org/RID/#RID43314"""
    if len(url) == 0:
        return 'ROOT'
    elif '/#' in url:
        return url[url.rfind('/') + 2:]
    elif '/' in url:
        return url[url.rfind('/') + 1:]
    else:
        return url


def descendants(src, dst, rids: List[str]):
    radlex = RadLex4(src)
    G = radlex.get_graph()
    rows = []
    for rid in rids:
        for n in nx.descendants(G, rid):
            rows.append(G.nodes[n]['item'].row)

    df = pd.DataFrame(rows)
    df.to_excel(dst, index=False)


class RadLexItem:
    def __init__(self):
        self.concept_id = None
        self.preferred_name = None
        self.synonyms = []
        self.parents = []
        self.row = None

    def __str__(self):
        return '[concept_id=%s,preferred_name=%s,synonyms=%s,parents=%s]' % \
               (self.concept_id, self.preferred_name, self.synonyms, self.parents)


class RadLex4:
    def __init__(self, filename):
        self.filename = filename
        self.df = pd.read_excel(self.filename)

    def iterrows(self, need_synonyms=False, need_parents=False) -> Tuple[int, Generator[RadLexItem, None, None]]:
        for i, row in tqdm.tqdm(self.df.iterrows(), total=len(self.df)):
            if not pd.isna(row['Comment']) \
                    and (row['Comment'].lower().startswith('duplicate') or row['Comment'].lower() == 'not needed'):
                continue
            concept_id = row['Class ID']
            concept_id = get_class_id(concept_id)

            concept = row['Preferred Label']
            if concept is None or type(concept) is not str or concept == '':
                continue

            item = RadLexItem()
            item.row = row
            item.concept_id = concept_id
            item.preferred_name = concept
            item.synonyms.append(concept)

            if need_synonyms:
                synonyms = row['Synonyms']
                if isinstance(synonyms, str):
                    item.synonyms += [t.strip() for t in synonyms.split('|')]

            if need_parents:
                parents = row['Parents']
                if not pd.isna(parents):
                    for parent in parents.split(';'):
                        parent_id = get_class_id(parent)
                        item.parents.append(parent_id)

            yield i, item

    def get_graph(self) -> nx.DiGraph:
        G = nx.DiGraph()
        for i, item in self.iterrows(need_parents=True):
            G.add_node(item.concept_id, item=item)
            for parent_id in item.parents:
                G.add_edge(parent_id, item.concept_id)
        print('Read nodes:', G.number_of_nodes())
        print('Read edges:', G.number_of_edges())
        return G

    def get_spacy_matchers(self, nlp, min_term_size: int = 1, max_term_size: int = 9,
                           min_char_size=3, max_char_size=100, lower=True) -> NerSpacyPhraseMatchers:
        matchers = NerSpacyPhraseMatchers()
        matchers.include_text_matcher = PhraseMatcher(nlp.vocab, attr='LOWER')
        matchers.include_lemma_matcher = PhraseMatcher(nlp.vocab, attr='LEMMA')

        # for i, item in self.iterrows(need_synonyms=True):
        #     matchers.id2concept[item.concept_id] = item.preferred_name
        #     docs = []
        #     for phrase in item.synonyms:
        #         if min_char_size <= len(phrase) <= max_char_size:
        #             try:
        #                 doc = nlp(phrase.lower())
        #             except:
        #                 logging.exception('Cannot parse row: %s' % item.concept_id)
        #             else:
        #                 if min_term_size <= len(doc) <= max_term_size:
        #                     docs.append(doc)
        #     matchers.include_text_matcher.add(item.concept_id, docs)
        #     matchers.include_lemma_matcher.add(item.concept_id, docs)


        for i, item in self.iterrows(need_synonyms=True):
            matchers.id2concept[item.concept_id] = item.preferred_name
            phrases = [phrase.lower() for phrase in item.synonyms if min_char_size <= len(phrase) <= max_char_size]
            if lower:
                phrases = [phrase.lower() for phrase in phrases]
            try:
                docs = nlp.pipe(phrases, batch_size=32, disable=["parser", "ner"])
                docs = [doc for doc in docs if min_term_size <= len(doc) <= max_term_size]
                matchers.include_text_matcher.add(item.concept_id, docs)
                matchers.include_lemma_matcher.add(item.concept_id, docs)
            except:
                logging.exception('Cannot parse row: %s' % item.concept_id)

        return matchers
