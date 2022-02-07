"""
Convert csv to the BioC output file

Usage:
    csv2bioc [options] -i FILE -o FILE

Options:
    --id_col <str>      [default: note_id]
    --text_col <str>    [default: note_text]
    -o FILE
    -i FILE
    --overwrite
"""

import bioc
import docopt
import pandas as pd

from cmd_utils import process_options
from radtext.csv2bioc import csv2bioc


def main():
    argv = docopt.docopt(__doc__)
    process_options(argv)

    df = pd.read_csv(argv['-i'], dtype=str)
    collection = csv2bioc(df, argv['--id_col'], argv['--text_col'])

    with open(argv['-o'], 'w') as fp:
        bioc.dump(collection, fp)


if __name__ == '__main__':
    main()
