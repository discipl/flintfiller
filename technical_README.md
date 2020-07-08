# FlintFiller

This project is created to automatically create Flint Frames. 
This is the technical README.

## flintfiller.py

This is the main file that reads the arguments and calls the right code to parse. 

## wetten_xml_to_dict.py
This code takes the xml from wetten.nl as input and translates it into a dictionary (json)

## dict_to_dataframe.py
This code takes the dictionary and transforms it to a Pandas dataframe.
The extracted columns are: artikelnr: (number of the article), text: (all text within that article), 
jci1.0: (jci1 code), jci1.3: (jci 1.3 code), versie: (version of the law). Adding more columns is possible in the same 
manner as they are currently coded.

## chunk_tag_dataframe.py
This code parses each sentence in the text and adds a list of lists as a column to the dataframe with part of speech 
tags. Additionally, a dictionary of infinitive:original_verb is added as an additional column (verbs:) in the 
dataframe.

## dataframe_to_frame_parser.py
This code takes as input the dataframe with the dict of the law and the added NLP (chunk tag and infinitives) columns.
This is the main code that transforms the texts to flint frames.
Currently only fact and act frames are produced.
The act frames use action verbs to start an act frame. The act frames are not complete nor checked, because this code automatically creates the frames.
The fact frames are only created using the definitions of Article 1.

## pyproject.toml
This is the file that states the packages that have to be downloaded to make the code run. You can install the 
requirements with:

### Getting started
- `pip install poetry`
- `poetry config virtualenvs.in-project true` # Makes sure that the env gets build in current directory/project
- `poetry install`
- Go to project settings set created virtual environment as project interpreter


### Development 
#### dependency management
- `poetry update` # Update to latest version of dependencies as specified in [pyproject.toml](pyproject.toml)
- `poetry add [packagename] --dev` # Install and document new package (--dev optional if development package)
- `poetry remove [packagename]` # Remove package
- `poetry run [command]` # Enters venv and then executes specified command
- `poetry shell` #activate virtual environment

## License

FlintFiller is released under Apache 2.0, for more information see the LICENSE.
