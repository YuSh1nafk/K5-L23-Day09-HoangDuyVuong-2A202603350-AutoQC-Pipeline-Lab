# Báo cáo Day 09 — <Họ và tên>, <MSHV>

> Xoá mọi `TODO(học viên)` và dòng gợi ý. Mỗi ý trả lời bằng **số lấy từ `submission/reports/`**, kèm mẫu số. Cả báo cáo ~1–2 trang.

## 1. Kết luận trước
kết luận: HOLD — 60/205 ảnh còn cảnh báo (29.3%), đạt/vượt ngưỡng 10.0%; cần duyệt thêm.
## 2. Lỗi và phân việc
Lấy từ `02_error_list_v1` (gom theo mã lỗi). Cột "ai sửa": **máy** (autofix) hay **người** (hàng đợi); chỉ ghi những mã có mặt trong lô của bạn.

| Mã lỗi | Số ảnh/dòng | Ai sửa (máy/người) | Vì sao |
|---|---:|---|---|
| BAD_CLASS_ID | 6 dòng (6 ảnh) | Máy | Id lớp (93, -1, 7, 4) không có trong danh sách, không đoán lại được nên xóa dòng. Nếu vật có thật, nó sẽ hiện ở POSSIBLE_MISSING. |
| BAD_CLASS_NAME | 2 dòng (data.yaml: 'Person', 'Bus') | Máy | Tên lớp lệch so với danh sách chuẩn trong cfg["classes"], nên đổi tên theo cấu hình. |
| BAD_FORMAT | 3 dòng (img_0014, img_0022: nan/inf; img_0179: thiếu cột) | Máy | Dòng hỏng không đọc được, nên xóa dòng. |
| BAD_SIZE | 3 ảnh (img_0107, img_0122: 180px; img_0113: 226px; ngưỡng 250px) | Người* | Ảnh nhỏ hơn ngưỡng. Loại hay giữ phụ thuộc bài toán. |
| BOX_OUT_OF_IMAGE | 8 dòng | Máy | Mức tràn 0.023 đến 0.06, nên cắt box vào trong ảnh. Box nằm hẳn ngoài ảnh thì xóa. |
| BOX_ZERO | 4 dòng | Máy* | Box rộng hoặc cao bằng 0 không còn thông tin vị trí, nên xóa dòng. |
| CORRUPT_IMAGE | 2 ảnh (img_0010, img_0136) | Người* | Ảnh không mở được. Nên thử tải lại ảnh gốc trước khi xóa, vì xóa là mất cả nhãn. |
| DUP_BOX | 7 dòng | Máy | Xóa dòng sau, giữ dòng trước (cùng lớp, IoU cao). |
| DUP_IMAGE_EXACT | 8 ảnh | Máy | Trùng từng byte với ảnh khác, nên xóa ảnh trùng cùng nhãn của nó. |
| DUP_IMAGE_NEAR | 2 ảnh (img_0076↔0042, img_0143↔0037, phash 0) | Người* | Hai ảnh rất giống nhưng không trùng byte. Cần xem ảnh nào có nhãn đầy đủ hơn để giữ. |
| LEAK_TEST | 4 ảnh (img_0049, 0167, 0174, 0221) | Máy | Ảnh trùng với kho test/val làm điểm đánh giá sai, nên xóa khỏi tập train. |
| MISSING_LABEL_FILE | 6 ảnh (img_0031, 0053, 0126, 0135, 0170, 0219) | Người | Không tạo file nhãn rỗng, vì rỗng nghĩa là "ảnh nền". Phải gán nhãn thật. |
| BOX_HUGE | 3 dòng (img_0018, 0128, 0196) | Người | Có thể đúng (vật sát camera) hoặc nhãn quá lớn. Chỉ nhìn ảnh mới biết. |
| BOX_TINY | 6 dòng (4 ảnh; img_0161 có 3 dòng) | Người | Vật nhỏ thật hay nhãn rác, cần xem ảnh. |
| CLASS_RARE | 4 lớp (-1, 4, 7, 93) | Máy (gián tiếp) | Bốn lớp này chính là các id lỗi của BAD_CLASS_ID, nên sẽ hết khi xóa các dòng sai và chạy lại. |
| EMPTY_LABEL | 12 ảnh | Người | Ảnh nền thật hay thiếu nhãn thì chỉ người nhìn ảnh mới phân biệt được. |
| POSSIBLE_FALSE_POS | 29 dòng (27 ảnh) | Người | Model chỉ gợi ý. Có 9 dòng trùng dòng lỗi máy sẽ sửa (img_0030:9, 0050:1, 0066:3, 0078:2, 0092:2, 0108:1, 0144:1, 0185:10, 0204:1) nên có thể tự hết. |
| POSSIBLE_LOOSE_BOX | 45 cảnh báo (37 ảnh) | Người | Box lệch hay quá lỏng, cần chỉnh theo mắt. |
| POSSIBLE_MISSING | 152 cảnh báo (86 ảnh) | Người | Model thấy vật chưa gán nhãn. Số lượng lớn, nên hiệu chỉnh second_opinion.conf trước rồi mới duyệt. |
| POSSIBLE_WRONG_CLASS | 22 cảnh báo (21 ảnh) | Người | Cần xem ảnh để quyết định lớp đúng. |

TODO(học viên): vì sao `05_review_queue.csv` xếp ảnh đầu hàng như vậy? Với ngân sách 80 ảnh, người xem được bao nhiêu lỗi ngữ nghĩa?

## 3. Calibration (2 ngưỡng)
| Tham số | Khởi đầu | Đã chọn | Precision / Recall (trước → sau) | Lý do (đánh đổi) |
|---|---|---|---|---|
| `duplicates.phash_dist` | 2 | TODO(học viên) | | |
| `second_opinion.conf` | 0.25 | TODO(học viên) | | |

TODO(học viên): **một chỗ calibration có thể đánh lừa bạn**, kèm bằng chứng từ dữ liệu của bạn (vd. mở xem vài cặp ảnh bị cho là trùng; số ảnh bị loại ở bước 1 có hợp lý không?).

## 4. Cửa chặn và điều pipeline KHÔNG bắt được
TODO(học viên): (a) chứng minh gate chặn đúng: chạy `python -m pipeline.run --budget 0 --reports work/rep_nb --export-dir work/exp_nb` (không có người duyệt nên ảnh thiếu file nhãn còn nguyên), chỉ ra kết luận **Rework**, mã thoát 20 và việc **không xuất** dataset. (Đừng sửa tay `work/run/ds`: pipeline dựng lại thư mục này từ raw mỗi lần chạy.) (b) ≥ 2 điểm mù có bằng chứng (box lỏng nhẹ, nhầm lớp mà model lớn cũng nhầm, ảnh trùng biến đổi mạnh…).
Bước 5/5  KHÔNG xuất: còn lỗi bắt buộc (Rework) — trả về bước 3
## 5. Train: raw vs clean (tùy chọn, chấm riêng)
Chưa train: ghi "chưa chạy" và lý do, rồi bỏ qua phần còn lại của mục này. Nếu đã train: dán bảng từ `submission/results/comparison.md` (model, epoch, seed, số ảnh train mỗi biến thể).

TODO(học viên): chênh mAP50 (clean − raw) so với **độ lệch chuẩn giữa các seed**; kết luận **trung thực** (nằm trong nhiễu thì nói là chưa kết luận được); ≥ 2 giả thuyết giải thích (ảnh trùng/rò rỉ test trong `raw`, nhãn máy còn lại trong `clean`, test chỉ 100 ảnh…) và cách kiểm.

## 6. Quyết định và ghi chú AI
TODO(học viên): (a) quyết định cuối; nếu Hold/Rework cần làm gì để thành Release? (b) Dùng AI viết code? Ghi 3 dòng: prompt chính, cách bạn kiểm code AI, 1 lần AI sai. Không dùng: ghi "không dùng".

*(Thưởng +2, tùy chọn)* CVAT: lọc `width < 20`, ảnh/số box khớp, đối chiếu `BOX_TINY` (xem docs/CVAT_FILTER.md), 1 câu về `can_review`.
