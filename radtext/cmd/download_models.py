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


if __name__ == '__main__':
    main()
