# Advanced Usage

This document covers some more advanced features of RadText.

## Running the pipeline step-by-step

The step-by-step pipeline generates all intermediate results. Users can easily
rerun any step if it makes any errors. The system pipeline looks like:

1. `csv2bioc` transforms the .csv text file into a BioC XML file.
2. `deid` de-identifies all the reports using [Philter](https://github.com/BCHSI/philter-ucsf), hides protected health information (PHI) such as Name, Contact, Age, etc.
3. `split_section` splits the report into sections. Users can choose to use [NegBio](https://github.com/bionlplab/negbio2) `reg` split or [`medspacy`](https://spacy.io/universe/project/medspacy).
4. `preprocess` splits and tokenizes texts into sentences. Users can choose to use [NLTK](https://www.nltk.org/api/nltk.tokenize.html), [spaCy](https://spacy.io/) or [Stanza](https://stanfordnlp.github.io/stanza/).
5. `ner` - Named entity recognition (NER) recognizes the named entities (e.g., disease findings) in sentences. Users can choose to use NegBio, MetaMap or scispaCy.
6. `parse` parses sentences to obtain the universal dependency graph (UDG) to describe the grammatical relationships in a sentence. Users can choose to use [Stanza](https://stanfordnlp.github.io/stanza/) or [Bllip parser](https://github.com/BLLIP/bllip-parser).
7. `neg` detects negative and uncertain findings using [NegBio](https://github.com/bionlplab/negbio2).
8. `collect_neg_label` merges negative and uncertain labels.


## Prepare the dataset

This is the same process as [Quickstart-Preparing the dataset](https://radtext.readthedocs.io/en/latest/getting_started.html#preparing-the-dataset). 
You can skip this step if the reports are already in the [BioC]( http://bioc.sourceforge.net/) format. 
Otherwise, you can store your input reports in a .csv file.
By default, column 'note_id' stores the unique identifier for each note. 
Column 'note_text' stores the content of the note.
Then, you can use the following module to convert your .csv file to the BioC format. 

```bash
$ radtext-csv2bioc -i /path/to/input.csv -o /path/to/output.xml
```

## Convert from OMOP CDM NOTE table to BioC

```shell
$ radtext-cdm2bioc -i /path/to/input.csv -o /path/to/output.xml
```

**If you have lots of reports, it is recommended to put them into several BioC files, 
for example, 5000 reports per BioC file.**

## De-identification

Radiology reports often contain the Protected Health Information 
([PHI](https://www.hhs.gov/hipaa/for-professionals/privacy/special-topics/de-identification/index.html#standard)).
This module uses [Philter](https://github.com/BCHSI/philter-ucsf) to remove PHI from the reports.

```bash
$ radtext-deid --repl=X -i /path/to/input.xml -o /path/to/output.xml
```

## Section Split

This module splits the report into sections. 
RadText provides two options for section split.

### Rule-based method

This script uses a list of section titles to split the notes.
The default section titles are hard-coded in `resources/section_titles.txt`.
Users can also specify customized section titles using the option `--section-titles=<file>`.

```shell
$ radtext-secsplit reg -i /path/to/input.xml -o /path/to/output.xml
```

### MedSpaCy

[MedSpaCy](https://github.com/medspacy/medspacy) is a spaCy tool for performing clinical 
NLP and text processing tasks. 
It includes an implementation of clinical section detection based on rule-based matching of the 
section titles with default rules adapted from [SecTag](https://pubmed.ncbi.nlm.nih.gov/18999303/) and 
expanded through practice.

```shell
$ radtext-secsplit medspacy -i /path/to/input.xml -o /path/to/output.xml
```

## Text preprocessing

This module provides sentence split, tokenization, part-of-speech tagging, lemmatization and dependency parsing.

### spaCy

[spaCy](https://spacy.io/) is an open-source Python library for Natural Language Processing.

```bash
$ radtext-preprocess spacy -i /path/to/input.xml -o /path/to/output.xml
```

### Stanza

[Stanza](https://stanfordnlp.github.io/stanza/) is a collection of efficient tools for Natural Language Processing.

```bash
$ radtext-preprocess stanza -i /path/to/input.xml -o /path/to/output.xml
```

## Sentence Split

This module splits the report into sentences using [NLTK](https://www.nltk.org/api/nltk.tokenize.html).

```shell
$ radtext-ssplit -i /path/to/input.xml -o /path/to/output.xml
```

## Constituency Parsing

radtext uses the BLLIP reranking parser to obtain the parse tree. 
The BLLIP parser was trained on the biomedical text.

```bash
$ radext-parse -i /path/to/input.xml -o /path/to/output.xml
```

## Named Entity Recognition

This module recognizes the named entities (e.g., disease findings, etc.) from the reports.

### Rule-based method

The rule-based method uses regular expressions that combine information from terminological 
resources and characteristics of the entities of interest.
They are manually constructed by domain experts.

```shell
$ ner regex --phrase /path/to/patterns.yml -i /path/to/input.xml -o /path/to/output.xml
```

### SpaCy's PhraseMatcher

```shell
$ ner spacy --radlex /path/to/Radlex.xls -i /path/to/input.xml -o /path/to/output.xml
```

[//]: # (We provide two NER options that users can choose from, Spacy and rule-based method. )
[//]: # (RadText detects all the findings and their corresponding UMLS concepts using MetaMap and spaCy.)
[//]: # (Spacy utilizes MetaMap ontology. In general, MetaMap is more comprehensive but at the same time MetaMap
[//]: # (can be noisy, while vocabulary is more accurate on the findings of interest. 
[//]: # (MetaMap is also slower and easier to break down than using vocabulary.
[//]: # (All vocabularies can be found in the folder named `resources`. )
[//]: # (Each file in the folder represents one type of named entities with various text expressions. )
[//]: # (You can specify your customized patterns via `--phrases_file=<file>`.&#41;&#41;&#41;)

## Dependency Parsing

Dependency Parsing is the process to analyze the grammatical structure in a sentence and find out related words 
as well as the type of the relationship between them.

RadText utilizes the Universal Dependency Graph ([UDG](https://universaldependencies.org/)) to describe the 
grammatical relationships in a sentence. 
UDG is a directed graph, which represents all universal dependency information in a sentence. 
The vertices in a UDG represent the information such as the word, part-of-speech and the word lemma. 
The edges in a UDG represent the typed dependencies from the governor to its dependent and are labeled 
with the corresponding dependency type. UDG effectively represents the syntactic head of each word in a 
sentence and the dependency relation between words.

* **spaCy**: See `Text preprocessing` > `spaCy`
* **Stanza**: See `Text preprocessing` > `Stanza` 
* **Bllip**: RadText obtains the universal dependencies by applying the 
[Stanford dependency converter](https://github.com/dmcc/PyStanfordDependencies) 
with the `CCProcessed` and `Universal` option. 

```shell
$ tree2dep -i /path/to/input.xml -o /path/to/output.xml
```

## Negation Detection

For negation detection, RadText employs [NegBio](https://github.com/bionlplab/negbio2), which utilizes universal dependencies for pattern definition and subgraph matching for graph traversal search so that the scope for negation/uncertainty is not limited to the fixed word distance.

```bash
$ python cmd/neg.py -i /path/to/parse_file.xml -o /path/to/neg_file.xml --overwrite
```

## Labels Collection

The final step merges all the labels and produces the output .csv file.

```bash
$ python cmd/collect_neg_labels.py --phrases ../resources/chexpert_phrases.yml -i /path/to/neg_file.xml -o /path/to/output_file.csv
```

