# Advanced Usage

This document covers some more advanced features of RadText.

### Running the pipeline step-by-step

The step-by-step pipeline generates all intermediate results. Users can easily rerun any step if it makes any errors. The system pipeline looks like:

1. `csv2bioc` transforms the .csv text file into a BioC XML file.
2. `deid` de-identifies all the reports using [Philter](https://github.com/BCHSI/philter-ucsf), hides protected health information (PHI) such as Name, Contact, Age, etc.
3. `split_section` splits the report into sections. Users can choose to use [NegBio](https://github.com/bionlplab/negbio2) `reg` split or [`medspacy`](https://spacy.io/universe/project/medspacy).
4. `preprocess` splits and tokenizes texts into sentences. Users can choose to use [NLTK](https://www.nltk.org/api/nltk.tokenize.html), [spaCy](https://spacy.io/) or [Stanza](https://stanfordnlp.github.io/stanza/).
5. `ner` - Named entity recognition (NER) recognizes the named entities (e.g., disease findings) in sentences. Users can choose to use NegBio, MetaMap or scispaCy.
6. `parse` parses sentences to obtain the universal dependency graph (UDG) to describe the grammatical relationships in a sentence. Users can choose to use [Stanza](https://stanfordnlp.github.io/stanza/) or [Bllip parser](https://github.com/BLLIP/bllip-parser).
7. `neg` detects negative and uncertain findings using [NegBio](https://github.com/bionlplab/negbio2).
8. `collect_neg_label` merges negative and uncertain labels.


### Prepare the dataset

This is the same process as [Quickstart-Preparing the dataset](https://radtext.readthedocs.io/en/latest/getting_started.html#preparing-the-dataset). You can skip this step if the reports are already in the [BioC]( http://bioc.sourceforge.net/) format. Otherwise, you can store your input reports in a .csv file (by default, column 'ID' stores the report ids, and column 'TEXT' stores the reports), and then use the following command to convert your .csv file into BioC format. 

```bash
$ python cmd/csv2bioc.py -i /path/to/input_file.csv -o /path/to/output_bioc_file.xml
```

**If you have lots of reports, it is recommended to put them into several BioC files, for example, 5000 reports per BioC file.**

### De-identification

This step de-identifies the radiology reports. Radiology reports often contain detailed sensitive information about individual patients, the nuances of their diseases, the treatment strategies and the resulting outcomes, which causes that clinical notes remain largely unused for research because they contain the protected health information (PHI) which is synonymous with individually identifying data. To address this issue, RadText uses [Philter](https://github.com/BCHSI/philter-ucsf) for de-identification, which removes PHI from the reports, such as Name, Contact, Age, Email, etc. 

To run de-identification, the output from last step (csv2bioc) is needed as the input.

```bash
$ python cmd/deidentify.py -i /path/to/bioc_file.xml -o /path/to/deid_file.xml
```

### Section Split

This step splits the report into sections. RadText provides two options for section split, rule-based section splitter and [MedSpaCy](https://github.com/medspacy/medspacy). To run section split, the output from last step (de-id) is needed as the input. 

MedSpaCy is a rule-based spaCy tool for performing clinical NLP and text processing tasks. MedSpaCy includes an implementation of clinical section detection based on rule-based matching of the section titles with default rules adapted from [SecTag](https://pubmed.ncbi.nlm.nih.gov/18999303/) and expanded through practice. If users decide to use medspacy for section splitting, simply run:

```bash
$ pip install medspacy
$ python cmd/split_section.py medspacy -i /path/to/deid_file.xml -o /path/to/section_file.xml
```

If users decide to use rule-based section splitter, simply run:

```bash
$ python cmd/split_section.py reg [option] -i /path/to/deid_file.xml -o /path/to/section_file.xml
```

The default section titles are hard-coded in `/cmd/split_section.py`, but users can specify their customized section titles using the option `--section-titles=<file>`.


### Preprocess or Sentence Split

This step splits the report into sentences, and RadText provides three options, [spaCy](https://spacy.io/), [Stanza](https://stanfordnlp.github.io/stanza/) and [NLTK](https://www.nltk.org/api/nltk.tokenize.html).

Similarly, to run sentence split, the output from last step (section_split) is needed as the input. To use spaCy for pre-processing or sentence split, simply run:

```bash
$ pip install -U pip setuptools wheel
$ pip install -U spaCy
$ python -m spacy download en_core_web_sm
$ 
$ python cmd/preprocess_pipeline.py spacy -i /path/to/section_file.xml -o /path/to/ud_file.xml --overwrite
```

### Named Entity Recognition

This step recognizes the named entities (e.g., disease findings, etc.) from the reports. We provide two NER options that users can choose from, Spacy and rule-based method. RadText detects all the findings and their corresponding UMLS concepts using MetaMap and  spaCy. 

Rule-based NER methods use regular expressions that combine information from terminological resources and characteristics of the entities of interest that are manually constructed from report corpus. Run the following command to use rule-based method for NER:

```bash
$ pip install intervaltree
$ python cmd/ner.py regex --phrases ../resources/cxr14_phrases_v2.yml  -i /path/to/ud_file.xml -o /path/to/ner_file.xml --overwrite

```

Spacy utilizes MetaMap ontology. In general, MetaMap is more comprehensive but at the same time MetaMap can be noisy, while vocabulary is more accurate on the findings of interest. MetaMap is also slower and easier to break down than using vocabulary. All vocabularies can be found in the folder named `resources`. Each file in the folder represents one type of named entities with various text expressions. You can specify your customized patterns via `--phrases_file=<file>`.

### Dependency Parsing

RadText utilizes the universal dependency graph (UDG) to describe the grammatical relationships in a sentence that can be simply understood by non-linguists and effectively used by downstream processing tasks. UDG is a directed graph, which represents all universal dependency information in a sentence. The vertices in a UDG represent the information such as the word, part-of-speech and the word lemma. The edges in a UDG represent the typed dependencies from the governor to its dependent and are labeled with the corresponding dependency type. UDG effectively represents the syntactic head of each word in a sentence and the dependency relation between words. 

This step parses sentences to obtain the UDG, and RadText provides two options that users can choose from, [Stanza](https://stanfordnlp.github.io/stanza/) and [Bllip parser](https://github.com/BLLIP/bllip-parser). 

Stanza parses each sentence for its syntactic structure. Stanza's dependency parsing module builds a tree structure of words from the input sentence, which represents the syntactic dependency relations between words. After `tokenization`, `multi-word token (MWT) expansion`, `part-of-speech (POS) and morphological features tagging`, and `lemmatization`, each sentence would have been parsed into universal dependencies structure. Bllip parser trained with the biomedical model will result in a parse tree, then RadText obtains the universal dependencies by applying the [Stanford dependency converter](https://github.com/dmcc/PyStanfordDependencies) with the `CCProcessed` and `Universal` option. 

```bash
$ python cmd/parse.py -i /path/to/ner_file.xml -o /path/to/parse_file.xml 
```


### Negation Detection

For negation detection, RadText employs [NegBio](https://github.com/bionlplab/negbio2), which utilizes universal dependencies for pattern definition and subgraph matching for graph traversal search so that the scope for negation/uncertainty is not limited to the fixed word distance.

```bash
$ python cmd/neg.py -i /path/to/parse_file.xml -o /path/to/neg_file.xml --overwrite
```

### Labels Collection

The final step merges all the labels and produces the output .csv file.

```bash
$ python cmd/collect_neg_labels.py --phrases ../resources/chexpert_phrases.yml -i /path/to/neg_file.xml -o /path/to/output_file.csv
```

