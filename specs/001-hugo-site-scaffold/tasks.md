---
description: "Task list for 001-hugo-site-scaffold"
---

# Tasks: Dựng khung site bản dịch tiếng Việt DDIA v2

**Input**: Design documents from `/specs/001-hugo-site-scaffold/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Chỉ có test cho `bin/check-vi.py` — SC-005 và `contracts/check-vi.md` yêu cầu rõ. Các phần còn lại được kiểm chứng bằng kịch bản trong `quickstart.md`.

**Nguyên tắc chung**: chỉ thêm file mới; file upstream chỉ được sửa ở đúng chỗ ghi trong task (`Makefile` append, `.gitignore`). Mọi đường dẫn tương đối với gốc repo.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Chạy song song được (khác file, không phụ thuộc task chưa xong)
- **[Story]**: US1/US2/US3 theo spec.md

---

## Phase 1: Setup

**Purpose**: Toolchain và remote

- [X] T001 Cài Hugo **0.170.1** (bản thường, từ release chính thức `gohugoio/hugo`) vào `~/.local/bin/hugo`; xác nhận `hugo version` in `v0.170.1` và `go version` ≥ 1.22 (research R1)
- [X] T002 [P] Thêm remote upstream: `git remote add upstream https://github.com/Vonng/ddia.git` (bỏ qua nếu đã có)
- [ ] T003 [P] Bỏ hai dòng `.claude` và `CLAUDE.md` khỏi `.gitignore` để version `CLAUDE.md`, `.specify/`, `specs/` (research R13; chỉ làm nếu chủ repo đồng ý — nếu không, bỏ qua task này)
- [X] T004 Xác nhận build upstream vẫn chạy: `make build` thành công trên fork chưa sửa (baseline trước khi thêm vi)

---

## Phase 2: Foundational (chặn mọi user story)

**Purpose**: Ngôn ngữ `vi` tồn tại và build được

- [X] T005 Tạo `hugo.vi.yaml` theo research R3: `defaultContentLanguage: vi`; `disableLanguages: [zh, tw, v1, v1_tw]`; `languages.vi` với `label: Tiếng Việt`, `locale: vi-VN`, `contentDir: content/vi`, `weight: 0`, `title`, `params` (description, `version: v2`, `versions` chỉ một mục v2 url `/`, `comments.giscus` aria/error tiếng Việt, `time_format_default`, `ui.command_palette.commands` dịch từ khối `zh` trong `hugo.yaml`) và `menus.main` dịch từ khối `zh` (Đọc, Mục lục, Thuật ngữ, Chỉ mục, Đóng góp); `services.googleAnalytics.id: ""`; `params.comments.enable: false`; `params.github_repo`/`github_project_repo: https://github.com/nguyendan07/ddia`; `params.copyright.authors` ghi nhóm dịch tiếng Việt và bản dịch tiếng Trung
- [X] T006 Chạy kịch bản S0 trong `quickstart.md`: `hugo config --config hugo.yaml,hugo.vi.yaml` phải cho `defaultcontentlanguage = 'vi'`, `disablelanguages` đúng, khối `languages.vi` đầy đủ và các khóa `markup`/`params.ui` của `hugo.yaml` vẫn còn (merge, không thay thế). Nếu sai: thử đảo thứ tự file; nếu vẫn sai, áp phương án dự phòng R3 (chuyển nội dung `hugo.vi.yaml` vào `hugo.yaml`) và ghi kết quả vào `specs/001-hugo-site-scaffold/research.md` mục R3
- [X] T007 Append khối tiếng Việt vào cuối `Makefile` theo `contracts/make-targets.md`: biến `VI_HUGO`, `BASE_URL`; target `stubs`, `vi-dev`, `vi-build` (target `vi-check` để lại cho T016); thêm vào `.PHONY`. `stubs`: với mỗi `content/zh/*.md` chưa có `content/vi/<cùng tên>`, chép sang và chèn dòng `draft: true` ngay sau dòng `---` đầu tiên (`sed '1a draft: true'`), in tên file đã tạo; không bao giờ ghi đè (data-model.md › Trang sách.slug, Trang sách.draft)

**Checkpoint**: `make stubs` tạo được trang và `make vi-build` chạy (có thể còn cảnh báo i18n)

---

## Phase 3: User Story 1 — Người dịch xem trước site cục bộ (P1) 🎯 MVP

**Goal**: Một lệnh xem được site tiếng Việt đủ 24 trang, giao diện tiếng Việt, trang chưa dịch hiện là nháp.

**Independent Test**: kịch bản S1 + S3 trong `quickstart.md`.

- [X] T008 [US1] Chạy `make stubs` để tạo 24 file `content/vi/*.md` (bản sao `content/zh/*.md` + `draft: true`); xác nhận tập tên file bằng nhau (data-model.md › Trang sách.slug) và front matter bất biến giữ nguyên (data-model.md › Trang sách.translationKey, Trang sách.weight, Trang sách.book_kind, Trang sách.book_number, Trang sách.book_part, Trang sách.type, Trang sách.layout, Trang sách.cascade, Trang sách.outputs)
- [X] T009 [US1] Dịch front matter hiển thị của 24 trang trong `content/vi/*.md`: `title`, `linkTitle`, `description`, `search_keywords` sang tiếng Việt (tham khảo `content/en/` cho tiêu đề chương); không đụng khóa bất biến và thân trang (data-model.md › Trang sách.title)
- [X] T010 [P] [US1] Tạo `i18n/vi.yaml`: đủ mọi khóa có trong `i18n/zh.yaml` và `i18n/v2.yaml`, dịch sang tiếng Việt (research R4)
- [X] T011 [P] [US1] Tạo `data/home/vi.yaml` dịch từ `data/home/zh.yaml`: giữ nguyên danh sách `sections` và cấu trúc; phần legal/people ghi tác giả gốc, bản dịch tiếng Trung (Vonng và cộng sự), nhóm dịch tiếng Việt, giấy phép CC BY 4.0; bỏ section `repository-cards`/`ddia-contributors` nếu chúng trỏ dữ liệu của repo Vonng (FR-012)
- [X] T012 [P] [US1] Tạo `data/footer/vi.yaml` dịch từ `data/footer/zh.yaml`, link repo trỏ `https://github.com/nguyendan07/ddia`
- [X] T013 [US1] Chạy `make vi-build` với `--printI18nWarnings --printPathWarnings`; sửa đến khi không còn cảnh báo i18n thiếu khóa `vi` và không lỗi build (bổ sung `i18n/vi.yaml` nếu OINK cần thêm khóa)
- [X] T014 [US1] Chạy kịch bản S1 và S3 của `quickstart.md`: `make vi-dev` hiển thị trang chủ/mục lục/14 chương tiếng Việt với banner nháp, tự tải lại khi sửa; HTML không chứa `googletagmanager`/`giscus`; `make vi-build` không sinh `public/ch2/index.html`. Hoàn tác mọi thay đổi thử trên `content/vi/ch1.md`

**Checkpoint**: US1 hoàn chỉnh — MVP dùng được cho người dịch

---

## Phase 4: User Story 3 — Kiểm tra cấu trúc bản dịch (P2)

Làm trước US2 vì workflow CI gọi `make vi-check`.

**Goal**: Một lệnh báo mọi sai lệch cấu trúc vi ↔ zh.

**Independent Test**: kịch bản S2 trong `quickstart.md`.

- [X] T015 [US3] Viết test `bin/tests/test_check_vi.py` (unittest, stdlib) theo `contracts/check-vi.md` › Kiểm thử: dựng cây tạm `content/zh`, `content/vi`, `static/`; một ca khớp hoàn toàn → mã 0; mỗi `kind` trong data-model.md › Báo cáo kiểm tra.kind (`missing-page`, `extra-page`, `front-matter`, `anchor`, `heading`, `shortcode`, `xref-target`, `footnote`, `url`, `image`, `duplicate-id`) có một ca → mã 1 và dòng báo cáo chứa đúng kind; thiếu `content/zh` → mã 2. Test phải đỏ trước T016
- [X] T016 [US3] Viết `bin/check-vi.py` theo `contracts/check-vi.md`: import `ATTR`, `SC`, `ID`, `HEAD`, `MDIMAGE` từ `bin/check-translation.py` (qua `importlib` vì tên file có dấu gạch); áp luật data-model.md › Phần tử cấu trúc.anchor, .heading, .fig/tbl/eg, .xref, .footnote-ref, .footnote-def, .url, .image và so front matter theo data-model.md › Trang sách (khóa bất biến phải bằng zh, khóa dịch được phép khác, `draft` chỉ có ở vi); bỏ qua code fence; định dạng đầu ra, dòng tóm tắt, `--json`, `SLUG ...` và mã thoát 0/1/2 đúng contract. Thêm target `vi-check` vào `Makefile` (khối vi): `python3 bin/check-vi.py` + `python3 -m unittest discover -s bin/tests -p 'test_check_vi.py'` + `vi-build` với `--printPathWarnings --printI18nWarnings` + `python3 bin/check-rendered-links.py --all`
- [X] T017 [US3] Chạy `python3 -m unittest discover -s bin/tests -p 'test_check_vi.py' -v` (xanh) và `python3 bin/check-vi.py` trên 24 stub → `checked 24 pages: OK (24 drafts, 0 done)` trong < 30 s; chạy phần lỗi cố ý của S2 để xác nhận mã 1, rồi hoàn tác
- [X] T018 [US3] Chạy `make vi-check`. Nếu `check-rendered-links.py --all` không xử lý được site chỉ có `vi` (research R8): sửa tối thiểu `bin/check-rendered-links.py` (thêm `vi` vào `LANGUAGES`, bỏ hard-code `'zh'` làm ngôn ngữ không tiền tố), ghi chú để gửi PR upstream

**Checkpoint**: `make vi-check` xanh trên máy local

---

## Phase 5: User Story 2 — Độc giả đọc trên GitHub Pages (P2)

**Goal**: Push `main` → build, kiểm tra, deploy tự động; lỗi thì không deploy.

**Independent Test**: kịch bản S5 + S6 trong `quickstart.md`.

- [X] T019 [US2] Chạy kịch bản S5 (`make vi-build BASE_URL=http://localhost:8000/ddia/` + `python3 -m http.server`): CSS, ảnh `fig`, ảnh `/map/…`, xref, mục lục tải đúng dưới `/ddia/`. Nếu link Markdown tuyệt đối (`](/map/…)`, `](/chN)`) vỡ: sửa bằng render hook trong `layouts/_markup/` (file mới, dùng `relURL`), không sửa nội dung (research R9)
- [X] T020 [US2] Tạo `.github/workflows/pages.yml` theo `contracts/make-targets.md` › GitHub Actions: trigger `pull_request`/`push` → `main`/`workflow_dispatch`; job `build` (checkout, `actions/setup-go`, tải `hugo_0.170.1_linux-amd64.tar.gz`, `actions/configure-pages`, `make vi-check vi-build BASE_URL=${{ steps.pages.outputs.base_url }}/`, `actions/upload-pages-artifact` với `public/`); job `deploy` chỉ khi `github.ref == 'refs/heads/main'`, `needs: build`, `actions/deploy-pages`, environment `github-pages`; `permissions: contents: read, pages: write, id-token: write`; `concurrency: {group: pages, cancel-in-progress: false}`; pin action theo SHA như `.github/workflows/repository-cards.yml`
- [X] T021 [US2] Hướng dẫn chủ repo bật Settings › Pages › Source = GitHub Actions trên `nguyendan07/ddia`, rồi (khi được phép push) chạy kịch bản S6: push `main` → `build` + `deploy` xanh, `https://nguyendan07.github.io/ddia/` hiển thị; trang nháp trả 404

**Checkpoint**: Site công khai hoạt động

---

## Phase 6: Polish

- [X] T022 [P] Tạo `.github/README.md` tiếng Việt (FR-014, research R12): giới thiệu, ghi công/giấy phép, yêu cầu (Hugo 0.170.1, Go, Python), `make stubs`/`vi-dev`/`vi-check`, quy trình dịch một chương (dịch tại chỗ, xóa `draft`, chạy `vi-check`), cách pull upstream (`git pull upstream main` rồi `make vi-check`)
- [X] T023 [P] Cập nhật `CLAUDE.md` mục "Lệnh": thêm `make stubs`, `make vi-dev`, `make vi-build`, `make vi-check`, cách chạy riêng `test_check_vi.py`; xóa câu "dự kiến" về overlay nếu T006 đã xác nhận
- [X] T024 Chạy toàn bộ `quickstart.md` (S0–S5) một lượt từ trạng thái sạch; xác nhận `git status` chỉ có các file liệt kê trong plan.md › Source Code (không có `public/`, `tmp/`, `resources/_gen/`)

---

## Dependencies & Execution Order

```text
Setup (T001–T004) → Foundational (T005–T007) → US1 (T008–T014) → US3 (T015–T018) → US2 (T019–T021) → Polish (T022–T024)
```

- T006 phụ thuộc T005; T007 phụ thuộc T001.
- US1: T008 → T009; T010/T011/T012 song song với nhau và với T008–T009; T013 sau tất cả; T014 sau T013.
- US3 chỉ cần T008 (có stub để chạy thật); về logic độc lập với T009–T014 nên có thể làm song song với US1 sau T008.
- US2 cần `make vi-check` (T016–T018) vì workflow gọi nó.
- T022, T023 song song với nhau; T024 cuối cùng.

## Parallel Examples

```text
# US1, sau T008:
T010 i18n/vi.yaml   |   T011 data/home/vi.yaml   |   T012 data/footer/vi.yaml   |   T009 front matter

# Sau T008, hai luồng:
Luồng A: T009 → T013 → T014        Luồng B: T015 → T016 → T017

# Polish:
T022 .github/README.md   |   T023 CLAUDE.md
```

## Implementation Strategy

1. **MVP = Phase 1–3** (đến T014): người dịch đã có site xem trước tiếng Việt và có thể bắt đầu dịch chương 1.
2. Thêm US3 (T015–T018): mỗi lần dịch có lưới an toàn cấu trúc.
3. Thêm US2 (T019–T021): xuất bản công khai khi đã có chương dịch xong đầu tiên.
4. Polish.
