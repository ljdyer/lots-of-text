import json
import os

import wikipedia
from nltk.tokenize import sent_tokenize, word_tokenize
from wikipedia.exceptions import DisambiguationError, PageError


# ====================
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


# ====================
def load_json(SAVED_JSON_PATH):

    with open(SAVED_JSON_PATH, 'r') as file:
        settings = json.load(file)
    return settings


# ====================
def save_json(settings, SAVED_JSON_PATH):

    with open(SAVED_JSON_PATH, 'w') as file:
        json.dump(settings, file, indent=4, sort_keys=True)


# ====================
def save_text_to_file(text: str, file_path: str):

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)


SAVE_FOLDER = "wiki_content"
SAVED_JSON_PATH = "wiki_content/saved.json"
STATS_JSON_PATH = "wiki_content/stats.json"

saved = load_json(SAVED_JSON_PATH)
stats = load_json(STATS_JSON_PATH)

saved_keys = list(map(int, saved.keys()))

if saved_keys:
    last_index = max(saved_keys)
else:
    last_index = 0

for i in range(10):
    page = wikipedia.random(1)
    try:
        if page not in saved.values():
            content = wikipedia.page(page).content
            last_index += 1
            saved[str(last_index)] = page
            save_text_to_file(content, f'{SAVE_FOLDER}/{last_index}.txt')
            stats['total_articles'] += 1
            stats['total_words'] += len(word_tokenize(content))
            stats['total_sents'] += len(sent_tokenize(content))
            save_json(saved, SAVED_JSON_PATH)
            save_json(stats, STATS_JSON_PATH)
            clear_screen()
            for key, value in stats.items():
                print(f'{key}: {value}')
    except (DisambiguationError, PageError):
        pass
