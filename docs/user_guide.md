# Advanced Usage

This document covers some more advanced features of RadText.

## De-identification

Radiology reports often contain the Protected Health Information 
([PHI](https://www.hhs.gov/hipaa/for-professionals/privacy/special-topics/de-identification/index.html#standard)).
This module uses [Philter](https://github.com/BCHSI/philter-ucsf) to remove PHI
from the reports.

```shell
$ radtext-deid --repl=X -i /path/to/input.xml -o /path/to/output.xml
```

## Section Split

This module splits the report into sections. 
RadText provides two options for section split.

The **rule-based method** uses a list of section titles to split the notes.
The default section titles are hard-coded in `resources/section_titles.txt`.
Users can also specify customized section titles using the option `--section-titles=<file>`.

```shell
$ radtext-secsplit regex -i /path/to/input.xml -o /path/to/output.xml
```

[**MedSpaCy**](https://github.com/medspacy/medspacy) is a spaCy tool for performing
clinical NLP and text processing tasks.
It includes an implementation of clinical section detection based on rule-based
matching of the section titles with default rules adapted from
[SecTag](https://pubmed.ncbi.nlm.nih.gov/18999303/) and
expanded through practice.

```shell
$ radtext-secsplit medspacy -i /path/to/input.xml -o /path/to/output.xml
```

## Text preprocessing

This module provides sentence split, tokenization, part-of-speech tagging,
lemmatization and dependency parsing.

[**spaCy**](https://spacy.io/) is an open-source Python library for Natural Language
Processing.

```bash
$ radtext-preprocess spacy -i /path/to/input.xml -o /path/to/output.xml
```

[**Stanza**](https://stanfordnlp.github.io/stanza/) is a collection of efficient
tools for Natural Language Processing.

```bash
$ radtext-preprocess stanza -i /path/to/input.xml -o /path/to/output.xml
```

## Sentence Split

This module splits the report into sentences using
[NLTK](https://www.nltk.org/api/nltk.tokenize.html).

```shell
$ radtext-ssplit -i /path/to/input.xml -o /path/to/output.xml
```

## Constituency Parsing

RadText uses the [Bllip parser](https://github.com/BLLIP/bllip-parser)
to obtain the parse tree. The Bllip parser was trained on the biomedical text.

```shell
$ radext-parse -i /path/to/input.xml -o /path/to/output.xml
```

## Named Entity Recognition

This module recognizes the named entities (e.g., disease findings) from the reports.

The **rule-based method** uses regular expressions that combine information from
terminological resources and characteristics of the entities of interest.
They are manually constructed by domain experts.

```shell
$ radext-ner regex --phrase /path/to/patterns.yml -i /path/to/input.xml -o /path/to/output.xml
```

[**SpaCy's PhraseMatcher**](https://spacy.io/api/phrasematcher) provides another
way to efficiently match large terminology lists. RadText uses PhraseMatcher to
recognize concepts in the [RadLex ontology](http://radlex.org/).

```shell
$ radext-ner spacy --radlex /path/to/Radlex4.1.xlsx -i /path/to/input.xml -o /path/to/output.xml
```

## Dependency Parsing

Dependency Parsing is the process to analyze the grammatical structure in a
sentence and find out related words as well as the type of the relationship
between them.

RadText utilizes the Universal Dependency Graph
([UDG](https://universaldependencies.org/)) to describe the grammatical
relationships in a sentence. UDG is a directed graph, which represents all
universal dependency information in a sentence. The vertices in a UDG represent
the information such as the word, part-of-speech and the word lemma.
The edges in a UDG represent the typed dependencies from the governor to its
dependent and are labeled with the corresponding dependency type. UDG
effectively represents the syntactic head of each word in a
sentence and the dependency relation between words.

* **spaCy**: See `Text preprocessing` > `spaCy`
* **Stanza**: See `Text preprocessing` > `Stanza` 
* **Bllip**: RadText obtains the universal dependencies by applying the 
[Stanford dependency converter](https://github.com/dmcc/PyStanfordDependencies) 
with the `CCProcessed` and `Universal` option. 

```shell
$ radext-tree2dep -i /path/to/input.xml -o /path/to/output.xml
```

## Negation Detection

For negation detection, RadText employs
[NegBio](https://github.com/bionlplab/negbio2), which utilizes universal
dependencies for pattern definition and subgraph matching for graph traversal
search so that the scope for negation/uncertainty is not limited to the fixed
word distance.

```shell
$ radext-neg -i /path/to/input.xml -o /path/to/output.xml
```

## Labels Collection

The final step merges all the labels and produces the output .csv file.

```shell
$ python radtext/cmd/collect_neg_labels.py \
    --phrases /path/to/patterns.yml \
    -i /path/to/input.xml \
    -o /path/to/output_file.csv
```

