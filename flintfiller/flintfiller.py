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
import pandas as pd

import chunk_tag_dataframe
import dataframe_to_frame_parser
import dict_to_dataframe
import wetten_xml_to_dict


def read_csv_to_df(csv_file):
    dataframe = pd.read_csv(csv_file)
    return dataframe


def process_from_commandline():
    args = parse_commandline_arguments()
    arguments_length = (len(sys.argv) - 1) / 2
    print("flintfiller is called with %i arguments" % arguments_length)

    if args.xml and args.dict_file:
        xml_file = args.xml
        output_dict = args.dict_file
        wetten_xml_to_dict.parse_xml_artikelen(xml_file, output_dict)
        if args.df_file:
            output_df = args.df_file
            xml_df = dict_to_dataframe.dict_to_dataframe(output_dict, output_df)
            if args.pt_file:
                output_pt = args.pt_file
                pos_dataframe = chunk_tag_dataframe.parser('pattern', xml_df, output_pt)
                if args.flint_output:
                    output_flint = args.flint_output
                    flint_frames = dataframe_to_frame_parser.dataframe_to_frame_parser(output_pt, output_flint)
                    print(f'finished with creating FLINT frames from xml, check file:' + output_flint)
                else:
                    print(f'finished with parsing xml to POS tagged dataframe, check file: ' + output_pt)
            else:
                print(
                    f'finished with parsing xml to dictionary and to dataframe, check file: ' + output_dict + output_df)
        else:
            print(f'finished with parsing xml to dictionary, check file: ' + output_dict)

    elif args.flint_output and args.pt_file and not args.df_file:
        input_pt_df = args.pt_file
        output_flint = args.flint_output
        dataframe_to_frame_parser.dataframe_to_frame_parser(input_pt_df, output_flint)
        print(f'finished with creating FLINT frames from dataframe, check file: ' + output_flint)

    elif args.df_file and args.pt_file and not (args.flint_output or args.dict_file):
        input_df_file = args.df_file
        input_df = read_csv_to_df(input_df_file)
        output_postagged_df = args.pt_file
        chunk_tag_dataframe.parser('pattern', input_df, output_postagged_df)
        print(f'finished with parsing dataframe to POS tagged dataframe, check file: ' + output_postagged_df)

    elif args.dict_file and args.df_file and not (args.xml or args.pt_file):
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
    process_from_commandline()
