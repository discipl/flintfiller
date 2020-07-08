from typing import List

import pytest

from flintfiller.dict_to_dataframe import process_artikel, DataFrameRegel, process_al, \
    get_meta_data, get_versie, MetaData


def test_get_content_artikel_dict_al():
    result: List[DataFrameRegel] = process_artikel(
        {"@bwb-ng-variabel-deel": "/Hoofdstuk1/Artikel1",
         "al": "In dit besluit en de daarop berustende bepalingen wordt verstaan onder:",
         "meta-data": {"brondata": {"inwerkingtreding": {"inwerkingtreding.datum": {"#text": "16-04-2020"}}}}
         })

    assert len(result) == 1
    assert result[0].brontekst == "In dit besluit en de daarop berustende bepalingen wordt verstaan onder:"
    assert result[0].nummer == "Hoofdstuk1"
    assert result[0].lid == "Artikel1"
    assert result[0].meta_data.versie == "16-04-2020"


def test_get_content_artikel_unexpected_structure():
    with pytest.raises(ValueError) as e:
        process_artikel('unexpected value')

    assert "onbekende structuur in artikel" in str(e)


def test_get_content_artikel_list():
    result: List[DataFrameRegel] = process_artikel(
        [
            {"@bwb-ng-variabel-deel": "/Hoofdstuk1/Artikel1",
             "al": "In dit besluit en de daarop berustende bepalingen wordt verstaan onder:",
             "meta-data": {"brondata": {"inwerkingtreding": {"inwerkingtreding.datum": {"#text": "16-04-2020"}}}}
             },
            {"@bwb-ng-variabel-deel": "/Hoofdstuk1/Artikel2",
             "al": "In dit besluit en de daarop berustende bepalingen wordt verstaan onder: artikel 2",
             "meta-data": {"brondata": {"inwerkingtreding": {"inwerkingtreding.datum": {"#text": "17-04-2020"}}}}
             }
        ]
    )

    assert len(result) == 2
    assert result[0].brontekst == "In dit besluit en de daarop berustende bepalingen wordt verstaan onder:"
    assert result[0].nummer == "Hoofdstuk1"
    assert result[0].lid == "Artikel1"
    assert result[0].meta_data.versie == "16-04-2020"

    assert result[1].brontekst == "In dit besluit en de daarop berustende bepalingen wordt verstaan onder: artikel 2"
    assert result[1].nummer == "Hoofdstuk1"
    assert result[1].lid == "Artikel2"
    assert result[1].meta_data.versie == "17-04-2020"


def test_get_content_artikel_dict_lijst():
    result: List[DataFrameRegel] = process_artikel(
        {"@bwb-ng-variabel-deel": "/Hoofdstuk1/Artikel1",
         "meta-data": {"brondata": {"inwerkingtreding": {"inwerkingtreding.datum": {"#text": "17-04-2020"}}}},
         "lijst": {"li": [{"@bwb-ng-variabel-deel": "/Artikel1/Onderdeel_1",
                           "al": "wettekst"}]}
         }
    )

    assert len(result) == 1
    assert result[0].brontekst == "wettekst"
    assert result[0].nummer == "Artikel1"
    assert result[0].lid == "Onderdeel_1"
    assert result[0].meta_data.versie == "17-04-2020"


def test_get_content_al():
    result: DataFrameRegel = process_al(
        "/Artikel1/Onderdeel_1",
        {"nadruk": {"#text": " nadruktekst"},
         "intref": {"#text": " intreftekst"},
         "extref": {"#text": " extreftekst"},
         "#text": "text"},
        MetaData("17-04-2020", "1.3blabla"))

    assert result.brontekst == "text intreftekst extreftekst nadruktekst"
    assert result.nummer == "Artikel1"
    assert result.lid == "Onderdeel_1"
    assert result.meta_data.versie == "17-04-2020"
    assert result.meta_data.jci == "1.3blabla"


def test_get_versie():
    result: str = get_versie(
        {
            "inwerkingtreding": {
                "inwerkingtreding.datum": {
                    "@isodatum": "2020-04-22",
                    "#text": "22-04-2020"
                }
            },
        }
    )

    assert result == "22-04-2020"


def test_get_versie_list():
    result: str = get_versie(
        [
            {
                "inwerkingtreding": {
                    "inwerkingtreding.datum": {
                        "@isodatum": "2013-06-01",
                        "#text": "01-06-2013"
                    }
                }
            },
            {
                "inwerkingtreding": {
                    "inwerkingtreding.datum": {
                        "@isodatum": "2013-06-01",
                        "#text": "01-06-2013"
                    }
                }
            }
        ]
    )
    assert result == "01-06-2013"
