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

from radtext.bioc_cdm_converter import cdm_note_table2bioc
from radtext.cmd.cmd_utils import process_options


def main():
    argv = docopt.docopt(__doc__)
    process_options(argv)

    df = pd.read_csv(argv['-i'], dtype=str)
    collection = cdm_note_table2bioc(df)

    with open(argv['-o'], 'w') as fp:
        bioc.dump(collection, fp)


if __name__ == '__main__':
    main()
