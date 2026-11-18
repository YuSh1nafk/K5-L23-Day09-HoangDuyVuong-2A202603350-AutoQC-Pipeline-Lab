"""CHECK 2 — kiểm định dạng và hình học của các dòng nhãn YOLO."""
from ..common import ERROR, WARN, Issue, iou_xywh, parse_yolo_line


def run(ds, cfg):
    rules = cfg["label_format"]
    issues = []
    for image in ds.image_files():
        stem = image.stem
        size = ds.image_size(stem)
        seen = []
        for line, text in ds.read_label_lines(stem) or []:
            try:
                cls, x, y, w, h = parse_yolo_line(text)
            except (ValueError, OverflowError) as exc:
                issues.append(Issue("label_format", ERROR, "BAD_FORMAT", stem, str(exc), line))
                continue
            if not 0 <= cls < len(ds.classes):
                issues.append(Issue("label_format", ERROR, "BAD_CLASS_ID", stem, f"id lớp {cls} nằm ngoài danh sách", line))
                continue
            if w <= 0 or h <= 0:
                issues.append(Issue("label_format", ERROR, "BOX_ZERO", stem, "rộng và cao phải lớn hơn 0", line))
                continue
            left, top, right, bottom = x - w / 2, y - h / 2, x + w / 2, y + h / 2
            overflow = max(0.0, -left, -top, right - 1.0, bottom - 1.0)
            if overflow > rules["overflow_tol"]:
                issues.append(Issue("label_format", ERROR, "BOX_OUT_OF_IMAGE", stem, f"box tràn ảnh {overflow:.6g}", line, {"overflow": overflow}))
            if any(old_cls == cls and iou_xywh((x, y, w, h), old_box) > rules["dup_box_iou"] for old_cls, old_box in seen):
                issues.append(Issue("label_format", ERROR, "DUP_BOX", stem, "box lặp với một dòng trước cùng lớp", line))
            seen.append((cls, (x, y, w, h)))
            if size:
                width, height = size
                if min(w * width, h * height) < rules["min_box_px"]:
                    issues.append(Issue("label_format", WARN, "BOX_TINY", stem, "cạnh ngắn của box nhỏ hơn ngưỡng pixel", line))
            if w * h > rules["max_box_frac"]:
                issues.append(Issue("label_format", WARN, "BOX_HUGE", stem, "diện tích box quá lớn so với ảnh", line))
    return issues
