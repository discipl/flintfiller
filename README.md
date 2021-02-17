# FlintFiller

This project is created to automatically create Flint Frames. 

## Usage

This project contains a small set of Dutch laws in xml format that are already processed and ready to view.
You can find the files under data, in different formats including flint frames.
If you want to run the code on a new xml, add your xml file and go to the project location on your computer 
and follow the following steps:

### Getting started
- `pip install poetry`
- `poetry config virtualenvs.in-project true`
- `poetry install`

- Go to project settings of your editor and set the created virtual environment as project interpreter
- **Important:** this tool uses python 3.6 because the pattern package, which is used for the part-of-speech tagging, 
only supports python 3.6. Running FlintFiller with a higher python version results in the following error:
```
packages\pattern\text\__init__.py", line 625, in <genexpr>
    dict.update(self, (x.split(" ")[:2] for x in _read(self._path) if len(x.split(" ")) > 1))
RuntimeError: generator raised StopIteration
```

#### Commandline usage of FlintFiller

After installation of the dependencies through poetry you can enter the following example command:

``` bash
python src/main.py 
-x data/xml_files/BWBR0011823_2019-02-27_(Vreemdelingenwet).xml 
-d data/json_files/BWBR0011823_2019-02-27_(Vreemdelingenwet).json 
-df data/csv_files/BWBR0011823_2019-02-27_Vreemdelingenwet.csv 
-pt data/csv_files/BWBR0011823_2019-02-27_Vreemdelingenwet_postagged.csv
-fo data/flint_frames_BWBR0011823_2019-02-27_Vreemdelingenwet.json
```

with arguments:
- -x/--xml : The input xml file
- -d/--dict_file : The (desired) file location of the dictionary
- -df/--df_file : The (desired) file location of the dataframe
- -pt/--pt_file : The (desired) file location of the postagged dataframe
- -fo/--flint_output: The desired output file for the flint frames 

Arguments are not required, for instance you can pass only an xml and a location for your dictionary file and it will
parse the xml to a dictionary. If you already have a POS tagged dataframe in the right format, you can also pass that,
and pass a location for the flint frames output. 

By running main, you are running both JuriDecompose and FlintFiller. JuriDecompose and FlintFiller are independently 
callable too (with the same arguments as src/main):
``` bash
python flintfiller/flintfiller.py 
python juridecompose/juridecompose.py 
```

For more technical information see the technical-README.md


## CSV

To view the CSV files that are parsed from the XML files:
Go to Powershell and the location of your CSV file.
Run the following command:

```
Import-Csv your_file.csv |Out-Gridview
```

You can also import csv data in excel. 

### Juriconnect

In the CSV you find the juriconnect columns, jci1.0 and jci1.3. a juriconnect reference is build like this: 

```
    jci1.3:{type}:{BWB-nummer}{key-value paar}*
```

For more information see https://www.forumstandaardisatie.nl/sites/bfs/files/Juriconnect_Standaard_BWB_1_3_1.pdf.

### JSON Flint Frames

The JSON flint frames can be opened using Visual Studio Code with the FlintEditor plugin.
Otherwise it can be opened using Text Editors such as Notepad++.

## Documentation

A more thorough theoretical description of FlintFiller can be found in the [TNO FlintFiller report](./TNO_FlintFiller_report.pdf)
(in Dutch only)

## Maintainers
Roos Bakker, TNO (roos.bakker@tno.nl)

Maaike de Boer, TNO (maaike.deboer@tno.nl)

## License

FlintFiller is released under Apache 2.0, for more information see the LICENSE.

