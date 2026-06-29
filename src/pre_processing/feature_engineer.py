"""Feature engineering"""
from sklearn.base import BaseEstimator, TransformerMixin
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


class FeatureCreator(BaseEstimator, TransformerMixin):
    """
    Module Kỹ thuật Đặc trưng (Feature Engineering) tạo các biến phái sinh tài chính.
    Được thiết kế theo chuẩn stateless (không lưu trữ trạng thái) do dữ liệu 
    đã được làm sạch 100% từ tầng SQL Data Warehouse.
    """
    def __init__(self):
         # 1. Khởi tạo Logger
        self.log = get_pipeline_logger(self.__class__.__name__)
        self.log.debug(f"Initializing {self.__class__.__name__} - Stateless mode.")
        
    def fit(self, X: pd.DataFrame, y: pd.Series = None) -> 'FeatureCreator':
        """
        Hàm Fit thuần túy. 
        Không có giá trị thống kê (Median/Mode) nào cần học từ tập Train do DB đã xử lý.
        """
        self.log.debug("Skipping .fit() process as module is stateless.")
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Thực thi tạo 3 biến phái sinh tài chính và xóa cột gốc.
        Tích hợp chốt chặn QA Pipeline tự động.
        """
        self.log.info(f"Starting .transform() process - Input shape: {X.shape}")

        # 1. Thao tác trên bản sao để bảo vệ dữ liệu gốc
        X_out = X.copy()
        origin_columns_count = X_out.shape[1]

        # 2. Tạo biến phái sinh (Feature Creation)
        # Độ chín muồi tài chính
        X_out['age_at_first_credit'] = X_out['person_age'] - X_out['cb_person_cred_hist_length']

        # Xóa vĩnh viễn cột gốc ngay sau khi tính để chặn đa cộng tuyến
        X_out = X_out.drop(columns=['cb_person_cred_hist_length'])
        self.log.info("Dropped original column 'cb_person_cred_hist_length' to prevent perfect multicollinearity.")

        # Áp lực lãi vay thực tế
        X_out['Estimated_Annual_Interest'] = X_out['loan_amnt'] * (X_out['loan_int_rate'] / 100)

        # Năng lực tạo dòng tiền
        X_out['Income_per_Employment_Year'] = X_out['person_income'] / X_out['person_emp_length']

        # 3. Chốt chặn Kiểm định tự động (QA Assertions)
        # ==========================================
        # ĐOẠN CODE DEBUG TẠM THỜI (THÊM VÀO ĐÂY)
        # ==========================================
        nan_counts = X_out.isna().sum()
        cols_with_nans = nan_counts[nan_counts > 0]
        if not cols_with_nans.empty:
            self.log.error(f"🚨 PHÁT HIỆN CỘT CÓ CHỨA NaN:\n{cols_with_nans}")
            self.log.error(f"Dữ liệu gốc trước khi tính toán có NaN không? {X.isna().sum()[X.isna().sum() > 0]}")
        # ==========================================
        # Cam kết không sinh ra bất kỳ giá trị NaN nào do ngoại lệ tính toán
        assert X_out.isna().sum().sum() == 0, \
            "🚨 PIPELINE ERROR: Pandas calculation unexpectedly generated NaN values!"

        # Kiểm tra kích thước cột đi ra phải tăng đúng 2 cột (+3 biến mới, -1 biến gốc)
        expected_columns_count = origin_columns_count + 2
        assert X_out.shape[1] == expected_columns_count, \
            f"🚨 PIPELINE ERROR: Shape mismatch! Expected {expected_columns_count} columns, but got {X_out.shape[1]}."

        self.log.info(f"Successfully completed .transform()! All QA assertions passed. Output shape: {X_out.shape}")
        
        return X_out