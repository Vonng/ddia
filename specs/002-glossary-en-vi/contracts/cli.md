# Contract: `bin/glossary-vi.py`

| Lệnh | Tác dụng | Thoát |
|---|---|---|
| `python3 bin/glossary-vi.py seed` | Trích term từ `content/en/glossary.md` và cặp trong chương `content/zh`: in nghiêng `*zh*（*en*）` và không in nghiêng `zh（en）` (chỉ chữ thường; bỏ viết tắt và tên riêng, thêm tay); thêm mục `status="todo"` còn thiếu vào `vi.toml`. Không ghi đè mục có sẵn. | 0 |
| `python3 bin/glossary-vi.py check` | Kiểm bảng (trùng, thiếu `ctx`/`note`, `vi` rỗng ngoài `todo`) và cặp `*vi* (*en*)` lần đầu trong `content/vi/ch*.md` phải khớp bảng. Chỉ đọc. | 0 hợp lệ; 1 có lỗi |
| `... check --release` | Cổng theo chương: như `check`, và `status="todo"` là lỗi nếu mục thuộc glossary sách hoặc có cặp trong chương vi không-nháp; kiểm phủ đủ term glossary sách (SC-001). Mục `todo` thuộc chương còn nháp không bị chặn. | 0 / 1 |

Định dạng lỗi (cùng kiểu `check-vi.py`): `<file>:<dòng>: <loại>: expected <...>, got <...>`.
Loại lỗi: `duplicate`, `missing-ctx`, `missing-note`, `empty-vi`, `todo`, `coverage`, `mismatch`. Cảnh báo `unknown-term` và `show-en` (chương vi viết thuật ngữ `show_en` mà thiếu `(*english term*)`) không làm đổi mã thoát.
`check` in thêm dòng `pairs: N khớp / M cặp` (chương không-nháp). Trang `terms` là đích của `make vi-check` (mục kiểm link render).
