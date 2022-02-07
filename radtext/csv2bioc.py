import bioc
import pandas as pd
import tqdm


def csv2bioc(df: pd.DataFrame, id_col: str, text_col: str) -> bioc.BioCCollection:
    """
    Convert df to the BioC collection
    """
    collection = bioc.BioCCollection()
    for i, row in tqdm.tqdm(df.iterrows(), total=len(df)):
        docid = row[id_col]
        text = row[text_col]
        if pd.isna(docid) or pd.isna(text):
            continue
        doc = bioc.BioCDocument.of_text(text)
        doc.id = docid
        collection.add_document(doc)
    return collection
