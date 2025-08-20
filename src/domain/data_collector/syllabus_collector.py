from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
from config.settings import ProjectSettings
import time
import re
import os
import threading
import math
import json


# process_and_save_syllabus 함수는 preprocessor.py에서 import하여 사용


def clean_text(text: str) -> str:
    """텍스트에서 공백을 정리하고 앞뒤 공백을 제거함."""
    text = re.sub(r"\s+", " ", text).strip()
    return text


class SyllabusCollector:
    """
    히즈넷에서 강의 계획서 정보를 수집하는 클래스.
    """

    def __init__(self, progress_callback=None):
        """
        SyllabusCollector 인스턴스를 초기화함.

        Args:
            progress_callback (callable, optional): 진행 상황을 업데이트할 콜백 함수.
                                                   메시지와 진행률(0-100)을 인자로 받음.
        """
        self.driver = None
        self.base_url = "https://hisnet.handong.edu/"
        self.login_url = self.base_url + "login/login.php"
        self.progress_callback = progress_callback
        self.current_user_year = None
        self.current_user_hakgi = None
        self.settings = ProjectSettings()
        self.all_syllabuses = []

    def _update_progress(self, message: str, percent: int):
        """진행 상황을 콜백 함수를 통해 업데이트함."""
        if self.progress_callback:
            self.progress_callback(message, percent)

    def _initialize_webdriver(self):
        """WebDriver를 초기화함."""
        if self.driver:
            return

        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
        except Exception as e:
            self._update_progress(f"WebDriver 초기화 실패: {e}", 0)
            raise

    def login(self, user_id: str, password: str) -> bool:
        """
        히즈넷 사이트에 로그인 수행.
        """
        self._initialize_webdriver()
        if not self.driver:
            self._update_progress("WebDriver가 초기화되지 않았습니다.", 0)
            return False

        self._update_progress("로그인 시도 중...", 50)
        self.driver.get(self.login_url)

        try:
            id_input = self.driver.find_element(
                By.CSS_SELECTOR,
                "#loginBoxBg > table:nth-child(2) > tbody > tr > td:nth-child(5) > form > table > tbody > tr:nth-child(3) > td > table > tbody > tr > td:nth-child(1) > table > tbody > tr:nth-child(1) > td:nth-child(2) > span > input[type=text]",
            )
            id_input.send_keys(user_id)

            password_input = self.driver.find_element(
                By.CSS_SELECTOR,
                "#loginBoxBg > table:nth-child(2) > tbody > tr > td:nth-child(5) > form > table > tbody > tr:nth-child(3) > td > table > tbody > tr > td:nth-child(1) > table > tbody > tr:nth-child(3) > td:nth-child(2) > input[type=password]",
            )
            password_input.send_keys(password)

            login_button = self.driver.find_element(
                By.CSS_SELECTOR,
                "#loginBoxBg > table:nth-child(2) > tbody > tr > td:nth-child(5) > form > table > tbody > tr:nth-child(3) > td > table > tbody > tr > td:nth-child(2) > input[type=image]",
            )

            login_button.click()

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#kang_yy"))
            )
            self.driver.switch_to.window(self.driver.window_handles[0])
            self._update_progress("로그인 성공!", 100)
            return True
        except Exception as e:
            self._update_progress(
                f"로그인에 실패했습니다. 아이디 또는 비밀번호를 확인하세요. ({e})", 0
            )
            if self.driver:
                self.driver.quit()
                self.driver = None
            return False

    def navigate_to_planner_page(self, year: str, hakgi: str) -> bool:
        self.current_user_year = year
        self.current_user_hakgi = hakgi

        if not self.driver:
            self._update_progress("WebDriver가 초기화되지 않았습니다.", 0)
            return False

        try:
            my_year_select = Select(
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "#kang_yy"))
                )
            )
            if year not in [
                option.get_attribute("value") for option in my_year_select.options
            ]:
                self._update_progress(
                    f"해당 학년도({year})에 대한 강의를 찾을 수 없습니다.", 0
                )
                return False
            my_year_select.select_by_value(year)

            my_hakgi_select = Select(
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "#kang_hakgi"))
                )
            )
            my_hakgi_select.select_by_value(hakgi)

            load_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (
                        By.CSS_SELECTOR,
                        "#tr_box_1 > table > tbody > tr:nth-child(1) > td > div > div > form > a",
                    )
                )
            )
            load_btn.click()
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#div_box_1"))
            )
            return True
        except (NoSuchElementException, TimeoutException) as e:
            self._update_progress(
                f"강의 계획서 페이지 이동 중 오류 발생 (요소 찾기 실패 또는 타임아웃): {e}",
                0,
            )
            if self.driver:
                self.driver.quit()
                self.driver = None
            return False
        except Exception as e:
            self._update_progress(
                f"강의 계획서 페이지 이동 중 예상치 못한 오류 발생: {e}", 0
            )
            if self.driver:
                self.driver.quit()
                self.driver = None
            return False

    def download_planners(self):
        if not self.driver:
            self._update_progress("WebDriver가 초기화되지 않았습니다.", 0)
            return

        classes_list = self._get_class_list()
        total_classes = len(classes_list)

        if total_classes == 0:
            self._update_progress("해당 학기 강의가 없습니다.", 100)
            return

        for idx, class_info in enumerate(classes_list, 1):
            url = class_info["href"]
            title = class_info["title"]

            print(f"처리 중인 URL: {url}")
            # old/crawler.py 방식: URL의 마지막 16자리를 사용해서 파라미터 추출
            temp = url[-16:]
            syllabus_detail_url = f"{self.base_url}SMART/lp_view_4student_1.php?kang_yy={temp[:4]}&kang_hakgi={temp[5]}&kang_code={temp[-8:]}&kang_ban={temp[6:8]}"

            try:
                data = self._parse_syllabus_page(
                    syllabus_detail_url,
                    title,
                    self.current_user_year,
                    self.current_user_hakgi,
                )
                # print(f"DEBUG: Data from _parse_syllabus_page for {title}: {data}")
                if data:
                    # 강의계획서 처리 및 번역 후 저장
                    from src.utils.file_process.preprocessor import (
                        process_and_save_syllabus,
                    )

                    processed_data = process_and_save_syllabus(
                        data, self.current_user_year, self.current_user_hakgi, title
                    )
                    # print(f"DEBUG: Processed data for {title}: {processed_data}")

                    if processed_data:
                        self.all_syllabuses.append(processed_data)

                # 프로그래스바 업데이트 (0~90%)
                progress_percent = int((idx / total_classes) * 90)
                self._update_progress(
                    f"[{idx}/{total_classes}] {title} 처리중",
                    progress_percent,
                )
            except Exception as e:
                # 오류가 발생해도 프로그래스바는 계속 진행
                progress_percent = int((idx / total_classes) * 90)
                self._update_progress(
                    f"[{idx}/{total_classes}] {title} 처리중",
                    progress_percent,
                )
                # print(f"ERROR: Exception during processing {title}: {e}")
                continue

        # print(f"DEBUG: self.all_syllabuses length before saving: {len(self.all_syllabuses)}")
        self._save_all_syllabuses_to_json()  # 모든 강의 계획서 데이터를 JSON 파일에 저장
        self._update_progress("크롤링 완료!", 100)

    def _get_class_list(self) -> list:
        classes_list = []
        try:
            print(f"현재 페이지 URL: {self.driver.current_url}")
            print("강의 목록 요소 대기 중...")

            # old/crawler.py 방식: 2초 대기 후 div 요소들을 순차적으로 확인
            time.sleep(2)

            div_elements = self.driver.find_elements(
                By.CSS_SELECTOR, "#div_box_1 > div"
            )
            print(f"div_box_1 내부의 div 요소 개수: {len(div_elements)}")

            for i in range(1, len(div_elements) + 1):
                try:
                    my_class = self.driver.find_element(
                        By.CSS_SELECTOR,
                        f"#div_box_1 > div:nth-child({i}) > a:nth-child(2)",
                    )
                    href = my_class.get_attribute("href")
                    text = my_class.text.strip()

                    if href and text:
                        classes_list.append({"href": href, "title": text})
                        print(f"강의 추가: {text} - {href}")

                except Exception as e:
                    print(f"div {i} 처리 중 오류: {e}")
                    continue

        except Exception as e:
            print(f"강의 목록 파싱 중 예상치 못한 오류 발생: {e}")
            # 오류 발생 시에만 프로그래스바에 메시지 표시
            self._update_progress(f"강의 목록 파싱 중 예상치 못한 오류 발생: {e}", 0)

        print(f"총 {len(classes_list)}개의 강의를 찾았습니다.")
        return classes_list

    def _parse_syllabus_page(
        self, url: str, class_title: str, year: str, hakgi: str
    ) -> dict:
        self.driver.get(url)
        soup = BeautifulSoup(self.driver.page_source, "html.parser")

        for script in soup(["script", "style"]):
            script.decompose()

        prof_name = ""
        try:
            prof_name_element = soup.select_one(
                "#div1 > div > table:nth-child(3) > tbody > tr:nth-child(5) > td:nth-child(1) > div"
            )
            if prof_name_element:
                prof_name = prof_name_element.get_text(strip=True)
        except Exception:
            pass

        prof_email = ""
        try:
            prof_email_element = soup.select_one(
                "#div1 > div > table:nth-child(3) > tbody > tr:nth-child(5) > td:nth-child(2)"
            )
            if prof_email_element:
                prof_email = prof_email_element.get_text(strip=True)
        except Exception:
            pass

        tds_description = soup.select(
            "#div1 > div > table:nth-child(13) > tbody > tr > td"
        )
        description_text = "\n".join(
            [clean_text(td.get_text()) for td in tds_description]
        )

        objectives_text = "Course Objectives\n"
        tds_objectives = soup.select("#tbl_Obj > tbody > tr")[1:]
        for tr in tds_objectives:
            td_element = tr.select_one("td.cls_AlignLeft")
            if td_element:
                objectives_text += clean_text(td_element.get_text()) + "\n"

        schedule_text = ""
        i = 2
        while True:
            selector = f"#tblN16 > tbody > tr:nth-child({i}) > td:nth-child(3)"
            td = soup.select_one(selector)
            if not td:
                break
            text = clean_text(td.get_text())
            if text:
                schedule_text += text + "\n"
            i += 1

        match = re.search(r"kang_code=([^&]+)", url)
        kang_code = match.group(1)
        temp = url[-16:]

        return {
            "class_name": class_title,
            "class_code": kang_code,
            "professor_name": prof_name,
            "prof_email": prof_email,
            "year": year,
            "hakgi": hakgi,
            "objectives": objectives_text.strip(),
            "description": description_text.strip(),
            "schedule": schedule_text.strip(),
        }

    def _save_all_syllabuses_to_json(self):
        """수집된 모든 강의 계획서 데이터를 개별 파일과 통합 파일에 저장합니다."""
        # 기본 경로 설정
        base_data_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "..",
            "data",
        )

        # syllabus 디렉토리 경로
        syllabus_dir = os.path.join(
            self.settings.paths["data_dir"], "syllabus")
        syllabus_file_path = self.settings.paths["syllabus_file"]

        try:
            # 디렉토리 생성
            os.makedirs(base_data_dir, exist_ok=True)
            os.makedirs(syllabus_dir, exist_ok=True)

            # 통합 syllabus.json 파일로 저장 (개별 파일은 이미 process_and_save_syllabus에서 저장됨)
            with open(syllabus_file_path, "w", encoding="utf-8") as f:
                json.dump(self.all_syllabuses, f, indent=4, ensure_ascii=False)

            # 데이터 저장은 95%에서 처리 (메시지 없이)
        except IOError as e:
            self._update_progress(f"강의 계획서 데이터 저장 실패: {e}", 0)
        except Exception as e:
            self._update_progress(
                f"강의 계획서 데이터 저장 중 예상치 못한 오류 발생: {e}", 0
            )

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
