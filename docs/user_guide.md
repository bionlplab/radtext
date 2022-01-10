# Advanced Usage

This document covers some more advanced features of RadText.

### Running the pipeline step-by-step

The step-by-step pipeline generates all intermediate documents. You can easily rerun one step if it makes errors. The whole steps are

1. `csv2bioc` transforms the .csv text files into a BioC XML file.
2. `deid` de-identifies all the reports, hides patient information such as Name, Contact, Age, etc.
3. `split_section` splits the report into sections. User can choose to use rule-based `reg` split or [`medspacy`](https://spacy.io/universe/project/medspacy).
4. `preprocess` splits texts into sentences. User can choose to use [`spacy`](https://spacy.io/) or [`stanza`](https://stanfordnlp.github.io/stanza/).
5. Named entity recognition. Users can choose to use rule-based `regex` or `spacy`. 
6. `parse` parses sentences. Users can choose to use [Stanza](https://stanfordnlp.github.io/stanza/) or [Bllip parser](https://github.com/BLLIP/bllip-parser).
7. `neg` detects negative and uncertain findings using [NegBio2](https://github.com/bionlplab/negbio2).
8. `collect_neg_label` merges negative and uncertain labels.


### Convert text files to BioC format

You can skip this step if the reports are already in the [BioC]( http://bioc.sourceforge.net/) format.
**If you have lots of reports, it is recommended to put them into several BioC files, for example, 5000 reports per BioC file.**

```bash
$ python cmd/csv2bioc.py -i /path/to/csv_file -o /path/to/bioc_file
```
### De-identify reports

This step de-identifies the radiology reports. Radiology reports often contain detailed sensitive information about individual patients, the nuances of their diseases, the treatment strategies and the resulting outcomes, which causes that clinical notes remain largely unused for research because they contain the protected health information (PHI) which is synonymous with individually identifying data. To address this issue, RadText uses [Philter](https://github.com/BCHSI/philter-ucsf) for de-identification, which removes PHI from the reports, such as Name, Contact, Age, Email, etc. 

### Split each report into sections

This step splits the report into sections. Users can choose to use rule-based section splitter or [MedSpaCy](https://github.com/medspacy/medspacy). MedSpaCy is a rule-based spaCy tool for performing clinical NLP and text processing tasks. If users decide to use rule-based section splitter, simply run:

```bash
$ python cmd/split_section.py reg [options] -i /path/to/input -o /path/to/output
```

The default section titles are hard-coded in `/cmd/split_section.py`, but users can specify their customized section titles using the option `--section-titles=<file>`.

If users decide to use medspacy for section splitting, simply run:

```bash
$ python cmd/split_section.py medspacy -i /path/to/input -o /path/to/output
```

### Splits each report into sentences

This step splits the report into sentences using the NLTK splitter
([nltk.tokenize.sent_tokenize](https://www.nltk.org/api/nltk.tokenize.html)).

### Named entity recognition

This step recognizes named entities (e.g., findings, diseases, devices, etc.) from the reports. We provide two NER options that users can choose from, Spacy and rule-based method.

```bash
$ python cmd/ner.py spacy -radlex "$radlex_file" -i "$ud_file" -o "$ner_file" 

```

or 

```bash
$ python cmd/ner.py regex -phrases "$phrase_file" -i "$ud_file" -o "$ner_file" 
```

Spacy utilizes MetaMap ontology. In general, MetaMap is more comprehensive but at the same time MetaMap can be noisy, while vocabulary is more accurate on the findings of interest. MetaMap is also slower and easier to break down than vocabulary. All vocabularies can be found at `resources`. Each file in the folder represents one type of named entities with various text expressions. You can specify your customized patterns via `--phrases_file=<file>`.

### Parse the sentences

This step parses sentences, and we provide two options that users can choose from, [Stanza](https://stanfordnlp.github.io/stanza/) and [Bllip parser](https://github.com/BLLIP/bllip-parser). The resulting parsing trees of Bliip parser will be further converted to universal dependencies using [Stanford converter](https://github.com/dmcc/PyStanfordDependencies).

### Detect negative and uncertain findings

This step detects negative and uncertain findings using [NegBio2](https://github.com/bionlplab/negbio2).
