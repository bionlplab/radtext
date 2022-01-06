# Advanced Usage

This document covers some more advanced features of RadText.

### Running the pipeline step-by-step

The step-by-step pipeline generates all intermediate documents. You can easily rerun one step if it makes errors. The whole steps are

1. `csv2bioc` transforms the .csv text files into a BioC XML file.
2. `deid` de-identifies all the reports.
3. `split_section` splits the report into sections. User can choose to use rule-based `reg` split or [`medspacy`](https://spacy.io/universe/project/medspacy).
4. `preprocess` splits texts into sentences. User can choose to use [`spacy`](https://spacy.io/) or [`stanza`](https://stanfordnlp.github.io/stanza/).
5. Named entity recognition. User can choose to use rule-based `regex` or spacy. RadText also detects UMLS concepts using MetaMap. 
6. `parse` parses sentence using the [Bllip parser](https://github.com/BLLIP/bllip-parser).
7. `ptb2ud` converts the parse tree to universal dependencies using [Stanford converter](https://github.com/dmcc/PyStanfordDependencies).
8. `neg` detects negative and uncertain findings.
9. `collect_neg_label` merges negative and uncertain labels.

### General arguments

The general command is 

```bash
python negbio/negbio_pipeline.py <command> [options] --output=/path/to/output/dir /path/to/inputs
```

The `<command>` must be one of the steps above. The `--output` specifies the output directory. The `inputs` can be one or multiple files.

Other options include

2. `--suffix`: Append an additional `SUFFIX` to file names.
3. `--verbose`: Print more information about progress.
4. `--workers`: Number of threads.
5. `--files_per_worker`: Number of input files per worker.
6. `--overwrite`: Overwrite the output file.

### Convert text files to BioC format

You can skip this step if the reports are already in the [BioC]( http://bioc.sourceforge.net/) format.
**If you have lots of reports, it is recommended to put them into several BioC files, for example, 5000 reports per BioC file.**

```bash
python cmd/csv2bioc.py -i /path/to/csv_file -o /path/to/bioc_file
```
### De-identify reports

This step de-identifies the information in the reports.

### Split each report into sections

This step splits the report into sections. The default section titles is at `patterns/section_titles.txt`. You can specify customized section titles using the option `--pattern=<file>`.

### Splits each report into sentences

This step splits the report into sentences using the NLTK splitter
([nltk.tokenize.sent_tokenize](https://www.nltk.org/api/nltk.tokenize.html)).

### Named entity recognition

This step recognizes named entities (e.g., findings, diseases, devices) from the reports. 
In general, MetaMap is more comprehensive while vocabulary is more accurate on 14 types of findings.
MetaMap is also slower and easier to break than vocabulary.

#### Using MetaMap

The first version of NegBio uses MetaMap to detect UMLS concepts. Please make sure that both ``skrmedpostctl`` and ``wsdserverctl`` are started

MetaMap intends to extract all UMLS concepts.
Many of them are not irrelevant to radiology.
Therefore, it is better to specify the UMLS concepts of interest via `--cuis=<file>`

```bash
$ export METAMAP_BIN=METAMAP_HOME/bin/metamap16
$ negbio_pipeline dner_mm --metamap=$METAMAP_BIN --output=$OUTPUT_DIR $INPUT_DIR/*.xml
```

#### Using vocabularies

NegBio also integrates the CheXpert's method to use vocabularies to recognize the presence of 14 observations.
All vocabularies can be found at `patterns`.
Each file in the folder represents one type of named entities with various text expressions. You can specify customized patterns via `--phrases_file=<file>`.


### Parse the sentence

This step parses sentence using the [Bllip parser](https://github.com/BLLIP/bllip-parser).

### Convert the parse tree to UD

This step converts the parse tree to universal dependencies using [Stanford converter](https://github.com/dmcc/PyStanfordDependencies).

### Detect negative and uncertain findings

This step detects negative and uncertain findings using patterns.
By default, the program uses the negation and uncertainty patterns in the `patterns` folder.
However, You can specify customized patterns such as  `--neg-patterns=<file>`.

#### Patterns on the dependency graph

The pattern is a [semgrex-type](https://nlp.stanford.edu/nlp/javadoc/javanlp/edu/stanford/nlp/semgraph/semgrex/SemgrexPattern.html) pattern for matching node in the dependency graph.
Currently, we only support `<` and `>` operations.
A detailed grammar specification (using PLY, Python Lex-Yacc) can be found in `ngrex/parser.py`.

Since v2.0, NegBio integrates the CheXpert algorithms. NegBio utilizes a 3-phase pipeline consisting of pre-negation uncertainty, negation, and post-negation uncertainty ([Irvin et al., 2019](https://arxiv.org/abs/1901.07031)).
Each phase consists of rules which are matched against the mention; if a match is found, then the mention is classified
accordingly (as uncertain in the first or third phase, and as negative in the second phase).
If a mention is not matched in any of the phases, it is classified as positive.

You can specify customized patterns via `--neg-patterns=<file>`, `--pre-uncertainty-patterns=<file>`, and `--post-uncertainty-patterns=<file>`. Each file is an yaml-format file that consists of a list of patterns. Each pattern must have an `id` field and a `pattern` field. This allows NegBio to associate each pattern with the detected negation/uncertainty, to maximum the transparency. Examples can be found at `patterns`.

#### Regular expression patterns

NegBio also allows to use the regular expression to match simple cases. This function can also speed up the detection process, because pattern matching on the dependency graph is relatively slower. NegBio will first use regular expressions to match the text. If not found, semgrex is then used.

You can specify customized patterns via `--neg-regex-patterns=<file>` and `--uncertainty-regex-patterns=<file>`. Each file is an yaml-format file that consists of a list of patterns. Each pattern must have an `id` field and an `pattern` field. Examples can be found in `patterns`.

### Cleans intermediate information

This step removes intermediate information (sentence annotations) from the BioC files.
