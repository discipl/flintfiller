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
import copy
import json

import pandas as pd
from typing import Union, List


# Todo: add docstrings


class MetaData:
    def __init__(self, versie: str = '',
                 jci: str = ''):
        self.versie = versie
        self.jci = jci


class DataFrameRegel:
    def __init__(self, brontekst: str,
                 aanduidingen: List[str],
                 meta_data: MetaData = MetaData(),
                 zin: int = ''):
        self.meta_data = meta_data
        self.zin = zin
        self.brontekst = brontekst
        self.nummer = ''
        self.lid = ''
        self.opsomming1 = ''
        self.opsomming2 = ''
        self.opsomming3 = ''
        for i, aanduiding in enumerate(aanduidingen):
            if i == 0:
                self.nummer = aanduiding
            elif i == 1:
                self.lid = aanduiding
            elif i == 2:
                self.opsomming1 = aanduiding
            elif i == 3:
                self.opsomming2 = aanduiding
            else:
                self.opsomming3 = aanduiding

    def to_dict(self):
        return {
            'Nummer': self.nummer,
            'Lid': self.lid,
            'Opsomming niveau 1': self.opsomming1,
            'Opsomming niveau 2': self.opsomming2,
            'Opsomming niveau 3': self.opsomming3,
            'Zin': self.zin,
            'Brontekst': self.brontekst,
            'Versie': self.meta_data.versie,
            'jci 1.3': self.meta_data.jci
        }

    def __repr__(self):
        return f"<{self.__class__}, {self.__dict__}>"


def dict_to_dataframe(my_dict, output_df) -> pd.DataFrame:
    dn = process_wet(my_dict)
    df = to_dataframe(dn)
    df.to_csv(output_df)
    return df


def to_dataframe(regels: List[DataFrameRegel]) -> pd.DataFrame:
    records = pd.DataFrame.from_records([regel.to_dict() for regel in regels])
    print(records.head())
    return records


def process_wet(my_dict: dict) -> List[DataFrameRegel]:
    regels: List[DataFrameRegel] = []

    if "wet-besluit" in my_dict['toestand']['wetgeving'].keys():
        regels.extend(process_wetbesluit(my_dict['toestand']['wetgeving']))
    elif "regeling" in my_dict['toestand']['wetgeving'].keys():
        regels.extend(process_regeling(my_dict['toestand']['wetgeving']['regeling']))
    else:
        raise ValueError(
            'this dictionary has text under unknown keys and cannot properly be parsed to a dataframe. Your '
            'dataframe might have errors or even be empty.')
    return regels


def process_wetbesluit(my_dict) -> List[DataFrameRegel]:
    regels: List[DataFrameRegel] = []
    for hoofdstuk in my_dict['wet-besluit']['wettekst']['hoofdstuk']:
        if 'artikel' in hoofdstuk.keys():
            regels.extend(process_artikel(hoofdstuk['artikel']))
        elif 'afdeling' in hoofdstuk.keys():
            for afdeling in hoofdstuk['afdeling']:
                regels.extend(process_afdeling(afdeling))
        elif 'paragraaf' in hoofdstuk.keys():
            regels.extend(process_paragraaf(hoofdstuk['paragraaf']))
    return regels


def process_regeling(regeling: dict) -> List[DataFrameRegel]:
    regels: List[DataFrameRegel] = []
    for artikel in regeling['regeling-tekst']['artikel']:
        regels.extend(process_artikel(artikel))
    return regels


def process_afdeling(afdeling: dict) -> List[DataFrameRegel]:
    regels: List[DataFrameRegel] = []
    if 'artikel' in afdeling.keys():
        regels.extend(process_artikel(afdeling['artikel']))
    elif 'paragraaf' in afdeling.keys():
        regels.extend(process_paragraaf(afdeling['paragraaf']))
    else:
        raise ValueError('onbekende structuur in afdeling')
    return regels


def process_paragraaf(paragraaf: Union[dict, list]) -> List[DataFrameRegel]:
    regels: List[DataFrameRegel] = []
    if isinstance(paragraaf, dict):
        if 'artikel' in paragraaf.keys():
            regels.extend(process_artikel(paragraaf['artikel']))
    elif isinstance(paragraaf, list):
        for paragraaf_item in paragraaf:
            regels.extend(process_paragraaf(paragraaf_item))
    else:
        raise ValueError(
            'This paragraph is neither a list nor a dictionary and cannot be parsed')
    return regels


def process_artikel(artikel: Union[dict, list]) -> List[DataFrameRegel]:
    regels: List[DataFrameRegel] = []
    if isinstance(artikel, dict):
        if artikel['@bwb-ng-variabel-deel'] == '/Hoofdstuk1/Afdeling1/Artikel1b':
            print('break here')
        meta_data = get_meta_data(artikel['meta-data'])
        regels.extend(generic_process(artikel, meta_data))

    elif isinstance(artikel, list):
        for item in artikel:
            regels.extend(process_artikel(item))
    else:
        raise ValueError('onbekende structuur in artikel')
    return regels


def generic_process(container: dict, meta_data: MetaData) -> List[DataFrameRegel]:
    regels: List[DataFrameRegel] = []
    bwb_nummer = container['@bwb-ng-variabel-deel']
    for key, value in container.items():
        if key == 'lijst':
            regels.extend(process_lijst(value, meta_data))
        elif key == 'al':
            regels.extend(unnest_and_process_al(bwb_nummer, value, meta_data))
        elif key == 'lid':
            for lid in value:
                meta_data_lid = copy.copy(meta_data)
                if 'meta-data' in lid.keys():
                    meta_data_lid.jci = get_jci(lid['meta-data']['jcis']['jci'])
                regels.extend(generic_process(lid, meta_data_lid))
    return regels


def process_lijst(lijst: dict, meta_data: MetaData) -> List[DataFrameRegel]:
    regels: List[DataFrameRegel] = []
    if isinstance(lijst, dict):
        for onderdeel in lijst['li']:
            if isinstance(onderdeel, dict):
                meta_data_onderdeel = copy.copy(meta_data)
                if 'meta-data' in onderdeel.keys():
                    meta_data_onderdeel.jci = get_jci(onderdeel['meta-data']['jcis']['jci'])
                regels.extend(generic_process(onderdeel, meta_data_onderdeel))
            else:
                raise ValueError('onbekende structuur in li')
    else:
        raise ValueError('onbekende structuur in lijst')
    return regels


def unnest_and_process_al(bwb_nummer: str, al: Union[str, dict], meta_data: MetaData) -> List[DataFrameRegel]:
    if isinstance(al, list):
        return [process_al(bwb_nummer=bwb_nummer, al=nested_al, meta_data=meta_data) for nested_al in al]
    else:
        return [process_al(bwb_nummer=bwb_nummer, al=al, meta_data=meta_data)]


def process_al(bwb_nummer: str, al: Union[str, dict], meta_data: MetaData) -> DataFrameRegel:
    if isinstance(al, dict):
        if '#text' in al.keys():
            text_al = al['#text']
            if 'intref' in al.keys() or 'extref' in al.keys() or 'nadruk' in al.keys():
                intref_text = get_ref(al.get('intref', {'#text': ""}))
                extref_text = get_ref(al.get('extref', {'#text': ""}))
                nadruk = get_ref(al.get('nadruk', {'#text': ""}))
                return DataFrameRegel(brontekst=text_al + str(intref_text) + str(extref_text) + str(nadruk),
                                      aanduidingen=get_aanduidingen(bwb_nummer), meta_data=meta_data)

            else:
                raise ValueError('onbekende structuur in al artikel')
        if 'redactie' in al.keys():
            return DataFrameRegel(brontekst=al['redactie']['#text'], aanduidingen=get_aanduidingen(bwb_nummer),
                                  meta_data=meta_data)
        else:
            raise ValueError('onbekende structuur in al artikel')
    elif isinstance(al, str):
        return DataFrameRegel(brontekst=al, aanduidingen=get_aanduidingen(bwb_nummer), meta_data=meta_data)
    else:
        raise ValueError('onbekende structuur in al')


def get_ref(ref: Union[list, dict]) -> str:
    if isinstance(ref, dict):
        ref_text = ref['#text']
        return ref_text
    else:
        for ref_item in ref:
            return get_ref(ref_item)


def get_aanduidingen(bwb_nummer: str) -> List[str]:
    split = bwb_nummer.split("/")
    split.remove("")
    return split


def get_meta_data(meta_data: dict) -> MetaData:
    versie = ""
    jci = ""
    if "brondata" in meta_data.keys():
        versie = get_versie(meta_data["brondata"])
    if "jcis" in meta_data.keys():
        jci = get_jci(meta_data["jcis"]['jci'])
    return MetaData(versie=versie, jci=jci)


def get_versie(brondata: Union[dict, list]) -> str:
    if isinstance(brondata, list):
        return get_versie(brondata[-1])
    elif isinstance(brondata, dict):
        if 'inwerkingtreding' in brondata.keys():
            versie = brondata['inwerkingtreding']['inwerkingtreding.datum']['#text']
            return versie
        else:
            return 'versie missing'


def get_jci(jci: Union[list, dict]) -> str:
    if isinstance(jci, list):
        return get_jci(jci[-1])
    elif isinstance(jci, dict):
        return jci['@verwijzing']
