import pandas as pd
from pathlib import Path
import sys
# ==========================================
#THÊM PROJECT ROOT VÀO SYS.PATH
# ==========================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.db_config import NeonDBManager
from src.path import DATA_RAW_FILE, check_and_create_directories

class DataUploader:
    """
    Class chuyên trách việc đọc dữ liệu thô từ thư mục 'data/' cục bộ
    và đẩy lên hệ quản trị cơ sở dữ liệu Neon PostgreSQL.
    """

    def __init__(self):
        self.db = NeonDBManager()

    # Đã bỏ tham số filename vì chúng ta dùng trực tiếp DATA_RAW_FILE
    def upload_raw_data(self, table_name: str, if_exists: str = "replace"):
        """
        Đọc file CSV/Excel và ghi lên bảng SQL.
        
        Args:
            table_name (str): Tên bảng sẽ được tạo hoặc ghi đè trên PostgreSQL.
            if_exists (str): 'replace' (ghi đè bảng cũ) hoặc 'append' (thêm dòng).
        """
        
        # Trỏ chính xác đến file dữ liệu nhờ biến DATA_RAW_FILE từ path.py
        file_path = DATA_RAW_FILE

        if not file_path.exists():
            print(f"❌ LỖI: Không tìm thấy file dữ liệu tại {file_path}")
            print("💡 Gợi ý: Hãy kiểm tra xem file đã được copy vào thư mục 'data/' chưa.")
            return False
        
        print(f"⏳ Đang đọc file dữ liệu từ: {file_path}...")

        try:
            # Hỗ trợ đọc cả định dạng CSV và Excel
            if file_path.suffix == ".csv":
                df = pd.read_csv(file_path)

            elif file_path.suffix in ['.xls', '.xlsx']:
                df = pd.read_excel(file_path) 

            else:
                print("❌ LỖI: Định dạng file không được hỗ trợ. Chỉ dùng .csv hoặc .xlsx")
                return False
            
            print(f"✅ Đã tải {len(df)} dòng dữ liệu vào bộ nhớ Pandas.")

        except Exception as e:
            print(f"❌ LỖI ĐỌC FILE: Quá trình đọc bộ nhớ cục bộ thất bại.\nChi tiết: {e}")
            return False
        
        # Đẩy dữ liệu lên cơ sở dữ liệu
        print(f"🚀 Bắt đầu đẩy dữ liệu lên bảng '{table_name}' trên DB...")

        success = self.db.push_data(df=df, table_name=table_name, if_exists=if_exists)

        if success:
            print(f"🎉 HOÀN TẤT: Dữ liệu đã an tọa trên DB. Bảng: '{table_name}'.")
        else:
            print("⚠️ THẤT BẠI: Không thể đẩy dữ liệu lên DB. Vui lòng xem log ở trên.")

        return success
    
# === Cách sử dụng (Thực thi độc lập) ===
if __name__ == "__main__":
    uploader = DataUploader()
    
    TARGET_TABLE = "db_credit_risk"
    
    uploader.upload_raw_data(
        table_name=TARGET_TABLE,
        if_exists="replace" 
    )