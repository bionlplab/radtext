"""
Usage:
    deid [options] -i FILE -o FILE

Options:
    --overwrite
    -o FILE
    -i FILE
    --replacement char  the PHI replacement char
"""
import sys
sys.path.append('../../radtext')
import bioc
import docopt
import tqdm

from cmd_utils import process_options
from radtext.deid import BioCDeidPhilter
from radtext.pphilter.philter import Philter

if __name__ == '__main__':
    argv = docopt.docopt(__doc__)
    print('the argv is: ',argv)
    process_options(argv)

    philter = Philter()
    deid = BioCDeidPhilter(philter)

    with open(argv['-i']) as fp:
        collection = bioc.load(fp)

    for doc in tqdm.tqdm(collection.documents):
        for passage in tqdm.tqdm(doc.passages, leave=False):
            deid.process_passage(passage, doc.id)
            if '--replacement' in argv:
                print('if is true')
                if argv['--replacement'] == None:
                    argv['--replacement'] = 'X'
                deid.deidentify_passage(passage, argv['--replacement'])

    with open(argv['-o'], 'w') as fp:
        bioc.dump(collection, fp)
