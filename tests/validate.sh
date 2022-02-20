# download models
python radtext/cmd/download.py all
# data preparation
python radtext/cmd/csv2bioc.py -i tests/examples/ex1.csv -o output/ex1.xml
python radtext/cmd/cdm2bioc.py -i tests/examples/ex2.csv -o output/ex2.xml
# deid
python radtext/cmd/deid.py --repl=X -i tests/examples/ex3.xml -o output/ex3.deid_philter.xml
# split section
python radtext/cmd/split_section.py reg -i tests/examples/ex4.xml -o output/ex4.secsplit_regex.xml
python radtext/cmd/split_section.py medspacy -i tests/examples/ex4.xml -o output/ex4.secsplit_medspacy.xml
# preprocess
python radtext/cmd/preprocess.py spacy -i tests/examples/ex4.secsplit_medspacy.xml -o output/ex4.preprocess_spacy.xml
python radtext/cmd/preprocess.py stanza -i tests/examples/ex4.secsplit_medspacy.xml -o output/ex4.preprocess_stanza.xml
# ssplit
python radtext/cmd/ssplit.py -i tests/examples/ex4.secsplit_medspacy.xml -o output/ex4.ssplit.xml
# parse
python radtext/cmd/parse.py -i tests/examples/ex4.ssplit.xml -o output/ex4.parse.xml
# convert constituency tree to dependencies
python radtext/cmd/tree2dep.py -i tests/examples/ex4.parse.xml -o output/ex4.depparse_billp.xml
# ner
python radtext/cmd/ner.py regex --phrase radtext/resources/chexpert_phrases.yml -i tests/examples/ex4.secsplit_medspacy.xml -o output/ex4.ner_regex.xml
python radtext/cmd/ner.py spacy --radlex radtext/resources/Radlex4.1.xlsx -i tests/examples/ex4.secsplit_medspacy.xml -o output/ex4.ner_radlex.xml
# neg
# convert bioc to note_nlp table
python radtext/cmd/bioc2cdm.py -i tests/examples/ex4.depparse_billp.xml -o output/ex4.deparser_billp.csv