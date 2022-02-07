"""
Convert the BioC-format file to OMOP CDM NOTE_NLP table.

Usage:
    bioc2cdm [options] -i FILE -o FILE

Options:
    -i FILE
    -o FILE
"""
import sys
sys.path.append('..')

import bioc
import docopt
import pandas as pd 
import tqdm
import json

from radtext.bioc_cdm_converter import BioC2CDM


if __name__ == '__main__':
	argv = docopt.docopt(__doc__)

	with open(argv['-i']) as fp:
		collection = bioc.load(fp)

	# initialize the BioC2CDM converter
	bioc2cdm = BioC2CDM()
	# convert
	cdm_df = bioc2cdm.convert(collection)

	cdm_df.to_csv(argv['-o'])
			
