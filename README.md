<!-- ![RadText](https://github.com/yfpeng/radtext/blob/master/radtext.png?raw=true) -->

<img src="https://github.com/yfpeng/radtext/blob/master/radtext.png?raw=true" alt="RadText" width="700"/>

RadText is a high-performance Python Radiology Text Analysis System.

## Prerequisites

1. Python >= 3.6
2. Linux
3. Java

## Get Started

1. Download RadText.

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

   NOTE: If you encouter `Building wheel for bllipparser (setup.py) ... error` when installing bllipparser, try installing these two packages first, then restarting your virtual environment:
   
   ```bash
   $ conda install gcc_linux-64
   $ conda install gxx_linux-64
   $ 
   $ conda deactivate
   $ conda activate radtext
   ```

3. Prepare the dataset. 

   RadText uses [BioC](http://bioc.sourceforge.net/) format as the unified interface. Some examples can be found in the `examples` folder. You can store your input reports in a .csv file (by default, column 'ID' stores the report ids, and column 'TEXT' stores the reports), and then use the following command to convert your .csv file into BioC format. 

   ```bash
   $ python cmd/csv2bioc.py -i /path/to/csv_file -o /path/to/bioc_file
   ```

   If you have lots of reports, it is recommended to put them into several BioC files, for example, 5000 reports per BioC file. 

4. Run RadText to analyze radiology reports. Please refer to [User guide](https://radtext.readthedocs.io/en/latest/user_guide.html) for details.

## Documentation

Documentation is available from http://radtext.readthedocs.io

## Contributing

Refer to our [contribution guide](https://radtext.readthedocs.io/en/latest/contributing.html).