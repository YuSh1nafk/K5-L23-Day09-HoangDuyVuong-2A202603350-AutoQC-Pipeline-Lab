"""CHECK 6 — so sánh nhãn với dự đoán cache của model để đưa ra cảnh báo cho người."""
import math

from ..common import WARN, Issue, iou_xywh, parse_yolo_line
from ..model_cache import get_preds


def _prediction(row):
    try:
        if len(row) < 6:
            return None
        cls_value, conf, x, y, w, h = map(float, row[:6])
        if not all(math.isfinite(value) for value in (cls_value, conf, x, y, w, h)) or cls_value != int(cls_value):
            return None
        if w <= 0 or h <= 0:
            return None
        return int(cls_value), conf, (x, y, w, h)
    except (TypeError, ValueError, OverflowError):
        return None


def run(ds, cfg, preds=None):
    preds = get_preds(ds, cfg, "checker") if preds is None else preds
    rules = cfg["second_opinion"]
    issues = []
    for image in ds.image_files():
        stem = image.stem
        rows = preds.get(stem)
        lines = ds.read_label_lines(stem)
        if rows is None or lines is None:
            continue
        width_height = ds.image_size(stem)
        if not width_height:
            continue
        width, height = width_height
        labels = []
        for number, text in lines:
            try:
                cls, x, y, w, h = parse_yolo_line(text)
            except (ValueError, OverflowError):
                continue
            if 0 <= cls < len(ds.classes):
                labels.append((number, cls, (x, y, w, h)))
        predictions = [p for row in rows if (p := _prediction(row)) is not None]
        trusted = [p for p in predictions if p[1] >= rules["conf"] and p[2][2] * width * p[2][3] * height >= rules["min_area_px"]]
        for cls, conf, box in trusted:
            overlaps = [(iou_xywh(box, label_box), label_cls) for _, label_cls, label_box in labels]
            candidates = [(iou, label_cls) for iou, label_cls in overlaps if iou >= rules["iou_missing"]]
            extra = {"conf": conf}
            if not candidates:
                issues.append(Issue("second_opinion", WARN, "POSSIBLE_MISSING", stem, "model thấy vật có thể chưa được gán nhãn", extra=extra))
                continue
            same_class = [iou for iou, label_cls in candidates if label_cls == cls]
            if same_class:
                best_iou = max(same_class)
                if best_iou < rules["iou_loose"]:
                    issues.append(Issue("second_opinion", WARN, "POSSIBLE_LOOSE_BOX", stem, "box nhãn cùng lớp có thể bị lệch hoặc quá lỏng", extra={**extra, "iou": best_iou}))
                continue
            best_other = max(iou for iou, _ in candidates)
            if best_other >= rules["iou_match"]:
                issues.append(Issue("second_opinion", WARN, "POSSIBLE_WRONG_CLASS", stem, "vật có thể được gán nhầm lớp", extra={**extra, "iou": best_other}))
        fp_predictions = [p for p in predictions if p[1] >= rules["fp_conf"]]
        for number, _, label_box in labels:
            best_iou = max((iou_xywh(label_box, p[2]) for p in fp_predictions), default=0.0)
            if best_iou < rules["iou_missing"]:
                issues.append(Issue("second_opinion", WARN, "POSSIBLE_FALSE_POS", stem, "box nhãn không khớp dự đoán nào của model", number, {"iou": best_iou}))
    return issues
