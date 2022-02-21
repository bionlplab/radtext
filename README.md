<!-- ![RadText](https://github.com/yfpeng/radtext/blob/master/radtext.png?raw=true) -->

<img src="https://github.com/yfpeng/radtext/blob/master/radtext.png?raw=true" alt="RadText" width="500"/>

[![Build
status](https://github.com/bionlplab/radtext/actions/workflows/pytest.yml/badge.svg)](https://github.com/bionlplab/radtext/)
[![Latest version on
PyPI](https://img.shields.io/pypi/v/radtext.svg)](https://pypi.python.org/pypi/radtext)
[![Downloads](https://img.shields.io/pypi/dm/radtext.svg)](https://pypi.python.org/pypi/radtext)
[![License](https://img.shields.io/pypi/l/radtext.svg)](https://opensource.org/licenses/MIT)
[![codecov](https://codecov.io/gh/bionlplab/radtext/branch/after_paper/graph/badge.svg?token=m4mJ9fD88s)](https://codecov.io/gh/bionlplab/radtext)
[![Documentation Status](https://readthedocs.org/projects/radtext/badge/?version=latest)](https://radtext.readthedocs.io/en/latest/?badge=latest)

## Purpose

RadText is a high-performance Python Radiology Text Analysis System.

## Prerequisites

* Python >= 3.6, <3.9
* Linux 
* Java

## Quickstart for RadText

```shell
# Set up environment
$ sudo apt-get install python3-dev build-essential default-java

# Checkout repository
$ git clone https://github.com/bionlplab/radtext.git
$ cd radtext

# Set up Python environment
$ python -m venv venv
$ source venv/bin/activate

# Install dependencies
$ python -m pip install --upgrade pip
$ pip install -r requirements.txt

# Install packages
$ python -m spacy download en_core_web_sm
$ export PYTHONPATH=src
$ python src/radtext/cmd/download.py all

# Test with pytest
$ pip install pytest
$ pytest tests
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

[MIT](https://github.com/bionlplab/radtext/blob/master/LICENSE) © 2022 BioNLP
Lab at Weill Cornell Medicine
