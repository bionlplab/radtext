<!-- ![RadText](https://github.com/yfpeng/radtext/blob/master/radtext.png?raw=true) -->

<img src="https://github.com/yfpeng/radtext/blob/master/radtext.png?raw=true" alt="RadText" width="500"/>

[![Build status](https://github.com/bionlplab/radtext/actions/workflows/pytest.yml/badge.svg)](https://github.com/bionlplab/radtext/)
[![Latest version on PyPI](https://img.shields.io/pypi/v/radtext.svg)](https://pypi.python.org/pypi/radtext)
[![Downloads](https://img.shields.io/pypi/dm/radtext.svg)](https://pypi.python.org/pypi/radtext)
[![License](https://img.shields.io/pypi/l/radtext.svg)](https://opensource.org/licenses/MIT)
[![codecov](https://codecov.io/gh/bionlplab/radtext/branch/after_paper/graph/badge.svg?token=m4mJ9fD88s)](https://codecov.io/gh/bionlplab/radtext)
[![Documentation Status](https://readthedocs.org/projects/radtext/badge/?version=latest)](https://radtext.readthedocs.io/en/latest/?badge=latest)
[![Pythong version](https://img.shields.io/pypi/pyversions/radtext)](https://pypi.python.org/pypi/radtext)

## Purpose

RadText is a high-performance Python Radiology Text Analysis System.

## Prerequisites

* Python >= 3.6, <3.9
* Linux 
* Java

```shell
# Set up environment
$ sudo apt-get install python3-dev build-essential default-java
```

## Quickstart

The latest radtext releases are available over
[pypi](https://pypi.python.org/pypi/radtext).

Using pip, RadText releases are available as source packages and binary wheels.
It is also generally recommended installing packages in a virtual environment to
avoid modifying system state:

```shell
$ python -m venv venv
$ source venv/bin/activate
$ pip install -U pip setuptools wheel
$ pip install -U radtext
$ python -m spacy download en_core_web_sm
$ radtext-download --all
```

To see RadText’s pipeline in action, you can launch the Python interactive
interpreter, and try the following commands:

```python
import radtext
nlp = radtext.Pipeline()
doc = nlp('There is no plural effusion')
print(doc)
```

RadText also supports command-line interfaces for specific NLP tasks (e.g.,
de-identification, sentence split, or named entity recognition).

```shell
$ radtext-deid --repl=X -i /path/to/input.xml -o /path/to/output.xml
$ radtext-ssplit -i /path/to/input.xml -o /path/to/output.xml
$ radext-ner spacy --radlex /path/to/Radlex4.1.xlsx -i /path/to/input.xml -o /path/to/output.xml
```

## Documentation

You will find complete documentation at our [Read the Docs
site](https://radtext.readthedocs.io/en/latest/index.html).

## Contributing

You can find information about contributing to RadText at our [Contribution
page](https://radtext.readthedocs.io/en/latest/contributing.html).

## Acknowledgment

This work is supported by the National Library of Medicine under Award No.
4R00LM013001 and the NIH Intramural Research Program, National Library of
Medicine.

You can find Acknowledgment information at our [Acknowledgment
page](https://radtext.readthedocs.io/en/latest/acknowledgments.html).

## License

Copyright BioNLP Lab at Weill Cornell Medicine, 2022.

Distributed under the terms of the [MIT](https://github.com/bionlplab/radtext/blob/master/LICENSE) license, RadText is free and open soure software.
