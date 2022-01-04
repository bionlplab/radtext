<!-- ![RadText](https://github.com/yfpeng/radtext/blob/master/radtext.png?raw=true) -->

<img src="https://github.com/yfpeng/radtext/blob/master/radtext.png?raw=true" alt="RadText" width="700"/>

RadText is a high-performance Python Radiology Text Analysis System.

## Get Started

1. Download RadText

	```bash
	$ git clone https://github.com/yfpeng/radtext.git
	$ cd /path/to/radtext
	```

2. Prepare the dataset. 
   We recommend that you store your input reports in [BioC](http://bioc.sourceforge.net/) format. Some examples can be found in the `examples` folder. If you have lots of reports, it is recommended to put them into several BioC files, for example, 5000 reports per BioC file.

   You can use the following commands to convert your text files into BioC format.

   ```bash
   $ export TEXT_DIR=/path/to/text
   $ export BIOC_DIR=/path/to/bioc_output
   $ python radtext/radtext_pipeline.py text2bioc --output=$BIOC_DIR/test.xml $TEXT_DIR/*.txt
   ```


3. Run the script. See [User guide](https://radtext.readthedocs.io/en/latest/user_guide.html).

## Documentation

Documentation is available from http://radtext.readthedocs.io

## Contributing

Refer to our [contribution guide](https://radtext.readthedocs.io/en/latest/contributing.html).