<!-- ![RadText](https://github.com/yfpeng/radtext/blob/master/radtext.png?raw=true) -->

<img src="https://github.com/yfpeng/radtext/blob/master/radtext.png?raw=true" alt="RadText" width="700"/>

RadText is a high-performance Python Radiology Text Analysis System.

## Prerequisites

1. Python >= 3.6
2. Linux
3. Java

## Get Started

1. Download RadText

	```bash
	$ git clone https://github.com/yfpeng/radtext.git
	$ cd radtext
	```

2. Once you have a copy of the resource, you can prepare a virtual environment.

   ```bash
   $ conda create --name radtext python=3.6
   $ source activate radtext 
   $ pip install --upgrade pip setuptools
   ```

   or 

   ```bash
   $ virtualenv --python=/usr/bin/python3.6 radtext_env
   $ source radtext_env/bin/activate
   ```

   Then install the required packages:

   ```bash
   $ pip install -r requirements.txt
   ```

3. Prepare the dataset. 
   We recommend that you store your input reports in [BioC](http://bioc.sourceforge.net/) format. Some examples can be found in the `examples` folder. If you have lots of reports, it is recommended to put them into several BioC files, for example, 5000 reports per BioC file.

   You can use the following commands to covert your .csv files (which have two columns, column named 'subject_id' for the report id, column named 'text' for the reports) into BioC format.

   ```bash
   $ python cmd/csv2bioc.py -i /path/to/csv_file -o /path/to/bioc_file --id_col subject_id --text_col text
   ```

4. Run the script to analyze radiology reports. Please refer to [User guide](https://radtext.readthedocs.io/en/latest/user_guide.html) for details.

## Documentation

Documentation is available from http://radtext.readthedocs.io

## Contributing

Refer to our [contribution guide](https://radtext.readthedocs.io/en/latest/contributing.html).