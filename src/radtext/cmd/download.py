"""
Usage:
    download all
    download deid
    download stanza
    dwonlaod spacy
    download ssplit
    download bllip [--bllip-model-dir DIR]
    download tree2dep
    download ner
    download all [--spacy-model-name NAME]

Options:
    --bllip-model-dir DIR       [default: ~/.radtext/bllipparser]
    --spacy-model-name NAME     [default: en_core_web_sm]
"""
import docopt
from radtext.models.download import download


def main():
    argv = docopt.docopt(__doc__)
    download(argv)

if __name__ == '__main__':
    main()
