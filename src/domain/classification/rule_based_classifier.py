from typing import List, Dict
from collections import Counter


class RuleBasedClassifier:
    def __init__(self, syllabus: List[Dict[str, str]]):
        self.syllabus = syllabus

    def classify(self, file_data: Dict[str, any]) -> str:
        first_content = file_data.get("first_content", "")
        metadata = file_data.get("metadata", {})
        title = metadata.get("title", "") or ""
        author = metadata.get("author", "") or ""
        professor_list = [e.get("professor_name", "") for e in self.syllabus]
        isDup = False # 중복 확인
        if len(professor_list) != len(set(professor_list)):
            isDup = True
            
        for entry in self.syllabus:
            class_code = entry.get("class_code", "")
            class_name = entry.get("class_name", "")
            prof_name = entry.get("professor_name", "")
            prof_email = entry.get("prof_email", "")

            # 규칙 1: 강의 코드가 파일 내용에 포함되는 경우
            if class_code and class_code in first_content:
                return class_name
            
            # 규칙 2: 강의명이 파일 내용이나 제목에 포함되는 경우
            if class_name and class_name in (first_content + title):
                return class_name
            
            # 규칙 3: 교수명이 파일 내용이나 작성자에 포함되는 경우
            if (not(isDup)):
                if prof_name and prof_name in (first_content + author):
                    return class_name   
                # 규칙 4: 교수 이메일이 파일 내용에 포함되는 경우
                if prof_email in first_content:
                    return class_name

        return "unclassified"