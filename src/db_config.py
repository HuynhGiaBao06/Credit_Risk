import os
import time
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine,text
from sqlalchemy.exc import SQLAlchemyError,OperationalError
from dotenv import load_dotenv
class NeonDBManager:
    """
    Class quản lý kết nối 2 chiều giữa Python và Neon PostgreSQL.
    Tích hợp pathlib để định vị chính xác file .env trong dự án.
    """

    def __init__(self):
        # =================================================================
        # 1. SỬ DỤNG PATHLIB ĐỂ TÌM ĐƯỜNG DẪN TUYỆT ĐỐI CỦA FILE .ENV
        # =================================================================

        try:
            # Nếu chạy bằng file .py thông thường
            base_dir = Path(__file__).resolve().parent
            # ĐÃ SỬA LỖI: Thêm .parent để lùi từ src/ ra ngoài thư mục gốc
            env_path = base_dir.parent / ".env" 
            
        except NameError:
            # Nếu chạy bằng Jupyter Notebook
            current_dir = Path.cwd()
            
            # Kiểm tra xem file .env có ở ngay thư mục hiện tại không
            if (current_dir / ".env").exists():
                env_path = current_dir / ".env"
            else:
                env_path = current_dir.parent / ".env"
        
        # Nạp biến môi trường từ đường dẫn vừa tìm được
        load_dotenv(dotenv_path=env_path)

        self.db_url = os.getenv("DATABASE_URL")
        if not self.db_url:
            raise ValueError(f"🚨 NGHIÊM TRỌNG: Không tìm thấy biến DATABASE_URL!\n")
        
        try:
            self.engine = create_engine(
                self.db_url,
                pool_pre_ping=True,
                pool_recycle=300,
                # THÊM connect_timeout để cho phép Neon có thêm thời gian thức dậy
                connect_args={'sslmode': 'require', 'connect_timeout': 10} 
            )
        except Exception as e:
            raise ConnectionError(f"🚨 LỖI KHỞI TẠO ENGINE: {e}")

    def test_connection(self, max_retries=3, delay=3):
        """
        Kiểm tra kết nối trước khi làm việc nặng.
        ĐÃ XỬ LÝ COLD START: Sẽ thử lại (retry) nếu database đang ngủ.
        """
        for attempt in range(max_retries):
            try:
                with self.engine.connect() as connection:
                    connection.execute(text("SELECT 1"))
                print("✅ Kết nối PostgreSQL thành công và đang hoạt động!")
                return True
            except OperationalError as e:
                print(f"⚠️ Lần thử {attempt + 1}/{max_retries} thất bại. Có thể do Neon Serverless đang Cold Start.")
                if attempt < max_retries - 1:
                    print(f"⏳ Đang chờ {delay} giây để thử lại...")
                    time.sleep(delay)  # Dừng lại 3 giây chờ database thức dậy
                else:
                    print(f"❌ LỖI KẾT NỐI: Đã thử {max_retries} lần nhưng không thành công.\nChi tiết: {e}")
                    return False
            except Exception as e:
                print(f"❌ LỖI KHÔNG XÁC ĐỊNH: {e}")
                return False
        
    def fetch_data(self,query:str) -> pd.DataFrame:
        """Kéo dữ liệu từ SQL về Pandas DataFrame"""
        try:
            print("⏳ Đang tải dữ liệu...")
            df = pd.read_sql(query, con=self.engine)
            print(f"✅ Tải thành công {len(df)} dòng dữ liệu.")
            return df
        except SQLAlchemyError as e:
            print(f"❌ LỖI TRUY VẤN SQL:\nChi tiết: {e}")
            return pd.DataFrame() 
        except Exception as e:
            print(f"❌ LỖI ĐỌC DỮ LIỆU: {e}")
            return pd.DataFrame()
        
    def push_data(self, df: pd.DataFrame, table_name: str, if_exists: str = 'append'):
        """Đẩy dữ liệu từ Pandas lên SQL"""
        if df.empty:
            print("⚠️ CẢNH BÁO: DataFrame rỗng, không có dữ liệu để ghi lên SQL.")
            return False

        try:
            print(f"⏳ Đang đẩy {len(df)} dòng lên bảng '{table_name}'...")
            df.to_sql(
                name=table_name,
                con=self.engine,
                if_exists=if_exists,
                index=False,
                chunksize=1000 
            )
            print(f"✅ Ghi dữ liệu thành công lên bảng '{table_name}'.")
            return True
        except ValueError as e:
            print(f"❌ LỖI CẤU TRÚC: Cấu trúc DataFrame không khớp với bảng.\nChi tiết: {e}")
            return False
        except SQLAlchemyError as e:
            print(f"❌ LỖI THỰC THI DB:\nChi tiết: {e}")
            return False
