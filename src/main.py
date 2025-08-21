import sys
import os

base_path = os.path.abspath(os.path.dirname(__file__))
if base_path not in sys.path:
    sys.path.insert(0, base_path)

from src.app_runner import run_app

if __name__ == "__main__":
    run_app()