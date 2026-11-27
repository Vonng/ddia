# Contract: `bin/check-vi.py`

Kiểm tra cấu trúc `content/vi` so với `content/zh` trong cùng repo. Chỉ đọc, chỉ stdlib Python ≥ 3.11.
Tái sử dụng regex `ATTR`, `SC`, `ID`, `HEAD`, `MDIMAGE` bằng cách import `bin/check-translation.py`.

## Gọi

```text
python3 bin/check-vi.py [--root DIR] [--json FILE] [SLUG ...]
```

| Tham số | Mặc định | Ý nghĩa |
|---|---|---|
| `--root DIR` | thư mục cha của `bin/` | Gốc repo (chứa `content/zh`, `content/vi`, `static/`) |
| `--json FILE` | không | Ghi thêm báo cáo JSON (danh sách sai lệch theo data-model) |
| `SLUG ...` | tất cả | Chỉ kiểm các trang này (ví dụ `ch1 glossary`); kiểm tập trang thừa/thiếu chỉ chạy khi không truyền SLUG |

## Hành vi

- `content/zh` hoặc `content/vi` không tồn tại ⇒ thoát mã **2** với thông báo trên stderr.
- Áp dụng mọi luật trong `data-model.md` › Phần tử cấu trúc, cho mọi trang (nháp và hoàn tất).
- Bỏ qua nội dung trong code fence khi trích heading/anchor.

## Đầu ra

stdout, mỗi sai lệch một dòng, sắp xếp theo file rồi dòng:

```text
content/vi/ch1.md:124: shortcode: expected fig 1-1 #fig_dwh_etl /fig/ddia_0101.png, got (missing)
content/vi/ch3.md: footnote: expected [^12] defined once, got 0
content/zh/ch9.md: missing-page: no Vietnamese page
```

Dòng cuối luôn là tóm tắt: `checked 24 pages: 3 issues (2 pages)` hoặc
`checked 24 pages: OK (20 drafts, 4 done)`.

## Mã thoát

| Mã | Nghĩa |
|---|---|
| 0 | Không sai lệch |
| 1 | Có ít nhất một sai lệch |
| 2 | Lỗi sử dụng / thiếu thư mục |

## Kiểm thử

`bin/tests/test_check_vi.py` (unittest): dựng cây tạm `content/zh` + `content/vi` + `static/`, khẳng
định mỗi `kind` trong data-model được phát hiện và trường hợp khớp hoàn toàn trả về 0 (SC-005).
Chạy cùng các test upstream: `python3 -m unittest discover -s bin/tests -p 'test_check_vi.py'`.
