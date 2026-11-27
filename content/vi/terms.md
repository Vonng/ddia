---
draft: true
book_status: draft
translationKey: ddia-v2-terms
title: Bảng thuật ngữ Anh–Việt
book_kind: glossary
weight: 510
breadcrumbs: false
---

Bảng thuật ngữ dùng chung cho toàn bộ bản dịch: mỗi thuật ngữ tiếng Anh có một bản dịch tiếng Việt, hoặc được giữ nguyên tiếng Anh khi giới IT/DEV quen dùng từ gốc hơn (kèm lý do). Bảng này khác trang [Thuật ngữ](/glossary/) của sách, nơi giải nghĩa các khái niệm cốt lõi.

{{< terms >}}

## Cách đóng góp

Nguồn của bảng là file `data/glossary/vi.toml` trong [kho mã](https://github.com/nguyendan07/ddia).

- **Thêm thuật ngữ**: thêm một khối `[[term]]` (trường `en`, `vi`; thêm `keep = true` và `note` nếu giữ nguyên tiếng Anh; thêm `ctx` nếu thuật ngữ có nhiều nghĩa), chạy `python3 bin/glossary-vi.py check`, rồi gửi PR.
- **Sửa bản dịch đã có**: sửa mục trong `vi.toml` rồi sửa mọi chương dùng bản cũ ở lần xuất hiện đầu (dạng `*thuật ngữ* (*english term*)`) trong cùng PR; lệnh `check` liệt kê các chương còn lệch và chặn nếu còn sót.
- **Nguyên tắc**: dịch nếu bản tiếng Việt đã phổ biến; giữ nguyên nếu giới IT/DEV quen dùng tiếng Anh hơn, và ghi lý do.
