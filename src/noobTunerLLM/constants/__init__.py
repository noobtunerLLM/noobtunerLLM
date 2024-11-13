from pathlib import Path
from datetime import datetime

"""
Logger realated constants
"""

ROOT_DIR = Path(__file__).parents[3]
LOG_FILE_NAME = f"{datetime.now().strftime('%m%d%Y__%H%M%S')}.log"
LOG_FILE_DIR = ROOT_DIR / "logs"
