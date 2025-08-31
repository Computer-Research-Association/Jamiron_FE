import re
import json
import os
from .translator import TextTranslator


class Preprocessor:
    def __init__(self, translate: bool = False):
        self.translate = TextTranslator()

    def preprocess_text(self, text: str) -> str:
        # 실제 텍스트 전처리 로직
        if not isinstance(text, str):
            return ""
        text = re.sub(r'<.*?>', '', text)
        text = re.sub(r'http[s]?://\S+', '', text)
        text = re.sub(r'www\.\S+', '', text)
        text = re.sub(r'\s*\n\s*', '\n', text)
        text = re.sub(r'\n{2,}', '\n', text)
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'[^a-zA-Z0-9\s.,!?\'"-]', '', text)
        
        return text.lower()