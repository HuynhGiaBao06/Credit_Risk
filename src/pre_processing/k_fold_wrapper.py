"""
K-Fold: Tập Train được chia thành K=5. Giá trị mã hóa của một dòng chỉ được tính từ tỷ lệ 
rủi ro của 4 fold còn lại, chặn đứng rò rỉ nhãn cục bộ.
Smoothing: Cứu vớt các nhóm thiểu số có dữ liệu mỏng bằng cách kéo tỷ lệ 
vỡ nợ của chúng về gần tỷ lệ trung bình của toàn bộ dữ liệu.
"""

import pandas as pd
import numpy as np
import sys
from typing import List
from pathlib import Path
from sklearn.base import BaseEstimator, TransformerMixin, clone
from sklearn.model_selection import StratifiedKFold

# ==========================================
# THÊM PROJECT ROOT VÀO SYS.PATH
# ==========================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# Import logger
from src.utils.logger import get_pipeline_logger

class KFoldWrapper(BaseEstimator, TransformerMixin):
    """
    Lớp vỏ bọc (Wrapper) điều phối K-Fold cho các module Mã hóa Đặc trưng.
    Tuyệt đối không chứa logic toán học. Chịu trách nhiệm tạo dữ liệu Out-of-Fold (OOF) 
    và bảo vệ tập Test khỏi rò rỉ dữ liệu.
    """
    def __init__(self, encoder: BaseEstimator, n_splits: int = 5, shuffle: bool = True, random_state: int = 42):
        # 1. Giao diện Giao tiếp: Chỉ gán tham số, tuyệt đối không có logic
        self.encoder = encoder
        self.n_splits = n_splits
        self.shuffle = shuffle
        self.random_state = random_state

        # Khởi tạo Logger
        self.log = get_pipeline_logger(self.__class__.__name__)
        self.log.debug(f"Initialized KFoldWrapper with n_splits={self.n_splits}")
    
    def fit(self, X: pd.DataFrame, y: pd.Series) -> 'KFoldWrapper':
        """
        Dành cho luồng Production / Tập Test: Học trên 100% dữ liệu gốc.
        Tuyệt đối không chạy K-Fold ở đây.
        """
        self.log.info("Executing .fit() - Training base encoder on 100% of data.")
        self.encoder.fit(X, y)
        return self
    
    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Dành cho luồng Production / Tập Test: Ánh xạ dữ liệu mới.
        Không nhận biến y, khóa chặt hệ thống.
        """
        self.log.info(f"Executing .transform() - Input shape: {X.shape}")
        return self.encoder.transform(X)
    
    def fit_transform(self, X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
        """
        BẮT BUỘC GHI ĐÈ: Dành riêng cho tập Train.
        Sử dụng StratifiedKFold để sinh dữ liệu OOF (Out-of-Fold), chặn rò rỉ Target.
        """
        self.log.info(f"Starting .fit_transform() - Initiating {self.n_splits}-Fold OOF generation.")

        # Tạo bản sao vật lý để lưu trữ dữ liệu OOF nhằm giữ nguyên cấu trúc index
        X_oof = X.copy()

        skf = StratifiedKFold(n_splits=self.n_splits, shuffle=self.shuffle, random_state=self.random_state)
        
        for fold, (train_idx, val_idx) in enumerate(skf.split(X, y)):
            self.log.debug(f"Processing Fold {fold + 1}/{self.n_splits}")

            # Xung đột 1 (State Mutation): Tạo bản sao sạch của encoder để tránh mang ký ức từ fold trước
            cloned_encoder = clone(self.encoder)

            # Xung đột 2 (Pandas Index Mismatch): Cắt dữ liệu an toàn thông qua vị trí vật lý .iloc
            X_train_fold, y_train_fold = X.iloc[train_idx], y.iloc[train_idx]
            X_val_fold = X.iloc[val_idx]

            # Huấn luyện trên tập Train của fold hiện tại
            cloned_encoder.fit(X_train_fold, y_train_fold)

            # Biến đổi (map) trên tập Validation (OOF) của fold hiện tại
            X_val_transformed = cloned_encoder.transform(X_val_fold)

            # Gán kết quả OOF trả lại vào đúng vị trí vật lý ban đầu 
            # (Sử dụng .values để ép kiểu Numpy, triệt tiêu hoàn toàn lỗi lệch Index của Pandas)
            X_oof.iloc[val_idx, :] = X_val_transformed.values

        self.log.info("Completed OOF generation. Locking Lookup Table by fitting on full dataset.")

        # 3. KHÓA BẢNG TRA CỨU: Huấn luyện lại encoder gốc trên 100% dữ liệu Train 
        # để lưu trữ các tham số chuẩn bị sẵn sàng cho tập Test/Production sau này.
        self.encoder.fit(X, y)
        
        return X_oof
        