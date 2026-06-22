#Hàm gọi SQL View trả ra Pandas DataFrame
import pandas as pd
from src.db_config import NeonDBManager
from src.path import TRAIN_DATA_FILE,TEST_DATA_FILE,check_and_create_directories
from pathlib import Path
from sklearn.model_selection import train_test_split

class DataIngestion:
    """
    Class kéo dữ liệu từ SQL View, thực hiện Sanity Checks, 
    cắt tập Train/Test theo tỷ lệ 80/20 có Stratify, và lưu Checkpoint.
    """

    def __init__(self):
        self.db = NeonDBManager()

        self.base_dir = Path(__file__).resolve().parent

    def process_and_checkpoint(self, view_name:str,target_col:str = 'loan_status'):
        """
        Thực thi chuỗi: Fetch -> Sanity Check -> Split -> Checkpoint
        """
        print(f"📥 Đang kéo dữ liệu từ View '{view_name}'...")
        query = f"SELECT * FROM {view_name};"
        df = self.db.fetch_data(query)

        if df.empty:
            print("❌ Dữ liệu trống, dừng quy trình.")
            return False
        
        initial_rows = len(df)

        # 2. SANITY CHECKS (Kiểm tra logic nghiệp vụ)
        print("🧹 Đang thực hiện Sanity Checks...")

        # Loại bỏ dòng trùng lặp có thể sinh ra do JOIN SQL
        df = df.drop_duplicates()

        # Loại bỏ thâm niên làm việc sai logic (Thâm niên > Tuổi đời)
        df = df[df['person_emp_length'] <= df['person_age']]

        cleaned_rows = len(df)
        print(f"✅ Sanity Checks hoàn tất. Đã lọc bỏ {initial_rows - cleaned_rows} dòng nhiễu.")

        # 3. EARLY SPLITTING (Phân tách từ gốc)
        print("✂️ Đang phân tách dữ liệu (80/20) với Stratify...")

        if target_col not in df.columns:
            print(f"❌ LỖI: Không tìm thấy cột mục tiêu '{target_col}' để Stratify.")
            return False
        
        train_df,test_df = train_test_split(df,test_size = 0.2, train_size = 0.8 ,random_state = 42,stratify = df[target_col])

        # 4. LƯU CHECKPOINT
        train_path = TRAIN_DATA_FILE
        test_path = TEST_DATA_FILE
        check_and_create_directories(auto_create=True)
        train_df.to_csv(train_path, index = False)
        test_df.to_csv(test_path,index=False)

        print(f"✅ Đã lưu Checkpoint thành công vào thư mục 'data/':")
        print(f"   ➔ Tập Train: {len(train_df)} dòng ({train_path.name})")
        print(f"   ➔ Tập Test: {len(test_df)} dòng ({test_path.name}) - ĐÃ BỊ KHÓA LẠI!")
        
        return True

        # === Cách sử dụng ===
if __name__ == "__main__":
    ingestor = DataIngestion()
    # Giả sử View bạn tạo trên SQL tên là 'vw_credit_risk_raw'
    ingestor.process_and_checkpoint(view_name="vw_credit_risk_raw")