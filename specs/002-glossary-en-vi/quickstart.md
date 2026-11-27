# Quickstart: kiểm chứng bảng thuật ngữ

Điều kiện: Python 3.12+, Hugo 0.170.1 như `make vi-check`.

1. **Khởi tạo khung**: `python3 bin/glossary-vi.py seed` → `data/glossary/vi.toml` có ~600 mục, phần lớn `status="todo"`. Chạy lại không tạo mục trùng.
2. **Điền bản dịch** cho một vài mục (một mục `keep = true` có `note`, một term hai nghĩa có `ctx`).
3. **Kiểm**: `python3 bin/glossary-vi.py check` → thoát 0. Cố ý thêm mục `en` trùng không `ctx` → thoát 1, nêu term và dòng (US3, SC-003).
4. **Chương**: trong chương vi, viết `*nguyên tử* (*atomic*)` khớp bảng → qua; đổi thành bản dịch khác → `mismatch` (SC-004).
5. **Đổi bản dịch** (thử ở chương đầu tiên dịch xong; trước đó test T017 phủ bằng dữ liệu giả) (FR-008): sửa `vi` của một mục đã dùng trong chương → `check` lỗi liệt kê chương; sửa chương → qua.
6. **Trang site**: `make vi-dev`, mở `/terms/` → có hai bảng và ô lọc; tìm một term Anh và một từ Việt, mỗi lần < 10 giây (US2).
7. **Tất cả**: `make vi-check` (đã gồm `check`, build kèm nháp dưới `/ddia/`, kiểm link render) → OK.
8. **Trước xuất bản**: `python3 bin/glossary-vi.py check --release` → thoát 0 khi không còn `todo` trong glossary sách và các chương không-nháp, và đủ term glossary sách (SC-001); sau đó xóa `draft` và `book_status` khỏi `content/vi/terms.md`.

**Quy trình thêm term** (FR-008): thêm mục vào `vi.toml` theo [contract](contracts/glossary-file.md) → chạy `check` → gửi PR; sửa bản dịch có sẵn thì sửa luôn các chương bị liệt kê trong cùng PR.
