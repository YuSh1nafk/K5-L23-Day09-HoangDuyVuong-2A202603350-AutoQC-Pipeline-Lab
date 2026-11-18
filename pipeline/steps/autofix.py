"""Sửa an toàn các lỗi bắt buộc trong bản sao dataset và ghi lại mọi thay đổi."""
from collections import defaultdict

import yaml

from ..common import ERROR, parse_yolo_line

_DROP_CODES = {"BAD_FORMAT", "BAD_CLASS_ID", "BOX_ZERO", "DUP_BOX"}
_REMOVE_CODES = {"LEAK_TEST", "CORRUPT_IMAGE", "BAD_SIZE"}


def _clip_line(text):
    cls, x, y, w, h = parse_yolo_line(text)
    left, top, right, bottom = x - w / 2, y - h / 2, x + w / 2, y + h / 2
    left, top, right, bottom = max(0.0, left), max(0.0, top), min(1.0, right), min(1.0, bottom)
    if right <= left or bottom <= top:
        return None
    vals = (cls, (left + right) / 2, (top + bottom) / 2, right - left, bottom - top)
    return " ".join(format(value, ".10g") for value in vals)


def fix(ds, issues, cfg):
    by_image = defaultdict(list)
    for issue in issues:
        if issue.severity == ERROR:
            by_image[issue.image].append(issue)
    fixes = []
    removed = set()
    for stem, found in by_image.items():
        codes = {issue.code for issue in found}
        if stem == "data.yaml" and "BAD_CLASS_NAME" in codes:
            data = yaml.safe_load(ds.yaml_path.read_text(encoding="utf-8")) or {}
            data["names"] = {i: name for i, name in enumerate(cfg["classes"])}
            ds.yaml_path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
            fixes.append({"image": stem, "line": "", "action": "rename_classes", "before": "names không đúng", "after": str(cfg["classes"])})
            continue
        if any(code.startswith("DUP_IMAGE_") or code in _REMOVE_CODES for code in codes):
            image = ds.image_path(stem)
            label = ds.label_path(stem)
            if image is not None:
                image.unlink(missing_ok=True)
            label.unlink(missing_ok=True)
            removed.add(stem)
            fixes.append({"image": stem, "line": "", "action": "remove_image", "before": "ảnh và nhãn trong dataset", "after": "đã loại bỏ"})
            continue
        if "MISSING_LABEL_FILE" in codes:
            fixes.append({"image": stem, "line": "", "action": "needs_label", "before": "(không có file)", "after": "chuyển người gán"})
        path = ds.label_path(stem)
        line_issues = {}
        for issue in found:
            if issue.line is not None and (issue.code in _DROP_CODES or issue.code == "BOX_OUT_OF_IMAGE"):
                line_issues.setdefault(issue.line, set()).add(issue.code)
        if not path.exists() or not line_issues:
            continue
        original = path.read_text(encoding="utf-8").splitlines(keepends=True)
        output = []
        changes = []
        for number, raw in enumerate(original, 1):
            codes = line_issues.get(number, set())
            before = raw.rstrip("\r\n")
            if codes & _DROP_CODES:
                changes.append({"image": stem, "line": number, "action": "drop_line", "before": before, "after": ""})
                continue
            if "BOX_OUT_OF_IMAGE" in codes:
                try:
                    after = _clip_line(before)
                except (ValueError, OverflowError):
                    after = None
                if after is None:
                    changes.append({"image": stem, "line": number, "action": "drop_line", "before": before, "after": ""})
                    continue
                ending = raw[len(before):]
                output.append(after + ending)
                if after != before:
                    changes.append({"image": stem, "line": number, "action": "clip_box", "before": before, "after": after})
            else:
                output.append(raw)
        if changes:
            path.write_text("".join(output), encoding="utf-8")
            fixes.extend(changes)
    return fixes
