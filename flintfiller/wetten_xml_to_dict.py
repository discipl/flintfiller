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
        read = xml.read()
        xml_dict = xmltodict.parse(remove_unicodes(read))
    with open(output_file, 'w') as file:
        print('Writing dictionary to json file')
        file.write(json.dumps(xml_dict))
    return xml_dict


def remove_unicodes(read):
    return read.encode('ascii', 'ignore').decode('unicode_escape')
