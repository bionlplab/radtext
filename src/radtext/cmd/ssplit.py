"""
Usage:
    ssplit [options] -i FILE -o FILE

Options:
    --newline   Whether to treat newlines as sentence breaks.
    -o FILE
    -i FILE
"""
import bioc
import docopt
import tqdm

from radtext.cmd.cmd_utils import process_options, process_file
from radtext.models.sentence_split_nltk import BioCSSplitterNLTK


def main():
    argv = docopt.docopt(__doc__)
    process_options(argv)

    processor = BioCSSplitterNLTK(newline=argv['--newline'])
    process_file(argv['-i'], argv['-o'], processor, bioc.PASSAGE)


if __name__ == '__main__':
    main()
