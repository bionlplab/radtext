"""
Usage:
    deid [options] -i FILE -o FILE

Options:
    --overwrite
    -o FILE
    -i FILE
    --repl CHAR    PHI replacement char [default: X]
"""
import bioc
import docopt

from radtext.cmd.cmd_utils import process_options, process_file
from radtext.models.deid import BioCDeidPhilter


def main():
    argv = docopt.docopt(__doc__)
    process_options(argv)

    processor = BioCDeidPhilter(argv['--repl'])
    process_file(argv['-i'], argv['-o'], processor, bioc.DOCUMENT)


if __name__ == '__main__':
    main()
