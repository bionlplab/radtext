"""
Convert csv to the BioC output file

Usage:
    csv2bioc [options] -i FILE -o FILE

Options:
    --id_col <str>      [default: ID]
    --text_col <str>    [default: TEXT]
    -o FILE
    -i FILE
"""

import bioc
import docopt
import pandas as pd
import tqdm

from cmd.cmd_utils import process_options


if __name__ == '__main__':
    argv = docopt.docopt(__doc__)
    process_options(argv)

    df = pd.read_csv(argv['-i'], dtype=str)
    collection = bioc.BioCCollection()
    for i, row in tqdm.tqdm(df.iterrows(), total=len(df)):
        text = row[argv['--text_col']]
        id = row[argv['--id_col']]
        if pd.isna(id) or pd.isna(text):
            continue
        doc = bioc.utils.as_document(text)
        doc.id = id
        collection.add_document(doc)

    with open(argv['-o'], 'w') as fp:
        bioc.dump(collection, fp)