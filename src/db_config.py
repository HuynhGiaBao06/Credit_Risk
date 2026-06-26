import os
import time
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from dotenv import load_dotenv
import sys
# ==========================================
#THÊM PROJECT ROOT VÀO SYS.PATH
# ==========================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# Import hàm cấu hình logger từ dự án của bạn
from src.utils.logger import get_pipeline_logger

class NeonDBManager:
    """
    Class quản lý kết nối 2 chiều giữa Python và Neon PostgreSQL.
    Tích hợp pathlib để định vị chính xác file .env trong dự án.
    """

    def __init__(self):
        # Khởi tạo logger ngay khi gọi class
        self.log = get_pipeline_logger(self.__class__.__name__)
        self.log.debug("Initializing NeonDBManager...")

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
            # Log mức CRITICAL trước khi quăng lỗi làm sập chương trình
            self.log.critical("CRITICAL: DATABASE_URL environment variable not found!")
            raise ValueError(f"🚨 NGHIÊM TRỌNG: Không tìm thấy biến DATABASE_URL!\n")
        
        try:
            self.engine = create_engine(
                self.db_url,
                pool_pre_ping=True,
                pool_recycle=300,
                # THÊM connect_timeout để cho phép Neon có thêm thời gian thức dậy
                connect_args={'sslmode': 'require', 'connect_timeout': 10} 
            )
            self.log.debug("SQLAlchemy engine created successfully.")
        except Exception as e:
            self.log.critical(f"ENGINE INITIALIZATION ERROR: {e}", exc_info=True)
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
                self.log.info("PostgreSQL connection successful and active!")
                return True
            except OperationalError as e:
                self.log.warning(f"Attempt {attempt + 1}/{max_retries} failed. Possible Neon Serverless Cold Start.")
                if attempt < max_retries - 1:
                    self.log.info(f"Waiting {delay} seconds before retrying...")
                    time.sleep(delay)  # Dừng lại 3 giây chờ database thức dậy
                else:
                    self.log.error(f"CONNECTION ERROR: Failed after {max_retries} attempts. Details: {e}", exc_info=True)
                    return False
            except Exception as e:
                self.log.error(f"UNKNOWN ERROR: {e}", exc_info=True)
                return False
        
    def fetch_data(self, query: str) -> pd.DataFrame:
        """Kéo dữ liệu từ SQL về Pandas DataFrame"""
        try:
            self.log.info("Loading data from database...")
            df = pd.read_sql(query, con=self.engine)
            self.log.info(f"Successfully loaded {len(df)} rows of data.")
            return df
        except SQLAlchemyError as e:
            self.log.error(f"SQL QUERY ERROR. Details: {e}", exc_info=True)
            return pd.DataFrame() 
        except Exception as e:
            self.log.error(f"DATA READING ERROR: {e}", exc_info=True)
            return pd.DataFrame()
        
    def push_data(self, df: pd.DataFrame, table_name: str, if_exists: str = 'append'):
        """Đẩy dữ liệu từ Pandas lên SQL"""
        if df.empty:
            self.log.warning("WARNING: DataFrame is empty, no data to push to SQL.")
            return False

        try:
            self.log.info(f"Pushing {len(df)} rows to table '{table_name}'...")
            df.to_sql(
                name=table_name,
                con=self.engine,
                if_exists=if_exists,
                index=False,
                chunksize=1000 
            )
            self.log.info(f"Successfully pushed data to table '{table_name}'.")
            return True
        except ValueError as e:
            self.log.error(f"STRUCTURE ERROR: DataFrame structure does not match the table '{table_name}'. Details: {e}", exc_info=True)
            return False
        except SQLAlchemyError as e:
            self.log.error(f"DB EXECUTION ERROR. Details: {e}", exc_info=True)
            return False