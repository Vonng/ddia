# Implementation Plan: Bảng thuật ngữ Anh–Việt dùng chung

**Branch**: `002-glossary-en-vi` | **Date**: 2026-11-27 | **Spec**: [spec.md](spec.md)

## Summary

Một file dữ liệu TOML (`data/glossary/vi.toml`) là nguồn sự thật duy nhất. Từ đó: (1) shortcode Hugo render trang công khai `content/vi/terms.md` với hai bảng Anh→Việt / Việt→Anh và ô lọc; (2) script stdlib `bin/glossary-vi.py` có hai lệnh — `seed` (trích khung term từ glossary sách và các cặp in nghiêng trong chương) và `check` (kiểm bảng + kiểm cặp thuật ngữ lần đầu trong chương); (3) `check` được nối vào `make vi-check`/CI. Không dependency mới, không sửa file upstream (chỉ thêm vào khối `vi-*` của Makefile).

## Technical Context

**Language/Version**: Python 3.12+ (stdlib `tomllib`), Hugo 0.170.1 template + JS inline vài dòng

**Primary Dependencies**: không thêm. Tái dùng regex/hàm `without_code` của `bin/check-translation.py` (như `check-vi.py` đã làm)

**Storage**: file TOML trong repo (`data/glossary/vi.toml`)

**Testing**: `unittest` (như `bin/tests/test_check_vi.py`) + `hugo` build kèm `check-rendered-links.py`

**Target Platform**: GitHub Pages dưới đường dẫn con `/ddia/`; CI `ubuntu-latest`

**Project Type**: nội dung tĩnh + script kiểm tra

**Performance Goals**: `check` < 2 giây trên toàn bộ repo; trang bảng tải/lọc tức thì với ~600 mục

**Constraints**: không sửa file upstream; link phải đúng dưới đường dẫn con; không `--panicOnWarning`

**Scale/Scope**: ~61 term glossary sách + ~550 term in nghiêng ≈ 600 mục

## Constitution Check

| Nguyên tắc | Đánh giá |
|---|---|
| I. Trung thành nguồn | Đạt. Bảng chỉ ghi thuật ngữ, không thay đổi nội dung kỹ thuật. Bản dịch term do người dịch điền, không tự sinh. |
| II. Tương đương cấu trúc 1:1 | Cần ghi nhận. `content/vi/terms.md` không có bản zh → `check-vi.py` hiện báo `extra-page`. Xử lý: thêm hằng `VI_ONLY_PAGES` trong `check-vi.py` (file phía vi, không phải upstream). Xem Complexity Tracking. |
| III. Thuật ngữ nhất quán | Chính feature này hiện thực hóa nguyên tắc; ngoại lệ ngữ cảnh = mục có trường `ctx`; ngoại lệ ghi kèm tiếng Anh = trường `show_en` (constitution v1.3.0). |
| IV. Kiểm chứng tự động | Đạt. `check` chạy cục bộ và CI bằng cùng lệnh `make vi-check`; chỉ đọc. |
| V. Tái dùng upstream, giữ đơn giản | Đạt. Không dependency, file mới có hậu tố `vi`, Makefile chỉ thêm cuối khối `vi-*`. Viết mới vì upstream không có bảng thuật ngữ Anh–Việt. |

Sau Phase 1: vẫn đạt, một khoản ghi ở Complexity Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/002-glossary-en-vi/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── glossary-file.md     # định dạng vi.toml
│   └── cli.md               # lệnh glossary-vi.py
└── tasks.md                 # /speckit-tasks
```

### Source Code (repository root)

```text
data/glossary/vi.toml                # nguồn sự thật (mới)
content/vi/terms.md                  # trang công khai, gọi shortcode (mới)
layouts/_shortcodes/terms.html       # render hai bảng + ô lọc (mới)
bin/glossary-vi.py                   # seed + check (mới)
bin/tests/test_glossary_vi.py        # test (mới)
bin/check-vi.py                      # thêm VI_ONLY_PAGES = {'terms'} (sửa phía vi)
Makefile                             # thêm dòng gọi check vào vi-check và target vi-release-check
.github/workflows/pages.yml         # job deploy (main) gọi vi-release-check trước khi build
i18n/vi.yaml                         # chuỗi UI cho trang (thêm khóa)
```

**Structure Decision**: dữ liệu tách khỏi trình bày (`data/` + shortcode) để một nguồn sinh được cả hai chiều tra và cho script kiểm tra đọc. Thư mục shortcode của layout OINK cần xác nhận tên (`layouts/_shortcodes` vs `layouts/shortcodes`) khi triển khai — xem research.md mục 4.

## Complexity Tracking

| Vi phạm | Vì sao cần | Phương án đơn giản hơn bị loại vì |
|---|---|---|
| Sửa `bin/check-vi.py` để cho phép trang `terms` không có bản zh | Spec yêu cầu trang riêng tách khỏi `glossary` (FR-007) | Nhét bảng vào `glossary.md` làm sai lệch cấu trúc 1:1 và nội dung gốc; đặt trang trong thư mục con thì lách kiểm tra thay vì khai báo rõ |
