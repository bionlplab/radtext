"""
Usage:
    download [--all | --annotators NAME]

Options:
    --annotators STR        Annotators' resources to download. You can list the names in a comma-separated string.
                            Supported annotators include:
                                deid:philter
                                secsplit:regex
                                secsplit:medspacy
                                ssplit:nltk
                                ner:regex
                                ner:spacy
                                parse:bllip
                                tree2dep
                                neg:negbio
    --bllip-model DIR       [default: ~/.radtext/bllipparser]
    --spacy-model NAME     [default: en_core_web_sm]
"""
import docopt
from radtext.models.download import download

def main():
    argv = docopt.docopt(__doc__)
    if argv['--all']:
        download()
    else:
        annotators = argv['--annotators'].split(',')
        download(annotators)


if __name__ == '__main__':
    main()
