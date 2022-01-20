"""
Convert the BioC-format file to OMOP CDM NOTE_NLP table.

Usage:
    bioc2cdm [options] -i FILE -o FILE

Options:
    -i FILE
    -o FILE
"""
import sys
sys.path.append('../radtext')

import bioc
import docopt
import pandas as pd 
import tqdm
import json

from radtext.bioc_cdm_converter import BioC2CDM

NOTE_TABLE_HEADERS = ["note_id", "note_nlp_id", "offset", "lexical_variant", "note_nlp_concept_id", "nlp_date", \
"section_concept_id", "note_nlp_source_concept_id", "nlp_system", "term_exists", "term_temporal", "term_modifiers"]

if __name__ == '__main__':
	argv = docopt.docopt(__doc__)

	with open(argv['-i']) as fp:
		collection = bioc.load(fp)

	# initialize the CDM Note table
	cdm_df = pd.DataFrame(columns=NOTE_TABLE_HEADERS)

	# initialize the BioC2CDM converter
	bioc2cdm = BioC2CDM()
	# convert
	cdm_df = bioc2cdm.convert(cdm_df, collection)

	cdm_df.to_csv(argv['-o'])
			
