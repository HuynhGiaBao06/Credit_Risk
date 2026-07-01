# Hàm gọi SQL View trả ra Pandas DataFrame
import pandas as pd
import sys
from pathlib import Path
# ==========================================
# THÊM PROJECT ROOT VÀO SYS.PATH
# ==========================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# Import logger
from src.utils.logger import get_pipeline_logger
from src.db_config import NeonDBManager
from src.path import TRAIN_DATA_FILE, TEST_DATA_FILE, check_and_create_directories

from sklearn.model_selection import train_test_split

class DataIngestion:
    """
    Class kéo dữ liệu từ SQL View, thực hiện Sanity Checks, 
    cắt tập Train/Test theo tỷ lệ 80/20 có Stratify, và lưu Checkpoint.
    """

    def __init__(self):
        self.db = NeonDBManager()
        self.base_dir = Path(__file__).resolve().parent
        
        # Khởi tạo logger
        self.log = get_pipeline_logger(self.__class__.__name__)
        self.log.debug("Initializing DataIngestion class...")

    def process_and_checkpoint(self, view_name:str, target_col:str = 'loan_status'):
        """
        Thực thi chuỗi: Fetch -> Sanity Check -> Split -> Checkpoint
        """
        self.log.info(f"Fetching data from View '{view_name}'...")
        query = f"SELECT * FROM {view_name};"
        df = self.db.fetch_data(query)

        if df.empty:
            self.log.error("Data is empty, aborting process.")
            return False
        
        initial_rows = len(df)

        # 2. SANITY CHECKS (Kiểm tra logic nghiệp vụ)
        self.log.info("Performing Sanity Checks...")

        # Loại bỏ dòng trùng lặp có thể sinh ra do JOIN SQL
        df = df.drop_duplicates()

        # Loại bỏ thâm niên làm việc sai logic (Thâm niên > Tuổi đời)
        df = df[df['person_emp_length'] <= df['person_age']]

        cleaned_rows = len(df)
        self.log.info(f"Sanity Checks completed. Filtered out {initial_rows - cleaned_rows} noisy rows.")

        # 3. EARLY SPLITTING (Phân tách từ gốc)
        self.log.info("Splitting data (80/20) with Stratify...")

        if target_col not in df.columns:
            self.log.error(f"ERROR: Target column '{target_col}' not found for Stratify.")
            return False
        
        train_df, test_df = train_test_split(df, test_size=0.2, train_size=0.8, random_state=42, stratify=df[target_col])

        # 4. LƯU CHECKPOINT
        train_path = TRAIN_DATA_FILE
        test_path = TEST_DATA_FILE
        check_and_create_directories(auto_create=True)
        train_df.to_csv(train_path, index=False)
        test_df.to_csv(test_path, index=False)

        self.log.info("Successfully saved Checkpoints to 'data/' directory:")
        self.log.info(f"   ➔ Train set: {len(train_df)} rows ({train_path.name})")
        self.log.info(f"   ➔ Test set: {len(test_df)} rows ({test_path.name}) - LOCKED!")
        
        return True

# === Cách sử dụng ===
if __name__ == "__main__":
    ingestor = DataIngestion()
    # Giả sử View bạn tạo trên SQL tên là 'vw_cleaning_data'
    ingestor.process_and_checkpoint(view_name="vw_cleaning_data")