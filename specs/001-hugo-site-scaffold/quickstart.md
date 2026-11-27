# Quickstart & kịch bản kiểm chứng: 001-hugo-site-scaffold

## Điều kiện

Hugo **0.170.1**, Go ≥ 1.22, Python ≥ 3.11. Không cần repo nào khác — `content/zh` có sẵn trong fork.

## S0 — Xác minh overlay cấu hình (rủi ro R3, chạy đầu tiên)

```sh
hugo config --config hugo.yaml,hugo.vi.yaml | grep -E '^defaultcontentlanguage|^disablelanguages'
```

Mong đợi: `defaultcontentlanguage = 'vi'`, `disablelanguages = ['zh', 'tw', 'v1', 'v1_tw']`, và
`languages` vẫn giữ khối `vi` cùng các trường của upstream (merge, không thay thế).

## S1 — Xem trước cục bộ (US1, SC-001, SC-002)

```sh
make stubs && make vi-dev        # http://127.0.0.1:1313/
```

Mong đợi: trang chủ tiếng Việt; `/toc/` liệt kê lời nói đầu, 3 phần, 14 chương; mọi trang mở được
với banner nháp; không có tiếng Trung trong menu/nhãn; không có script Google Analytics/giscus trong HTML.
Sửa `content/vi/ch1.md` → trình duyệt tự tải lại. `make stubs` lần hai: không tạo file nào.

## S2 — Kiểm tra cấu trúc (US3, SC-005, SC-006)

```sh
python3 -m unittest discover -s bin/tests -p 'test_check_vi.py' -v   # pass
python3 bin/check-vi.py                    # "checked 24 pages: OK (24 drafts, 0 done)", < 30 s
# Cố ý: xóa dòng định nghĩa [^1] và đổi id="fig_dwh_etl" thành id="x" trong content/vi/ch1.md
python3 bin/check-vi.py ch1; echo $?       # ≥ 2 sai lệch (footnote, shortcode, xref-target), mã 1
git checkout content/vi/ch1.md
```

## S3 — Trang nháp không xuất bản (FR-002, SC-007)

```sh
make vi-build && test ! -e public/ch2/index.html && echo "draft hidden"
# Xóa dòng draft: true trong content/vi/ch1.md:
make vi-build && test -e public/ch1/index.html && echo "published"
```

## S4 — Toàn bộ kiểm tra như CI (FR-010)

```sh
make vi-check     # check-vi + test + build có cảnh báo + check-rendered-links: thành công
```

## S5 — Đường dẫn con GitHub Pages (FR-008, SC-004)

```sh
make vi-build BASE_URL=http://localhost:8000/ddia/
mkdir -p tmp/site && rm -rf tmp/site/ddia && cp -r public tmp/site/ddia
python3 -m http.server -d tmp/site 8000      # mở http://localhost:8000/ddia/
```

Mong đợi: CSS, ảnh `fig`, ảnh sơ đồ chương `/map/…`, xref và mục lục đều tải đúng dưới `/ddia/`
(`tmp/` đã nằm trong `.gitignore`).

## S6 — Xuất bản tự động (US2, SC-003)

1. GitHub › `nguyendan07/ddia` › Settings › Pages › Source = **GitHub Actions**.
2. Push vào `main` → `build` rồi `deploy` xanh; `https://nguyendan07.github.io/ddia/` cập nhật ≤ 10 phút.
3. PR có lỗi cấu trúc cố ý → `build` đỏ, không `deploy`; site không đổi.
