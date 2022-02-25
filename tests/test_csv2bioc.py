import pandas as pd

from radtext.models import csv2bioc


def test_csv2bioc(example_dir):
    file = example_dir / 'ex1.csv'
    df = pd.read_csv(file, dtype=str)
    collection = csv2bioc.csv2bioc(df, 'note_id', 'note_text')
    assert len(collection.documents) == 2

    for i in range(1, 3):
        assert collection.documents[i-1].passages[0].text == df['note_text'][i]
