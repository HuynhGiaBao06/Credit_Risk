-- =========================================================================
-- BƯỚC 1: Xóa các User cũ (nếu có)
-- Lưu ý: Trong Postgres, lệnh DROP ROLE sẽ xóa cả quyền Login và User.
-- ========================================================================= 
DROP ROLE IF EXISTS member_duyna;
DROP ROLE IF EXISTS member_kietnh;

-- =========================================================================
-- BƯỚC 2: Tạo User mới kèm Mật khẩu (Mặc định đã có quyền LOGIN)
-- =========================================================================

CREATE USER member_duyna WITH PASSWORD'NguyenAnDuy123';
CREATE USER member_kietnh WITH PASSWORD 'NguyenHuuKiet123';

-- =========================================================================
-- BƯỚC 3: Cấp quyền truy cập (Chắc chắn đang chạy trên DB dự án, vd: neondb)
-- =========================================================================

-- 1. Cấp quyền truy cập vào schema public (Bắt buộc để nhìn thấy bảng)
GRANT USAGE ON SCHEMA PUBLIC TO member_duyna, member_kietnh;

-- 2. Cấp quyền đọc dữ liệu (SELECT) - Tương đương db_datareader
GRANT SELECT ON ALL TABLES IN SCHEMA public TO member_duyna, member_kietnh;

-- 4. QUAN TRỌNG: Đảm bảo các bảng tạo MỚI trong tương lai thì 2 user này vẫn có quyền Đọc/Ghi
ALTER DEFAULT PRIVILEGES IN SCHEMA public 
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO member_duyna, member_kietnh;

-- Cấp quyền tạo (CREATE) và sử dụng (USAGE) trên schema public
GRANT ALL ON SCHEMA public TO member_duyna, member_kietnh;