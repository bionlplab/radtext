export PYTHONPATH=$PYTHONPATH:src
examples='radtext/examples'
$output='$output'

[ -d $$output ] || mkdir $$output

# download models
python src/radtext/cmd/download.py all
# data preparation
radtext-csv2bioc -i $examples/ex1.csv -o $output/ex1.xml
radtext-cdm2bioc -i $examples/ex2.csv -o $output/ex2.xml
# deid
radtext-deid --repl=X -i $examples/ex3.xml -o $output/ex3.deid_philter.xml
# split section
radtext-split_section reg -i $examples/ex4.xml -o $output/ex4.secsplit_regex.xml
radtext-split_section medspacy -i $examples/ex4.xml -o $output/ex4.secsplit_medspacy.xml
# preprocess
radtext-preprocess spacy -i $examples/ex4.secsplit_medspacy.xml -o $output/ex4.preprocess_spacy.xml
radtext-preprocess stanza -i $examples/ex4.secsplit_medspacy.xml -o $output/ex4.preprocess_stanza.xml
# ssplit
radtext-ssplit -i $examples/ex4.secsplit_medspacy.xml -o $output/ex4.ssplit.xml
# parse
radtext-parse -i $examples/ex4.ssplit.xml -o $output/ex4.parse.xml
# convert constituency tree to dependencies
radtext-tree2dep -i $examples/ex4.parse.xml -o $output/ex4.depparse_billp.xml
# ner
radtext-ner regex --phrase radtext/resources/chexpert_phrases.yml -i $examples/ex4.secsplit_medspacy.xml -o $output/ex4.ner_regex.xml
radtext-ner spacy --radlex radtext/resources/Radlex4.1.xlsx -i $examples/ex4.secsplit_medspacy.xml -o $output/ex4.ner_radlex.xml
# neg
#radtext-neg --ngrex_negation radtext/resources/patterns/ngrex_negation.yml \
#  --regex_patterns radtext/resources/patterns/regex_patterns.yml \
#  -i $examples/ex4.secsplit_medspacy.xml \
#  -o $output/ex4.ner_radlex.xml
# convert bioc to note_nlp table
radtext-bioc2cdm -i $examples/ex4.depparse_billp.xml -o $output/ex4.deparser_billp.csv