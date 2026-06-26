# src/utils/logger.py
import logging 
import sys
from pathlib import Path

# ==========================================
# THÊM PROJECT ROOT VÀO SYS.PATH
# ==========================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.path import LOGGER_DATA_FILE, check_and_create_directories

def get_pipeline_logger(module_name):
    """
    Hàm khởi tạo logger dùng chung cho toàn bộ dự án.
    Tự động ghi log ra cả màn hình console và file.
    """
    logger = logging.getLogger(module_name)
    logger.setLevel(logging.INFO)

    # Kiểm tra trên chính đối tượng 'logger'
    if not logger.handlers:
        # Định dạng dòng log chuẩn
        formatter = logging.Formatter('%(asctime)s - %(name)s - [%(levelname)s] - %(message)s')

        # 1. Cấu hình Handler in ra màn hình (Console)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # 2. Cấu hình Handler ghi vào file văn bản
        # Đưa phần tạo file vào TRONG khối if để tránh lặp file handler
        check_and_create_directories(auto_create=True)
        
        # Nhớ thêm encoding='utf-8' để tránh lỗi font tiếng Việt
        txt_handler = logging.FileHandler(LOGGER_DATA_FILE, encoding='utf-8')
        txt_handler.setLevel(logging.INFO)
        txt_handler.setFormatter(formatter)
        logger.addHandler(txt_handler)

    return logger