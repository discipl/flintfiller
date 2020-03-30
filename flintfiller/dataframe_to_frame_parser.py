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

# This script transforms POStagged text to a FLINT frame.
import json
from typing import Tuple

import pandas as pd
import ast

action_verbs = ['aanbrengen', 'aanwijzen', 'achterwege blijven', 'afnemen', 'afwijken', 'afwijzen',
                'ambtshalve verlenen', 'ambtshalve verlengen', 'annuleren', 'behandelen', 'beheren', 'bepalen',
                'beperken', 'betreden', 'beveiligen', 'bevelen', 'bevorderen', 'bieden gelegenheid', 'bijhouden',
                'buiten behandeling stellen', 'buiten werking stellen', 'doorzoeken', 'erop wijzen',
                'gebruiken maken van', 'gedwongen ontruimen', 'geven', 'heffen', 'in bewaring stellen',
                'in de gelegenheid stellen zich te doen horen', 'in kennis stellen', 'in werking doen treden',
                'in werking stellen', 'indienen', 'innemen', 'instellen', 'intrekken', 'invorderen', 'inwilligen',
                'maken', 'naar voren brengen', 'nemen', 'niet in behandeling nemen', 'niet-ontvankelijk verklaren',
                'nogmaals verlengen', 'om niet vervoeren', 'onderwerpen', 'onderzoeken', 'ongewenstverklaren',
                'onmiddellijk bepalen', 'onmiddellijk verlaten', 'ontnemen', 'ontvangen', 'opheffen', 'opleggen',
                'oproepen', 'overbrengen', 'overdragen', 'plaatsen', 'schorsen', 'schriftelijk in kennis stellen',
                'schriftelijk laten weten', 'schriftelijk mededelen', 'schriftelijk naar voren brengen', 'signaleren',
                'sluiten', 'staande houden', 'stellen', 'straffen', 'ter hand stellen', 'teruggeven',
                'tijdelijk in bewaring nemen', 'toetsen', 'toezenden', 'uitstellen', 'uitvaardigen', 'uitzetten',
                'van rechtswege verkrijgen', 'vaststellen', 'vergelijken', 'verhalen', 'verhogen', 'verklaren',
                'verkorten', 'verkrijgen', 'verlaten', 'verlenen', 'verlengen', 'verplichten', 'verschaffen',
                'verstrekken', 'verzoeken', 'voegen', 'vorderen', 'vragen', 'willigen', 'weigeren', 'wijzigen']
set_propernouns = ["PRP", "PRP$", "NNP", "NNPS"]
global facts_list


def read_csv_to_df(csv_file):
    datafrm = pd.read_csv(csv_file)
    print("csv loaded from " + csv_file)
    return datafrm


def write_df_to_csv(df, fle):
    df.to_csv(fle)
    print("df written to " + fle)


def get_empty_flint_frame_format() -> dict:
    flint_frame = {
        "acts": [],
        "facts": [],
        "duties": []
    }
    return flint_frame


def get_empty_act_frame() -> dict:
    act_frame = {
        "act": "",
        "actor": "",
        "action": "",
        "object": "",
        "recipient": "",
        "preconditions": {
            "expression": "",
            "operands": []
        },
        "create": [],
        "terminate": [],
        "sources": [],  # with validFrom, validTo, citation juriconnect and text
        "explanation": ""
    }
    return act_frame


def get_empty_fact_frame() -> dict:
    fact_frame = {
        "fact": "",
        "function": [],
        "sources": [],  # with validFrom, validTo, citation juriconnect and text
        "explanation": ""
    }
    return fact_frame


def get_source_dict(row, text) -> dict:
    source_dict = {"validFrom": row["versie:"], "validTo": ""}
    try:
        source_dict["citation"] = "art. " + row['jci1.3:'].split("artikel=")[1].split('&')[0] + "lid " + \
                                  row['jci1.3:'].split("lid=")[1].split('&')[0] + ", Vw"
    except:
        # if split("lid=")[1] is not filled in, do not add this part
        source_dict["citation"] = "art. " + row['jci1.3:'].split("artikel=")[1].split('&')[0] + ", Vw"
    source_dict['text'] = text.replace('\n', '').replace('\r', '').replace("\t", " ")
    source_dict['juriconnect'] = row['jci1.3:']
    return source_dict


def create_fact_or_act_function(list_text: list) -> dict:
    fact_function = {"expression": "AND"}
    fact_function_operands = []
    for fct in list_text:
        try:
            fact_function_operands.append(
                "[" + fct.replace('\n', '').replace('\r', '').split(";")[0].replace("\t", "")[1:] + "]")  # .
        except:
            # if the fact is empty or has length of 0, [1:] does not work
            'do nothing'
    # get rid of the empty list at the beginning
    if len(fact_function_operands) > 1:
        fact_function_operands.pop(0)
    else:
        fact_function = {}

    fact_function["operands"] = fact_function_operands
    return fact_function


def get_object_and_actor(orig, tags) -> Tuple[str, str]:
    vp_found = False
    obj = ""
    actor_num = -1

    # check the index of the verb
    for i in range(0, len(tags)):
        try:
            # find the VP
            if tags[i][0] == "VP" and (tags[i][len(tags[i][0])][0] == orig):
                vp_found = True

            for num in range(1, len(tags[i])):
                # get the first NP; this is the object
                # TODO: version 2: create better code using dependencies to determine the object and actor
                if not vp_found:
                    # bug fix: no lower, because the link to the actor is gone then
                    obj += " " + (str(tags[i][num][0]))
                # only add NPs if they are in the same sentence as the VP of the act
                if "$" in str(tags[i][num][0]) and not vp_found:
                    obj = ""

                # try to find the actor and recipient
                # Hack: make a list of characters and check whether the first is uppercased (capitalized)
                if tags[i][num][1] in set_propernouns and list(tags[i][num][0])[0].isupper() and actor_num < 0:
                    actor_num = i
        except:
            # if tags[i][len(tags[i][0])][0] or tags[i][0] does not exist, we have an error
            'do nothing'

    # the actor is the NP of the actor_num (number in the tags)
    actor = ""
    # fixed bug: bigger than -1 if the word occurs as the first word
    if actor_num > -1:
        # range starts with 1, because 0 is the type NP
        for nr in range(1, len(tags[actor_num])):
            actor += " " + tags[actor_num][nr][0]

    # hacks to get a better object
    if len(actor) > 1 and actor in obj:
        obj = obj.replace(actor, "")

    if "kan" in obj:
        obj = obj.replace("kan", "")
    return actor, obj


def check_infinitive(inf, row) -> bool:
    return inf in action_verbs and not \
        ("het " + inf) in row['text:'] or \
           ("de " + inf) in row['text:'] or \
           ("een " + inf) in row['text:']


# This is a first version!
def get_acts(row, verbs, tags, flint_frames) -> dict:
    # for each verb (if one verb this also works)
    for infinitive, original in verbs.items():
        # if the verb is in the first part (before the :) (could be more verbs)
        parts = row['text:'].split(":")
        # addition to wrong parsing: acts are not those that have a determiner before it; Dutch determiners are 'de',
        # 'het' and 'een'
        if check_infinitive(infinitive, row):
            act_frame = get_empty_act_frame()
            act_frame['action'] = "[" + infinitive + "]"

            # if we know that there should be preconditions, add them
            if ":" in row['text:'] and original in parts[0]:
                act_function = create_fact_or_act_function(''.join(parts[1:]).split("$$"))
                act_frame['preconditions'] = act_function
                # TODO in version 2: make a fact of the pre-condition
                # get_empty_fact_frame()

            actor, obj = get_object_and_actor(original, tags)

            # hack: first character is a space; use from second on
            act_frame['actor'] = "[" + actor[1:] + "]"
            act_frame['act'] = "<<" + infinitive + obj.lower() + ">>"
            act_frame['object'] = "[" + obj[1:].lower() + "]"

            # TODO in version 2: make code better; now only vreemdeling as recipient
            if "vreemdeling" in row['text:']:
                act_frame['recipient'] = "[vreemdeling]"

            source_dict_act = get_source_dict(row, row['text:'])
            act_frame['sources'].append(source_dict_act)

            flint_frames['acts'].append(act_frame)
    return flint_frames


def get_facts(row, part) -> dict:
    global facts_list
    fact_frame = get_empty_fact_frame()
    source_dict = get_source_dict(row, part)
    fact_frame['sources'].append(source_dict)
    # The facts has to be in between brackets
    fact_frame['fact'] = "[" + part.split(":")[0][1:] + "]"
    facts_list.append(part.split(":")[0][1:])

    # create the function. In case of Artikel 1 this is the (one) definition that is after the :
    list_defs = [part.split(":")[1]]
    fact_function = create_fact_or_act_function(list_defs)
    fact_frame['function'] = fact_function
    return fact_frame


def create_flint_frames(df) -> dict:
    flint_frames = get_empty_flint_frame_format()
    global facts_list
    facts_list = []
    # loop through the rows and create acts and facts as we go
    for index, row in df.iterrows():
        # we start with Facts that are present in the First Article
        # try:
        if str(row['artikelnr:']) == '/Hoofdstuk1/Afdeling1/Artikel1' and type(row['text:']) != float:
            for part in row['text:'].split("$$"):
                if ":" in part:
                    if part.split(":")[0][1:] not in facts_list:
                        # Facts
                        fact_frame = get_facts(row, part)
                        flint_frames['facts'].append(fact_frame)

        # Acts: only if we have verbs
        if not "[]" == row['verbs']:
            # hack: make it a dict / list again is we load in a dataframe from another format
            verbs = ast.literal_eval(row['verbs'])
            tags = ast.literal_eval(row['tags'])
            # because more than one act_frame could be created, go on the level of the flint_frames
            flint_frames = get_acts(row, verbs, tags, flint_frames)
        else:
            'no acts'
    return flint_frames


def write_flint_frames_to_json(flint_frames, flint_file):
    with open(str(flint_file), 'w') as f:
        json.dump(flint_frames, f)
    print("flint frames written to " + str(flint_file))


def dataframe_to_frame_parser(csv_file, output_file):
    pos_tagged_df = read_csv_to_df(str(csv_file))
    flint_frames = create_flint_frames(pos_tagged_df)
    write_flint_frames_to_json(flint_frames, output_file)

# if __name__ == '__main__':
#     # df = read_csv_to_df(str(csv_file))
#     flint_frames = create_flint_frames(df)
#     write_flint_frames_to_json(flint_frames)
