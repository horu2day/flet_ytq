import os
import sys
import logging
import tempfile
from datetime import datetime

def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def setup_logging():
    log_file = os.path.join(
        tempfile.gettempdir(),
        f'youtube_analyzer_{datetime.now().strftime("%Y%m%d")}.log'
    )
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )