# Implementation Plan: Dựng khung site bản dịch tiếng Việt DDIA v2

**Branch**: `001-hugo-site-scaffold` | **Date**: 2026-11-27 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-hugo-site-scaffold/spec.md`

## Summary

Repo là fork của `Vonng/ddia`, nên site, theme, layout, ảnh và bản zh tham chiếu đã có sẵn. Feature
chỉ **thêm** lớp tiếng Việt lên trên, gần như không sửa file upstream: overlay cấu hình
`hugo.vi.yaml` (ngôn ngữ `vi` mặc định, tắt zh/tw/v1, tắt GA/giscus), i18n/data tiếng Việt,
`content/vi/` gồm 24 stub sao chép từ `content/zh/` có `draft: true`, script `bin/check-vi.py`
so vi ↔ zh, vài target `vi-*` trong Makefile, và workflow GitHub Pages.

## Technical Context

**Language/Version**: Hugo 0.170.1; Python ≥ 3.11 (stdlib); Go ≥ 1.22 (Hugo module)

**Primary Dependencies**: OINK v1.6.0 (đã pin trong `go.mod` của fork)

**Storage**: N/A — Markdown trong git

**Testing**: `unittest` stdlib (`bin/tests/test_check_vi.py`); `hugo --printPathWarnings --printI18nWarnings`; `bin/check-rendered-links.py` có sẵn

**Target Platform**: GitHub Pages project site `https://nguyendan07.github.io/ddia/`

**Project Type**: static site (sách) — fork

**Performance Goals**: `check-vi` 24 trang < 30 s; CI build + deploy ≤ 10 phút

**Constraints**: không sửa file upstream trừ append Makefile (và tùy chọn 2 dòng `.gitignore`); không commit `public/`; không `--panicOnWarning`

**Scale/Scope**: 24 trang vi; ~12 file mới

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Nguyên tắc | Đánh giá | Trạng thái |
|---|---|---|
| I. Trung thành với nguồn | Stub chép nguyên văn zh; nguồn nay là `content/zh` trong repo (constitution ghi `../ddia/content/zh` — cần sửa đường dẫn) | PASS |
| II. Cấu trúc 1:1 | `make stubs` tạo đúng tập trang zh; `check-vi` thực thi luật | PASS |
| III. Thuật ngữ | Ngoài phạm vi | N/A |
| IV. Kiểm chứng tự động | `make vi-check` cục bộ = CI; lỗi ⇒ không deploy | PASS |
| V. Tái sử dụng upstream | Dùng nguyên theme/layout/ảnh/`check-rendered-links`; `check-vi` import regex của `check-translation` | PASS (xem Complexity Tracking) |
| Ràng buộc kỹ thuật | Hugo 0.170.1 là mức OINK v1.6.0 yêu cầu; constitution ghi 0.168.0 — cần sửa con số | PASS |
| Ghi công & giấy phép | `data/home/vi.yaml` giữ phần legal/people, thêm nhóm dịch vi | PASS |

**Post-design re-check**: không vi phạm mới. Việc chuyển sang fork làm giảm phạm vi (bỏ sao chép
layout/ảnh/CSS, bỏ `UPSTREAM` + checkout upstream trong CI, bỏ `sync-stubs.py`).

## Project Structure

### Documentation (this feature)

```text
specs/001-hugo-site-scaffold/
├── plan.md, research.md, data-model.md, quickstart.md
├── contracts/{check-vi.md, make-targets.md}
├── checklists/requirements.md
└── tasks.md             # /speckit-tasks
```

### Source Code (repository root) — chỉ liệt kê file mới/sửa

```text
hugo.vi.yaml                     # MỚI: overlay cấu hình tiếng Việt
content/vi/*.md                  # MỚI: 24 trang (stub draft từ content/zh)
i18n/vi.yaml                     # MỚI
data/home/vi.yaml                # MỚI
data/footer/vi.yaml              # MỚI
bin/check-vi.py                  # MỚI
bin/tests/test_check_vi.py       # MỚI
.github/workflows/pages.yml      # MỚI
README.md                        # SỬA: README tiếng Việt (merge=ours trong .gitattributes)
.gitattributes                   # MỚI
Makefile                         # SỬA: append khối vi-*
.gitignore                       # SỬA (tùy chọn): bỏ CLAUDE.md, .claude
bin/check-rendered-links.py      # SỬA chỉ khi --all không đủ (R8)
```

**Structure Decision**: giữ nguyên bố cục fork; mọi thứ tiếng Việt nằm trong file mới có hậu tố/
thư mục `vi` để pull upstream không xung đột.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| `bin/check-vi.py` là script mới (Nguyên tắc V) | Cần so vi ↔ zh; `check-translation.py` hard-code en ↔ zh và luật riêng chữ Hán | Sửa script upstream gây xung đột khi pull; script mới import lại regex upstream nên không nhân đôi định nghĩa cú pháp |
