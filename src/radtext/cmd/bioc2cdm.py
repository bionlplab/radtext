"""
Convert the BioC-format file to OMOP CDM NOTE_NLP table.

Usage:
    bioc2cdm [options] -i FILE -o FILE

Options:
    -i FILE
    -o FILE
"""
import bioc
import docopt

from radtext.models.bioc_cdm_converter import convert_bioc_to_note_nlp


def main():
	argv = docopt.docopt(__doc__)
	with open(argv['-i']) as fp:
		collection = bioc.load(fp)
	df = convert_bioc_to_note_nlp(collection)
	df.to_csv(argv['-o'])


if __name__ == '__main__':
	main()
			
