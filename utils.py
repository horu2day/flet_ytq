import os
import sys
import socket
import logging
import tempfile
from datetime import datetime

def get_resource_path(relative_path):
    """Get absolute path to resource for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def find_free_port():
    """Find an available port"""
    with socket.socket() as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def setup_logging():
    """Setup logging configuration"""
    log_file = os.path.join(
        tempfile.gettempdir(),
        f'youtube_analyzer_{datetime.now().strftime("%Y%m%d")}.log'
    )
    
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )