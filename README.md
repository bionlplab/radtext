<!-- ![RadText](https://github.com/yfpeng/radtext/blob/master/radtext.png?raw=true) -->

<img src="https://github.com/yfpeng/radtext/blob/master/radtext.png?raw=true" alt="RadText" width="700"/>

[![Build
status](https://github.com/bionlplab/radtext/actions/workflows/pytest.yml/badge.svg)](https://github.com/bionlplab/radtext/)
[![Latest version on
PyPI](https://img.shields.io/pypi/v/radtext.svg)](https://pypi.python.org/pypi/radtext)
[![Downloads](https://img.shields.io/pypi/dm/radtext.svg)](https://pypi.python.org/pypi/radtext)
[![License](https://img.shields.io/pypi/l/radtext.svg)](https://opensource.org/licenses/MIT)

RadText is a high-performance Python Radiology Text Analysis System.

## Prerequisites

1. Python >= 3.6, <3.9
2. Linux
3. Java

## Get Started

### Download radtext

```bash
$ git clone https://github.com/bionlplab/radtext.git
$ cd radtext
```

Once you have a copy of the resource, you can prepare a virtual environment.

```shell
$ python -m venv radtext_env
$ source radtext_env/bin/activate
```

Then install the required packages:

```bash
$ pip install -r requirements.txt
```

NOTE: If you encounter `Building wheel for bllipparser (setup.py) ... error` when installing bllipparser, 
try installing these two packages first, then restarting your virtual environment:
   
```bash
$ conda install gcc_linux-64
$ conda install gxx_linux-64
$ conda deactivate
$ conda activate radtext
```

### Prepare the dataset. 

RadText uses [BioC](http://bioc.sourceforge.net/) format as the unified interface. Some examples can be found in the `examples` folder. You can store your input reports in a .csv file (by default, column 'ID' stores the report ids, and column 'TEXT' stores the reports), and then use the following command to convert your .csv file into BioC format. 

```bash
$ python cmd/csv2bioc.py -i /path/to/csv_file -o /path/to/bioc_file
```

If you have lots of reports, it is recommended to put them into several BioC files, for example, 5000 reports per BioC file. 

### Run radtext

Run RadText to analyze radiology reports. Please refer to [User guide](https://radtext.readthedocs.io/en/latest/user_guide.html) for details.

## Import radtext as a Python Library and use API

This following code snippet shows an example of using radtext's pipeline to analyze radiology report.

```python
import radtext

# initialize RadText's pipeline.
nlp = radtext.Pipeline()

# run RadText's pipeline on a sample report.
collection = nlp('FINDINGS: The lungs are clear without consolidation, effusion or edema...')

print(collection)
```

The annotation results are stored in a `Collection` instance, the following code snippet shows an example of accessing the detected disease findings and the corresponding negation status.

```python
for doc in collection.documents:
   for passage in doc.passages:
      for annotation in passage.annotations:
         print(annotation.infon['source_concept'], annotation.infon['negation'])
```

RadText's API supports the mutual conversion between BioC format and OMOP CDM. The following code snippet shows an example of converting BioC to CDM, and then converting CDM to BioC.

```python
import bioc
from radtext import BioC2CDM, CDM2BioC

# initialize RadText's BioC2CDM converter.
bioc2cdm = BioC2CDM()
with open('/PATH/TO/BIOC_FILE.xml') as fp:
    collection = bioc.load(fp)

cdm_df = bioc2cdm(collection)

# initialize RadText's CDM2BioC converter.
cdm2bioc = CDM2BioC()
bioc_collection = cdm2bioc(cdm_df)
```

## Documentation

Documentation is available [here](https://radtext.readthedocs.io/en/latest/index.html).

## Contributing

Refer to our [contribution guide](https://radtext.readthedocs.io/en/latest/contributing.html).

## Acknowledgment

This work is supported by the National Library of Medicine under Award No. 4R00LM013001 and the NIH Intramural Research Program, National Library of Medicine. 
