# Data Model

## Mục thuật ngữ (`[[term]]` trong `data/glossary/vi.toml`)

| Trường | Bắt buộc | Kiểu | Quy tắc |
|---|---|---|---|
| `en` | có | chuỗi | term tiếng Anh gốc, chữ thường trừ tên riêng/viết tắt; khóa tra cứu (so khớp không phân biệt hoa/thường) |
| `vi` | có (trừ `status="todo"`) | chuỗi | bản dịch; bằng `en` khi `keep = true` |
| `keep` | không (mặc định false) | bool | giữ nguyên tiếng Anh (FR-005) |
| `ctx` | có nếu `en` xuất hiện > 1 lần | chuỗi | ngữ cảnh phân biệt nghĩa (vd. "đồng thời", "giao dịch") |
| `note` | có nếu `keep = true` hoặc quyết định không hiển nhiên | chuỗi | lý do ngắn (FR-006) |
| `abbr` | không | chuỗi | dạng đầy đủ nếu `en` là từ viết tắt |
| `def` | không | chuỗi | định nghĩa ngắn |
| `status` | không | `"todo"` \| `"ok"` (mặc định `ok`) | `todo` = mới trích, chưa dịch |

### Ràng buộc (kiểm bởi `check`)
- Cặp (`en` chuẩn hóa, `ctx`) là duy nhất; cùng `en` nhưng khác `ctx` được phép, thiếu `ctx` thì lỗi (FR-003).
- `vi` rỗng chỉ hợp lệ khi `status = "todo"`; `check --release` coi `todo` là lỗi với mục thuộc glossary sách hoặc dùng trong chương không-nháp (SC-001 trước xuất bản).
- `keep = true` ⇒ phải có `note`.

## Bảng thuật ngữ
Tập hợp mọi `[[term]]`. Không có trạng thái vòng đời ngoài `status` từng mục.

## Đề xuất thay đổi
Không là thực thể lưu trữ: là một PR sửa `vi.toml` + các chương bị ảnh hưởng; `check` là cổng chặn.
