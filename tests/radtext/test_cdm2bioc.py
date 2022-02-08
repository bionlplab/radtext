import pytest

from radtext.models.bioc_cdm_converter import cdm_note_table2bioc, NOTE_TABLE_HEADERS
from tests import Example_Dir
import pandas as pd


def test_cdm_note_table2bioc():
    file = Example_Dir / 'note.csv'
    df = pd.read_csv(file, dtype=str)
    collection = cdm_note_table2bioc(df)
    assert len(collection.documents) == 8

    for i in range(8):
        assert collection.documents[i].passages[0].text == df['note_text'][i]
        assert collection.documents[i].id == df['note_id'][i]

        for k in NOTE_TABLE_HEADERS:
            if k not in ('note_id', 'note_text'):
                assert collection.documents[i].infons[k] == df[k][i]


def test_cdm_note_table2bioc2():
    file = Example_Dir / 'note.csv'
    df = pd.read_csv(file, dtype=str)

    df1 = df.drop(['note_text'], axis=1)
    with pytest.raises(KeyError):
        cdm_note_table2bioc(df1)

    df1 = df.drop(['note_type_concept_id'], axis=1)
    collection = cdm_note_table2bioc(df1)
    assert len(collection.documents) == 8
