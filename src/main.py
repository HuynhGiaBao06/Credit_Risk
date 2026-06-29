# Class xuất EDA_file để khảo xát và kiểm thứ, không chạy file này nếu không cần thiết
import pandas as pd 
import sys
import pandas as pd
import sys
from pathlib import Path

# ==========================================
# THÊM PROJECT ROOT VÀO SYS.PATH
# ==========================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# ==========================================
# IMPORT ĐƯỜNG DẪN CẤU HÌNH TẬP TRUNG
# ==========================================
from src.path import TRAIN_DATA_FILE

# ==========================================
# IMPORT Logger
# ==========================================
from src.utils.logger import get_pipeline_logger

# Import Pipeline
from src.pipeline_builder import PipelineBuilder

def main():
    # 1. Khởi tạo Logger cho luồng Main
    log = get_pipeline_logger("MainExecution")
    log.info("Starting Credit Risk Pipeline Execution...")

    # 2. Định nghĩa cấu hình Biến (Configuration)
    # Lưu ý: Các biến phái sinh mới tạo từ FeatureCreator cũng phải được khai báo vào đây
    # để ColumnTransformer phía sau biết đường xử lý.
    categorical_cols = [
        'person_home_ownership', 
        'loan_intent', 
        'loan_grade', 
        'cb_person_default_on_file'
    ]
    
    # Không đưa 'person_age' vào đây vì đã có AgeBinner lo riêng
    # Không đưa 'cb_person_cred_hist_length' vì nó sẽ bị .drop() ở bước FeatureCreator
    continuous_cols = [
        'person_income', 
        'loan_amnt', 
        'loan_int_rate', 
        'loan_percent_income',
        'age_at_first_credit',        # Biến phái sinh 1
        'Estimated_Annual_Interest',  # Biến phái sinh 2
        'Income_per_Employment_Year'  # Biến phái sinh 3
    ]

    # 3. Data Ingestion (Nạp dữ liệu gốc)
    log.info(f"Loading raw training data from: {TRAIN_DATA_FILE}")
    try:
        df_train = pd.read_csv(TRAIN_DATA_FILE)
    except FileNotFoundError:
        log.error(f"FATAL ERROR: Could not find training data at {TRAIN_DATA_FILE}")
        return

    # Tách Features (X) và Target (y)
    # Giả định biến mục tiêu của dự án tên là 'loan_status'
    X_train = df_train.drop(columns=['loan_status'])
    y_train = df_train['loan_status']
    
    log.info(f"Data loaded successfully. X_train shape: {X_train.shape}, y_train shape: {y_train.shape}")

    # 4. Khởi tạo Nhà máy Pipeline (Instantiate Builder)
    log.info("Instantiating PipelineBuilder...")
    pipeline_builder = PipelineBuilder(cat_cols=categorical_cols, cont_cols=continuous_cols)

    # ==========================================
    # 5. THỰC THI NHIỆM VỤ: XUẤT DATA EDA
    # ==========================================
    # Gọi hàm export_survey_data để chạy fit_transform() và xuất ra file CSV
    # Hàm này tự động bật transform_output="pandas" để giữ nguyên tên cột
    log.info("Executing EDA Survey Data Export task...")
    
    try:
        pipeline_builder.export_survey_data(X_train, y_train)
        log.info("Pipeline execution completed successfully! Safe to terminate.")
    except Exception as e:
        log.error(f"Pipeline execution failed with error: {str(e)}")
        raise e

if __name__ == "__main__":
    main()