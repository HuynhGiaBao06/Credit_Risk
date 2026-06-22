# 📘 HƯỚNG DẪN KẾT NỐI DATABASE POSTGRESQL (NEON.TECH) TRÊN VS CODE

Tài liệu này hướng dẫn chi tiết cách thiết lập kết nối vào Cơ sở dữ liệu chung của dự án từ lúc chưa cài đặt gì cho đến khi đăng nhập và làm việc thành công.

---

## 🛠️ BƯỚC 1: CÀI ĐẶT EXTENSION TRÊN VS CODE

Để quản lý và viết lệnh SQL trực tiếp trong VS Code, chúng ta sẽ sử dụng tiện ích mở rộng **Database Client**.

1. Mở **VS Code** của bạn lên.
2. Nhấn tổ hợp phím `Ctrl + Shift + X` (hoặc `Cmd + Shift + X` trên Mac) để mở chợ ứng dụng **Extensions**.
3. Tại thanh tìm kiếm, nhập từ khóa: **`Database Client`**.
4. Tìm đúng tiện ích có tên đầy đủ là: **`Database Client - JDBC (MySQL/PostgreSQL/MongoDB/Redis)`** *(của tác giả cweijan)*.
5. Nhấn nút **Install** để cài đặt. Sau khi cài xong, bạn sẽ thấy một biểu tượng **hình tháp hình trụ (Database)** xuất hiện ở thanh công cụ bên lề trái của VS Code.

---

## 🔐 BƯỚC 2: THÔNG TIN ĐĂNG NHẬP (CREDENTIALS)

Mỗi thành viên sẽ sử dụng thông tin chung của Server kết hợp với **User / Password** riêng đã được cấp phát dưới đây.

### 1. Thông số Server chung (Dùng chung cho cả nhóm)
* **Host:** `ep-quiet-queen-aop3s0b5-pooler.c-2.ap-southeast-1.aws.neon.tech`
* **Database (DB Name):** `neondb`
* **Port:** `5432`
* **SSL Mode:** `require` *(Bắt buộc phải bật)*

### 2. Tài khoản đăng nhập riêng (Tìm đúng tên của bạn)

* **Thành viên Duy:**
  * **User:** `member_duyna`
  * **Password:** `NguyenAnDuy123@`
* **Thành viên Kiệt:**
  * **User:** `member_kietnh`
  * **Password:** `NguyenHuuKiet123@`

---

## ⚡ BƯỚC 3: CẤU HÌNH KẾT NỐI CHỈ LẦN ĐẦU TIÊN (LOGIN)

Bạn chỉ cần thực hiện thiết lập này **duy nhất một lần**, lần sau VS Code sẽ tự động lưu lại.

1. Click vào biểu tượng **Database** (hình tháp trụ) ở thanh menu bên lề trái VS Code.
2. Nhấn vào nút dấu cộng **`+` (Create Connection)** ở góc trên cùng.
3. Một danh sách các loại cơ sở dữ liệu sẽ hiện ra -> Chọn **PostgreSQL**.
4. Điền chính xác các thông số từ **Bước 2** vào các ô tương ứng:
   * **Host:** Dán chuỗi Host chung của nhóm vào.
   * **Port:** Điền `5432`.
   * **Database:** Điền `neondb`.
   * **User:** Điền chính xác Username của bạn.
   * **Password:** Điền chính xác Mật khẩu của bạn.
5. **CẤU HÌNH SSL (Bắt buộc):** Cuộn xuống tìm mục **SSL**, chuyển trạng thái từ *False* sang **True** (hoặc tích chọn kích hoạt). Tại ô **SSL Mode**, bạn chọn hoặc gõ chữ: `require`.
6. Nhấn nút **Test Connection** ở góc dưới cùng:
   * Nếu hiện thông báo màu xanh **Success / Connected** -> Bạn đã đăng nhập thành công! Nhấn **Save** để lưu lại.
   * Nếu báo lỗi -> Kiểm tra kỹ lại xem mật khẩu/tên user có bị dính khoảng trắng (space) ở đầu hoặc cuối hay không.

---

## 🚀 BƯỚC 4: HƯỚNG DẪN LÀM VIỆC VÀ QUẢN LÝ DATA

Sau khi đã lưu kết nối, bạn sẽ thấy tên kết nối xuất hiện ở thanh bên trái. Bạn có thể bắt đầu làm việc bằng các thao tác sau:

* **Mở trình gõ lệnh SQL (SQL Editor):** Click chuột phải vào chữ **`neondb`** ở thanh bên trái -> Chọn **New Query**. Một tab trống sẽ hiện ra ở giữa màn hình để bạn viết các lệnh như `SELECT`, `INSERT`, `UPDATE`...
* **Chạy lệnh SQL:** Sau khi viết code xong, bạn bôi đen đoạn lệnh cần chạy và nhấn nút **Run** (Hình tam giác Play nhỏ xuất hiện ngay phía trên dòng code đó hoặc ở góc trên bên phải màn hình). Bạn cũng có thể dùng phím tắt `Ctrl + Enter`.
* **Xem dữ liệu trực quan (Giống Excel):** Mở rộng cây thư mục theo đường dẫn: `neondb` -> `Schemas` -> `public` -> `Tables`. **Click đúp chuột** vào một bảng bất kỳ, dữ liệu sẽ hiển thị dạng bảng tính, bạn có thể sửa chữ hoặc bấm dấu `+` để thêm dòng trực tiếp mà không cần viết code.

> ⚠️ **LƯU Ý QUAN TRỌNG VỀ TÍNH NĂNG TỰ NGỦ (COLD START):**
> Vì chúng ta đang dùng gói Serverless miễn phí, nếu không có ai thao tác trong vòng 5 phút, database trên mạng sẽ tự động "đi ngủ" để tiết kiệm tài nguyên. 
> Do đó, mỗi khi bạn mở máy lên hoặc sau một thời gian dài không đụng vào, lệnh chạy đầu tiên hoặc lần click đúp vào bảng đầu tiên sẽ bị khựng lại khoảng **2 đến 3 giây** để đợi database khởi động lại. Từ các lệnh tiếp theo, tốc độ sẽ phản hồi cực nhanh ngay lập tức!