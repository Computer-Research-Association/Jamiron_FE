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

    def process_syllabus_files(self, files_to_process, progress_callback=None):
        if not files_to_process:
            if progress_callback:
                progress_callback("처리할 파일이 없습니다.", 100)
            return

        total_files = len(files_to_process)
        processed_files = 0

        for filepath, subject in files_to_process:
            if os.path.exists(filepath):
                try:
                    with open(filepath, "r+", encoding="utf-8") as f:
                        contents = json.load(f)

                        # 번역할 필드들 (title은 제외)
                        fields_to_translate = ["objectives", "description", "schedule"]

                        for field in fields_to_translate:
                            if contents.get(field) and contents[field].strip():
                                # print(
                                #     f"  {field} 번역 중... ({len(contents[field]):,}자)"
                                # )
                                try:
                                    # 5000자 이상은 분할 번역 사용
                                    translated = self.translate.translate_long_text(contents[field])
                                    contents[field] = translated
                                    print(f"    ✅ 번역 완료")
                                except Exception as e:
                                    print(f"    ❌ 번역 실패: {e}")

                        # 파일에 다시 쓰기
                        f.seek(0)
                        f.truncate()
                        json.dump(contents, f, ensure_ascii=False, indent=4)

                except Exception as e:
                    print(f"파일 처리 오류 ({filepath}): {e}")

            processed_files += 1
            if progress_callback:
                percent = int(processed_files / total_files * 100)
                progress_callback(
                    f"처리 중: {os.path.basename(filepath)}",
                    percent,
                )

        if progress_callback:
            progress_callback("모든 파일 처리 완료.", 100)


def process_and_save_syllabus(
    data: dict,
    user_year: str,
    user_hakgi: str,
    class_name: str,
    output_dir: str = "src/data/syllabus",
):
    translator = TextTranslator()
    try:
        print(f"\n=== 강의계획서 처리 및 번역: {class_name} ===")

        # 번역할 필드들 (title은 제외 - 강의명은 원본 유지)
        fields_to_translate = [
            ("objectives", "목표"),
            ("description", "설명"),
            ("schedule", "일정"),
        ]

        processed_data = {
            "class_name": data.get("class_name", ""),  # 제목은 번역하지 않고 원본 유지
            "class_code": data.get("class_code", ""),
            "professor_name": data.get("professor_name", ""),
            "prof_email": data.get("prof_email", ""),
            "year": data.get("year", ""),
            "hakgi": data.get("hakgi", ""),
        }

        # 각 필드별로 번역 수행
        for field_key, field_name in fields_to_translate:
            original_text = data.get(field_key, "")
            if original_text and original_text.strip():
                # print(f"  {field_name} 번역 중... ({len(original_text):,}자)")
                try:
                    # 5000자 이상은 분할 번역 사용
                    translated_text = translator.translate_long_text(original_text)

                    # 번역 결과 검증
                    if translated_text and translated_text.strip():
                        processed_data[field_key] = translated_text
                        # print(
                        #     f"    ✅ 번역 성공: {original_text[:30]}... → {translated_text[:30]}..."
                        # )
                    else:
                        # 번역 실패 시 원본 사용
                        processed_data[field_key] = original_text
                        print(f"    ⚠️ 번역 실패, 원본 사용: {original_text[:50]}...")

                except Exception as e:
                    # 번역 중 예외 발생 시 원본 사용
                    processed_data[field_key] = original_text
                    print(f"    ❌ 번역 오류, 원본 사용: {e}")

            else:
                processed_data[field_key] = original_text
                print(f"  {field_name} 번역 건너뜀 (빈 내용)")

        # 출력 디렉토리 생성
        syllabus_output_path = os.path.join(os.getcwd(), output_dir)
        print(f"디렉토리 생성: {syllabus_output_path}")
        os.makedirs(syllabus_output_path, exist_ok=True)

        # 파일명을 안전하게 만들기 (특수 문자 제거)
        import re

        safe_class_name = re.sub(
            r'[<>:"/\\|?*]', "_", class_name
        )  # Windows에서 금지된 문자들을 '_'로 대체
        safe_class_name = safe_class_name.strip()  # 앞뒤 공백 제거

        # 파일명 생성
        file_name = f"{user_year[2:]}-{user_hakgi}_{safe_class_name}.json"
        file_path = os.path.join(syllabus_output_path, file_name)
        print(f"파일 저장 시도: {file_path}")

        # JSON 파일로 저장
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(processed_data, f, ensure_ascii=False, indent=4)

        print(f"강의 계획서 저장 완료: {file_path}")

        # 파일이 실제로 생성되었는지 확인
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"파일 생성 확인: {file_path} (크기: {file_size} bytes)")
        else:
            print(f"파일 생성 실패: {file_path}")
        return processed_data

    except Exception as e:
        print(f"강의 계획서 처리 및 저장 실패: {class_name} - {e}")
        # 오류 발생 시에도 원본 데이터 반환 (번역 없이)
        return {
            "class_name": data.get("class_name", ""),
            "class_code": data.get("class_code", ""),
            "professor_name": data.get("professor_name", ""),
            "year": data.get("year", ""),
            "hakgi": data.get("hakgi", ""),
            "objectives": data.get("objectives", ""),
            "description": data.get("description", ""),
            "schedule": data.get("schedule", ""),
        }