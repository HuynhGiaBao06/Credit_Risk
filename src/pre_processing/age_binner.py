import pandas as pd
import numpy as np
import sys
from pathlib import Path
from typing import List
from sklearn.base import BaseEstimator, TransformerMixin

# ==========================================
# THÊM PROJECT ROOT VÀO SYS.PATH
# ==========================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# Import logger
from src.utils.logger import get_pipeline_logger

class AgeBinningEncoder(BaseEstimator, TransformerMixin):
    """
    Module Rời rạc hóa (Fixed Binning) và Mã hóa WoE cho biến độ tuổi (hoặc tương đương).
    Giữ nguyên logic chia biên an toàn (-inf, inf) và tích hợp kiến trúc List[str], 2D Array.
    """
    
    def __init__(self, cols: List[str], bin_width: int = 7, age_cap: int = 62, epsilon: float = 0.5):
        # 1. Khởi tạo thuộc tính
        self.cols = cols
        self.bin_width = bin_width
        self.age_cap = age_cap
        self.epsilon = epsilon
        
        # Lưu trữ cấu hình dạng dictionary để hỗ trợ nhiều cột nếu cần
        self.bins_ = {}           
        self.labels_ = {}         
        self.woe_dicts_ = {}      # Lưu trữ từ điển ánh xạ {bin_label: woe_value}
        self.global_woe_ = 0.0    # Mức WoE toàn cục cho cơ chế Cold Start
        
        # 2. Khởi tạo Logger
        self.log = get_pipeline_logger(self.__class__.__name__)
        self.log.debug(f"Initializing {self.__class__.__name__} for columns: {self.cols}")
        
    def fit(self, X: pd.DataFrame, y: pd.Series) -> 'AgeBinningEncoder':
        """
        Học (Fit) các biên độ tuổi và bảng WoE từ tập Train.
        Tuyệt đối không áp dụng hàm này lên tập Test.
        """
        self.log.info("Starting .fit() process on Train dataset.")
        
        # Tính toán Global WoE để phòng hờ trường hợp Cold Start
        TotalGood = (y == 0).sum()
        TotalBad = (y == 1).sum()

        # Áp dụng Laplace smoothing cho Global WoE
        global_good_pct = (TotalGood + self.epsilon) / (TotalGood + self.epsilon * 2)
        global_bad_pct = (TotalBad + self.epsilon) / (TotalBad + self.epsilon * 2)
        self.global_woe_ = np.log(global_good_pct / global_bad_pct)

        for col in self.cols:
            # Lấy 2D array
            df_col = X[[col]] 
            min_val = int(df_col.iloc[:, 0].min())
            
            # 1. TẠO CÁC MỐC CẮT (BINNING LOGIC)
            core_bins = list(range(min_val, self.age_cap, self.bin_width))
            if not core_bins or core_bins[-1] != self.age_cap:
                core_bins.append(self.age_cap)
                
            # Mở rộng biên (-inf và inf) để bắt các ngoại lệ trên tập Test
            bins = [-np.inf] + core_bins + [np.inf]
            
            # Tạo nhãn (Labels)
            labels = []
            for i in range(len(bins) - 1):
                if i == 0:
                    labels.append(f"<{core_bins[0]}")
                elif i == len(bins) - 2:
                    labels.append(f">={core_bins[-1]}")
                else:
                    labels.append(f"{bins[i]}-{bins[i+1] - 1}")
            
            self.bins_[col] = bins
            self.labels_[col] = labels
            self.log.info(f"[{col}] Successfully learned bin boundaries. Total bins: {len(labels)}")

            # 2. MÃ HÓA WoE (WoE ENCODING LOGIC)
            # Dùng pd.cut trên tập Train để phân nhóm
            binned_series = pd.cut(df_col.iloc[:, 0], bins=bins, labels=labels, right=False)
            woe_dict = {}

            for label in np.unique(binned_series):
                # Bỏ qua nếu có giá trị NaN do lỗi dữ liệu thô
                if pd.isna(label):
                    continue
                    
                mask = (binned_series == label)
                good_i = (y[mask] == 0).sum()
                bad_i = (y[mask] == 1).sum()

                # Cảnh báo và xử lý Zero-frequency
                if good_i == 0 or bad_i == 0:
                    self.log.warning(f"[{col}] - Bin [{label}] frequency is 0. Laplace Smoothing activated (epsilon={self.epsilon}).")

                # Áp dụng công thức WoE với Laplace Smoothing
                good_pct = (good_i + self.epsilon) / (TotalGood + self.epsilon)
                bad_pct = (bad_i + self.epsilon) / (TotalBad + self.epsilon)

                woe_dict[label] = np.log(good_pct / bad_pct)

            self.woe_dicts_[col] = woe_dict
            self.log.info(f"[{col}] WoE mapping dictionary computed successfully.")
            
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Áp dụng (Transform) quy tắc cắt pd.cut và từ điển WoE lên dữ liệu.
        Tuyệt đối không học lại.
        """
        self.log.info(f"Starting .transform() process - Input shape: {X.shape}")
        
        X_out = X.copy()
        original_col_count = X_out.shape[1]

        for col in self.cols:
            df_col = X_out[[col]]
            
            # 1. Rời rạc hóa bằng biên (-inf, inf) đã học, không bao giờ sinh ra NaN do rớt ngoài khoảng
            binned_series = pd.cut(
                df_col.iloc[:, 0],
                bins=self.bins_[col],
                labels=self.labels_[col],
                right=False
            )
            
            # 2. Map nhãn sang giá trị WoE, nếu nhãn lạ (Cold Start) thì dùng Global WoE
            X_out[col] = binned_series.map(self.woe_dicts_[col]).astype(float).fillna(self.global_woe_)

        # =================================================================
        # 3. CHỐT CHẶN KIỂM ĐỊNH TỰ ĐỘNG (POST-PROCESSING ASSERTIONS)
        # =================================================================
        assert X_out.isna().sum().sum() == 0, "🚨 LỖI PIPELINE: Quá trình Transform đã sinh ra giá trị NaN ngầm định!"
        assert X_out.shape[1] == original_col_count, f"🚨 LỖI PIPELINE: Số lượng cột bị biến đổi so với đầu vào!"
        
        self.log.info(f"Transform completed successfully. Data is safe, all QA assertions passed. Output shape: {X_out.shape}")
        return X_out