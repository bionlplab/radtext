"""
Usage:
    download [options]

Options:
    --all
    --deid
"""
import docopt
import nltk


def main():
    argv = docopt.docopt(__doc__)
    if '--deid' in argv or '--all' in argv:
        nltk.download('averaged_perceptron_tagger')
    if '--spacy' in argv or '--all' in argv:
        # python -m spacy download en_core_web_sm
        pass

if __name__ == '__main__':
    main()
