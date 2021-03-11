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

import flintfiller.chunk_tag_dataframe as chunk_tag_dataframe
import flintfiller.dataframe_to_frame_parser as dataframe_to_frame_parser


def read_csv_to_df(csv_file):
    dataframe = pd.read_csv(csv_file)
    return dataframe


def flintfiller():
    args = parse_commandline_arguments()

    if args.df_file and args.pt_file:
        input_df_file = args.df_file
        input_df = read_csv_to_df(input_df_file)
        output_pt = args.pt_file
        chunk_tag_dataframe.parser('pattern', input_df, output_pt)
        if args.flint_output:
            input_pt_df = args.pt_file
            output_flint = args.flint_output
            dataframe_to_frame_parser.dataframe_to_frame_parser(input_pt_df, output_flint)
            print(f'finished with creating FLINT frames from dataframe, check file: ' + output_flint)
        else:
            print(f'finished with parsing xml to POS tagged dataframe, check file: ' + output_pt)

    elif args.flint_output and args.pt_file and not args.df_file:
        input_pt_df = args.pt_file
        output_flint = args.flint_output
        dataframe_to_frame_parser.dataframe_to_frame_parser(input_pt_df, output_flint)
        print(f'finished with creating FLINT frames from dataframe, check file: ' + output_flint)

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
    flintfiller()
