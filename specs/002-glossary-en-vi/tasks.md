---

description: "Task list — Bảng thuật ngữ Anh–Việt dùng chung"
---

# Tasks: Bảng thuật ngữ Anh–Việt dùng chung

**Input**: `specs/002-glossary-en-vi/` (plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md)

**Tests**: một file unittest cho `bin/glossary-vi.py` (phần logic kiểm tra); không TDD, không test từng hàm.

**Format**: `- [ ] Txxx [P] [USn] Mô tả kèm đường dẫn file`. `[P]` = làm song song được (khác file, không phụ thuộc task chưa xong).

## Phase 1: Setup

- [X] T001 Xác nhận thư mục shortcode Hugo 0.170.1 + OINK 1.6.0 nhận: thử shortcode tối thiểu in "ok" ở `layouts/_shortcodes/terms.html` rồi `layouts/shortcodes/terms.html`, gọi từ `content/vi/terms.md` (tạo với `draft: true` và `book_status: draft` theo constitution); giữ vị trí chạy được, xóa vị trí còn lại; ghi kết quả vào research.md mục 4
- [X] T002 Xem cách bản en ghi term in nghiêng lần đầu trong `content/en/ch1.md`–`ch3.md` (research.md mục 3 ghi regex chỉ khớp 23 cặp) và chốt mẫu trích; ghi vào research.md mục 3

## Phase 2: Foundational (chặn mọi user story)

- [X] T003 Tạo khung `bin/glossary-vi.py` (argparse với lệnh `seed`, `check`, cờ `--release`; hàm nạp `data/glossary/vi.toml` bằng `tomllib`; chuẩn hóa `en`: chữ thường, gạch nối tương đương khoảng trắng) theo `contracts/cli.md`
- [X] T004 [P] Tạo `data/glossary/vi.toml` rỗng (chỉ comment đầu file nêu định dạng theo `contracts/glossary-file.md`)
- [X] T005 [P] Thêm `VI_ONLY_PAGES = {'terms'}` vào `bin/check-vi.py` và bỏ `terms` khỏi kiểm `extra-page` (Complexity Tracking trong plan.md)

**Checkpoint**: script chạy được `--help`, `check-vi.py` không báo `extra-page` cho `terms`.

## Phase 3: User Story 1 — Người dịch tra thuật ngữ trước khi dịch (P1) 🎯 MVP

**Goal**: bảng có đủ term khung để người dịch tra, quyết định dịch/giữ nguyên rõ ràng.

**Independent Test**: lấy 20 term ngẫu nhiên từ `content/en/glossary.md`; mỗi term có mục trong `vi.toml` (SC-001 mẫu), tra < 30 giây.

- [X] T006 [US1] Hiện thực lệnh `seed` trong `bin/glossary-vi.py`: trích mọi `###` heading của `content/en/glossary.md` và cặp in nghiêng đầu tiên trong chương theo mẫu chốt ở T002; thêm mục `status = "todo"`, `vi = ""` vào `data/glossary/vi.toml`, không ghi đè mục có sẵn, chạy lại không tạo mục trùng (FR-004; data-model.md `Mục thuật ngữ.en`, `Mục thuật ngữ.vi`, `Mục thuật ngữ.status`)
- [X] T007 [US1] Chạy `python3 bin/glossary-vi.py seed` và commit `data/glossary/vi.toml` khung (~600 mục)
- [X] T008 [US1] Điền bản dịch cho toàn bộ term trong `content/en/glossary.md` (61 mục) trong `data/glossary/vi.toml` theo chính sách cân bằng (FR-005): `keep = true` kèm `note` lý do khi giữ nguyên; term nhiều nghĩa như "atomic" tách mục có `ctx` (data-model.md `Mục thuật ngữ.keep`, `Mục thuật ngữ.note`, `Mục thuật ngữ.ctx`)
- [X] T009 [US1] Viết quy trình thêm/sửa term (FR-008) thành đoạn "Cách đóng góp" ở đầu `content/vi/terms.md` nội dung lấy từ cuối quickstart.md

**Checkpoint**: `vi.toml` có khung đầy đủ và 61 term glossary sách đã dịch; người dịch tra được bằng cách mở file.

## Phase 4: User Story 2 — Người đọc tra cứu hai chiều trên site (P2)

**Goal**: trang công khai `/terms/` có Anh→Việt, Việt→Anh và ô lọc.

**Independent Test**: `make vi-dev`, mở `/terms/`, tìm một term Anh và một từ Việt, mỗi lần < 10 giây; `make vi-check` qua kiểm link.

- [X] T010 [P] [US2] Viết shortcode `terms` ở thư mục chốt tại T001: đọc `site.Data.glossary.vi.term`, bỏ mục `status = "todo"`, sinh bảng Anh→Việt (sort theo `en`) và bảng Việt→Anh (sort theo `vi`, bỏ mục `keep = true`), hiển thị `ctx`, `note`, `def`, `abbr` khi có (data-model.md `Mục thuật ngữ.ctx`, `Mục thuật ngữ.abbr`, `Mục thuật ngữ.def`), kèm ô lọc JS inline ~10 dòng; link trang dùng `relURL` để đúng đường dẫn con
- [X] T011 [P] [US2] Thêm chuỗi UI (tiêu đề hai bảng, nhãn ô lọc, "không có kết quả") vào `i18n/vi.yaml`
- [X] T012 [US2] Hoàn thiện `content/vi/terms.md` (giữ `draft: true` và `book_status: draft` cho tới khi `check --release` qua; xóa hai cờ này trong cùng PR xuất bản): front matter (`title: Bảng thuật ngữ Anh–Việt`, `weight` sau `glossary`, `book_kind: glossary`, `breadcrumbs: false` — theo kiểu `content/vi/glossary.md`), gọi shortcode; gắn trang vào menu/điều hướng nếu layout OINK cần (kiểm `data/home/vi.yaml`, `data/footer/vi.yaml`; chỉ thêm, không sửa file upstream)
- [ ] T013 [US2] Chạy `make vi-dev` kiểm tay trang `/terms/` (hai chiều, lọc, link dưới `/ddia/`), rồi `make vi-check`. Lưu ý `vi-dev` hiện cả trang nháp (`-D`), còn `vi-build` thì không

**Checkpoint**: trang công khai hoạt động độc lập với US3.

## Phase 5: User Story 3 — Kiểm tra tự động nhất quán (P3)

**Goal**: một lệnh bắt term trùng, thiếu ngữ cảnh/ghi chú, và cặp thuật ngữ lần đầu trong chương lệch bảng.

**Independent Test**: cố ý thêm mục `en` trùng không `ctx` → `check` thoát 1, nêu term và dòng; bảng hợp lệ → thoát 0.

- [X] T014 [US3] Hiện thực lệnh `check` bảng trong `bin/glossary-vi.py`: lỗi `duplicate`, `missing-ctx`, `missing-note`, `empty-vi`; định dạng `<file>:<dòng>: <loại>: expected ..., got ...` (data-model.md `Mục thuật ngữ.ctx`, `Mục thuật ngữ.note`, `Mục thuật ngữ.keep`, `Mục thuật ngữ.vi`, `Mục thuật ngữ.status`; contracts/cli.md)
- [X] T015 [US3] Mở rộng `check`: quét `content/vi/ch*.md` (bỏ code bằng `without_code` của `bin/check-translation.py`, nạp như `bin/check-vi.py`), lấy cặp `*vi* (*en*)` đầu tiên của mỗi `en` trong chương; `en` có trong bảng mà `vi` không khớp mục (xét `ctx`) → `mismatch`; `en` không có trong bảng → cảnh báo `unknown-term`, không đổi mã thoát (research.md mục 5); cuối đầu ra in dòng tổng `pairs: N khớp / M cặp` cho các chương vi không-nháp (không đổi mã thoát); `mismatch` tính cả chương còn nháp (chương dịch dở cũng phải nhất quán)
- [X] T016 [US3] Thêm cờ `check --release` (cổng theo chương): lỗi `todo` nếu mục `status = "todo"` thuộc `content/en/glossary.md` hoặc có cặp `*vi* (*en*)` trong chương vi không-nháp (`draft` không là `true`); term trong `content/en/glossary.md` thiếu trong bảng → `coverage` (SC-001). Mục `todo` chỉ dùng ở chương còn nháp không bị chặn
- [X] T017 [P] [US3] Viết `bin/tests/test_glossary_vi.py` (unittest, dữ liệu dựng trong thư mục tạm): bảng hợp lệ → 0; term trùng không `ctx` → lỗi `duplicate`; chương có cặp lệch bảng → `mismatch`; `--release` với `todo` → lỗi
- [X] T018 [US3] Thêm một dòng `python3 bin/glossary-vi.py check` và chạy test mới vào cuối khối `vi-check` của `Makefile` (chỉ thêm; pattern hiện tại ở dòng 111 chỉ bắt `test_check_vi.py` nên thêm dòng `unittest discover ... -p 'test_glossary_vi.py'`)
- [X] T018a [US3] Thêm target `vi-release-check` vào cuối khối `vi-*` của `Makefile`, chạy `python3 bin/glossary-vi.py check --release`; trong `.github/workflows/pages.yml` job deploy trên `main`, gọi target này trước bước build xuất bản (job PR vẫn chỉ chạy `vi-check`)

**Checkpoint**: `make vi-check` chạy `check` cả cục bộ lẫn CI.

## Phase 6: Polish & Cross-Cutting

- [X] T019 Cập nhật `CLAUDE.md`: thêm lệnh `glossary-vi.py seed|check` vào mục "Lệnh cho bản tiếng Việt" và nêu `data/glossary/vi.toml` là nguồn sự thật thuật ngữ
- [X] T020 Chạy toàn bộ quickstart.md các bước 1–8, ghi kết quả; sửa tài liệu nếu bước nào lệch
- [ ] T021 Nhờ ít nhất một người đọc IT/DEV rà ≥ 100 mục ngẫu nhiên (SC-005); ghi các mục bị đánh giá "không tự nhiên" và sửa; đo thêm thời gian tra một term của người dịch (SC-002, mục tiêu < 30 giây)

## Phase 7: Bổ sung (sau Clarification 2026-11-27)

- [X] T022 [US1] Mở rộng `seed` trong `bin/glossary-vi.py`: trích thêm cặp không in nghiêng `（english term）` (ASCII chữ cái, khoảng trắng, gạch nối; 3–40 ký tự) từ `content/zh/ch*.md`, chỉ nhận chữ thường nên tự bỏ viết tắt và tên riêng (thêm tay như SLO, Agile); không ghi đè mục có sẵn (FR-004; data-model.md `Mục thuật ngữ.en`, `Mục thuật ngữ.status`)
- [X] T023 [US1] Thêm test cho T022 vào `bin/tests/test_glossary_vi.py` (dữ liệu zh giả có `（throughput）` không in nghiêng → có mục `todo`; chạy lại không trùng) và cập nhật `contracts/cli.md` mô tả `seed` trích cả hai dạng

- [X] T024 Sửa constitution III thêm ngoại lệ `show_en` (v1.3.0, Sync Impact Report) và ghi `show_en` vào `data-model.md`/`spec.md` (FR-011)
- [X] T025 [P] Trong `bin/glossary-vi.py` `check`: `show_en` phải là bool và không đi cùng `keep = true` (lỗi `show-en`); thêm test vào `bin/tests/test_glossary_vi.py`; đặt `show_en = true` cho `index`, `secondary index` trong `data/glossary/vi.toml`

- [X] T026 [US3] Trong `bin/glossary-vi.py` `check`: với mỗi mục `show_en = true`, quét văn xuôi `content/vi/ch*.md` (bỏ code bằng `without_code`), khớp cụm tiếng Việt dài nhất trước (sắp xếp theo độ dài giảm dần, bỏ phần đã khớp); mỗi lần xuất hiện không kèm ` (*en*)` ngay sau → in cảnh báo `show-en`, không đổi mã thoát (FR-011; data-model.md `Mục thuật ngữ.show_en`)
- [X] T027 [US3] Thêm test cho T026 vào `bin/tests/test_glossary_vi.py`: "chỉ mục thưa (*sparse index*)" và "chỉ mục (*index*)" không cảnh báo; "chỉ mục thưa" trơn cảnh báo một lần (không cảnh báo thêm cho "chỉ mục" bên trong); cập nhật `contracts/cli.md` thêm loại cảnh báo `show-en`

## Dependencies & Execution Order

- Phase 1 → Phase 2 → các user story. T002 chặn T006; T001 chặn T010–T012.
- T018a phụ thuộc T016 và T018.
- US1 (MVP) không phụ thuộc US2/US3. US2 cần dữ liệu từ T007–T008 để thấy nội dung nhưng build được với bảng rỗng. US3 cần khung script từ T003; T015 cần `vi.toml` có mục để thử thật.
- Phase 7: T023←T022, T025←T024, T026←T025, T027←T026.
- Hoàn thiện bản dịch toàn bộ ~600 mục (ngoài 61 mục glossary) diễn ra dần theo từng chương, không chặn các task trên; `--release` (T016) là cổng trước xuất bản.

## Parallel Opportunities

- Phase 2: T004 và T005 song song sau T003.
- US2: T010 và T011 song song; US3: T017 song song với T014–T016 (khác file).
- US2 và US3 chạy song song sau Phase 2 nếu có hai người.

## Implementation Strategy

- **MVP**: Phase 1–3 (US1): có bảng khung + 61 term glossary sách để người dịch dùng ngay.
- Tiếp theo US3 (chặn lệch thuật ngữ sớm khi số chương dịch tăng), rồi US2 (trang công khai) — US2 chỉ cần xong trước khi xuất bản.
- Mỗi phase kết thúc ở checkpoint có thể dừng và dùng được.
