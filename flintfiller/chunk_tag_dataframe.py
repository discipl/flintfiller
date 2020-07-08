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

# This script transforms xml text to a FLINT frame.

import pandas as pd

from nltk.corpus import alpino as alp
from nltk.tag import UnigramTagger, BigramTagger

from pattern.text.nl import parse, split, conjugate, INFINITIVE


def train_dutch_tagger():
    training_corpus = alp.tagged_sents()
    unitagger = UnigramTagger(training_corpus)
    bitagger = BigramTagger(training_corpus, backoff=unitagger)
    pos_tag = bitagger.tag
    return pos_tag


def read_csv_to_df(csv_file):
    datafrm = pd.read_csv(csv_file)
    print("csv loaded from " + csv_file)
    return datafrm


def write_df_to_csv(df, fle):
    df.to_csv(fle)
    print("dataframe with POS tags written to " + fle)


def parse_text_alpino(text_per_sentence, pos_tag):
    parsed_text = []
    for sentence in text_per_sentence:
        pos_tagged_text = pos_tag(sentence.split())
        parsed_text.append(pos_tagged_text)
    return parsed_text


def parse_text_pattern(text_column: pd.Series):
    parsed_text = []
    parsed_verbs = []

    for artikel in text_column:
        list_per_artikel = []
        verbs_per_artikel = {}
        if isinstance(artikel, str):
            s = parse(artikel)
            for pos_tagged_text in split(s):
                for chunk in pos_tagged_text.chunks:
                    list_per_artikel.append([chunk.type] + [(w.string, w.type) for w in chunk.words])
                    # add the infinitive form of the words as 'verbs'
                    for words in chunk.words:
                        if 'VB' in words.type:
                            verbs_per_artikel[conjugate(str(words), 'INFINITIVE')] = str(words)
        # else:
        #     print('Dit artikel bevat geen text')
        parsed_text.append(list_per_artikel)
        parsed_verbs.append(verbs_per_artikel)

    return parsed_text, parsed_verbs


def write_parsed_text_to_file(parsed_text, file):
    with open(str(file), 'w') as f:
        for sentence in parsed_text:
            f.write("%s\n" % sentence)


def read_pos_tags_to_file(file):
    with open(str(file), 'r') as f:
        lines = f.readlines()
        for line in lines:
            for chunk in line.chunks:
                print(chunk.type, [(w.string, w.type) for w in chunk.words])


def parser(tagger_name, dataframe, output_file):
    # dataframe = read_csv_to_df(str(csv_df_file))

    print("parsing using " + tagger_name)

    if tagger_name == "alpino":
        pos_tag = train_dutch_tagger()
        parsed_text = parse_text_alpino(dataframe['Brontekst'], pos_tag)
        fle = "postags_alpino.txt"
    elif tagger_name == "pattern":
        parsed_text, parsed_verbs = parse_text_pattern(dataframe['Brontekst'])
        fle = "postags_pattern-nl.txt"
    else:
        print("parser not recognized")

    dataframe['tags'] = parsed_text
    try:
        dataframe['verbs'] = parsed_verbs
    except:
        print('verbs do not exist; used alpino')
    write_df_to_csv(dataframe, output_file)
    return dataframe
