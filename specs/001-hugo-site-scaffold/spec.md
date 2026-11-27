# Feature Specification: Dựng khung site bản dịch tiếng Việt DDIA v2

**Feature Branch**: `001-hugo-site-scaffold`

**Created**: 2026-11-27

**Status**: Draft

**Input**: User description: "Dựng site Hugo (v0.170) + OINK cho bản dịch tiếng Việt DDIA v2, cấu trúc content/vi giống ../ddia/content/zh, deploy GitHub Pages qua GitHub Actions, kèm kiểm tra cấu trúc bản dịch"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Người dịch xem trước site cục bộ (Priority: P1)

Người dịch clone repo, chạy một lệnh duy nhất và xem được site sách tiếng Việt trên máy:
trang chủ, mục lục, đủ 24 trang (lời nói đầu, 3 phần, 14 chương, thuật ngữ, chỉ mục,
colophon, đóng góp…) với cùng thứ tự và cách điều hướng như bản tiếng Trung. Trang chưa dịch
hiển thị rõ là "đang dịch" trong chế độ xem trước.

**Why this priority**: Không có khung site thì không thể dịch và xem kết quả từng chương; đây là
nền tảng của mọi công việc sau.

**Independent Test**: Trên máy sạch có công cụ yêu cầu, clone repo → chạy lệnh xem trước → mở
trình duyệt thấy trang chủ, mục lục liệt kê 14 chương, bấm vào từng chương mở được trang.

**Acceptance Scenarios**:

1. **Given** repo vừa clone, **When** người dịch chạy lệnh xem trước, **Then** site hiển thị tại
   địa chỉ cục bộ trong vòng 1 phút với giao diện tiếng Việt (menu, nút, nhãn).
2. **Given** site đang chạy xem trước, **When** người dịch sửa nội dung một chương, **Then** trang
   tự cập nhật mà không cần khởi động lại.
3. **Given** một chương chỉ có khung (chưa dịch), **When** xem trước, **Then** trang vẫn xuất
   hiện và được đánh dấu là bản nháp/đang dịch.

---

### User Story 2 - Độc giả đọc sách trên web công khai (Priority: P2)

Mỗi khi nhánh chính được cập nhật, site được xây dựng và xuất bản tự động lên GitHub Pages.
Độc giả truy cập địa chỉ công khai và chỉ thấy các trang đã dịch xong; trang nháp không xuất hiện.

**Why this priority**: Mục tiêu cuối của dự án là bản dịch có thể đọc công khai, nhưng chỉ có giá
trị khi đã có ít nhất một chương dịch xong.

**Independent Test**: Đổi một trang sang trạng thái hoàn tất, đẩy lên nhánh chính → trong vòng
10 phút trang đó xuất hiện ở địa chỉ công khai; trang nháp trả về không tồn tại.

**Acceptance Scenarios**:

1. **Given** một commit mới trên nhánh chính, **When** quy trình xuất bản chạy xong, **Then**
   site công khai phản ánh commit đó.
2. **Given** quy trình xây dựng thất bại (lỗi build hoặc kiểm tra), **When** commit được đẩy lên,
   **Then** site công khai giữ nguyên phiên bản trước và người duy trì nhận được trạng thái thất bại.
3. **Given** site được phục vụ dưới đường dẫn con của GitHub Pages, **When** độc giả bấm mọi
   link nội bộ, hình ảnh, CSS, **Then** tất cả tải đúng (không có link vỡ do sai đường dẫn gốc).

---

### User Story 3 - Kiểm tra cấu trúc bản dịch tự động (Priority: P2)

Người dịch (và CI) chạy một lệnh kiểm tra để biết mỗi trang tiếng Việt có còn khớp cấu trúc với
trang tiếng Trung tương ứng hay không: front matter giữ nguyên các khóa bất biến, đủ anchor/ID,
hình, bảng, tham chiếu chéo, footnote, link tham khảo. Báo cáo chỉ rõ file, vị trí và sai lệch.

**Why this priority**: Thực thi Nguyên tắc II và IV của constitution; bắt lỗi trước khi xuất bản.

**Independent Test**: Cố ý xóa một footnote và đổi một anchor trong một chương → chạy kiểm tra →
lệnh báo đúng 2 lỗi với tên file và thất bại; hoàn tác → lệnh thành công.

**Acceptance Scenarios**:

1. **Given** mọi trang khớp cấu trúc, **When** chạy kiểm tra, **Then** lệnh thành công và in tóm tắt.
2. **Given** một trang thiếu footnote hoặc anchor so với bản zh, **When** chạy kiểm tra, **Then**
   lệnh thất bại và liệt kê từng sai lệch (file, loại, giá trị mong đợi/thực tế).
3. **Given** một trang tiếng Việt không có trang zh tương ứng (hoặc ngược lại), **When** chạy
   kiểm tra, **Then** lệnh báo trang thừa/thiếu.
4. **Given** một xref trỏ tới anchor không tồn tại, **When** chạy kiểm tra, **Then** lệnh báo link vỡ.

---

### Edge Cases

- Trang còn ở trạng thái khung (nội dung chưa dịch): kiểm tra cấu trúc bỏ qua so khớp phần thân
  nhưng vẫn kiểm front matter; trang không được xuất bản.
- Bản zh ở upstream thay đổi sau khi đã dịch (thêm footnote, đổi anchor): kiểm tra phải báo sai
  lệch thay vì im lặng.
- Pull upstream làm thay đổi trang zh đã dịch: kiểm tra phải đỏ ở trang vi tương ứng.
- Footnote/anchor trùng lặp trong cùng một trang: báo lỗi.
- Hình ảnh được tham chiếu nhưng không tồn tại trong repo: báo lỗi.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Repo MUST chứa một trang tiếng Việt cho mỗi trang trong `content/zh/`
  (24 trang), cùng tên file và cùng các khóa front matter bất biến (`translationKey`, `weight`,
  `book_kind`, `book_number`, `book_part`, `type`, `layout`, `cascade`, `outputs`).
- **FR-002**: Trang chưa dịch MUST được đánh dấu bản nháp, hiển thị khi xem trước cục bộ và
  không được xuất bản lên site công khai.
- **FR-003**: Site MUST có giao diện tiếng Việt: tiêu đề sách, menu (Đọc, Mục lục, Thuật ngữ,
  Chỉ mục, Đóng góp), nhãn điều hướng, mô tả, chỉ dẫn tìm kiếm, bảng lệnh nhanh.
- **FR-004**: Site MUST hỗ trợ các tính năng đọc như bản upstream: mục lục, điều hướng chương
  trước/sau, tìm kiếm toàn văn, chế độ tối, xem in toàn sách, hình có thể phóng to, tham chiếu
  chéo hình/bảng có đánh số.
- **FR-005**: Toàn bộ hình minh họa của bản v2 MUST có sẵn trong site và được tham chiếu đúng.
- **FR-006**: Người dịch MUST xem trước site cục bộ bằng một lệnh, có tự tải lại khi sửa file.
- **FR-007**: Mỗi lần cập nhật nhánh chính MUST tự động build, chạy kiểm tra và xuất bản lên
  GitHub Pages; nếu build hoặc kiểm tra thất bại thì không xuất bản.
- **FR-008**: Mọi link nội bộ và tài nguyên MUST hoạt động khi site phục vụ dưới đường dẫn con
  của GitHub Pages lẫn khi phục vụ tại gốc tên miền.
- **FR-009**: Lệnh kiểm tra cấu trúc MUST so mỗi trang vi với trang zh tương ứng về: tập trang,
  khóa front matter bất biến, tập anchor/ID, số lượng và định danh hình/bảng/xref/footnote, URL
  tham khảo; và MUST báo xref trỏ tới anchor không tồn tại.
- **FR-010**: Lệnh kiểm tra MUST thoát với mã lỗi khác 0 khi có sai lệch, in báo cáo đọc được
  (file, loại lỗi, giá trị mong đợi/thực tế), và chạy được cả cục bộ lẫn trong CI bằng cùng lệnh.
- **FR-011**: Kiểm tra MUST chạy được chỉ với nội dung của repo (fork chứa sẵn `content/zh`), không cần repo nào khác.
- **FR-012**: Site MUST ghi công tác giả gốc, bản dịch tiếng Trung (Vonng và cộng sự) và nhóm dịch
  tiếng Việt, kèm thông tin giấy phép CC BY 4.0 ở trang chủ và colophon.
- **FR-013**: Sản phẩm build và file tạm MUST không được đưa vào version control.
- **FR-014**: Repo MUST có README tiếng Việt mô tả cách xem trước, kiểm tra và đóng góp.

### Key Entities

- **Trang sách**: một đơn vị nội dung (chương, phần, lời nói đầu, thuật ngữ…); thuộc tính: tên
  file, tiêu đề, khóa dịch, thứ tự, loại, số chương, phần; trạng thái nháp/hoàn tất.
- **Trang tham chiếu (zh)**: trang tương ứng trong bản tiếng Trung, là chuẩn cấu trúc để so khớp.
- **Phần tử cấu trúc**: anchor/ID, hình (số, id, nguồn), bảng, tham chiếu chéo, footnote, URL tham khảo.
- **Báo cáo kiểm tra**: danh sách sai lệch theo trang, mỗi mục gồm loại, vị trí, mong đợi, thực tế.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Người đóng góp mới xem trước được site cục bộ trong ≤ 10 phút kể từ khi clone, chỉ
  theo README.
- **SC-002**: 100% (24/24) trang của bản zh có trang vi tương ứng, xuất hiện đúng thứ tự trong mục lục.
- **SC-003**: Thay đổi trên nhánh chính xuất hiện trên site công khai trong ≤ 10 phút.
- **SC-004**: 0 link nội bộ hoặc tài nguyên vỡ trên site công khai.
- **SC-005**: Kiểm tra cấu trúc phát hiện 100% sai lệch được cố ý đưa vào trong bộ kịch bản kiểm
  thử (thiếu footnote, đổi anchor, thiếu hình, xref vỡ, trang thừa/thiếu) và không báo lỗi giả
  trên các trang khớp.
- **SC-006**: Kiểm tra cấu trúc toàn bộ 24 trang hoàn tất trong ≤ 30 giây.
- **SC-007**: Trang nháp không bao giờ xuất hiện trên site công khai.

## Assumptions

- Công cụ: Hugo Extended **0.170** (theo yêu cầu, mới hơn 0.168.0 của upstream) và theme OINK
  phiên bản do upstream pin trong `go.mod`. Constitution ghi "pin theo upstream"; lệch phiên bản
  này là quyết định có chủ đích và nên được ghi nhận bằng một bản sửa PATCH của constitution.
- Site chỉ có một ngôn ngữ (tiếng Việt, v2); không gồm bản v1, bản zh/tw hay bản tiếng Anh song song.
- Trang chưa dịch là bản sao trang zh có đánh dấu nháp (xem research R5); dịch nội dung nằm ngoài phạm vi.
- Xuất bản qua GitHub Pages với địa chỉ mặc định dạng project site (đường dẫn con); tên miền riêng,
  bình luận (giscus), analytics, EPUB, `llms.txt` nằm ngoài phạm vi feature này.
- Hình minh họa lấy nguyên từ upstream (`static/fig/`), không dịch chữ trong hình.
- Kiểm tra cấu trúc tái sử dụng hoặc chuyển thể từ script kiểm tra của upstream thay vì viết mới
  (Nguyên tắc V); bản zh dùng làm chuẩn được cố định theo một commit upstream xác định.
- Repo là fork `nguyendan07/ddia` của `Vonng/ddia` (đã chứa `content/zh`, ảnh, layout, theme); bản vi
  được thêm vào mà hạn chế tối đa sửa file upstream để còn pull upstream được.
