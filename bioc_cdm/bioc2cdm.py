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
import pandas as pd 
import tqdm
import json

if __name__ == '__main__':
	argv = docopt.docopt(__doc__)

	with open(argv['-i']) as fp:
		collection = bioc.load(fp)

	# load the bioc2cdm mapping
	with open('./bioc2cdm_map.json', 'r') as file:
		mapping = json.load(file)

	headers = list(mapping.keys())

	cdm_df = pd.DataFrame(columns=headers)

	nlp_date = collection.date

	for doc in tqdm.tqdm(collection.documents):
		nlp_system = None
		section_concept_id = None
		note_id = doc.id
		for passage in tqdm.tqdm(doc.passages, leave=False):
			if passage.infons != None:
				if 'title' in passage.infons:
					section_concept_id = passage.infons['title']

			for ann in passage.annotations:
				note_nlp_id, offset, lexical_variant, note_nlp_concept_id, \
				term_exists, term_temporal, term_modifiers = None, None, None, None, None, None, None 

				note_nlp_id = ann.id
				for location in ann.locations:
					if location.offset != None:
						offset = location.offset
				lexical_variant = ann.text
				if 'preferred_name' in ann.infons:
					note_nlp_concept_id = ann.infons['preferred_name']
				if 'negation' in ann.infons:
					term_exists = ann.infons['negation']
				if 'temporal' in ann.infons:
					term_temporal = ann.infons['temporal']
				if 'modifiers' in ann.infons:
					term_modifiers = ann.infons['modifiers']

				cdm_df = cdm_df.append({"note_id": note_id, \
					"note_nlp_id": note_nlp_id, \
					"offset": offset, \
					"lexical_variant": lexical_variant, \
					"note_nlp_concept_id": note_nlp_concept_id, \
					"nlp_date": nlp_date, \
					"section_concept_id": section_concept_id, \
					"note_nlp_source_concept_id": note_nlp_concept_id, \
					"nlp_system": nlp_system, \
					"term_exists": term_exists, \
					"term_temporal": term_temporal, \
					"term_modifiers": term_modifiers}, ignore_index=True)

	cdm_df.to_csv(argv['-o'])
			
