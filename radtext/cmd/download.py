"""
Usage:
    download [options]

Options:
    --all
    --deid
    --stanza
"""
import docopt
import nltk
import stanza


def main():
    argv = docopt.docopt(__doc__)
    if '--deid' in argv or '--all' in argv:
        nltk.download('averaged_perceptron_tagger')
    if '--stanza' in argv or '--all' in argv:
        stanza.download('en')
    if '--ssplit' in argv or '--all' in argv:
        nltk.download('punkt')

if __name__ == '__main__':
    main()
