import time
import threading
import os

class FileSystemWatcher:
    def __init__(self, watch_dir: str, on_new_file_callback, poll_interval: float = 1.0):
        self.watch_dir = watch_dir
        self.on_new_file_callback = on_new_file_callback
        self.poll_interval = poll_interval
        self.running = False
        self._thread = None
        self._seen_files = set()

    def start(self):
        if self.running:
            print("이미 감시가 실행 중입니다.")
            return

        if not os.path.isdir(self.watch_dir):
            print(f"[오류] 감시 대상 폴더를 찾을 수 없습니다: {self.watch_dir}")
            return

        print(f"🔍 '{self.watch_dir}' 폴더에 대한 감시를 시작합니다.")
        self.running = True
        self._seen_files = set(os.listdir(self.watch_dir))
        self._thread = threading.Thread(target=self.watch_loop, daemon=True)
        self._thread.start()

    def stop(self):
        if not self.running:
            return
        
        print(f"🛑 '{self.watch_dir}' 폴더 감시를 중지합니다.")
        self.running = False
        if self._thread and self._thread.is_alive():
            self._thread.join()

    def watch_loop(self):
        while self.running:
            try:
                if not os.path.isdir(self.watch_dir):
                    print(f"[⚠️ 경고] 감시 대상 폴더가 사라졌습니다: {self.watch_dir}")
                    self.stop()
                    break

                current_files = set(os.listdir(self.watch_dir))
                new_files = current_files - self._seen_files

                if new_files:
                    for filename in new_files:
                        file_path = os.path.join(self.watch_dir, filename)
                        if os.path.isfile(file_path):
                            # 파일이 완전히 복사될 때까지 잠시 대기
                            initial_size = -1
                            time.sleep(0.1)
                            while True:
                                try:
                                    current_size = os.path.getsize(file_path)
                                    if current_size == initial_size:
                                        break
                                    initial_size = current_size
                                    time.sleep(0.2)
                                except OSError:
                                    break # 파일이 사라졌을 수 있음
                            
                            print(f"✨ 새 파일 감지: {filename}")
                            self.on_new_file_callback(file_path)
                
                self._seen_files = current_files

            except Exception as e:
                print(f"[❌ 감시 오류] {e}")

            time.sleep(self.poll_interval)