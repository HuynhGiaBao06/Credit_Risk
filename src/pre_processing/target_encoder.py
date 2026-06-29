import pandas as pd
import numpy as np
import sys
from typing import List
from pathlib import Path
from sklearn.base import BaseEstimator,TransformerMixin

# ==========================================
# THÊM PROJECT ROOT VÀO SYS.PATH
# ==========================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

#Import Logger
from src.utils.logger import get_pipeline_logger

class TargetEncoder(BaseEstimator,TransformerMixin):
    """
    Module Risk Target Encoding dành cho biến phân loại (Categorical).
    Thiết kế dưới dạng "Pure Encoder" (Không chứa K-Fold nội bộ), 
    sử dụng M-estimate Smoothing để chống nhiễu từ các danh mục hiếm.
    """
    def __init__(self, cols:List[str], m:int = 100):
        # 1. Khởi tạo tham số và thuộc tính
        self.cols = cols
        self.m = m
        self.lookup_table_ = {}
        self.mu_global_ = 0.0 

        # 2. Khởi tạo Logger
        self.log = get_pipeline_logger(self.__class__.__name__)
        self.log.debug(f"Initializing {self.__class__.__name__} for columns: {self.cols} with smoothing m={self.m}")

    def fit(self, X:pd.DataFrame, y:pd.Series) -> 'TargetEncoder':
        """
        Học (Fit) bảng tra cứu xác suất rủi ro trên 100% dữ liệu đầu vào.
        Tính toán mu_global và áp dụng công thức M-estimate smoothing.
        """
        self.log.info("Starting .fit() process to build Risk Lookup Table.")

        # Tính tỷ lệ nợ xấu trung bình toàn cục (mu_global)

        self.mu_global_ = y.mean()
        self.log.info(f"Global mean risk (mu_global) calculated: {self.mu_global_:.6f}")

        for col in self.cols:
            # Gom nhóm đếm số lượng (N_group) và số ca vỡ nợ (Sum_Y)
            stats = y.groupby(X[col]).agg(N_group = 'count', Sum_Y = 'sum')

            N_group = stats['N_group']
            Sum_Y = stats['Sum_Y']

            # Tính toán trọng số alpha
            alpha_i = N_group / (N_group + self.m)

            # Tính Risk Probability bằng M-estimate Smoothing
            E_i = (alpha_i * (Sum_Y / N_group)) + ((1 - alpha_i) * self.mu_global_)

            # Lưu vào từ điển tĩnh (Lookup Table)
            self.lookup_table_[col] = E_i.to_dict()
            self.log.info(f"Successfully built lookup table for column: {col}")

        return self
    
    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Ánh xạ (Map) xác suất rủi ro từ Bảng tra cứu sang tập dữ liệu.
        Xử lý Cold Start bằng mu_global và tích hợp Assertions bảo vệ.
        """
        self.log.info(f"Starting .transform() process - Input shape: {X.shape}")

        X_out = X.copy()
        original_col_count_ = X_out.shape[1]

        for col in self.cols:
            # 1. Thực hiện ánh xạ (Mapping) từ từ điển đã học
            X_out[col] = X_out[col].map(self.lookup_table_[col])

            # 2. Xử lý Cold Start (Danh mục lạ chưa từng có trong Train)
            missing_mark = X_out[col].isna()
            missing_count = missing_mark.sum()

            if missing_count > 0:
                self.log.warning(f"[{col}] Cold Start detected: {missing_count} unknown categories. Imputing with mu_global.")
                X_out[col] = X_out[col].fillna(self.mu_global_)

            # Ép kiểu float để tương thích hoàn toàn với thuật toán downstream
            X_out[col] = X_out[col].astype(float)

        # 3. Chốt chặn Kiểm định tự động (QA Assertions)
        # Khẳng định không có giá trị rỗng (NaN) nào bị bỏ sót

        assert X_out.isna().sum().sum() == 0, \
            "🚨 PIPELINE ERROR: NaN values generated during Target Encoding mapping!"
        
        # Khẳng định kích thước cột đầu ra khớp với đầu vào
        assert X_out.shape[1] == original_col_count_, \
            f"🚨 PIPELINE ERROR: Shape mismatch! Expected {original_col_count_} columns, but got {X_out.shape[1]}."

        self.log.info(f"Successfully completed .transform()! Data safe, output shape: {X_out.shape}")
        
        return X_out
    