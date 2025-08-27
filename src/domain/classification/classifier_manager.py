import os
from typing import List, Dict
from src.config.settings import ProjectSettings
from src.domain.classification.rule_based_classifier import RuleBasedClassifier
from src.domain.classification.ml_classifier import MLClassifier
from src.utils.file_process.preprocessor import Preprocessor

class ClassifierManager:
    def __init__(self, rule_classifier: RuleBasedClassifier, ml_classifier: MLClassifier, settings: ProjectSettings):
        self.rule_classifier = rule_classifier
        self.ml_classifier = ml_classifier
        self.settings = settings
        self.total_files = 0
        self.classified_files = []

    def clear_plan(self):
        """분류 계획을 초기화합니다."""
        self.classified_files = []
        print("분류 계획이 초기화되었습니다.")
        
    def set_total_files(self, total_files: int):
        self.total_files = total_files
    
    def plan_file_move(self, file_path: str, translated_content: str):        
        file_data = {
            "file_path": file_path,
            "all_content": translated_content,
            "first_content": translated_content[:500],
            "metadata": {"title": "", "author": ""} 
        }
        
        label = self.rule_classifier.classify(file_data)
        success = label != 'unclassified'
        return success, label, None

    def get_classification_plan(self):
        plan = {}
        # if not hasattr(self, 'classified_files') or not self.classified_files:
        #     return plan
            
        def get_output_folder_for_label(label):
            base_path = self.settings.load_classified_output_folder_path()
            if not base_path:
                print("⚠️ Classified output folder not set in settings. Using default 'classified/'.")
                base_path = "classified"
            return os.path.join(base_path, label)
            
        for file_data in self.classified_files:
            label = file_data.get('label')
            if label and label != 'unclassified':
                plan[file_data['file_name']] = get_output_folder_for_label(label)
        return plan
      
    def run_pipeline(self, file_data_list: List[Dict[str, str]]) -> List[Dict[str, str]]:
        for file_data in file_data_list:
            if file_data.get('label') == 'unclassified' or not file_data.get('label'):
                file_data['label'] = self.rule_classifier.classify(file_data)

        print(f"Rule-based classify가 완료되었습니다.")
        
        unclassified_files = [data for data in file_data_list if data['label'] == 'unclassified']
        
        if self.ml_classifier and unclassified_files:
            print(f"ML-based classify를 시작합니다. 대상 파일: {len(unclassified_files)}개")
            for file_data in unclassified_files:
                content_for_ml = file_data.get('all_content', '')
                preprocessor = Preprocessor()
                preprocessed_content = preprocessor.preprocess_text(content_for_ml)
                if preprocessed_content:
                    file_data['label'] = self.ml_classifier.classify(file_data) # 수정된 부분

        self.classified_files = file_data_list
        return file_data_list

    def update_syllabus_data(self, syllabus_data: List[Dict]):
        self.rule_classifier = RuleBasedClassifier(syllabus=syllabus_data)
        self.ml_classifier = MLClassifier(syllabus=syllabus_data)