# Research: Dựng khung site bản dịch tiếng Việt DDIA v2

Ngày: 2026-11-27 (cập nhật cùng ngày sau khi repo được chuyển thành fork).

**Bối cảnh mới**: repo hiện là fork `nguyendan07/ddia` của `Vonng/ddia`, đang ở commit upstream
`7954373` (2026-11-24). Mọi thứ của upstream — `content/zh`, `static/fig`, `static/map`, layout,
CSS, `data/`, `bin/`, `go.mod` (OINK v1.6.0) — đã có sẵn trong repo. Nguyên tắc chi phối mọi quyết
định bên dưới: **chỉ thêm file mới, gần như không sửa file upstream**, để `git pull upstream main`
không xung đột.

## R1. Phiên bản Hugo

- **Decision**: Hugo **0.170.1**, không cần Extended.
- **Rationale**: OINK v1.6.0 (pin trong `go.mod`) đòi `hugoVersion.min: 0.169.0`; ghi chú 0.168.0
  trong `AGENTS.md` đã cũ. CSS của OINK là CSS thuần.
- **Alternatives**: 0.168.0 — dưới mức tối thiểu của theme; loại.

## R2. Theme, layout, ảnh, CSS

- **Decision**: dùng nguyên những gì fork đã có. Không chép, không vendor gì thêm.
- **Rationale**: layout upstream không phụ thuộc ngôn ngữ — `layouts/book/landing.html` render
  `data/home/<lang>.yaml`; `ddia-legal.html` dùng `relLangURL`. Thêm ngôn ngữ `vi` chỉ cần thêm
  file data/i18n tương ứng.

## R3. Cấu hình ngôn ngữ `vi`: file overlay thay vì sửa `hugo.yaml`

- **Decision**: file mới `hugo.vi.yaml`, build bằng `hugo --config hugo.yaml,hugo.vi.yaml`. Overlay chứa:
  - `languages.vi` (`contentDir: content/vi`, `locale: vi-VN`, `weight: 0`, menus và command
    palette chuyển ngữ từ khối `zh`),
  - `defaultContentLanguage: vi`, `disableLanguages: [zh, tw, v1, v1_tw]` → site chỉ có tiếng Việt (spec),
  - tắt dịch vụ của upstream: `services.googleAnalytics.id: ""`, `params.comments.enable: false`,
  - `params.github_repo`/`github_project_repo` trỏ fork, `params.copyright` ghi nhóm dịch vi.
- **Rationale**: `hugo.yaml` upstream thay đổi thường xuyên; sửa trực tiếp sẽ xung đột mỗi lần pull.
  Overlay = 0 dòng diff trên file upstream. Không để GA/giscus của Vonng chạy trên site vi.
- **Rủi ro cần xác minh ở task đầu tiên**: thứ tự ưu tiên và deep-merge khi truyền nhiều `--config`
  (file bên phải phải ghi đè). Nếu Hugo không merge như mong đợi → phương án dự phòng: thêm khối
  `vi` trực tiếp vào `hugo.yaml` (chấp nhận xung đột khi pull).
- **Alternatives**: thêm `vi` thành ngôn ngữ thứ 5 bên cạnh zh/tw/v1 — site lẫn tiếng Trung, trái spec; loại.

## R4. i18n và trang chủ tiếng Việt

- **Decision**: file mới `i18n/vi.yaml` (từ khóa của `i18n/zh.yaml` + `i18n/v2.yaml`),
  `data/home/vi.yaml` (từ `data/home/zh.yaml`), `data/footer/vi.yaml` (từ `data/footer/zh.yaml`).
- **Rationale**: OINK không có `vi.yaml`; thiếu thì giao diện rơi về tiếng Anh (FR-003).
  Trang chủ chứa phần ghi công/giấy phép (FR-012).

## R5. Trang khung (stub) cho trang chưa dịch

- **Decision**: stub = **bản sao nguyên văn `content/zh/<slug>.md`** + `draft: true`. Người dịch
  thay chữ Hán bằng tiếng Việt tại chỗ, xóa `draft` khi xong.
- **Cách tạo**: một lần, bằng vòng lặp shell trong Makefile (`make stubs`): với mỗi file zh chưa có
  bản vi → chép và chèn `draft: true` sau dòng `---` đầu. Không cần script Python riêng.
- **Rationale**: kiểm tra cấu trúc chạy được trên mọi trang từ đầu; shortcode/anchor/footnote đã
  đúng chỗ; Hugo không xuất bản trang nháp ở build production (FR-002, SC-007).
- **Điều chỉnh so với spec**: Assumption "thân trang là ghi chú 'đang dịch'" được thay bằng bản sao zh.

## R6. Nguồn tham chiếu zh (FR-011)

- **Decision**: chuẩn so khớp là `content/zh/` **trong chính repo**. Bỏ file `UPSTREAM` và bước
  checkout upstream trong CI của plan cũ.
- **Rationale**: fork chứa sẵn zh; CI checkout repo là có tham chiếu. Commit chuẩn = commit hiện tại.
  Khi pull upstream làm zh thay đổi, kiểm tra cấu trúc sẽ đỏ ở các trang vi bị lệch — đúng hành vi
  mà Quy trình làm việc của constitution yêu cầu (đối chiếu trong commit riêng).

## R7. Kiểm tra cấu trúc vi ↔ zh

- **Decision**: file mới `bin/check-vi.py` (stdlib), import và tái sử dụng regex `ATTR`, `SC`, `ID`,
  `HEAD`, `MDIMAGE` từ `bin/check-translation.py` (module này import an toàn: "Importing this module
  does not read the repository"). Test: `bin/tests/test_check_vi.py`.
- **Rationale**: `check-translation.py` so `content/en` ↔ `content/zh` với luật riêng bản Trung;
  không sửa nó (tránh xung đột), chỉ dùng lại định nghĩa cú pháp.
- **Alternatives**: thêm tham số `--target content/vi` vào script upstream — diff vào file upstream
  hay đổi; loại.

## R8. Kiểm tra link sau render

- **Decision**: dùng nguyên `bin/check-rendered-links.py`. Cần một thay đổi nhỏ: tuple
  `LANGUAGES` chưa có `vi` và logic "ngôn ngữ mặc định không có tiền tố" đang hard-code `'zh'`.
  Thử trước `--all` (kiểm mọi trang render, không cần biết ngôn ngữ). Nếu `--all` đủ → không sửa
  gì; nếu không → sửa 2 dòng (thêm `vi`, thay `'zh'` bằng tham số), ghi lại để gửi PR upstream.
- Đường dẫn con GitHub Pages: kiểm tra trên bản build với `baseURL` gốc `/` (link nội bộ phải đúng),
  và chạy riêng một lần dưới `/ddia/` trong quickstart S5.

## R9. Đường dẫn con của GitHub Pages (FR-008)

- **Decision**: CI build với `--baseURL "${{ steps.pages.outputs.base_url }}/"` (project site:
  `https://nguyendan07.github.io/ddia/`). Nội dung giữ link tuyệt đối kiểu upstream.
- **Rationale**: `xref` của OINK dùng `RelPermalink`, `fig` đi qua partial ảnh của theme. Rủi ro còn
  lại: link Markdown `](/map/…)` — S5 sẽ phát hiện.

## R10. Workflow GitHub Actions

- **Decision**: file mới `.github/workflows/pages.yml`: `pull_request`, `push` → `main`,
  `workflow_dispatch`. Job `build`: checkout, setup Go, tải Hugo 0.170.1 từ release chính thức,
  `make vi-check`, `make vi-build BASE_URL=…`, `upload-pages-artifact`. Job `deploy`
  (`actions/deploy-pages`) chỉ trên `main`. Pin action theo SHA như `repository-cards.yml`.
- `repository-cards.yml` của upstream: job `publish` đã có guard `github.repository == 'Vonng/ddia'`;
  job `check` chạy vô hại trên fork → để nguyên.

## R11. Makefile

- **Decision**: thêm target `vi-*` vào cuối `Makefile` upstream (`stubs`, `vi-dev`, `vi-build`,
  `vi-check`). Không đổi target có sẵn.
- **Rationale**: một khối append ở cuối file ít xung đột nhất; `make check` của upstream vẫn kiểm
  bản zh như cũ.
- **Alternatives**: Makefile riêng (`vi.mk`) — thêm một cách gọi phải nhớ (`make -f`); loại.

## R12. README tiếng Việt (FR-014)

- **Decision**: file mới `.github/README.md`. GitHub hiển thị `.github/README.md` thay cho
  `README.md` ở gốc.
- **Rationale**: `README.md` gốc bị workflow repository-cards của upstream cập nhật thường xuyên;
  không đụng vào để tránh xung đột.

## R13. File bị upstream `.gitignore` bỏ qua

- `.gitignore` upstream bỏ qua `CLAUDE.md` và `.claude`; `.specify/`, `specs/` đang untracked.
  Muốn version các file quy trình của dự án vi thì phải bỏ 2 dòng đó khỏi `.gitignore`
  (thay đổi nhỏ, chấp nhận). Đây là quyết định của chủ repo — xem câu hỏi trong báo cáo.

## Ghi chú triển khai (2026-11-27)

- **R3 xác nhận**: `--config hugo.yaml,hugo.vi.yaml` deep-merge, file bên phải thắng (`defaultContentLanguage`, `params.*`); GA bị xóa khỏi cấu hình. Không cần phương án dự phòng. Bỏ `versions`/`version_menu` (site một ấn bản; mục `url: '/'` sinh link thiếu base path).
- **R5 bổ sung**: banner nháp của OINK dựa vào `book_status: draft`, không phải `draft: true`; stub mang cả hai dòng (`check-vi` coi cả hai là khóa riêng của vi). `_index.md` và `toc.md` được dịch và xuất bản ngay để site công khai có trang chủ/mục lục.
- **R8**: không sửa `check-rendered-links.py`. `make vi-check` build **kèm nháp** vào `tmp/site/<sub-path>` và chạy `--all --public tmp/site --origin <origin>` → mọi link thiếu base path đều vỡ, nên S5 được kiểm tự động (18.640 link, 0 lỗi).
- **Lỗi upstream/OINK gặp dưới đường dẫn con**: logo footer bị lặp base path khi lấy từ `params.logo` (sửa bằng `brand.logo` trong `data/footer/vi.yaml`); footer link `#chapters` chỉ đúng ở trang chủ (vi dùng `/#chapters`); trang `_print` để nguyên link tới trang không có trong bản in (= trang nháp) — tự hết khi trang được xuất bản.
- **URL rule**: `check-vi` miễn so URL cho `_index` và `contrib` (link repo/phản hồi trỏ về fork).
- `make vi-dev` chạy với `--baseURL /` để xem tại `http://127.0.0.1:1313/`.
