"""
Convert OMOP CDM NOTE table (.csv) file to the BioC collection.

Usage:
    cdm2bioc [options] -i FILE -o FILE

Options:
    -i FILE
    -o FILE
    --overwrite
"""
import bioc
import docopt
import pandas as pd

from radtext.models.bioc_cdm_converter import convert_note_nlp_table_to_bioc
from radtext.cmd.cmd_utils import process_options


def main():
    argv = docopt.docopt(__doc__)
    process_options(argv)

    df = pd.read_csv(argv['-i'], dtype=str)
    collection = convert_note_nlp_table_to_bioc(df)

    with open(argv['-o'], 'w') as fp:
        bioc.dump(collection, fp)


if __name__ == '__main__':
    main()
