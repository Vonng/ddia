# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Dự án

Bản dịch **tiếng Việt** của *Designing Data-Intensive Applications (2nd Edition)* — Martin Kleppmann & Chris Riccomini — xuất bản trên **GitHub Pages**.

Repo là **fork `nguyendan07/ddia` của `Vonng/ddia`** (bản dịch tiếng Trung, https://ddia.vonng.com). Mọi thứ của upstream — `content/zh` (nguồn dịch), `content/en` (bản gốc tiếng Anh), ảnh, layout, theme, script `bin/` — có sẵn trong repo. `AGENTS.md` là của upstream.

**Quy tắc vàng: thêm file mới, đừng sửa file upstream** (`hugo.yaml`, `README.md`, script `bin/` có sẵn, `content/zh` …), để `git pull upstream main` không xung đột. Phần tiếng Việt nằm trong file có hậu tố/thư mục `vi`.

Quy trình làm việc dùng Spec Kit: constitution ở `.specify/memory/constitution.md`, feature ở `specs/NNN-*/`.

## Kiến trúc

- **Hugo 0.170.1** + theme **OINK v1.6.0** (Hugo module, pin trong `go.mod`; OINK đòi Hugo ≥ 0.169 nên con số 0.168.0 trong `AGENTS.md` đã cũ). Cần Go để Hugo tải module.
- **Đa ngôn ngữ qua Hugo `languages`** trong `hugo.yaml`: mỗi bản có `contentDir` riêng (`content/zh` mặc định, `content/tw` sinh từ zh bằng OpenCC, `content/v1`, `content/v1_tw`). Bản vi dùng overlay `hugo.vi.yaml` (build bằng `--config hugo.yaml,hugo.vi.yaml`; Hugo deep-merge, file bên phải thắng): thêm ngôn ngữ `vi`, đặt làm mặc định, `disableLanguages` các ngôn ngữ khác, tắt GA/giscus của upstream, không có menu phiên bản. Site deploy dưới đường dẫn con `https://nguyendan07.github.io/ddia/` — link nào thiếu base path sẽ vỡ.
- Layout không phụ thuộc ngôn ngữ: trang chủ render `data/home/<lang>.yaml`, footer `data/footer/<lang>.yaml`, chuỗi UI ở `i18n/<lang>.yaml`.
- **Mỗi trang là một file Markdown** (`ch1.md` … `ch14.md`, `part-i/ii/iii.md`, `preface.md`, `glossary.md`, `indexes.md`, `toc.md`, `colophon.md`, `contrib.md`, `_index.md`). Front matter bất biến giữa các bản dịch: `translationKey`, `weight`, `book_kind`, `book_number`, `book_part` (và `type`, `layout`, `cascade`, `outputs` ở `_index.md`).
- **Shortcode OINK** trong nội dung — giữ nguyên, chỉ dịch `caption` và text hiển thị:
  - `{{< fig num="1-1" id="fig_dwh_etl" src="/fig/ddia_0101.png" caption="..." class="..." width="2953" height="2099" />}}`
  - `{{< xref fig="1-1" page="/ch1" anchor="fig_dwh_etl" >}}Hình 1-1{{< /xref >}}` (cũng có `tbl=`, và shortcode `eg`, `tbl`)
  - Anchor `<a id="...">` / `{#id}`, footnote `[^N]`, mục tham khảo cuối chương — giữ nguyên ID, số, URL.
- Ảnh: `static/fig/ddia_CCNN.png` (hình), `static/map/chNN.png` (sơ đồ chương).
- `bin/check-translation.py` so `content/en` ↔ `content/zh` (luật riêng bản Trung); module import an toàn, có thể dùng lại regex `ATTR`, `SC`, `ID`, `HEAD`, `MDIMAGE`. `bin/check-rendered-links.py` kiểm link trên `public/` đã build.

## Lệnh cho bản tiếng Việt (khối `vi-*` cuối `Makefile`)

```sh
make vi-dev       # hugo server -D tại http://127.0.0.1:1313/ (PORT=...), hiện trang nháp
make vi-check     # check-vi.py + test + build kèm nháp vào tmp/site/ddia/ + check-rendered-links (như CI)
make vi-build     # build xuất bản vào public/ (không nháp); BASE_URL=... để đổi baseURL
make stubs        # tạo trang nháp vi cho trang zh còn thiếu (không ghi đè)
python3 bin/check-vi.py ch1 glossary                                # kiểm vài trang
python3 -m unittest discover -s bin/tests -p 'test_check_vi.py'     # test của checker
```

`vi-check` build **kèm nháp** và gắn site vào đúng đường dẫn con để mọi link giữa các trang được kiểm; trang in `_print` để nguyên link tới trang nháp (lỗi OINK, tự hết khi trang được xuất bản). CI: `.github/workflows/pages.yml` (PR: kiểm tra; `main`: kiểm tra + deploy GitHub Pages).

Lỗi OINK 1.6.0 đã gặp dưới đường dẫn con: logo footer bị lặp base path nếu không khai báo `brand.logo` trong `data/footer/vi.yaml`.

## Lệnh có sẵn (upstream, phục vụ bản zh)

```sh
make build              # hugo build
make serve              # preview production
make check              # translation-check + hugo build strict + check-rendered-links
make translation-tests  # unit test bin/tests (cần uv)
python3 -m unittest bin/tests/test_translation_checks.py   # một file test
```

`make dev` cần OINK checkout tại `~/pgsty/oink` — không dùng được trên máy này. Không bật `--panicOnWarning` / `HUGO_PANICONWARNING`.

## Quy ước dịch

- Dịch từ `content/zh/<slug>.md`, đối chiếu `content/en/<slug>.md` khi mơ hồ; mâu thuẫn thì theo bản tiếng Anh.
- Trang vi khởi đầu là bản sao trang zh có `draft: true`; dịch tại chỗ, xóa `draft` khi xong. `check-vi.py` yêu cầu URL giống zh, trừ `_index` và `contrib` (link repo trỏ về fork).
- Tên sách tiếng Việt: *Thiết kế các ứng dụng chuyên sâu về dữ liệu*; tên chương thống nhất với `data/home/vi.yaml`.
- Giá trị YAML trong front matter không được chứa `: ` không có ngoặc (bản zh dùng dấu `：` full-width) — dùng `—` hoặc đặt trong ngoặc kép.
- Thuật ngữ: bản zh ghi `*术语*（*english term*）` ở lần đầu; bản vi dùng `*thuật ngữ* (*english term*)` với ngoặc ASCII.
- Không đưa vào Git: `public/`, `resources/_gen/`, `.hugo_build.lock`, artifact build, file lớn (`AGENTS.md`).
- `.gitignore` upstream bỏ qua `CLAUDE.md` và `.claude/`.
