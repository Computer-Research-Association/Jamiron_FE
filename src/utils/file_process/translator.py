import time
import re
from typing import List
from googletrans import Translator as GoogleTranslatorAPI


class TextTranslator:
    def __init__(self):
        self.translator = GoogleTranslatorAPI()
        self.chunk_size = 5000
        self.chunk_delay = 2.0
        self.max_retries = 3

    def translate(self, text: str, source: str = "ko", target: str = "en") -> str:
        if not text or not text.strip():
            return ""

        try:
            result = self.translator.translate(text, src=source, dest=target)
            if result and hasattr(result, "text") and result.text:
                return result.text.strip()
            return text
        except Exception as e:
            print(f"번역 오류: {e}")
            return text
          
    def translate_long_text(self, text) -> str:
        source='auto'
        target='en'
        if not text or not text.strip():
            return ""

        # 짧은 텍스트는 바로 번역
        if len(text) <= self.chunk_size:
            return self._translate_with_retry(text, source, target)

        # 긴 텍스트는 청크로 분할하여 번역
        chunks = self._split_into_chunks(text, self.chunk_size)
        translated_parts = []

        for i, chunk in enumerate(chunks, 1):
            if not chunk.strip():
                translated_parts.append(chunk)
                continue

            # print(f"  청크 {i}/{len(chunks)} 번역 중...")
            translated_chunk = self._translate_with_retry(chunk, source, target)
            translated_parts.append(translated_chunk)

            # 마지막 청크가 아니면 대기
            if i < len(chunks):
                time.sleep(self.chunk_delay)

        return " ".join(translated_parts)

    def _translate_with_retry(self, text: str, source: str, target: str) -> str:
        for attempt in range(self.max_retries):
            try:
                if attempt > 0:
                    self.translator = GoogleTranslatorAPI()
                    time.sleep(2.0 * attempt)

                result = self.translator.translate(text, src=source, dest=target)
                if result and hasattr(result, "text") and result.text:
                    return result.text.strip()

            except Exception as e:
                if attempt == self.max_retries - 1:
                    print(f"번역 실패 (최대 재시도 초과): {e}")
                    return text

        return text

    def _split_into_chunks(self, text: str, max_length: int) -> List[str]:
        if len(text) <= max_length:
            return [text]

        chunks = []
        sentences = re.split(r"[.!?]\s+", text)
        current_chunk = ""

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            test_chunk = current_chunk + (" " if current_chunk else "") + sentence

            if len(test_chunk) <= max_length:
                current_chunk = test_chunk
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks