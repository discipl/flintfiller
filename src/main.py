"""
    Copyright (C) 2020 Nederlandse Organisatie voor Toegepast Natuur-
    wetenschappelijk Onderzoek TNO / TNO, Netherlands Organisation for
    applied scientific research


   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

    @author: Maaike de Boer, Roos Bakker
    @contact: maaike.deboer@tno.nl, roos.bakker@tno.nl
"""

import argparse
import json
import sys
import pandas as pd
import xmltodict

import src.flintfiller.flintfiller as flintfiller
import src.juridecompose.juridecompose as xml_to_dataframe


def read_csv_to_df(csv_file):
    dataframe = pd.read_csv(csv_file)
    return dataframe


def json_to_dict(json_file) -> dict:
    with open(json_file, encoding="utf8") as json_dict:
        my_dict = json.load(json_dict)
        return my_dict


def xml_to_dict(xml_file) -> dict:
    with open(xml_file, encoding="utf8") as xml:
        read = xml.read()
        xml_dict = xmltodict.parse(remove_unicodes(read))
        return xml_dict


def remove_unicodes(read):
    return read.encode('ascii', 'ignore').decode('unicode_escape')


def process_from_commandline():
    args = parse_commandline_arguments()
    arguments_length = (len(sys.argv) - 1) / 2
    print("Main is called with %i arguments" % arguments_length)

    xml_to_dataframe.xml_to_dataframe()
    flintfiller.flintfiller()


def parse_commandline_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-x', '--xml',
                        help="input xml file")
    parser.add_argument('-d', '--dict_file',
                        help="location of file with dictionary of xml")
    parser.add_argument('-df', '--df_file',
                        help="location of file with dataframe of xml")
    parser.add_argument('-pt', '--pt_file',
                        help="location of dataframe with pos tags")
    parser.add_argument('-fo', '--flint_output',
                        help="Output file with Flint frames.")
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    process_from_commandline()
