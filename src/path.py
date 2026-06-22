from pathlib import Path
import sys

# ==========================================
# 1. ĐỊNH VỊ THƯ MỤC GỐC (PROJECT ROOT)
# ==========================================
# --- Định vị thư mục gốc (Project Root) ---
# Kiểm tra nếu đang chạy trong môi trường Jupyter Notebook
is_notebooks = 'ipykernel' in sys.modules

if is_notebooks:
    # Nếu là Notebook, lấy thư mục hiện hành làm mỏ neo để mò đường
    NOTEBOOKS_DIR = Path.cwd().resolve()
    PROJECT_ROOT = NOTEBOOKS_DIR.parent if NOTEBOOKS_DIR.name == 'notebooks' else NOTEBOOKS_DIR

else:
    # Nếu là file .py truyền thống
    # __file__: lấy vị trí của chính file paths.py này
    # .resolve(): chuyển thành đường dẫn tuyệt đối (VD: C:/User/.../src/paths.py)
    # .parent: lùi 1 cấp (bỏ paths.py -> ra thư mục src)
    SRC_DIR = Path(__file__).resolve().parent

    # .parent lần nữa: lùi thêm 1 cấp (bỏ src -> ra thư mục gốc dự án)
    PROJECT_ROOT = SRC_DIR.parent

# ==========================================
# 2. ĐƯỜNG DẪN ĐẦU VÀO (INPUT PATHS)
# ==========================================

DATA_DIR = PROJECT_ROOT/ "data"
# Đường dấn data checkpoint
CHECKPOINT_DATA_DIR = DATA_DIR / "checkpoint_data" 
TRAIN_DATA_FILE = CHECKPOINT_DATA_DIR / "train_df.csv"
TEST_DATA_FILE = CHECKPOINT_DATA_DIR/ "test.csv"
# Đường dẫn data_raw (chỉ Bảo dùng)
DATA_RAW = DATA_DIR / "data_raw"
DATA_RAW_FILE = DATA_RAW / "data_raw.csv"

# ==========================================
# 3. ĐƯỜNG DẪN ĐẦU RA (OUTPUT PATHS)
# ==========================================

MODELS_DIR = PROJECT_ROOT / "models"        # Nơi lưu file model (.pkl, .joblib)
REPORTS_DIR = PROJECT_ROOT / "reports"      # Nơi lưu báo cáo
FIGURES_DIR = REPORTS_DIR / "figures"       # Nơi xuất file ảnh biểu đồ (.png, .jpg)
DATA_REPORTS_DIR = REPORTS_DIR / "data_reports"     # Nơi lưu các trọng số và tham số cho PowerBI(.csv,.pkl) nếu nó

# ==========================================
# 4. TỰ ĐỘNG KHỞI TẠO THƯ MỤC
# ==========================================

def check_and_create_directories(auto_create = False):
    """
    Kiểm tra trạng thái các thư mục trong dự án.
    - auto_create=False (Mặc định): Chỉ kiểm tra và thông báo nếu thiếu.
    - auto_create=True: Tiến hành tạo các thư mục còn thiếu.
    """

    # TỰ ĐỘNG GOM ĐƯỜNG DẪN BẰNG GLOBALS()
    # Quét tất cả các biến đang có, lấy ra những biến:
    # 1. Là đối tượng Path (isinstance)
    # 2. Tên biến kết thúc bằng "_DIR"
    # 3. Không phải là các thư mục gốc/mỏ neo (như SRC_DIR hay NOTEBOOK_DIR)

    dirs_to_create = [
        obj for name, obj in globals().items()
        if isinstance(obj, Path) 
        and name.endswith("_DIR") 
        and name not in ["SRC_DIR", "NOTEBOOK_DIR"]
    ]
    missing_dirs = []

    # Bước 1: Quét xem có thư mục nào chưa tồn tại không
    for dirs_path in dirs_to_create:
        if not dirs_path.exists():
            try:
                display_path = dirs_path.relative_to(PROJECT_ROOT)
            except ValueError:
                display_path = dirs_path
            
            missing_dirs.append((dirs_path,display_path))
    
    # Bước 2: Xử lý dựa trên biến cờ (Flag)
    if missing_dirs:
        print(f"⚠️ Phát hiện {len(missing_dirs)} thư mục dự án chưa tồn tại:")
        for _,display_path in missing_dirs:
            print(f"   - {display_path}")

        if auto_create:
            print("\n⚙️ Đang tự động khởi tạo...")
            for dir_path,display_path in missing_dirs:
                dir_path.mkdir(parents = True,exist_ok = True)
                print(f"   ✅ Đã tạo: {display_path}")
        else:
            print("\n💡 Gợi ý: Nếu muốn tự động tạo các thư mục này, hãy chạy hàm:")
            print("   `check_and_create_directories(auto_create=True)`")

    else:
        print("✅ Tất cả các thư mục cấu trúc dự án đã đầy đủ và sẵn sàng!")

