import nltk
from typing import List
from transformers import MarianMTModel, MarianTokenizer

class Translation:
    """
    The Translation class provides methods to translate text from English to French using a pre-trained MarianMT model.
    It splits the input text into smaller parts to avoid exceeding the model's maximum token limit and translates each part independently.

    Attributes:
        model_name (str): The name of the pre-trained translation model from HuggingFace's model hub (Helsinki-NLP/opus-mt-en-fr).
        tokenizer (MarianTokenizer): Tokenizer associated with the pre-trained MarianMT model.
        model (MarianMTModel): The MarianMT model used for translation.

    Methods:
        translation(text: str) -> str:
            Translates the entire input text from English to French, splitting it into smaller parts if necessary to avoid token limit issues.
        
        _split_text_into_parts(sentences: List[str], max_length: int = 128) -> List[str]:
            Splits the input sentences into parts, ensuring that the total number of tokens in each part does not exceed the specified maximum length.
        
        _translate_part(part: str) -> str:
            Translates a single part of the text from English to French using the MarianMT model.
    """
    model_name = "Helsinki-NLP/opus-mt-en-fr"

    tokenizer = MarianTokenizer.from_pretrained(model_name)

    model = MarianMTModel.from_pretrained(model_name)

    @classmethod
    def translation(cls, text: str) -> str:
        """
        Translates the input English text to French. The text is split into smaller parts if necessary to avoid exceeding the model's maximum token length.

        Args:
            text (str): The English text to be translated.

        Returns:
            str: The translated text in French.
        """
        sentences = nltk.sent_tokenize(text)
        parts = cls._split_text_into_parts(sentences)

        translated_parts = [cls._translate_part(part) for part in parts]
        translated_text = " ".join(translated_parts)

        return translated_text

    @classmethod
    def _split_text_into_parts(cls, sentences: List[str], max_length: int = 128) -> List[str]:
        """
        Splits the sentences into smaller parts, ensuring that the total number of tokens in each part does not exceed the specified maximum length.

        Args:
            sentences (List[str]): A list of sentences to be split.
            max_length (int, optional): The maximum token length for each part. Default is 128.

        Returns:
            List[str]: A list of sentence parts where each part's token length is within the specified limit.
        """       
        current_part = []
        current_length = 0
        parts = []

        for sentence in sentences:
            sentence_tokens = cls.tokenizer.encode(sentence, add_special_tokens=False)
            sentence_length = len(sentence_tokens)
            
            if current_length + sentence_length <= max_length:
                current_part.append(sentence)
                current_length += sentence_length
            else:
                parts.append(" ".join(current_part))
                current_part = [sentence]
                current_length = sentence_length

        if current_part:
            parts.append(" ".join(current_part))
            
        return parts


    @classmethod
    def _translate_part(cls, part: str) -> str:
        """
        Translates a single part of text using the MarianMT model.

        Args:
            part (str): A part of the text to be translated.

        Returns:
            str: The translated part of the text.
        """
        inputs = cls.tokenizer.encode(part, return_tensors="pt", padding=True, truncation=True)
        translated = cls.model.generate(inputs)
        translated_text = cls.tokenizer.decode(translated[0], skip_special_tokens=True)
        return translated_text
