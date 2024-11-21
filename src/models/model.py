from typing import List
from pydantic import BaseModel

class WordInfo(BaseModel):
    word: str
    freq: int
    gram_info: str

class TextInfo(BaseModel):
    words_info: List[WordInfo]
    words_count: int

class TextRequest(BaseModel):
    text: str