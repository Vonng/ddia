# Contract: `data/glossary/vi.toml`

```toml
[[term]]
en = "atomic"
vi = "nguyên tử"
ctx = "giao dịch"
def = "Gom các thao tác ghi: hoặc tất cả được commit, hoặc tất cả bị rollback."

[[term]]
en = "atomic"
vi = "nguyên tử"
ctx = "đồng thời"

[[term]]
en = "shard"
vi = "shard"
keep = true
note = "Giới IT/DEV Việt Nam quen dùng nguyên từ gốc; 'mảnh' dễ nhầm với partition."

[[term]]
en = "sparse index"
vi = "chỉ mục thưa"
show_en = true

[[term]]
en = "backpressure"
vi = ""
status = "todo"
```

`show_en = true`: luôn ghi kèm `(*en*)` ở mọi lần xuất hiện trong văn bản (dạng `chỉ mục thưa (*sparse index*)`); `check` cảnh báo `show-en` khi thiếu.

Trường và ràng buộc: xem [data-model.md](../data-model.md). Shortcode đọc file qua `site.Data.glossary.vi.term`.
