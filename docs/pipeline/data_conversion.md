# Data conversion

This section describes how to seamlessly convert between BioC data model, the
plain str, and CDM NOTE table.

## BioC 

RadText uses the [BioC](http://bioc.sourceforge.net/) format as the unified interface. 
BioC is a simple format to share text data and annotations. It allows a large number of different annotations to be
represented. The BioC data model can represent a broad range of data elements from a collection of documents through
passages, sentences, down to annotations on individual tokens and relations between them. Thus it is suitable for
reflecting information at different levels and is appropriate for a wide range of common tasks.
   
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

```{warning}
If you have lots of reports, it is recommended to put them into several BioC
files, for example, 5000 reports per BioC file.
```

## OMOP CDM NOTE and NOTE_NLP tables

RadText also offers a tool to convert from [OMOP CDM NOTE
table](https://www.ohdsi.org/web/wiki/doku.php?id=documentation:cdm:note) (in
the CSV format) to the BioC collection. By default, column `note_id` stores
the report ids, and column `note_text` stores the reports.

```shell
# Convert from csv to BioC
$ radtext-csv2bioc -i /path/to/csv_file.csv -o /path/to/bioc_file.xml

# Convert from NOTE table to BioC
$ radtext-cdm2bioc -i /path/to/csv_file.csv -o /path/to/bioc_file.xml
```

