__author__ = 'roos bakker'

import tempfile

from juridecompose.dict_to_dataframe import dict_to_dataframe
from main import json_to_dict


def test_dict_to_dataframe_regeling_regression():
    my_dict = json_to_dict("test_data/BWBR0043324_2020-04-22_0_TOGS.json")
    with tempfile.NamedTemporaryFile() as result:
        expected_path = "test_data/expected_regression_regeling.csv"
        result_path = result.name + ".csv"
        dict_to_dataframe(my_dict, result_path)
        assert [row for row in open(result_path)] == [row for row in open(expected_path)]


def update_expected_regression_regeling():
    my_dict = json_to_dict("test_data/BWBR0043324_2020-04-22_0_TOGS.json")
    expected_path = "test_data/expected_regression_regeling.csv"
    dict_to_dataframe(my_dict, expected_path)


def test_dict_to_dataframe_wetbesluit_regression():
    my_dict = json_to_dict("test_data/BWBR0011823_2019-02-27_Vreemdelingenwet.json")
    with tempfile.NamedTemporaryFile() as result:
        expected_path = "test_data/expected_regression_wetbesluit.csv"
        result_path = result.name + ".csv"
        dict_to_dataframe(my_dict, result_path)
        assert [row for row in open(result_path)] == [row for row in open(expected_path)]


def update_expected_regression_wetbesluit():
    my_dict = json_to_dict("test_data/BWBR0011823_2019-02-27_Vreemdelingenwet.json")
    expected_path = "test_data/expected_regression_wetbesluit.csv"
    dict_to_dataframe(my_dict, expected_path)


def test_dict_to_dataframe_lerarenbeurs_regression():
    my_dict = json_to_dict("test_data/BWBR0039319_2020-06-24_0_lerarenbeurs.json")
    with tempfile.NamedTemporaryFile() as result:
        expected_path = "test_data/expected_regression_lerarenbeurs.csv"
        result_path = result.name + ".csv"
        dict_to_dataframe(my_dict, result_path)
        assert [row for row in open(result_path)] == [row for row in open(expected_path)]
