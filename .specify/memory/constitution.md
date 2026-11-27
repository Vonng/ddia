<!--
Sync Impact Report
- Version change: 1.2.0 → 1.3.0 (MINOR: Principle III gains a table-driven exception — terms flagged `show_en`
  keep the English term beside the Vietnamese one at every occurrence)
- Previous: 1.1.0 → 1.2.0 (MINOR: license constraint materially changed)
- Modified sections: Ràng buộc kỹ thuật & bản quyền — license corrected from "CC Non-Commercial
  Share Alike 3.0" (stale value from upstream metadata.yaml) to CC BY 4.0 (upstream LICENSE and
  README); "không được dùng cho mục đích thương mại" removed (contradicts CC BY 4.0); added
  "MUST ghi đúng tên giấy phép" and scope note (translation only, not the original work)
- Modified principles: none | Added sections: none | Removed sections: none
- Deferred TODOs: none
-->

# DDIA Tiếng Việt (2nd Edition) Constitution

## Core Principles

### I. Trung thành với nguồn

- Bản dịch MUST dịch từ `content/zh/` (bản Trung giản thể v2) và MUST đối chiếu
  `content/en/` khi câu chữ mơ hồ hoặc bản zh có vẻ lệch nghĩa; khi mâu thuẫn, bản tiếng Anh thắng.
- Không được thêm, bớt hay diễn giải lại nội dung kỹ thuật. Chú thích của người dịch MUST được
  đánh dấu rõ ràng (ví dụ "Ghi chú người dịch") và tách khỏi văn bản gốc.
- Văn phong MUST là tiếng Việt tự nhiên, không dịch word-by-word từ tiếng Trung.

**Lý do**: người đọc tin rằng họ đang đọc Kleppmann & Riccomini, không phải người dịch.

### II. Tương đương cấu trúc 1:1

- Mỗi file `content/vi/<trang>.md` MUST tương ứng 1:1 với file cùng tên trong `content/zh/`.
- Front matter: chỉ được đổi `title` (và mô tả hiển thị); `translationKey`, `weight`, `book_kind`,
  `book_number`, `book_part` MUST giữ nguyên.
- Mọi anchor/ID (`<a id>`, `{#id}`), shortcode (`fig`, `xref`, `eg`) và thuộc tính của chúng,
  footnote `[^N]`, URL tham khảo MUST giữ nguyên; chỉ dịch `caption` và text hiển thị.
- Số lượng heading, hình, bảng, xref, footnote trong một chương MUST bằng với bản zh.

**Lý do**: cho phép tái sử dụng script kiểm tra của upstream và đồng bộ khi upstream sửa đổi.

### III. Thuật ngữ nhất quán

- Thuật ngữ kỹ thuật MUST được ghi `*thuật ngữ tiếng Việt* (*english term*)` ở lần xuất hiện đầu
  tiên trong mỗi chương, sau đó chỉ dùng thuật ngữ tiếng Việt. Ngoại lệ: mục trong bảng thuật ngữ có
  `show_en = true` (ví dụ các thuật ngữ "chỉ mục") MUST luôn ghi kèm tiếng Anh ở mọi lần xuất hiện,
  dạng `chỉ mục thưa (*sparse index*)`.
- Mọi thuật ngữ MUST được tra/ghi vào một bảng thuật ngữ duy nhất của dự án; một term tiếng Anh
  chỉ có một bản dịch trừ khi bảng ghi rõ ngoại lệ theo ngữ cảnh.
- Thuật ngữ không có bản dịch phổ biến (ví dụ tên sản phẩm, "B-tree", "SSTable") MUST giữ nguyên
  tiếng Anh thay vì tự chế.

**Lý do**: thuật ngữ trôi nổi giữa các chương là lỗi phổ biến nhất của sách dịch kỹ thuật.

### IV. Kiểm chứng tự động trước khi xuất bản

- Không chương nào được merge vào nhánh xuất bản nếu `hugo build` có lỗi hoặc kiểm tra cấu trúc
  (Nguyên tắc II) và kiểm tra link render thất bại.
- Cảnh báo Hugo MUST được hiển thị và xem xét; không bật `--panicOnWarning`.
- Kiểm tra là đọc-only và chạy được cục bộ lẫn trong CI bằng cùng một lệnh.

**Lý do**: tham chiếu chéo và footnote vỡ là lỗi người đọc thấy ngay và khó phát hiện bằng mắt.

### V. Tái sử dụng upstream, giữ đơn giản

- Repo là fork của `Vonng/ddia`. Toolchain (Hugo, theme OINK, shortcode, layout, script `bin/`)
  MUST dùng nguyên của upstream; chỉ viết mới khi upstream không có thứ tương đương, và lý do MUST
  được ghi trong plan.
- Phần tiếng Việt MUST nằm trong file mới (hậu tố/thư mục `vi`, ví dụ `hugo.vi.yaml`,
  `content/vi/`, `bin/check-vi.py`). File upstream chỉ được sửa bằng cách thêm vào cuối (ví dụ khối
  `vi-*` trong `Makefile`) hoặc khi plan ghi rõ lý do, để `git pull upstream main` không xung đột.
  Lỗi của upstream/OINK SHOULD được khắc phục phía vi (data/overlay) và báo lên upstream.
- Không thêm dependency, framework hay bước build mà site upstream không cần.
- Hình ảnh `static/fig/` dùng lại nguyên của upstream; không dịch hình raster.

**Lý do**: dự án là bản dịch, không phải sản phẩm phần mềm — mỗi dòng code tự viết và mỗi dòng sửa
file upstream là gánh nặng bảo trì.

## Ràng buộc kỹ thuật & bản quyền

- Site tĩnh build bằng Hugo (không cần Extended) ở phiên bản tối thiểu mà theme OINK pin trong
  `go.mod` yêu cầu — hiện OINK v1.6.0, Hugo 0.170.1 (OINK đòi ≥ 0.169.0). Khi pull upstream nâng
  OINK, phiên bản Hugo trong CI MUST được nâng theo.
- Triển khai lên GitHub Pages qua GitHub Actions, dưới đường dẫn con
  `https://nguyendan07.github.io/ddia/`; mọi link và tài nguyên MUST hoạt động dưới đường dẫn con.
- Bản dịch kế thừa giấy phép của upstream: Creative Commons Attribution 4.0 International
  (CC BY 4.0, file `LICENSE`); giấy phép chỉ áp dụng cho phần dịch, không cho nguyên tác.
  Trang chủ/colophon MUST ghi công tác giả gốc, bản dịch tiếng Trung (Vonng và cộng sự) và
  người dịch tiếng Việt, và MUST ghi đúng tên giấy phép.
- Không đưa vào Git: `public/`, `resources/_gen/`, `.hugo_build.lock`, artifact build, file nhị
  phân/dữ liệu lớn ngoài hình minh họa của sách.

## Quy trình làm việc

- Đơn vị công việc là một chương (hoặc một trang dùng chung như glossary, preface).
- Trình tự: dịch → cập nhật bảng thuật ngữ → chạy kiểm tra (Nguyên tắc IV) → review đọc lại
  toàn chương → merge → triển khai.
- Trang chưa dịch xong MUST mang `draft: true` (ẩn khỏi site production) và `book_status: draft`
  (banner nháp khi xem trước); xóa cả hai khi dịch xong. Trang khung là bản sao trang zh, tạo bằng
  `make stubs`.
- Khi upstream (`Vonng/ddia`, remote `upstream`) sửa chương đã dịch, thay đổi MUST được đối chiếu và áp dụng vào bản vi
  trong một commit riêng ghi rõ commit upstream tương ứng.

## Governance

- Constitution này có hiệu lực cao hơn mọi quy ước khác trong repo; `CLAUDE.md` chứa hướng dẫn
  vận hành chi tiết và không được mâu thuẫn với nó.
- Sửa đổi: đề xuất qua PR thay đổi file này, kèm Sync Impact Report và lý do; chủ dự án phê duyệt.
- Versioning theo SemVer: MAJOR khi bỏ/định nghĩa lại nguyên tắc; MINOR khi thêm nguyên tắc hoặc
  mở rộng đáng kể; PATCH khi sửa câu chữ.
- Mỗi plan (`/speckit-plan`) MUST có mục Constitution Check đối chiếu năm nguyên tắc trên; mọi vi
  phạm MUST được ghi lý do trong mục Complexity Tracking.

**Version**: 1.3.0 | **Ratified**: 2026-11-27 | **Last Amended**: 2026-11-27
