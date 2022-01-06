# Quickstart

Now that you have properly installed RadText, let's walk you through how to get started with RadText to analyze your radiology reports!


## Preparing the dataset
    
The inputs of RadText should be in the [BioC](http://bioc.sourceforge.net/>) format. 

Briefly, a BioC-format file is an XML document as the basis of the BioC data exchange and the BioC data classes. Each file contains a group of documents. Each document should have a unique id and one or more passages. Each passage should have (1) a non-overlapping offset that specifies the location of the passage with respect to the whole document, and (2) the original text of the passage. 

The text can contains special characters such as newlines. An example of BioC-format file is shown here:
   
```xml
<?xml version='1.0' encoding='utf-8' standalone='yes'?>
<collection>
  <source>ChestXray-NIHCC</source>
  <date>2017-05-31</date>
  <key></key>
  <document>
    <id>0001</id>
    <passage>
      <offset>0</offset>
      <text>findings:
chest: four images:
right picc with tip within the upper svc.
probable enlargement of the main pulmonary artery.
mild cardiomegaly.
no evidence of focal infiltrate, effusion or pneumothorax.
dictating </text>
    </passage>
  </document>
  <document>
    <id>0002</id>
    <passage>
      <offset>0</offset>
      <text>findings: pa and lat cxr at 7:34 p.m.. heart and mediastinum are
stable. lungs are unchanged. air- filled cystic changes. no
pneumothorax. osseous structures unchanged scoliosis
impression: stable chest.
dictating </text>
    </passage>
  </document>
</collection>
```
If you have lots of reports, it is recommended to put them into several BioC files, for example, 5000 reports per BioC file.

You can use the following commands to covert your .csv files (by default, column 'ID' stores the report id, and columns 'TEXT' stores the reports) into BioC format.

```bash
  $ python cmd/csv2bioc.py -i /path/to/csv_file -o /path/to/bioc_file
```

## Running RadText

```bash
$ export OUTPUT_DIR=/path/to/output
$ export OUTPUT_LABELS=/path/to/output/labels.csv 
$ export INPUT_FILES="examples/1.xml examples/2.xml"
$ bash examples/run_negbio_examples.sh
```

You can also include all reports in one folder, so that the `$INPUT_FILES=examples/*.xml`

After the script is finished, you can find the labels at `examples-local/labels.csv`. It contains three rows with respect to three documents. Each row has multiple findings, such as Atelectasis and Cardiomegaly. The definition of findings can be found at `patterns/cxr14_phrases_v2.yml`. In this file, 1 means positive findings, 0 means negative findings, and -1 means uncertain findings.

Besides the final label file, 6 folders contain the intermediate files of each step, respectively. For example, the `ssplit` folder consists of sentences, and the `parse` folder consists of the parse tree of each sentence. The content and format of these files should be self-explained.

-----

Ready for more? Check out the `Advanced Usage` section.