# Thiết kế các ứng dụng chuyên sâu về dữ liệu (Ấn bản thứ hai) — bản dịch tiếng Việt

[![Đọc trực tuyến](https://img.shields.io/badge/đọc_trực_tuyến-ấn_bản_2-slategray?style=flat)](https://nguyendan07.github.io/ddia/)

**Tác giả**: [Martin Kleppmann](https://martin.kleppmann.com) và [Chris Riccomini](https://cnr.sh/) — [*Designing Data-Intensive Applications, 2nd Edition*](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/) (O'Reilly).

**Nguồn dịch**: [bản dịch tiếng Trung](https://github.com/Vonng/ddia) của [冯若航 / Vonng](https://github.com/Vonng) và cộng sự — repo này là fork của nó. Bản tiếng Việt dịch từ bản tiếng Trung, đối chiếu với nguyên tác tiếng Anh.

**Đọc**: https://nguyendan07.github.io/ddia/ — các chương được xuất bản dần khi dịch xong.

## Mục lục

* [Lời nói đầu](https://nguyendan07.github.io/ddia/preface/)
* [Phần I: Nền tảng của hệ thống dữ liệu](https://nguyendan07.github.io/ddia/part-i/)
  1. [Đánh đổi trong kiến trúc hệ thống dữ liệu](https://nguyendan07.github.io/ddia/ch1/)
  2. [Định nghĩa yêu cầu phi chức năng](https://nguyendan07.github.io/ddia/ch2/)
  3. [Mô hình dữ liệu và ngôn ngữ truy vấn](https://nguyendan07.github.io/ddia/ch3/)
  4. [Lưu trữ và truy xuất](https://nguyendan07.github.io/ddia/ch4/)
  5. [Mã hóa và tiến hóa](https://nguyendan07.github.io/ddia/ch5/)
* [Phần II: Dữ liệu phân tán](https://nguyendan07.github.io/ddia/part-ii/)
  6. [Sao chép](https://nguyendan07.github.io/ddia/ch6/)
  7. [Phân mảnh](https://nguyendan07.github.io/ddia/ch7/)
  8. [Giao dịch](https://nguyendan07.github.io/ddia/ch8/)
  9. [Những rắc rối của hệ phân tán](https://nguyendan07.github.io/ddia/ch9/)
  10. [Nhất quán và đồng thuận](https://nguyendan07.github.io/ddia/ch10/)
* [Phần III: Dữ liệu dẫn xuất](https://nguyendan07.github.io/ddia/part-iii/)
  11. [Xử lý theo lô](https://nguyendan07.github.io/ddia/ch11/)
  12. [Xử lý luồng](https://nguyendan07.github.io/ddia/ch12/)
  13. [Triết lý của hệ thống xử lý luồng](https://nguyendan07.github.io/ddia/ch13/)
  14. [Làm điều đúng đắn](https://nguyendan07.github.io/ddia/ch14/)
* [Thuật ngữ](https://nguyendan07.github.io/ddia/glossary/) · [Chỉ mục](https://nguyendan07.github.io/ddia/indexes/) · [Lời kết](https://nguyendan07.github.io/ddia/colophon/)

## Cấu trúc repo

| Đường dẫn | Nội dung |
|---|---|
| `content/vi/` | Bản dịch tiếng Việt — mỗi trang tương ứng 1:1 với `content/zh/` |
| `content/zh/`, `content/en/` | Nguồn dịch (tiếng Trung) và nguyên tác (tiếng Anh) từ upstream |
| `hugo.vi.yaml` | Cấu hình tiếng Việt, phủ lên `hugo.yaml` của upstream |
| `i18n/vi.yaml`, `data/home/vi.yaml`, `data/footer/vi.yaml` | Giao diện, trang chủ, footer tiếng Việt |
| `bin/check-vi.py` | Kiểm tra cấu trúc trang vi so với trang zh |

Phần tiếng Việt nằm trong file mới; file của upstream giữ nguyên (trừ `README.md` này) để có thể `git pull upstream main`.

## Chạy cục bộ

Cần [Hugo](https://github.com/gohugoio/hugo/releases/tag/v0.170.1) **0.170.1** (bản thường là đủ), Go ≥ 1.22, Python ≥ 3.11.

```sh
make vi-dev      # xem trước tại http://127.0.0.1:1313/, hiện cả trang nháp, tự tải lại
make vi-check    # kiểm tra cấu trúc + test + build + link (giống CI)
make vi-build    # build bản xuất bản vào public/ (không có trang nháp)
```

## Đóng góp: dịch một chương

1. Mở `content/vi/chN.md`. Trang chưa dịch là bản sao trang tiếng Trung, có hai dòng `draft: true` và `book_status: draft`.
2. Dịch tại chỗ: thay chữ Hán bằng tiếng Việt, đối chiếu `content/en/chN.md` khi câu chữ mơ hồ (mâu thuẫn thì theo bản tiếng Anh).
   **Giữ nguyên** front matter (trừ `title`/`description`), mọi neo `<a id>`/`{#id}`, shortcode
   `{{< fig >}}`/`{{< xref >}}`/`{{< eg >}}` (chỉ dịch `caption` và chữ hiển thị), footnote `[^N]` và URL.
3. Thuật ngữ: lần đầu xuất hiện trong chương ghi `*thuật ngữ* (*english term*)`.
4. Chạy `make vi-check` cho đến khi xanh, xóa hai dòng nháp và gửi pull request.

Phát hiện lỗi dịch hoặc trình bày: mở [issue](https://github.com/nguyendan07/ddia/issues).

## Cập nhật từ upstream

```sh
git remote add upstream https://github.com/Vonng/ddia.git   # một lần
git config merge.ours.driver true                           # một lần: giữ README.md của fork khi merge
git pull upstream main
make stubs       # tạo trang nháp cho trang zh mới (nếu có)
make vi-check    # trang vi nào lệch so với zh mới sẽ báo lỗi → đối chiếu, sửa trong commit riêng
```

## Xuất bản

Mỗi lần push vào `main`, GitHub Actions (`.github/workflows/pages.yml`) chạy `make vi-check`, build và deploy lên GitHub Pages. Kiểm tra lỗi thì không deploy. Pull request chỉ chạy kiểm tra.

## Giấy phép

Bản dịch được thực hiện vì mục đích học tập, không theo đuổi lợi ích kinh tế. Giấy phép dưới đây chỉ áp dụng cho phần dịch; quyền đối với nguyên tác thuộc về tác giả và nhà xuất bản O'Reilly. Bạn đọc có khả năng đọc tiếng Anh xin hãy mua [sách gốc](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/) để ủng hộ tác giả.

Repo kế thừa giấy phép của bản dịch tiếng Trung: [CC BY 4.0](LICENSE) ([nội dung giấy phép](https://creativecommons.org/licenses/by/4.0/deed.vi)).
