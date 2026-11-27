# Contract: target Makefile cho bản tiếng Việt

Append vào cuối `Makefile` upstream; target có sẵn (`dev`, `build`, `check`, …) không đổi và vẫn
phục vụ bản zh. Biến `VI_HUGO = $(PINNED_HUGO) --config hugo.yaml,hugo.vi.yaml`.

| Target | Hành vi |
|---|---|
| `make stubs` | Với mỗi `content/zh/*.md` chưa có trong `content/vi/`: chép sang và chèn `draft: true` vào front matter; không ghi đè; in tên file đã tạo |
| `make vi-dev` | `$(VI_HUGO) server -D --renderToMemory --bind 127.0.0.1 --port $(PORT)` — hiện trang nháp, tự tải lại |
| `make vi-build` | `$(VI_HUGO) --minify --cleanDestinationDir $(if $(BASE_URL),--baseURL $(BASE_URL))` → `public/` (không có trang nháp) |
| `make vi-check` | `python3 bin/check-vi.py` + `unittest` cho `test_check_vi.py` + `vi-build` với `--printPathWarnings --printI18nWarnings` + `bin/check-rendered-links.py --all` |

Biến: `PORT` (có sẵn, mặc định 1313), `BASE_URL` (mặc định trống; CI đặt URL GitHub Pages).
Không bật `--panicOnWarning`.

# Contract: GitHub Actions (`.github/workflows/pages.yml`)

| Sự kiện | Job | Kết quả |
|---|---|---|
| `pull_request` → `main` | `build` | Trạng thái kiểm tra trên PR; không deploy |
| `push` → `main`, `workflow_dispatch` | `build` → `deploy` | Site công khai cập nhật; `build` lỗi ⇒ không deploy |

`build`: checkout → setup Go → cài Hugo 0.170.1 → `configure-pages` →
`make vi-check vi-build BASE_URL=${{ steps.pages.outputs.base_url }}/` → `upload-pages-artifact public/`.
`deploy`: `deploy-pages`, environment `github-pages`. Quyền: `contents: read`, `pages: write`,
`id-token: write`. `concurrency: { group: pages, cancel-in-progress: false }`.
