import pandas as pd
import numpy as np
import sys
from pathlib import Path
from sklearn.base import BaseEstimator, TransformerMixin

# ==========================================
# THÊM PROJECT ROOT VÀO SYS.PATH
# ==========================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# Import logger
from src.utils.logger import get_pipeline_logger

class AgeBinner(BaseEstimator, TransformerMixin):
    """
    Rời rạc hóa (binning) biến độ tuổi person_age thành các khoảng cố định
    7 năm/khoảng (ví dụ: 20-26, 27-33). 
    Giúp các mô hình thuật toán tuyến tính bắt được tính chu kỳ rủi ro theo từng nhóm tuổi vay vốn.
    """
    
    def __init__(self, col_name: str = "person_age", bin_width: int = 7, age_cap: int = 62):
        # 1. Khởi tạo thuộc tính
        self.col_name = col_name
        self.bin_width = bin_width
        self.age_cap = age_cap
        self.bins_ = None
        self.labels_ = None
        self.train_features_shape_ = None
        
        # 2. Khởi tạo Logger
        self.log = get_pipeline_logger(self.__class__.__name__)
        self.log.debug(f"Initializing AgeBinner class for column: {self.col_name}")
        
    def fit(self, X: pd.DataFrame, y=None):
        """
        Học (Fit) các biên độ tuổi từ tập Train để thiết lập quy tắc cắt cố định.
        Tuyệt đối không áp dụng hàm này lên tập Test.
        """
        self.log.info("Starting .fit() process on Train dataset.")

        # Lưu lại số lượng đặc trưng gốc để kiểm định Shape sau này
        self.train_features_shape_ = X.shape[1]

        min_age = int(X[self.col_name].min())
        
        # 1. Tạo các mốc cắt cốt lõi, nhưng chỉ chạy đến trước mốc 62
        core_bins = list(range(min_age, self.age_cap, self.bin_width))

        # 2. Đóng chốt mốc cuối cùng chắc chắn là 62
        if not core_bins or core_bins[-1] != self.age_cap:
            core_bins.append(self.age_cap)
            
        # ==========================================
        # Mở rộng biên (-inf và inf) để bắt các ngoại lệ trên tập Test
        self.bins_ = [-np.inf] + core_bins + [np.inf]

        # Tạo nhãn (Labels)
        labels = []
        for i in range(len(self.bins_) - 1):
            if i == 0:
                labels.append(f"<{core_bins[0]}")
            elif i == len(self.bins_) - 2:
                labels.append(f">={core_bins[-1]}")
            else:
                # Trừ 1 để lấy khoảng đóng chuẩn [x, y)  (vd: 20 đến 26)
                labels.append(f"{self.bins_[i]}-{self.bins_[i+1] - 1}")

        self.labels_ = labels
        self.log.info(f"Successfully learned binning logic. Total bins generated: {len(self.labels_)}")
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Áp dụng (Transform) quy tắc đã học lên dữ liệu đầu vào.
        Tích hợp 2 chốt chặn Assertions tự động để bảo vệ Pipeline.
        """
        self.log.info(f"Starting .transform() process - Input shape: {X.shape}")

        # Khuyến nghị luôn thao tác trên bản sao để không làm biến đổi dữ liệu gốc ngầm định
        X_transformed = X.copy()
        
        # Áp dụng Data Binning bằng thư viện pandas
        X_transformed[self.col_name] = pd.cut(
            X_transformed[self.col_name],
            bins=self.bins_,
            labels=self.labels_,
            right=False  #Bao gồm cạnh trái, không bao gồm cạnh phải [x, y) 
        )

        # =================================================================
        # CHỐT CHẶN KIỂM ĐỊNH TỰ ĐỘNG (POST-PROCESSING ASSERTIONS)
        # =================================================================

        # 1. Check Missing Values: Đảm bảo riêng cột được binning không bị lỗi giá trị trống [cite: 131]
        assert X_transformed[self.col_name].isna().sum() == 0, \
            "🚨 ASSERTION ERROR: The Binning process generated NaN values. Please verify the bin boundaries!"
            
        # 2. Check Data Leakage Shape: Đảm bảo số lượng cột trước và sau biến đổi khớp nhau [cite: 132]
        assert X_transformed.shape[1] == self.train_features_shape_, \
            f"🚨 ASSERTION ERROR: Feature shape mismatch! Original: {self.train_features_shape_}, Current: {X_transformed.shape[1]}"
            
        self.log.info(f"Successfully completed .transform()! Data passed all assertions. Output shape: {X_transformed.shape}")
        return X_transformed
    
