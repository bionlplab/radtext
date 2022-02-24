# Quickstart

This section runs through a pipeline for common tasks to analyze the radiology
reports.

## Working with data
    
See [this doc](pipeline/data_conversion.md).

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