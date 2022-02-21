from typing import Dict

import bioc
import pandas as pd
import tqdm
from radtext.models.constants import NEGATION, UNCERTAINTY


NOTE_NLP_TABLE_HEADERS = [
    "note_nlp_id",
    "note_id",
    "section_concept_id",
    "offset",
    "lexical_variant",
    "note_nlp_concept_id",
    "note_nlp_source_concept_id",
    "nlp_system",
    "nlp_date",
    "nlp_date_time",
    "term_exists",
    "term_temporal",
    "term_modifiers"
]

NOTE_TABLE_HEADERS = [
    "note_id",
    "person_id",
    "note_date",
    "note_datetime",
    "note_type_concept_id",
    "note_class_concept_id",
    "note_title",
    "note_text",
    "encoding_concept_id",
    "language_concept_id",
    "provider_id",
    "visit_occurrence_id",
    "visit_detail_id",
    "note_source_value"
]


def convert_ann_to_row(ann: bioc.BioCAnnotation) -> Dict:
    row = {
        "note_nlp_id": ann.id,
        "offset": ann.total_span.offset,
        "lexical_variant": ann.text
    }
    exists = None
    if NEGATION in ann.infons and ann.infons[NEGATION]:
        exists = 'Negation=True'
    if UNCERTAINTY in ann.infons and ann.infons[UNCERTAINTY]:
        exists = 'Uncertain=True'
    if exists is not None:
        row['term_exists'] = exists
    if 'lemma' in ann.infons:
        row['note_nlp_concept_id'] = ann.infons['lemma']
    if 'section_concept' in ann.infons:
        row['section_concept_id'] = ann.infons['section_concept']

    new_row = {}
    for k in NOTE_NLP_TABLE_HEADERS:
        if k in row:
            new_row[k] = row[k]
        elif k in ann.infons:
            new_row[k] = ann.infons[k]
        else:
            new_row[k] = None
    return new_row


def convert_bioc_to_note_nlp(collection: bioc.BioCCollection) -> pd.DataFrame:
    rows = []
    for doc in tqdm.tqdm(collection.documents):
        note_id = doc.id
        section_concept = None
        for passage in tqdm.tqdm(doc.passages, disable=True):
            if 'section_concept' in passage.infons:
                section_concept = passage.infons['section_concept']
            for ann in passage.annotations:
                row = convert_ann_to_row(ann)
                row['section_concept_id'] = section_concept
                row['note_id'] = note_id
                rows.append(row)
            for sentence in passage.sentences:
                for ann in sentence.annotations:
                    row = convert_ann_to_row(ann)
                    row['section_concept_id'] = section_concept
                    row['note_id'] = note_id
                    rows.append(row)
        for ann in doc.annotations:
            row = convert_ann_to_row(ann)
            row['note_id'] = note_id
            rows.append(row)
    df = pd.DataFrame(rows)
    # df = df[NOTE_NLP_TABLE_HEADERS]
    return df


def convert_note_nlp_table_to_bioc(df: pd.DataFrame) -> bioc.BioCCollection:
    """
    Convert from CDM NOTE table to bioc collection.
    https://www.ohdsi.org/web/wiki/doku.php?id=documentation:cdm:note
    """
    collection = bioc.BioCCollection()
    for _, row in df.iterrows():
        doc = bioc.BioCDocument.of_text(row['note_text'])
        doc.id = row['note_id']
        collection.add_document(doc)
        for col in NOTE_TABLE_HEADERS:
            if col not in ('note_id', 'note_text') and col in df.columns:
                doc.infons[col] = str(row[col])
    return collection
