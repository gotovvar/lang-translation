from fastapi import APIRouter, Response
from src.translation.core import Translation
from src.text_parsing.core import TextProcess
from src.models.model import TextRequest
from src.utils.utils import update_dict

def create_router() -> APIRouter:
    query_router = APIRouter()

    @query_router.post("/translation")
    async def translate(request: TextRequest):
        english_processed_text = TextProcess.process(request.text)

        text_translation = Translation.translation(request.text)

        french_processed_text = TextProcess.process(text_translation, "french")

        update_dict(request.text)

        return {
            "original_text": request.text,
            "original_text_analysis": {
                "words_count": english_processed_text.words_count,
                "words_info": [
                    {"word": wi.word, "freq": wi.freq, "gram_info": wi.gram_info}
                    for wi in english_processed_text.words_info
                ],
            },
            "translated_text": text_translation,
            "translated_text_analysis": {
                "words_count": french_processed_text.words_count,
                "words_info": [
                    {"word": wi.word, "freq": wi.freq, "gram_info": wi.gram_info}
                    for wi in french_processed_text.words_info
                ],
            },
        }
    
    @query_router.post("/tree")
    async def get_tree(request: TextRequest):
        image_data = TextProcess.syntactic_tree(request.text)
        return Response(content=image_data, media_type="image/png")   
    
    return query_router