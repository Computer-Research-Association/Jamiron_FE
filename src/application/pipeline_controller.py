import os
from typing import List, Dict
from src.utils.file_process.preprocessor import Preprocessor
from src.utils.file_process.translator import TextTranslator
from src.utils.file_system.file_extractor import FileExtractor
from src.utils.file_system.file_handler import FileHandler
from src.utils.file_system.file_watcher import FileWatcher
from src.domain.classification.classifier_manager import ClassifierManager

class PipelineController:
    def __init__(self, file_extractor: FileExtractor,  file_watcher: FileWatcher,
                 file_handler: FileHandler, preprocessor: Preprocessor, translator: TextTranslator,
                 classifier: ClassifierManager):

        self.preprocessor = preprocessor
        self.classifier = classifier
        self.translator = translator
        self.file_extractor = file_extractor
        self.file_watcher = file_watcher
        self.file_handler = file_handler

        self.file_data_list: List[Dict[str, str]] = []
        self.syllabus_data_list: List[Dict[str, str]] = []

    # 파이프라인 시작 전처리된 파일 넘겨주고 감시자 실행하고 감시자 끝내고
    # 파일 분류 다 된 경우
    # 혹은 사용자가 종료를 원할 경우
    # def run(self):
    #     while True:
    #         self.start_pipeline()
    #         if : break
    #     self.stop_pipeline()

    def start_pipeline(self):
      
        print("========"*30)

        # 감시자 시작
        self.file_watcher.start_watching()

        # 폴더 경로 받아서
        folder_path = "data/syllabus"
        # 파일 처리, 저장
        for dirpath, _, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                self.file_data_list.append(self.process_files(file_path))

        # 파일 분류
        self.classifier.run_pipeline(self.file_data_list)

        # # 파일 이동
        # self.file_handler.move_file()
        #
        # # 감시자 종료
        # self.stop_pipeline()

    def stop_pipeline(self):
        pass
        # """
        # 파이프라인 종료
        # """
        # if self.file_watcher and self.file_watcher.running:
        #     print("🛑 Pipeline stopped.")
        #     self.file_watcher.stop_watching()

    # 파일 전처리 번역 및 저장.
    def process_files(self, file_path):
        # 경로를 받아서 파일 프로세스
        file_data = {}
        # 1. 텍스트 추출
        all_content = self.file_extractor.extract_text(file_path)
        one_page_content = self.file_extractor.extract_one_page(file_path)

        # 2. 간단한 전처리
        rule_based_content = self.preprocessor.simple_preprocess(one_page_content)
        pre_ml_content = self.preprocessor.simple_preprocess(all_content)

        # 3. 번역
        # trs_ml_content = self.translator.translate(pre_ml_content)

        # 4. 전처리
        # self.preprocessor.preprocess(pre_ml_content)

        # 5. 파싱
        file_data['file_name'] = os.path.basename(file_path)

        # 6. 딕셔너리에 삽입
        file_data['first_content'] = rule_based_content
        file_data['ml_content']= pre_ml_content
        file_data['label'] = 'unclassified'  # 초기값 설정

        return file_data
#
# if __name__ == "__main__":
