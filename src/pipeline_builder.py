# Lắp ráp các class trên thành luồng Pipeline hoàn chỉnh

import pandas as pd
import sys
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from pathlib import Path
from sklearn import set_config
from typing import List, Tuple

# ==========================================
# THÊM PROJECT ROOT VÀO SYS.PATH
# ==========================================
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.append(str(PROJECT_ROOT))

# ==========================================
# IMPORT ĐƯỜNG DẪN CẤU HÌNH TẬP TRUNG
# ==========================================
# Tuyệt đối không hardcode đường dẫn trong file này
from src.path import EDA_DATA_FILE,check_and_create_directories

# ==========================================
# IMPORT Logger
# ==========================================
from src.utils.logger import get_pipeline_logger

# ==========================================
# IMPORT CÁC CUSTOM TRANSFORMERS ĐÃ VIẾT
# ==========================================
from src.pre_processing import AgeBinningEncoder, DecisionTreeBinner, FeatureCreator, KFoldWrapper, TargetEncoder

class PipelineBuilder:
    """
    Class Tổng tư lệnh chịu trách nhiệm khởi tạo, điều phối và lắp ráp 
    toàn bộ các luồng tiền xử lý dữ liệu cho dự án Credit Risk.
    """
    def __init__(self, cat_cols: List[str], cont_cols: List[str]):
         # 1. Khởi tạo tham số và thuộc tính
        self.cat_cols = cat_cols
        self.cont_cols = cont_cols
    
        # 2. Khởi tạo Logger
        self.log = get_pipeline_logger(self.__class__.__name__)
        self.log.debug(f"Initializing {self.__class__.__name__}")

    def _build_base_pipeline(self) -> Pipeline:
        """
        Khởi tạo Base Pipeline (Tiền xử lý cơ bản & Mã hóa).
        Áp dụng KFoldWrapper để chống rò rỉ dữ liệu (Data Leakage).
        """
        self.log.debug("Building Base Pipeline...")
        
        # Bước 1: Điều phối các luồng mã hóa song song
        preprocessor = ColumnTransformer(
            transformers=[
                # Luồng 1: Rời rạc hóa và mã hóa riêng cho độ tuổi
                ('age_bin', KFoldWrapper(AgeBinningEncoder(cols=['person_age'])), ['person_age']),
                
                # Luồng 2: Mã hóa các biến số liên tục (Income, Loan Amount, v.v.)
                ('dt_bin', KFoldWrapper(DecisionTreeBinner(cols=self.cont_cols)), self.cont_cols),
                
                # Luồng 3: Mã hóa biến danh mục bằng M-estimate
                ('target_enc', KFoldWrapper(TargetEncoder(cols=self.cat_cols)), self.cat_cols)
            ],
            remainder='passthrough' # Giữ nguyên các biến phái sinh không mã hóa
        )

        # Bước 2: Ghép Kỹ thuật đặc trưng vào đầu luồng
        base_pipeline = Pipeline(steps=[
            ('feature_creation', FeatureCreator()),
            ('preprocessing', preprocessor)
        ])

        return base_pipeline
    
    def build_branch_base_line(self) -> Pipeline:
        """
        Nhánh A: Dành riêng cho thuật toán tuyến tính (Ridge Classifier).
        Bắt buộc phải xử lý ngoại lai (Capping) và chuẩn hóa khoảng cách (Scaling).
        """
        self.log.info("Assembling Branch A: Ridge Classifier Pipeline.")
        base_pipe = self._build_base_pipeline()

        ridge_pipeline = Pipeline(steps=[
            ('base_pipeline', base_pipe),
            # TODO: Insert OutlierCapper module here (Chờ team DA/EDA chốt ngưỡng khảo sát)
            ('outlier_capping', 'passthrough'), 
            ('scaling', StandardScaler())
        ])
        return ridge_pipeline
    
    def build_branch_B_tree(self) -> Pipeline:
        """
        Nhánh B: Dành riêng cho thuật toán Cây (AdaBoost, LightGBM).
        Bỏ qua Capping và Scaling để giữ nguyên thông tin nội tại của dữ liệu.
        """
        self.log.info("Assembling Branch B: Tree-based Pipeline (LightGBM/AdaBoost).")
        base_pipe = self._build_base_pipeline()
        
        tree_pipeline = Pipeline(steps=[
            ('base_pipeline', base_pipe)
            # Dừng luồng xử lý tại đây, đẩy thẳng vào mô hình
        ])
        return tree_pipeline
    
    def run_production_pipeline(self, pipeline: Pipeline, X: pd.DataFrame, y: pd.Series = None, is_train: bool = True) -> pd.DataFrame:
        """
        HÀM 1: Chế độ Thực thi Production (In-memory).
        Tuyệt đối không lưu file CSV. Chỉ xử lý trên RAM.
        """
        self.log.info(f"Activating Production pipeline. Train mode: {is_train}")
        
        if is_train:
            # Sẽ gọi hàm .fit_transform() được ghi đè của KFoldWrapper tạo ra dữ liệu OOF
            X_processed = pipeline.fit_transform(X, y)
        else:
            # Khóa Test set: Chỉ map từ bảng tra cứu
            X_processed = pipeline.transform(X)
            
        self.log.info("Production Pipeline completed In-memory processing successfully.")
        return X_processed
    
    def export_survey_data(self, X: pd.DataFrame, y: pd.Series) -> None:
        """
        HÀM 2: Chế độ Khảo sát EDA.
        Ép Scikit-learn xuất ra Pandas DataFrame để giữ nguyên tên cột, sau đó lưu CSV.
        """
        self.log.info("Activating Export Survey Data pipeline. Setting transform_output='pandas'.")
        
        # Lệnh cấu hình SỐNG CÒN giúp giữ lại định dạng DataFrame thay vì Numpy Array
        set_config(transform_output="pandas")
        
        # Chỉ dùng Base Pipeline cho việc xuất dữ liệu EDA khảo sát
        base_pipe = self._build_base_pipeline()
        
        self.log.info("Executing fit_transform() on Train data...")
        X_survey = base_pipe.fit_transform(X, y)
        
        # Xuất file CSV ra thư mục đã định nghĩa, tự động tại file mới nếu chưa có
        check_and_create_directories(auto_create= True)
        X_survey.to_csv(EDA_DATA_FILE, index=False)
        self.log.info(f"Successfully exported EDA survey data to: {EDA_DATA_FILE}")
        
        # Khôi phục cấu hình mặc định (tùy chọn nhưng an toàn)
        set_config(transform_output="default")