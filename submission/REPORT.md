# Báo cáo Day 09 — Hoàng Duy Vương, 2A202603350


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

Hàng đợi được xếp bằng trọng số trong `cfg["review"]`; các mã `POSSIBLE_WRONG_CLASS` và `POSSIBLE_MISSING` có trọng số cao, kèm confidence cho issue model nên ảnh nhiều mã/ngữ nghĩa có priority cao. Ảm ưu tiên đầu gồm `img_0160` (35.692), `img_0127` (22.753), `img_0020` (17.449). Ngân sách 80 ảnh đã duyệt; chủ yếu là các cảnh báo semantic: thiếu vật, sai/lỏng box và nhầm lớp, còn phần FIXED/NEEDS_LABEL cũng được ưu tiên.

## 3. Calibration (2 ngưỡng)
| Tham số | Khởi đầu | Đã chọn | Precision / Recall (trước → sau) | Lý do (đánh đổi) |
|---|---|---|---|---|
| `duplicates.phash_dist` | 2 | 16 | DUP_IMAGE_NEAR 1.00/0.50 → 1.00/0.83 | Tại 16, recall gần gấp 1.66 lần (`5/6` thay `3/6`) trong khi precision vẫn 1.00 và exact duplicate vẫn P/R 1.00/1.00. Giá trị 20 làm exact recall giảm xuống 0.33 nên không chọn. |
| `second_opinion.conf` | 0.25 | 0.60 | WRONG 0.556/0.833 → 0.625/0.833; MISSING 0.500/1.000 → 0.571/1.000 | Ngưỡng 0.60 giữ recall missing 1.00, giảm FP, đồng thời tăng precision wrong từ 0.556 lên 0.625; nó không làm false-positive cải thiện nhưng giá trị này ổn giữa recall và noise. |


Calibration có thể đánh lừa vì trong 39 ảnh calib, các số liên quan đến cảnh báo model có nhiều FP: với cấu hình 0.25, `POSSIBLE_FALSE_POS` có precision chỉ 0.312 (5 TP/16 predicted) và `POSSIBLE_LOOSE_BOX` chỉ 0.286 (2 TP/7 predicted). Vì vậy cần nhìn ảnh/cặp ảnh thay vì tin F1 tự động; `0.60` giảm đánh giá false/tiếng ồn cho missing và wrong nhưng không loại bỏ tất cả cảnh báo giả.

## 4. Cửa chặn và điều pipeline KHÔNG bắt được

Gate hoạt động đúng: sau khi máy tự sửa lỗi bắt buộc và mô phỏng duyệt 80 ảnh, vòng 3 vẫn không còn lỗi `severity=error` nhưng có 60/205 ảnh cảnh báo, nên kết luận `Hold`, không phải Release. Đây là kiểm chứng trực tiếp: `08_summary.json` ghi `n_errors=0`, `n_warn_images=60`, `n_images=205`, `warn_ratio=0.2927`.

Với `--budget 0`, người không duyệt; 6 ảnh `MISSING_LABEL_FILE` và các lỗi bắt buộc còn lại sẽ làm pipeline dừng `Rework` thay vì xuất bản. Theo logic gate, chỉ cảnh báo không thể gây Rework: 60 ảnh cảnh báo ở v3 do đó là Hold khi chưa duyệt đủ. Pipeline không bắt được độ chính xác semantic hoàn toàn: trùng cạnh, box “lỏng”, vật bị thiếu, nhãn sai lớp và ảnh nền/thật thiếu nhãn cần mắt người. Ngoài ra `POSSIBLE_FALSE_POS`/`POSSIBLE_MISSING` chỉ là gợi ý của model và có thể sai.

## 5. Train: raw vs clean (tùy chọn, chấm riêng)
chưa train
## 6. Quyết định và ghi chú AI
Quyết định cuối: giữ **HOLD** theo kết quả hiện tại. Để hướng tới Release, cần duyệt số ảnh còn cảnh báo hoặc làm giảm chúng bằng cách nâng/ổn định ngưỡng, sau đó chạy lại v3 và giữ tỷ lệ cảnh báo dưới 10.0%; đồng thời đảm bảo không còn `error`. Do mẫu v3 còn 60/205 = 29.3%, cần duyệt giảm hơn 40 cảnh báo riêng biệt trước khi có thể đạt ngưỡng.

Dùng AI để hỗ trợ code? Ghi 3 dòng:
- **Prompt chính:** mô tả rõ vào/ra cho 4 module: nhãn YOLO, quy tắc issue, thao tác autofix, ý kiến thứ hai cache, kèm test mong đợi.
- **Cách kiểm:** đọc diff không ghi đè file đã viết sẵn, chạy từng test/TDD rồi `python -m pytest -q`, và thử ca dòng dính 2 lỗi/dòng trống/nhiều dự đoán.
- **Một lần AI sai:** khi AI không tôn trọng số dòng gốc hoặc quy tắc “drop_line thắng clip_box”, tôi sửa để gom thay đổi theo file và ưu tiên xóa dòng; kiểm lại bằng `test_blank_line...` và `test_line_with_two_errors...`.

*(Thưởng +2, tùy chọn)* CVAT: lọc `width < 20`, ảnh/số box khớp, đối chiếu `BOX_TINY` (xem docs/CVAT_FILTER.md), 1 câu về `can_review`.
