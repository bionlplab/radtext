# Quickstart

This section runs through the API for common tasks to analyze the radiology
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
the csv format) to the BioC collection. By default, column 'note_id' stores
the report ids, and column 'note_text' stores the reports

```shell
# Convert from csv to BioC
$ radtext-csv2bioc -i /path/to/csv_file.csv -o /path/to/bioc_file.xml

# Convert from NOTE table to BioC
$ radtext-cdm2bioc -i /path/to/csv_file.csv -o /path/to/bioc_file.xml
```

**Note**:
If you have lots of reports, it is recommended to put them into several BioC
files, for example, 5000 reports per BioC file.

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
For example, the the `parse.xml` file consists of the parse tree of each
sentence. The content and format of these files should be self-explained.

-----

Read more about [Advanced
Usage](https://radtext.readthedocs.io/en/latest/user_guide.html).