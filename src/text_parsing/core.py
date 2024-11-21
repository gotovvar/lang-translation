import io
import string
import nltk
import spacy
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.draw.util import CanvasFrame
from nltk.draw import TreeWidget
from PIL import Image

from src.models.model import WordInfo, TextInfo

class TextProcess:
    """
    The TextProcess class is designed for natural language processing tasks, such as text tokenization, part-of-speech tagging, and syntactic parsing. 
    It supports both English and French languages, offering functionality for extracting relevant information from text, such as word frequencies, grammatical roles, and sentence structure.

    Attributes:
        nlp (spacy.language): A spaCy model for processing French text ('fr_core_news_sm').
        metadata_english (dict): A mapping of part-of-speech tags to their descriptions in Russian for English.
        metadata_french (dict): A mapping of part-of-speech tags to their descriptions in Russian for French.
        grammer (nltk.RegexpParser): A regular expression-based parser for syntactic structure in English.

    Methods:
        process(text: str, language: str = 'english') -> TextInfo:
            Processes the input text, tokenizes it, removes stopwords and punctuation, and returns a structured representation of the word information, including frequency and grammatical role.
        
        pos_tag(word: str, language: str) -> str:
            Tags a word with its part-of-speech and returns its Russian description based on the language specified.
        
        syntactic_tree(text: str) -> bytes:
            Generates a syntactic tree based on the sentence structure and returns an image (in PNG format) of the tree.
    """
    nlp = spacy.load('fr_core_news_sm')
    
    metadata_english = {
        "CC": "координирующая конъюнкция",
        "CD": "цифра",
        "DT": "артикль",
        "EX": "указательное местоимение",
        "FW": "иностранное слово",
        "IN": "предлог/союз",
        "JJ": "прилагательное",
        "JJR": "прилагательное сравнительное",
        "JJS": "прилагательное в превосходной степени",
        "LS": "элемент списка",
        "MD": "модальный глагол",
        "NN": "существительное в единственном числе",
        "NNS": "существительное во множественном числе",
        "NNP": "имя собственное в единственном числе",
        "NNPS": "имя собственное во множественном числе",
        "PDT": "определительное местоимение",
        "POS": "притяжательное окончание",
        "PRP": "местоимение",
        "PRP$": "притяжательное местоимение",
        "RB": "наречие",
        "RBR": "наречие в сравнительной степени",
        "RBS": "наречие в превосходной степени",
        "RP": "частица",
        "SYM": "символ",
        "TO": "предлог to",
        "UH": "междометие",
        "VB": "глагол, базовая форма",
        "VBD": "глагол, прошедшее время",
        "VBG": "глагол, герундий/причастие настоящего времени",
        "VBN": "глагол, причастие прошедшего времени",
        "VBP": "глагол, настоящее время, не 3-е лицо",
        "VBZ": "глагол, настоящее время, 3-е лицо",
        "WDT": "вопросительное определение",
        "WP": "вопросительное местоимение",
        "WP$": "притяжательное вопросительное местоимение",
        "WRB": "вопросительное наречие"
    }

    metadata_french = {
        "ADJ": "прилагательное",
        "ADP": "предлог",
        "ADV": "наречие",
        "AUX": "вспомогательный глагол",
        "CCONJ": "сочинительный союз",
        "DET": "определитель",
        "INTJ": "междометие",
        "NOUN": "существительное",
        "NUM": "числительное",
        "PART": "частица",
        "PRON": "местоимение",
        "PROPN": "имя собственное",
        "PUNCT": "пунктуация",
        "SCONJ": "подчинительный союз",
        "SYM": "символ",
        "VERB": "глагол",
        "X": "неизвестное или другое"
    }
    
    grammer = nltk.RegexpParser(
        """
        NP: {<DT>?<JJ>*<NN.*>}
        P: {<IN>}
        V: {<V.*>}
        PP: {<P> <NP>}
        VP: {<V> <NP|PP>*}
        S:  {<NP> <VP>}
        """
    )
    
    @classmethod
    def process(cls, text: str, language: str = 'english') -> TextInfo:
        """
        Processes the input text by tokenizing it, removing stopwords and punctuation, and analyzing the grammatical roles of the words.

        Args:
            text (str): The text to be processed.
            language (str, optional): The language of the text ('english' or 'french'). Defaults to 'english'.

        Returns:
            TextInfo: A structured representation containing information about the processed words, including their frequency and grammatical roles.
        """
        stop_words = set(stopwords.words(language))
        word_tokens = word_tokenize(text.lower())
        
        processed_words = []
        
        for word in set(word_tokens):
            if word.lower() not in stop_words and word.lower() not in (string.punctuation + '“”'):
                gram_info = cls.pos_tag(word, language)
                if gram_info:
                    processed_words.append(
                        WordInfo(
                            word=word,
                            freq=word_tokens.count(word),
                            gram_info=gram_info
                        )
                    )
        processed_words.sort(key=lambda x: x.freq, reverse=True)

        return TextInfo(words_info=processed_words, words_count=len(processed_words))
    
    @classmethod
    def pos_tag(cls, word: str, language: str) -> str:
        """
        Tags a word with its part-of-speech based on the specified language.

        Args:
            word (str): The word to be tagged.
            language (str): The language of the word ('english' or 'french').

        Returns:
            str: The part-of-speech tag description in Russian based on the language and the word's grammatical role.
        """
        if language == 'english':
            return cls.metadata_english[nltk.pos_tag([word])[0][1]]
        elif language == 'french':
            token = cls.nlp(word)[0]
            return cls.metadata_french.get(token.pos_)
    
    @classmethod
    def syntactic_tree(cls, text: str) -> bytes:
        """
        Generates a syntactic tree for the input text using part-of-speech tagging and a regular expression-based grammar.
        The tree is saved as a PostScript file and then converted to a PNG image, which is returned as a byte stream.

        Args:
            text (str): The text for which the syntactic tree is to be generated.

        Returns:
            bytes: A byte stream containing the syntactic tree image in PNG format.
        """
        tagged = nltk.pos_tag(
            [word for word in word_tokenize(text) if word not in string.punctuation]
        )
        window = CanvasFrame(width=1500, height=500)
        output = cls.grammer.parse(tagged)
        tree = TreeWidget(window.canvas(), output)
        window.add_widget(tree, 10, 10)
        window.print_to_file('tree.ps')
        window.destroy()
        
        psimage=Image.open('tree.ps')
        psimage.load(scale=2) 
        img_byte_arr = io.BytesIO()
        psimage.save(img_byte_arr, format='PNG', dpi=(300, 300))
        img_byte_arr = img_byte_arr.getvalue()
        
        return img_byte_arr