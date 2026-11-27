# Data Model: Dựng khung site bản dịch tiếng Việt DDIA v2

Dự án không có cơ sở dữ liệu; "dữ liệu" là file Markdown và báo cáo kiểm tra.

## Trang sách (`content/vi/<slug>.md`)

| Trường | Nguồn | Quy tắc |
|---|---|---|
| `slug` (tên file) | = tên file zh | Tập slug vi MUST = tập slug zh (24 trang) |
| `title`, `linkTitle`, `description`, `search_keywords` | dịch | Được phép khác zh |
| `translationKey`, `weight`, `book_kind`, `book_number`, `book_part`, `type`, `layout`, `cascade`, `outputs`, `breadcrumbs`, `no_print`, `search_exclude`, `search_boost` | = zh | **Bất biến** — MUST bằng giá trị zh |
| `draft` | vi riêng | `true` ⇒ trang nháp; vắng mặt/`false` ⇒ hoàn tất |
| thân trang | dịch từ zh | Các phần tử cấu trúc (dưới) MUST khớp zh |

Khóa front matter không thuộc hai nhóm trên: được phép nếu zh cũng có; khóa có trong zh mà vi
thiếu (trừ nhóm "dịch") ⇒ lỗi.

### Trạng thái

```text
(không có) --make stubs--> nháp (draft: true, thân = zh) --người dịch xóa draft--> hoàn tất
                                                         <--upstream đổi, kiểm tra báo lỗi-- (cần đối chiếu)
```

- Nháp: hiện khi `hugo server -D`, không có trong build production.
- Hoàn tất: xuất bản. Kiểm tra cấu trúc áp dụng **như nhau** cho cả hai trạng thái.
- `make stubs` chỉ tạo trang còn thiếu; không bao giờ ghi đè.

## Trang tham chiếu (zh)

`content/zh/<slug>.md` trong cùng repo (fork của `Vonng/ddia`), tại commit hiện tại.
Chỉ đọc.

## Phần tử cấu trúc (trích từ thân trang)

| Loại | Nhận dạng | So khớp vi ↔ zh |
|---|---|---|
| `anchor` | `<a id="X">`, `{#X}` | Dãy ID theo thứ tự MUST bằng nhau; trùng trong một trang ⇒ lỗi |
| `heading` | `^#{1,6} ` ngoài code block | Số lượng theo từng cấp MUST bằng nhau |
| `fig` / `tbl` / `eg` | shortcode, khóa `(kind, num, id, src)` | Dãy theo thứ tự MUST bằng nhau (bỏ qua `caption`, `alt`, `title`) |
| `xref` | shortcode, khóa `(kind, num, page, anchor)` | Multiset MUST bằng nhau; `anchor` MUST tồn tại trong trang vi `page` |
| `footnote-ref` | `[^N]` trong văn bản | Multiset nhãn MUST bằng nhau |
| `footnote-def` | `^[^N]:` | Tập nhãn MUST bằng nhau, mỗi nhãn định nghĩa đúng một lần |
| `url` | `https?://…` | Multiset MUST bằng nhau |
| `image` | `![…](path)` và `src=` của `fig` | Đường dẫn cục bộ MUST tồn tại dưới `static/` |

## Báo cáo kiểm tra

Mỗi sai lệch:

| Trường | Mô tả |
|---|---|
| `file` | đường dẫn trang vi (hoặc zh nếu trang vi thiếu) |
| `kind` | `missing-page`, `extra-page`, `front-matter`, `anchor`, `heading`, `shortcode`, `xref-target`, `footnote`, `url`, `image`, `duplicate-id` |
| `expected` / `actual` | giá trị zh / giá trị vi (rút gọn) |
| `line` | dòng trong file vi nếu xác định được |

Định dạng in: xem `contracts/check-structure.md`.
