# Feature Specification: Bảng thuật ngữ Anh–Việt dùng chung

**Feature Branch**: `002-glossary-en-vi`

**Created**: 2026-11-27

**Status**: Draft

**Input**: User description: "Xây dựng bảng thuật ngữ Anh–Việt dùng chung, thuật ngữ cho dân IT/DEV"

## Clarifications

### Session 2026-11-27

- Q: Chính sách mặc định khi term vừa có bản dịch Việt vừa quen dùng nguyên tiếng Anh? → A: Cân bằng theo thực tế dùng — dịch nếu bản Việt đã phổ biến; giữ nguyên nếu giới IT/DEV quen dùng tiếng Anh hơn; ghi lý do.
- Q: Bảng xuất bản cho người đọc hay chỉ nội bộ? → A: Xuất bản thành trang riêng trên site, tra hai chiều Anh→Việt và Việt→Anh, bên cạnh trang `glossary` của sách.
- Q: Đổi bản dịch đã có có bắt buộc sửa mọi chương đã dịch không? → A: Có, trong cùng thay đổi; kiểm tra tự động chặn nếu còn chương dùng bản dịch cũ.
- Q: Mức kiểm tra tự động độ nhất quán giữa chương và bảng? → A: Kiểm tra bảng (trùng, thiếu trường, nhiều bản dịch không ngữ cảnh) và các cặp `*thuật ngữ* (*english term*)` ở lần đầu trong chương phải khớp bảng; không quét toàn văn.
- Q: Khởi tạo bảng thế nào để phủ đủ term? → A: Tự động trích danh sách term (glossary sách và term in nghiêng `(*english term*)`) làm khung; bản dịch do người dịch điền hoặc duyệt, không sinh bản dịch tự động.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Người dịch tra thuật ngữ trước khi dịch (Priority: P1)

Người dịch gặp một thuật ngữ tiếng Anh (ví dụ "replication lag", "quorum", "idempotent") khi dịch một chương. Họ mở bảng thuật ngữ, tìm term và biết ngay: dùng bản dịch tiếng Việt nào, hay giữ nguyên tiếng Anh, kèm ghi chú ngữ cảnh nếu có.

**Why this priority**: Nguyên tắc III của constitution đòi mọi thuật ngữ nằm trong một bảng duy nhất; thiếu bảng này thì thuật ngữ trôi nổi giữa các chương — lỗi phổ biến nhất của sách dịch kỹ thuật.

**Independent Test**: Lấy 20 term ngẫu nhiên từ `content/en/glossary.md`; người dịch tìm từng term trong bảng và trả lời được "dịch hay giữ nguyên, và dịch thế nào" trong dưới 30 giây mỗi term.

**Acceptance Scenarios**:

1. **Given** một term có trong bảng, **When** người dịch tìm theo tiếng Anh, **Then** thấy đúng một bản dịch tiếng Việt (hoặc quyết định "giữ nguyên tiếng Anh") và, nếu cần, ghi chú ngữ cảnh.
2. **Given** một term chưa có trong bảng, **When** người dịch muốn thêm, **Then** có quy trình rõ để đề xuất term mới mà không tạo bản dịch thứ hai cho cùng một term.

---

### User Story 2 - Người đọc là dân IT/DEV tra cứu thuật ngữ (Priority: P2)

Người đọc là lập trình viên/kỹ sư đọc bản tiếng Việt, gặp một thuật ngữ và muốn biết term tiếng Anh gốc (để tìm tài liệu, đọc docs, trao đổi với đồng nghiệp). Họ mở trang Bảng thuật ngữ trên site và tra theo cả hai chiều Anh→Việt và Việt→Anh.

**Why this priority**: Giá trị với người đọc cuối; dân IT thường làm việc song ngữ nên cần biết term gốc hơn là chỉ bản dịch.

**Independent Test**: Từ trang bảng thuật ngữ trên site đã build, tìm được một term bằng tiếng Anh và một term bằng tiếng Việt, mỗi lần dưới 10 giây.

**Acceptance Scenarios**:

1. **Given** trang Bảng thuật ngữ đã xuất bản, **When** người đọc tìm một term tiếng Anh, **Then** thấy bản dịch tiếng Việt và định nghĩa ngắn.
2. **Given** người đọc biết từ tiếng Việt, **When** tra ngược, **Then** tìm được term tiếng Anh tương ứng.

---

### User Story 3 - Kiểm tra tự động tính nhất quán thuật ngữ (Priority: P3)

Người bảo trì chạy lệnh kiểm tra (cục bộ và CI) để phát hiện: term trùng lặp trong bảng, một term tiếng Anh có hai bản dịch, hoặc chương dùng bản dịch khác với bảng.

**Why this priority**: Giữ bảng không bị mục nát khi số chương dịch tăng; nhưng bảng dùng được trước khi có kiểm tra tự động.

**Independent Test**: Cố ý thêm một term trùng vào bảng; lệnh kiểm tra báo lỗi nêu rõ term và vị trí.

**Acceptance Scenarios**:

1. **Given** bảng có hai dòng cùng term tiếng Anh với bản dịch khác nhau, **When** chạy kiểm tra, **Then** báo lỗi và thoát mã khác 0.
2. **Given** bảng hợp lệ, **When** chạy kiểm tra, **Then** thành công không cảnh báo.

---

### Edge Cases

- Term nhiều nghĩa theo ngữ cảnh (ví dụ "atomic" trong đồng thời vs. giao dịch): bảng phải cho phép nhiều nghĩa dưới một term, mỗi nghĩa ghi rõ ngữ cảnh — đây là ngoại lệ duy nhất được phép cho "một term một bản dịch".
- Term không có bản dịch phổ biến (tên sản phẩm, "B-tree", "SSTable", "Kafka"): ghi nhận là "giữ nguyên".
- Từ viết tắt (ACID, CAP, CRDT, 2PC): ghi dạng đầy đủ và cách dùng; không dịch dạng viết tắt.
- Viết hoa/thường, dấu gạch nối so với khoảng trắng: tra cứu không phân biệt. Số ít/số nhiều là hai mục riêng khi cần.
- Trang glossary của sách (`content/vi/glossary.md`) có định nghĩa riêng theo nguồn; bảng dùng chung không được làm sai lệch hay thay thế nội dung đó.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Dự án MUST có đúng một bảng thuật ngữ Anh–Việt dùng chung cho mọi chương.
- **FR-002**: Mỗi mục MUST gồm: term tiếng Anh, bản dịch tiếng Việt (hoặc đánh dấu "giữ nguyên tiếng Anh"), và ngữ cảnh khi term nhiều nghĩa.
- **FR-003**: Mỗi term tiếng Anh MUST có đúng một bản dịch, trừ term nhiều nghĩa có ngữ cảnh ghi rõ.
- **FR-004**: Bảng MUST bao phủ tối thiểu mọi term trong `content/en/glossary.md` và các term được in nghiêng kèm `(*english term*)` ở lần đầu trong các chương. Khung danh sách term MUST được trích tự động từ các nguồn này; bản dịch tiếng Việt MUST do người dịch điền hoặc duyệt (không dùng bản dịch sinh tự động chưa duyệt).
- **FR-005**: Chính sách mặc định MUST là cân bằng theo thực tế dùng: dịch term khi bản tiếng Việt đã phổ biến trong giới IT/DEV; giữ nguyên tiếng Anh khi giới này quen dùng term gốc hơn (ví dụ "cache", "commit", "shard", "leader"). Mỗi ca chọn giữ nguyên MUST có ghi chú lý do (xem FR-006).
- **FR-006**: Mỗi quyết định không hiển nhiên (giữ nguyên vs. dịch) SHOULD có ghi chú lý do ngắn.
- **FR-007**: Bảng MUST được xuất bản thành một trang riêng trên site (tách khỏi trang `glossary` của sách), tra được theo cả hai chiều Anh→Việt và Việt→Anh; link tới và từ trang này MUST hoạt động dưới đường dẫn con của site.
- **FR-008**: Có quy trình thêm/sửa term được ghi lại. Sửa một bản dịch đã có MUST kèm sửa mọi chương đã dịch dùng bản cũ trong cùng thay đổi; kiểm tra tự động (FR-009) MUST chặn thay đổi nếu còn cặp thuật ngữ lần đầu trong chương dùng bản cũ (các chỗ dùng khác trong văn bản do người dịch rà soát).
- **FR-009**: Có lệnh kiểm tra tự động, chạy được cục bộ và trong CI bằng cùng một lệnh, MUST: (a) phát hiện term trùng, term có nhiều bản dịch không ghi ngữ cảnh và dòng thiếu trường bắt buộc; (b) với mỗi cặp `*thuật ngữ* (*english term*)` ở lần xuất hiện đầu trong chương, nếu term tiếng Anh có trong bảng thì bản dịch MUST khớp bảng. Kiểm tra KHÔNG quét toàn văn chương tìm bản dịch cũ.
- **FR-010**: Bảng MUST không sửa file upstream (theo quy tắc vàng của dự án), ngoại trừ thêm vào cuối khối `vi-*` của `Makefile`; nằm trong file/thư mục có hậu tố `vi`.

### Key Entities

- **Mục thuật ngữ (Term entry)**: một term tiếng Anh, bản dịch tiếng Việt hoặc cờ "giữ nguyên", ngữ cảnh/loại từ, ghi chú lý do, (tùy chọn) định nghĩa ngắn, từ viết tắt/dạng đầy đủ.
- **Bảng thuật ngữ (Glossary)**: tập hợp mọi mục thuật ngữ; nguồn sự thật duy nhất cho người dịch và người đọc.
- **Đề xuất thay đổi**: yêu cầu thêm/sửa một mục, kèm lý do và các chương bị ảnh hưởng.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% term trong `content/en/glossary.md` có mặt trong bảng thuật ngữ.
- **SC-002**: Người dịch tra được một term trong dưới 30 giây; người đọc dưới 10 giây.
- **SC-003**: 0 term tiếng Anh có hai bản dịch mâu thuẫn không kèm ngữ cảnh (kiểm tra tự động thông qua).
- **SC-004**: Sau khi dịch xong 3 chương đầu, lệnh kiểm tra báo 100% cặp `*thuật ngữ* (*english term*)` ở lần đầu trong các chương đó khớp bảng (không có lỗi `mismatch`).
- **SC-005**: Rà soát bởi ít nhất một người đọc là dân IT/DEV: ≥ 90% bản dịch được đánh giá "tự nhiên, dùng được trong công việc".

## Assumptions

- Phạm vi: thuật ngữ trong sách DDIA 2e (cơ sở dữ liệu, hệ phân tán, xử lý dữ liệu), không phải từ điển IT tổng quát.
- Nguồn term: `content/en/glossary.md`, các term in nghiêng trong `content/en` và bản zh để đối chiếu.
- Bảng bằng tiếng Việt, người dùng chính: người dịch (một người hoặc nhóm nhỏ) và người đọc kỹ thuật tiếng Việt.
- Định nghĩa ngắn là tùy chọn; bản dịch term là bắt buộc.
- Thêm term mới theo từng chương trong quá trình dịch; không cần hoàn chỉnh trước khi bắt đầu dịch chương đầu tiên, nhưng phải đủ term của glossary sách (SC-001) trước khi xuất bản.
- Bảng không thay thế trang `glossary` của sách; hai thứ cùng tồn tại.
