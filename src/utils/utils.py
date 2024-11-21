import json
import re
import string
import os
from nltk.corpus import stopwords
from src.translation.core import Translation


def update_dict(text: str) -> None:
    """
    The update_dict function takes a text input, processes it to remove stopwords and punctuation,
    and adds the unique words to a dictionary. If the word is not already in the dictionary,
    it is translated into French using the Translation class and added to the dictionary. 
    The dictionary is stored as a JSON file.

    Args:
        text (str): The input text to be processed and updated in the dictionary.
    
    Process:
        1. Tokenizes the input text.
        2. Filters out stopwords and punctuation.
        3. For each unique word, if it is not in the dictionary, it is translated and added to the dictionary.
        4. Updates the dictionary JSON file with new translations.

    File:
        - Reads and writes to a JSON file (`dict.json`) to store the dictionary of words and their translations.

    Returns:
        None
    """
    stop_words = set(stopwords.words())
    filtered_words = []

    for w in set(text.split()):
        if w.lower() not in stop_words and w.lower() not in (string.punctuation + '“”'):
            filtered_words.append(re.sub(r'(^\W+|\W+$)', ' ', w).strip())

    dict_file = "dict.json"
    if not os.path.exists(dict_file):
        with open(dict_file, 'w') as f:
            json.dump({}, f)

    with open(dict_file, 'r') as f:
        word_dict = json.load(f)

    for word in filtered_words:
        if word not in word_dict:
            translated_text = Translation.translation(word)
            word_dict[word] = translated_text

    with open(dict_file, 'w', encoding='utf-8') as f:
        json.dump(word_dict, f, indent=4, ensure_ascii=False)
