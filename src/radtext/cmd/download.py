"""
Usage:
    download all
    download deid
    download stanza
    download spacy
    download ssplit
    download bllip [--bllip-model DIR]
    download tree2dep
    download ner
    download all [--spacy-model NAME]

Options:
    --bllip-model DIR       [default: ~/.radtext/bllipparser]
    --spacy-model NAME     [default: en_core_web_sm]
"""
import docopt
from radtext.models.download import download


def main():
    argv = docopt.docopt(__doc__)
    download(argv)

if __name__ == '__main__':
    main()
