from pathlib import Path
from sklearn.tree import DecisionTreeClassifier
from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd
import numpy as np
from typing import List
import sys

# ==========================================
# THÊM PROJECT ROOT VÀO SYS.PATH
# ==========================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# Import logger
from src.utils.logger import get_pipeline_logger

class DecisionTreeBinner(BaseEstimator, TransformerMixin):
    """
    Module Rời rạc hóa (Decision Tree) và Mã hóa Rủi ro (WoE) cho Biến số Liên tục.
    Tuân thủ tuyệt đối quy tắc chống Leakage: Fit trên Train, Transform trên Test.
    """
    def __init__(self, cols: List[str], max_depth: int = 3, epsilon: float = 0.5):
        # 1. Khởi tạo thuộc tính
        self.cols = cols
        self.max_depth = max_depth
        self.epsilon = epsilon
        self.tree_ = {}              # Lưu trữ mô hình Decision Tree cho từng biến
        self.woe_dicts_ = {}         # Lưu trữ từ điển ánh xạ {leaf_id: woe_value}
        self.global_woe_ = 0.0       # Mức WoE toàn cục cho cơ chế Cold Start
        
        # 2. Khởi tạo Logger
        self.log = get_pipeline_logger(self.__class__.__name__)
        self.log.debug(f"Initializing {self.__class__.__name__} for columns: {self.cols}")

    def fit(self, X: pd.DataFrame, y: pd.Series) -> 'DecisionTreeBinner':
        # Tính toán Global WoE để phòng hờ trường hợp Cold Start
        TotalGood = (y == 0).sum()
        TotalBad = (y == 1).sum() 

        # Áp dụng Laplace smoothing cho Global WoE
        global_good_pct = (TotalGood + self.epsilon) / (TotalGood + self.epsilon * 2)
        global_bad_pct = (TotalBad + self.epsilon) / (TotalBad + self.epsilon * 2)
        self.global_woe_ = np.log(global_good_pct / global_bad_pct)

        for col in self.cols:
            # 1. Rời rạc hóa tự động bằng Decision Tree
            tree = DecisionTreeClassifier(max_depth=self.max_depth, random_state=42)
            tree.fit(X[[col]], y)  # Đã fix lỗi typo .fix() thành .fit() và truyền 2D array
            self.tree_[col] = tree

            # Khai thác các điểm cắt (splits) để logging
            threshold = tree.tree_.threshold[tree.tree_.feature != -2]  # Đã fix lỗi features (số nhiều)
            self.log.info(f"[{col}] Decision Tree found optimal split thresholds: {np.round(threshold, 2)}")

            # Lấy danh sách các lá (bins) do cây phân chia
            leaves = tree.apply(X[[col]]) 
            woe_dict = {}

            # 2. Mã hóa WoE cho từng lá (nhóm)
            for leaf in np.unique(leaves):
                mask = (leaves == leaf)
                good_i = (y[mask] == 0).sum()
                bad_i = (y[mask] == 1).sum()

                # Cảnh báo và xử lý Zero-frequency
                if good_i == 0 or bad_i == 0:
                    self.log.warning(f"[{col}] - Bin [{leaf}] frequency is 0. Laplace Smoothing activated (epsilon={self.epsilon}).")

                # Áp dụng công thức WoE với Laplace Smoothing
                good_pct = (good_i + self.epsilon) / (TotalGood + self.epsilon)
                bad_pct = (bad_i + self.epsilon) / (TotalBad + self.epsilon)

                woe_dict[leaf] = np.log(good_pct / bad_pct)

            self.woe_dicts_[col] = woe_dict
            self.log.info(f"[{col}] WoE mapping dictionary computed successfully.")
        
        return self
    
    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Áp dụng ngưỡng cắt và bảng từ điển lên dữ liệu. 
        Tuyệt đối không học lại.
        """
        X_out = X.copy()
        original_col_count = X_out.shape[1]

        for col in self.cols:
            # Sử dụng .apply() của tree đã học để phân loại dữ liệu mới vào các lá (bins)
            leaves = self.tree_[col].apply(X_out[[col]])

            # Map lá sang giá trị WoE, nếu lá lạ (Cold Start) thì dùng Global WoE
            X_out[col] = pd.Series(leaves, index=X_out.index).map(self.woe_dicts_[col]).fillna(self.global_woe_)

        # 3. Chốt chặn QA tự động (Assertions)
        assert X_out.isna().sum().sum() == 0, "PIPELINE ERROR: Unexpected NaN values generated during transform!"
        assert X_out.shape[1] == original_col_count, "PIPELINE ERROR: Number of columns changed after transform!"
        self.log.info("Transform completed successfully. Data is safe, all QA assertions passed.")
        return X_out
    
    