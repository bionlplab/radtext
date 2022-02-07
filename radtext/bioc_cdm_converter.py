import bioc
import docopt
import pandas as pd
import tqdm
import json

NOTE_NLP_TABLE_HEADERS = ["note_id", "note_nlp_id", "offset", "lexical_variant", "note_nlp_concept_id", "nlp_date", \
                      "section_concept_id", "note_nlp_source_concept_id", "nlp_system", "term_exists", "term_temporal",
                      "term_modifiers"]

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


class BioC2CDM:
    def convert(self, collection):
        nlp_date = collection.date

        cdm_df = pd.DataFrame(columns=NOTE_NLP_TABLE_HEADERS)

        for doc in tqdm.tqdm(collection.documents):
            nlp_system = None
            section_concept_id = None
            note_id = doc.id
            for passage in tqdm.tqdm(doc.passages, leave=False):
                if passage.infons != None:
                    if 'title' in passage.infons:
                        section_concept_id = passage.infons['title']

                for ann in passage.annotations:
                    note_nlp_id, offset, lexical_variant, note_nlp_concept_id, \
                    term_exists, term_temporal, term_modifiers = None, None, None, None, None, None, None

                    note_nlp_id = None
                    for location in ann.locations:
                        if location.offset != None:
                            offset = location.offset
                    lexical_variant = ann.text
                    if 'preferred_name' in ann.infons:
                        note_nlp_concept_id = ann.infons['preferred_name']
                    if 'concept_id' in ann.infons:
                        note_nlp_source_concept_id = ann.infons['concept_id']
                    if 'negation' in ann.infons:
                        term_exists = ann.infons['negation']
                    if 'temporal' in ann.infons:
                        term_temporal = ann.infons['temporal']
                    if 'modifiers' in ann.infons:
                        term_modifiers = ann.infons['modifiers']

                    cdm_df = cdm_df.append({"note_id": note_id, \
                                            "note_nlp_id": note_nlp_id, \
                                            "offset": offset, \
                                            "lexical_variant": lexical_variant, \
                                            "note_nlp_concept_id": note_nlp_concept_id, \
                                            "nlp_date": nlp_date, \
                                            "section_concept_id": section_concept_id, \
                                            "note_nlp_source_concept_id": note_nlp_source_concept_id, \
                                            "nlp_system": nlp_system, \
                                            "term_exists": term_exists, \
                                            "term_temporal": term_temporal, \
                                            "term_modifiers": term_modifiers}, ignore_index=True)

        return cdm_df


def cdm_note_table2bioc(df: pd.DataFrame) -> bioc.BioCCollection:
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

