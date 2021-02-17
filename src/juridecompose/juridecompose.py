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
import sys

import src.juridecompose.dict_to_dataframe as dict_to_dataframe
import src.juridecompose.wetten_xml_to_dict as wetten_xml_to_dict


def xml_to_dataframe():
    args = parse_commandline_arguments()

    if args.xml and args.dict_file:
        xml_file = args.xml
        output_dict = args.dict_file
        wetten_dict = wetten_xml_to_dict.parse_xml_artikelen(xml_file, output_dict)
        if args.df_file:
            output_df = args.df_file
            xml_df = dict_to_dataframe.dict_to_dataframe(wetten_dict, output_df)
        else:
            print(f'finished with parsing xml to dictionary, check file: ' + output_dict)

    elif args.dict_file and args.df_file and not args.xml:
        input_dict_file = args.dict_file
        output_df_file = args.df_file
        dict_to_dataframe.dict_to_dataframe(input_dict_file, output_df_file)
        print(f'finished with creating dataframe from dictionary, check file: ' + output_df_file)

    else:
        print('you did not pass the right combination of arguments, parsing not possible.')


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
    xml_to_dataframe()
