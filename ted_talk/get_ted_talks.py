# https://www.kaggle.com/thegupta/ted-talk?select=TED_Talk.csv

import pandas as pd
import re

from nltk.tokenize import sent_tokenize, word_tokenize


# ====================
def save_text_to_file(text: str, file_path: str):

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)


df = pd.read_csv('TED_Talk.csv')

talk_info = []

for index, row in df.iterrows():
    transcript = row['transcript']
    talk_id = row['talk__id']
    try:
        transcript = re.sub(r' *(\(Laughter\)|\(Applause\) *)+ *', ' ', transcript)
        num_words = len(word_tokenize(transcript))
        num_sents = len(sent_tokenize(transcript))
        talk_info.append({
            'talk_id': talk_id,
            'num_words': num_words,
            'num_sents': num_sents
        })
        save_text_to_file(transcript, f"{talk_id}.txt")
    except TypeError:
        # Some rows appear to have NaN in transcript column. Print and move on
        print(transcript)

talk_info_df = pd.DataFrame(talk_info)
talk_info_df.to_excel('talk_info.xlsx')
