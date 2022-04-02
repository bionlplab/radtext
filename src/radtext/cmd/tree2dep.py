"""
Usage:
    tree2dep [options] -i FILE -o FILE

Options:
    --overwrite
    -o FILE
    -i FILE
"""
import bioc
import docopt
import tqdm

from radtext.cmd.cmd_utils import process_options, process_file
from radtext.models.tree2dep import BioCPtb2DepConverter


def main():
    argv = docopt.docopt(__doc__)
    process_options(argv)

    processor = BioCPtb2DepConverter()
    process_file(argv['-i'], argv['-o'], processor, bioc.SENTENCE)


if __name__ == '__main__':
    main()