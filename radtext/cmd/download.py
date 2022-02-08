"""
Usage:
    download all
    download deid
    download stanza
    download ssplit
    download bllip [options]
    download all [options]

Options:
    --bllip-model-dir <dir>     [default: ~/.radtext/bllipparser]
"""
from pathlib import Path

import docopt
import nltk
import stanza
from bllipparser import ModelFetcher

from radtext.constants import MODELS


def main():
    argv = docopt.docopt(__doc__)
    if argv['deid'] or argv['all']:
        nltk.download('averaged_perceptron_tagger')
    if argv['stanza'] or argv['all']:
        stanza.download('en')
    if argv['ssplit'] or argv['all']:
        nltk.download('punkt')
    if argv['bllip'] or argv['all']:
        model_dir = Path(argv['--bllip-model-dir'])
        if not model_dir.exists():
            model_dir.mkdir(parents=True)

        print("downloading GENIA+PubMed model ... [%s]" % model_dir)
        ModelFetcher.download_and_install_model(MODELS['BLLIP-GENIA-PubMed'], str(model_dir))

if __name__ == '__main__':
    main()
