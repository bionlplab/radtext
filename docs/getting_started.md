# Quickstart

This section runs through a pipeline for common tasks to analyze the radiology
reports.

## Working with data
    
RadText uses [BioC](http://bioc.sourceforge.net/) format as the unified interface. 
BioC is a simple format to share text data and annotations. It allows a large
number of different annotations to be represented.
The BioC data model is capable of representing a broad range of data elements
from a collection of documents through passages, sentences, down to annotations
on individual tokens and relations between them. Thus it is suitable for
reflecting information at different levels and is appropriate for a wide range
of common tasks.
   
```xml
<?xml version='1.0' encoding='utf-8' standalone='yes'?>
<collection>
  <source>SOURCE</source>
  <date>DATE</date>
  <key>KEY</key>
  <document>
    <id>0001</id>
    <passage>
      <offset>0</offset>
      <text>FINDINGS:...</text>
    </passage>
    <passage>
      <offset>120</offset>
      <text>IMPRESSION:...</text>
    </passage>  
  </document>
  <document>
    <id>0002</id>
    <passage>
      <offset>0</offset>
      <text>FINDINGS:...</text>
    </passage>
    <passage>
      <offset>170</offset>
      <text>IMPRESSION:...</text>
    </passage>
  </document>
</collection>
```

RadText also offers a tool to convert from [OMOP CDM NOTE
table](https://www.ohdsi.org/web/wiki/doku.php?id=documentation:cdm:note) (in
the CSV format) to the BioC collection. By default, column 'note_id' stores
the report ids, and column 'note_text' stores the reports.

```shell
# Convert from csv to BioC
$ radtext-csv2bioc -i /path/to/csv_file.csv -o /path/to/bioc_file.xml

# Convert from NOTE table to BioC
$ radtext-cdm2bioc -i /path/to/csv_file.csv -o /path/to/bioc_file.xml
```

```{warning}
If you have lots of reports, it is recommended to put them into several BioC
files, for example, 5000 reports per BioC file.
```

## Running RadText 

You can configure the input file names in `run_pipeline.sh`. Then use the
following command to run RadText's pipeline:

```bash
$ bash run_pipeline.sh
```

After the script is finished, you can find the labels at `output/output.csv`.
Each row is related to one report, and has multiple findings, such as
Atelectasis and Cardiomegaly. In this file, 1 means positive findings, 0 means
negative findings, and -1 means uncertain findings. The definition of findings
can be found at `./resources/cxr14_phrases_v2.yml`.

The pipeline will also generate 6 intermediate files.
For example, the `parse.xml` file consists of the parse tree of each
sentence. The content and format of these files should be self-explained.

## Building a Pipeline

RadText provides simple, flexible, and unified interfaces for downloading and
running various NLP models. At a high level, to start annotating text, you need
to first initialize a Pipeline, which pre-loads and chains up a series of
BioCProcessor, with each processor performing a specific NLP task (e.g.,
de-identification, sentence split, or named entity recognition).

Downloading models and building a pipeline of models shares roughly the same
interface. Additionally, when building a pipeline, you can add customized
options that select annotators, specify model path, or set variables. 
Here we aim to provide examples that cover common use cases.
For all available options in the download and pipeline interface, please refer
to the [Advanced Usage](https://radtext.readthedocs.io/en/latest/user_guide.html).

The following minimal example shows how to download and load default processors
into a pipeline for radiology reports:

```python
radtext.download()
nlp = radtext.Pipeline()
```

```{note}
You only need to call download once for a fresh install or to check for model
updates.
```

### Specifying Processors

You can specify the processors to load, by listing the processor names in a list
of string. For example, here we only load the default de-identification and
ssplit processors:

```python
nlp = radtext.Pipeline(annotators=['deid:philter', 'ssplit'])
```

### Annotating text

Annotating text is simple after a Pipeline is built and finishes loading: you
can simply pass the text to the pipeline instance and access all annotations
from the bioc object.

If the input is a str, the returned object is BioSentence. If the input is
BioCCollection, BioCDocument, BioCPassage, or BioCSentence, the returned object
is the same as the input.

```python
doc = nlp('There is no plural effusion')
```

```python
with open(filename) as fp:
    collection = bioc.load(fp)
collection = nlp(collection)
```

The following example shows how to print the text, lemma and POS tag of each
word in each sentence of an annotated document:

```python
for doc in collection.documents:
    for passage in doc.passages:
        for sentence in passage.sentences:
            for ann in sentence.annotations:
                print(ann.text, ann.infons['lemma'], ann.infons['tag'])
```

The following example shows how to print all abnormal findings in a document:

```python
for doc in collection.documents:
    for passage in doc.passages:
        for ann in passage.annotations:
            if 'nlp_system' in ann.infons \
                and 'ner:regex' in ann.infons['nlp_system']:
                print(ann.text)
```

-----

Read more about [Advanced
Usage](https://radtext.readthedocs.io/en/latest/user_guide.html).