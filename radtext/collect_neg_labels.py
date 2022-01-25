"""
Usage:
    collect [options] --phrases FILE -i FILE -o FILE

Options:
    --phrases FILE
    -o FILE
    -i FILE
    --start_with_findings
"""
import collections
import logging
from typing import Dict, Set

import bioc
import docopt
import pandas as pd
import tqdm
import yaml

# Numeric constants
from radtext.neg.constants import NEGATION, UNCERTAINTY

POSITIVE = 'p'
NEGATIVE = 'n'
UNCERTAIN = 'u'
NOT_MENTIONED = '-'


def merge_labels(label_dict: Dict[str, Set[int]]) -> Dict[str, int]:
    new_d = {}
    for category, labels in label_dict.items():
        # Only one label, no conflicts.
        if len(labels) == 1:
            new_d[category] = labels.pop()
        elif NEGATIVE in labels and UNCERTAIN in labels:
            # Case 1. There is negated and uncertain.
            new_d[category] = NEGATIVE
        # Case 2. There is negated and positive.
        elif NEGATIVE in labels and POSITIVE in labels:
            new_d[category] = POSITIVE
        # Case 3. There is uncertain and positive.
        elif UNCERTAIN in labels and POSITIVE in labels:
            new_d[category] = POSITIVE
        # Case 4. All labels are the same.
        else:
            raise RuntimeError('Should not reach here')
    return new_d


def is_cardiomegaly(ann: bioc.BioCAnnotation) -> bool:
    return ann.text.lower() in ('chf', 'heart failure')


def find_findings(doc: bioc.BioCDocument):
    keys = ('FINDINGS', 'FIDING', 'FIMPRESSION', 'FINDGING', 'FINDIGN', 'FINDINDG', 'FINDIN', 'FINDNG', 'FINDNING',
            'FINDOING', 'FINIDNG')

    def is_finding(title):
        for k in keys:
            if k in title:
                return True
        return False

    for i, p in enumerate(doc.passages):
        if 'section_concept' in p.infons and is_finding(p.infons['section_concept']):
            return i
    return -1


def aggregate(doc: bioc.BioCDocument, start_with_finding: bool=False) -> Dict[str, Set[int]]:
    i = 0
    if start_with_finding:
        i = find_findings(doc)
        if i == -1:
            i = 0

    label_dict = collections.defaultdict(set)
    no_finding = True
    for p in doc.passages[i:]:
        for ann in p.annotations:
            category = ann.infons['source_concept']
            # Don't add any labels for No Finding
            if category == "No Finding":
                continue

            if NEGATION in ann.infons and ann.infons[NEGATION]:
                label = NEGATIVE
            elif UNCERTAINTY in ann.infons and ann.infons[UNCERTAINTY]:
                label = UNCERTAIN
            else:
                label = POSITIVE

            # If at least one non-support category has a uncertain or
            # positive label, there was a finding
            if category != 'Support Devices' and label in [UNCERTAIN, POSITIVE]:
                no_finding = False

            # add exception for 'chf' and 'heart failure'
            if label in [UNCERTAIN, POSITIVE] and is_cardiomegaly(ann):
                label_dict["Cardiomegaly"].add(UNCERTAIN)

            label_dict[category].add(label)

    if no_finding:
        label_dict["No Finding"] = {POSITIVE}

    return label_dict


def create_prediction(source, dest, phrases_file, start_with_findings: bool):
    """

    Args:
        source: source bioc file
        dest: output file name
        phrases_file: phrase pathname
    """
    logger = logging.getLogger(__name__)
    with open(phrases_file) as fp:
        phrases = yaml.load(fp, yaml.FullLoader)

    rows = []
    cnt = collections.Counter()
    with open(source, encoding='utf8') as fp:
        collection = bioc.load(fp)

    for doc in tqdm.tqdm(collection.documents):
        label_dict = aggregate(doc, start_with_findings)
        label_dict = merge_labels(label_dict)
        findings = {k: v for k, v in label_dict.items() if k in phrases.keys()}
        findings['docid'] = str(doc.id)
        rows.append(findings)

    columns = ['docid'] + sorted(phrases.keys())
    row_df = pd.DataFrame(sorted(rows, key=lambda x: x['docid']), columns=columns)
    row_df = row_df.fillna(NOT_MENTIONED)
    row_df.to_csv(dest, index=False, float_format='%1.0f')
    if cnt:
        logger.debug('Label statistics: \n%s', cnt)

