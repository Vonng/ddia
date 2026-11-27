# Research: Bảng thuật ngữ Anh–Việt

Không còn NEEDS CLARIFICATION. Các quyết định:

## 1. Định dạng lưu trữ
- **Decision**: TOML, mảng `[[term]]`.
- **Rationale**: Python 3.11+ có `tomllib` (stdlib, không cần cài PyYAML trên CI); Hugo đọc TOML trong `data/`; dễ sửa tay và diff theo từng mục.
- **Alternatives**: YAML (cần PyYAML hoặc parser tự viết); JSON (khó sửa tay, không chú thích); Markdown table (khó kiểm tra và render hai chiều); CSV (ngữ cảnh/ghi chú nhiều dòng bất tiện).

## 2. Một nguồn, hai chiều tra
- **Decision**: Shortcode đọc `site.Data.glossary.vi`, sinh bảng Anh→Việt (sort theo `en`) và Việt→Anh (sort theo `vi`, bỏ mục giữ nguyên tiếng Anh), kèm ô lọc bằng JS inline ~10 dòng.
- **Rationale**: không lặp dữ liệu; lọc client-side đủ nhanh cho ~600 mục; không thêm thư viện tìm kiếm.
- **Alternatives**: Pagefind/Lunr (dependency + bước build mới); trang riêng mỗi chiều (hai nguồn dễ lệch).

## 3. Khởi tạo khung (FR-004)
- **Decision**: `glossary-vi.py seed` trích (a) mọi `###` heading của `content/en/glossary.md`, (b) mọi cặp `（*english*）`/`(*english*)` ở lần đầu trong `content/zh/ch*.md` và `content/en/ch*.md`. Ghi mục với `vi = ""`, `status = "todo"`; không ghi đè mục đã có. Người dịch điền; `check` ở chế độ xuất bản yêu cầu không còn `todo`.
- **Rationale**: không bỏ sót term, bản dịch vẫn do người quyết (spec: không sinh tự động).
- **Alternatives**: nhập tay hoàn toàn (dễ sót); dịch máy (loại theo Clarification 5).
- **Kết quả (T002)**: bản en viết term in nghiêng dạng `*term*` không kèm ngoặc, nên không trích từ en. `seed` trích cặp `*zh*（*en*）` từ `content/zh/ch*.md` (regex `\*([^*\n]+)\*[（(]\*([A-Za-z][^*\n]*)\*[）)]`) cộng các heading `###` của `content/en/glossary.md`: 508 mục sau khi gộp trùng.
- **Lưu ý (cũ)**: số cặp thực tế đo được: ~570 cặp in nghiêng ở zh, ~550 term riêng biệt; ở en regex chỉ khớp 23 vì cách ghi khác — khi triển khai cần xem lại mẫu của bản en trước khi tin vào regex.

## 4. Chỗ đặt shortcode
- **Kết quả (T001)**: `layouts/_shortcodes/` chạy được với Hugo 0.170.1 (đã thử, shortcode in ra trong `/terms/` và `_print`).
- **Decision (ban đầu)**: kiểm tra khi triển khai xem OINK 1.6.0/Hugo 0.170 dùng `layouts/_shortcodes/` hay `layouts/shortcodes/` (repo hiện chỉ có `layouts/_partials`, `layouts/partials`, `layouts/book`); đặt theo thư mục Hugo 0.170 nhận. Thử bằng một shortcode rỗng trước.
- **Rationale**: đoán sai thì shortcode không chạy và build chỉ báo cảnh báo.

## 5. Phạm vi kiểm tra chương (Clarification 4)
- **Decision**: `check` quét `content/vi/ch*.md` (bỏ code), lấy cặp `*vi* (*en*)` đầu tiên của mỗi `en` trong chương; nếu `en` có trong bảng (khớp không phân biệt hoa/thường, gạch nối tương đương khoảng trắng; số ít/số nhiều là mục riêng) thì `vi` phải bằng một trong các bản dịch của mục (có hỗ trợ nhiều nghĩa qua `ctx`). `en` không có trong bảng → cảnh báo (không lỗi) để người dịch bổ sung.
- **Rationale**: dạng cặp cố định nên khớp chính xác; không quét văn xuôi tránh báo động giả.

## 6. Chặn khi sửa bản dịch (FR-008)
- **Decision**: không cần cơ chế riêng. Sửa `vi.toml` mà chương còn cặp dùng bản cũ → `check` lỗi → CI/`make vi-check` chặn. Quy trình ghi trong quickstart: đổi term → chạy `check` → sửa các chương được liệt kê.

## 7. Ghi kèm tiếng Anh (`show_en`)
- **Decision**: trường bool `show_en` trên mục thuật ngữ; mục có `show_en = true` luôn được ghi kèm `(*en*)` ở mọi lần xuất hiện (ngoại lệ của constitution III, v1.3.0). `check` cảnh báo `show-en` (không đổi mã thoát), khớp cụm dài nhất trước, chấp nhận cả dạng `*vi* (*en*)` lẫn `vi (*en*)`.
- **Rationale**: người dịch muốn các thuật ngữ "chỉ mục" và "sao chép" luôn đi kèm tiếng Anh để dân IT/DEV đối chiếu tài liệu gốc.
- **Alternatives**: chỉ ghi cả hai trong bảng (không ảnh hưởng văn bản); giữ nguyên tiếng Anh (mất bản dịch); kiểm lỗi chặn merge (báo động giả nặng với hàng trăm lần xuất hiện).
