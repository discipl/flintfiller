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

import pandas as pd
import json
from typing import TypeVar, Union

PandasDataFrame = TypeVar('pandas.core.frame.Dataframe')


def dict_to_dataframe(json_dict_file, output_df) -> PandasDataFrame:
    with open(json_dict_file, encoding="utf8") as json_dict:
        my_dict = json.load(json_dict)
        print('Writing dataframe to csv file')
        dn = get_content_wet(my_dict)
        dn.to_csv(output_df)
        return dn


def get_content_wet(my_dict: dict) -> PandasDataFrame:
    wettexten = []
    artikel_nummers = []
    jcis = []
    versiedata = []
    if "wet-besluit" in my_dict['toestand']['wetgeving'].keys():
        get_content_wetbesluit(artikel_nummers, jcis, my_dict, versiedata, wettexten)
    elif "regeling" in my_dict['toestand']['wetgeving'].keys():
        get_content_regeling(artikel_nummers, jcis, my_dict, versiedata, wettexten)
    else:
        print(
            'this dictionary has text under unknown keys and cannot properly be parsed to a dataframe. Your '
            'dataframe might have errors or even be empty.')
    df0 = pd.DataFrame(artikel_nummers, columns=['artikelnr:'])
    df1 = pd.DataFrame(wettexten, columns=['text:'])
    df2 = pd.DataFrame(jcis, columns=['jci1.0:', 'jci1.3:'])
    df3 = pd.DataFrame(versiedata, columns=['versie:'])
    wet_df = pd.concat([df0, df1, df2, df3], axis=1, sort=False)
    # wet_df.set_index('artikelnr:', inplace=True)
    return wet_df


def get_content_regeling(artikel_nummers, jcis, my_dict, versiedata, wettexten):
    if 'artikel' in my_dict['toestand']['wetgeving']['regeling']['regeling-tekst'].keys():
        for artikel in my_dict['toestand']['wetgeving']['regeling']['regeling-tekst']['artikel']:
            get_content_artikel(artikel, wettexten, artikel_nummers, jcis, versiedata)
    elif 'hoofdstuk' in my_dict['toestand']['wetgeving']['regeling']['regeling-tekst'].keys():
        get_content_hoofdstuk(artikel_nummers, jcis, my_dict, versiedata, wettexten)


def get_content_hoofdstuk(artikel_nummers, jcis, my_dict, versiedata, wettexten):
    for hoofdstuk in my_dict['toestand']['wetgeving']['regeling']['regeling-tekst']['hoofdstuk']:
        if 'artikel' in hoofdstuk.keys():
            get_content_artikel(hoofdstuk['artikel'], wettexten, artikel_nummers, jcis, versiedata)
        elif 'afdeling' in hoofdstuk.keys():
            get_content_afdeling(hoofdstuk, wettexten, artikel_nummers, jcis, versiedata)
        elif 'paragraaf' in hoofdstuk.keys():
            get_content_paragraaf(hoofdstuk['paragraaf'], wettexten, artikel_nummers, jcis, versiedata)


def get_content_wetbesluit(artikel_nummers, jcis, my_dict, versiedata, wettexten):
    for hoofdstuk in my_dict['toestand']['wetgeving']['wet-besluit']['wettekst']['hoofdstuk']:
        if 'artikel' in hoofdstuk.keys():
            get_content_artikel(hoofdstuk['artikel'], wettexten, artikel_nummers, jcis, versiedata)
        elif 'afdeling' in hoofdstuk.keys():
            get_content_afdeling(hoofdstuk, wettexten, artikel_nummers, jcis, versiedata)
        elif 'paragraaf' in hoofdstuk.keys():
            get_content_paragraaf(hoofdstuk['paragraaf'], wettexten, artikel_nummers, jcis, versiedata)


def get_content_paragraaf(paragraaf: Union[dict, list], wettexten: list, artikel_nummers: list, jcis: list, versiedata: list):
    if isinstance(paragraaf, dict):
        if 'artikel' in paragraaf.keys():
            get_content_artikel(paragraaf['artikel'], wettexten, artikel_nummers, jcis, versiedata)
    elif isinstance(paragraaf, list):
        for paragraaf_item in paragraaf:
            get_content_paragraaf(paragraaf_item, wettexten, artikel_nummers, jcis, versiedata)
    else:
        print('This paragraph is neither a list nor a dictionary and cannot be parsed')


def get_content_afdeling(hoofdstuk: dict, wettexten: list, artikel_nummers: list, jcis: list, versiedata: list):
    for afdeling in hoofdstuk['afdeling']:
        if 'artikel' in afdeling.keys():
            get_content_artikel(afdeling['artikel'], wettexten, artikel_nummers, jcis, versiedata)
        elif 'paragraaf' in afdeling.keys():
            get_content_paragraaf(afdeling['paragraaf'], wettexten, artikel_nummers, jcis, versiedata)


def get_content_artikel(artikel: Union[dict, list], wettexten: list, artikel_nummers: list, jcis: list, versiedata: list):
    if isinstance(artikel, dict):
        artikel_nummers.append(artikel['@bwb-ng-variabel-deel'])
        unlayered_data = {}
        texts_artikel = []
        get_jci(artikel['meta-data'], jcis)
        get_versie_datum(artikel['meta-data'], versiedata)

        for key_artikel, value_artikel in artikel.items():
            if key_artikel == 'lijst':
                get_content_lijst(value_artikel, texts_artikel)
            elif key_artikel == 'al' and isinstance(value_artikel, dict):
                if '#text' in value_artikel.keys():
                    text_al = value_artikel['#text']
                    if 'intref' in value_artikel.keys():
                        intref_text = get_content_ref(value_artikel['intref'])
                        if isinstance(intref_text, str):
                            texts_artikel.append(text_al + intref_text)
                    elif 'extref' in value_artikel.keys():
                        extref_text = get_content_ref(value_artikel['extref'])
                        if isinstance(extref_text, str):
                            texts_artikel.append(text_al + extref_text)
                    else:
                        print('onbekende structuur in al artikel')
            elif key_artikel == 'al' and isinstance(value_artikel, str):
                texts_artikel.append(artikel['al'])
            elif key_artikel == 'lid':
                get_content_lid(value_artikel, texts_artikel)
            else:
                unlayered_data[key_artikel] = value_artikel

        texts_artikel = [' '.join(texts_artikel)]
        wettexten.append(texts_artikel)

    if isinstance(artikel, list):
        for artikel_item in artikel:
            get_content_artikel(artikel_item, wettexten, artikel_nummers, jcis, versiedata)


def get_content_lijst(lijst, text_list: list) -> list:
    if isinstance(lijst, dict):
        for onderdeel in lijst['li']:
            bwb_nummer = onderdeel['@bwb-ng-variabel-deel']
            text_list.append(' $ ' + get_onderdeel(bwb_nummer) + " : " + ' $ ')
            if isinstance(onderdeel, dict):
                if 'al' in onderdeel.keys() and isinstance(onderdeel['al'], str):
                    text_list.append(onderdeel['al'])
                elif 'al' in onderdeel.keys() and isinstance(onderdeel['al'], dict):
                    content_al = onderdeel['al']
                    if 'nadruk' in content_al.keys():
                        text_nadruk = content_al['nadruk']['#text']
                        text_list.append(text_nadruk)
                    if '#text' in content_al.keys():
                        text_al = content_al['#text']
                        if 'intref' in content_al.keys():
                            intref_text = get_content_ref(content_al['intref'])
                            if isinstance(intref_text, str):
                                text_list.append(text_al + intref_text)
                        if 'extref' in content_al.keys():
                            extref_text = get_content_ref(content_al['extref'])
                            if isinstance(extref_text, str):
                                text_list.append(text_al + extref_text)
                        else:
                            text_list.append(text_al)

                if 'lijst' in onderdeel.keys() and isinstance(onderdeel['lijst'], dict):
                    get_content_lijst(onderdeel['lijst'], text_list)
            else:
                print('onbekende structuur in lijst')
    else:
        for subonderdeel in lijst:
            get_content_lijst(subonderdeel, text_list)
    return text_list


def get_content_lid(leden, text_list: list) -> list:
    for lid in leden:
        bwb_nummer = lid['@bwb-ng-variabel-deel']
        text_list.append(' $ ' + get_onderdeel(bwb_nummer) + " : " + ' $ ')

        if 'al' in lid.keys() and isinstance(lid['al'], str):
            text_list.append(lid['al'])

        elif 'al' in lid.keys() and isinstance(lid['al'], dict):
            content_al = lid['al']
            if 'redactie' in content_al.keys():
                return text_list
            else:
                text_al = content_al['#text']
                if 'intref' in content_al.keys():
                    intref_text = get_content_ref(content_al['intref'])
                    if isinstance(intref_text, str):
                        text_list.append(text_al + intref_text)
                if 'extref' in content_al.keys():
                    extref_text = get_content_ref(content_al['extref'])
                    if isinstance(extref_text, str):
                        text_list.append(text_al + extref_text)
                else:
                    text_list.append(text_al)

        if 'lijst' in lid.keys():
            get_content_lijst(lid['lijst'], text_list)
    return text_list


def get_content_ref(ref):
    if isinstance(ref, dict):
        ref_text = ref['#text']
        return ref_text
    else:
        for ref_item in ref:
            return get_content_ref(ref_item)


def get_jci(metadata, jcis: list):
    jci_list = []
    for jci in metadata['jcis']['jci']:
        jci_list.append(jci['@verwijzing'])
    jcis.append(jci_list)


def get_versie_datum(metadata, versiedata):
    versiedatums_list = []
    if isinstance(metadata['brondata'], dict):
        if 'inwerkingtreding' in metadata['brondata'].keys():
            versiedata.append(metadata['brondata']['inwerkingtreding']['inwerkingtreding.datum']['#text'])
        else:
            versiedata.append(metadata['brondata']['oorspronkelijk']['publicatie']['uitgiftedatum']['#text'])
    elif isinstance(metadata['brondata'], list):
        for data in metadata['brondata']:
            if 'inwerkingtreding' in data.keys():
                versiedatums_list.append(data['inwerkingtreding']['inwerkingtreding.datum']['#text'])
            else:
                versiedatums_list.append(data['oorspronkelijk']['publicatie']['uitgiftedatum']['#text'])
        if versiedatums_list[0] == versiedatums_list[1]:
            del versiedatums_list[0]
        versiedata.append(versiedatums_list)


def get_onderdeel(bwb_deel):
    return bwb_deel.rsplit('/', 1)[-1]
