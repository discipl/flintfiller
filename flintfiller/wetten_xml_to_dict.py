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

import json
import xmltodict


def parse_xml_artikelen(xml_file, output_file):
    with open(xml_file, encoding="utf8") as xml:
        xml_dict = xmltodict.parse(xml.read())
        # If you want just the text out of the xml, uncomment the following part and
        # replace xml_dict below with artikelen
        #
        # artikelen = {}
        # if "wet-besluit" in xml_dict['toestand']['wetgeving'].keys():
        #     for hoofdstuk in xml_dict['toestand']['wetgeving']['wet-besluit']['wettekst']['hoofdstuk']:
        #         if 'artikel' in hoofdstuk.keys():
        #             get_text_artikelen(hoofdstuk, artikelen)
        #         if 'afdeling' in hoofdstuk.keys():
        #             for afdeling in hoofdstuk['afdeling']:
        #                 if 'artikel' in afdeling.keys():
        #                     get_text_artikelen(afdeling, artikelen)
        # elif "regeling" in xml_dict['toestand']['wetgeving'].keys():
        #     print('this XML is differently build and the text cannot be extracted by itself')
        # else:
        #     print('this XML is differently build and the text cannot be extracted by itself')
    with open(output_file, 'w') as file:
        print('Writing dictionary to json file')
        file.write(json.dumps(xml_dict))


def get_text_artikelen(afdeling, artikelen):
    for artikel in afdeling['artikel']:
        if isinstance(artikel, dict):
            if 'lijst' in artikel.keys():
                for regel in artikel['lijst']['li']:
                    if isinstance(regel['al'], str):
                        artikelen[regel['@bwb-ng-variabel-deel']] = regel['al']
                    else:
                        artikelen[regel['@bwb-ng-variabel-deel']] = regel['al']['#text']
            if 'al' in artikel.keys() and isinstance(artikel['al'], str):
                artikelen[artikel['@bwb-ng-variabel-deel']] = artikel['al']
