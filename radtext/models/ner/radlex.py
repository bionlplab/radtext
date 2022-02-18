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
    def __init__(self, dataset: Union[pd.DataFrame, str, PathLike]):
        if type(dataset) is str or type(dataset) is PathLike:
            self.filename = dataset
            self.df = pd.read_excel(self.filename)
        elif type(dataset) is pd.DataFrame:
            self.filename = None
            self.df = dataset

    def descendants(self, rids: List[str]):
        G = self.get_graph()
        rows = []
        for rid in rids:
            for n in nx.descendants(G, rid):
                rows.append(G.nodes[n]['item'].row)

        df = pd.DataFrame(rows)
        return RadLex4(df)


    def iterrows(self) -> Tuple[int, Generator[RadLexItem, None, None]]:
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

            synonyms = row['Synonyms']
            if isinstance(synonyms, str):
                item.synonyms += [t.strip() for t in synonyms.split('|')]

            parents = row['Parents']
            if not pd.isna(parents):
                for parent in parents.split(';'):
                    parent_id = get_class_id(parent)
                    item.parents.append(parent_id)

            yield i, item

    def get_graph(self) -> nx.DiGraph:
        G = nx.DiGraph()
        for i, item in self.iterrows():
            G.add_node(item.concept_id, item=item)
            for parent_id in item.parents:
                G.add_edge(parent_id, item.concept_id)

        print('Read nodes:', G.number_of_nodes())
        print('Read edges:', G.number_of_edges())
        return G

    def get_spacy_matchers(self, nlp, min_term_size: int = 1, max_term_size: int = 9,
                           min_char_size=3, max_char_size=100) -> NerSpacyPhraseMatchers:
        matchers = NerSpacyPhraseMatchers()
        matchers.include_text_matcher = PhraseMatcher(nlp.vocab, attr='ORTH')
        matchers.include_lemma_matcher = PhraseMatcher(nlp.vocab, attr='LEMMA')

        for i, item in self.iterrows():
            matchers.id2concept[item.concept_id] = item.preferred_name
            docs = []
            for phrase in item.synonyms:
                if min_char_size <= len(phrase) <= max_char_size:
                    try:
                        doc = nlp(phrase.lower())
                    except:
                        logging.exception('Cannot parse row: %s' % item.concept_id)
                    else:
                        if min_term_size <= len(doc) <= max_term_size:
                            docs.append(doc)
            matchers.include_text_matcher.add(item.concept_id, docs)
            matchers.include_lemma_matcher.add(item.concept_id, docs)

        return matchers
