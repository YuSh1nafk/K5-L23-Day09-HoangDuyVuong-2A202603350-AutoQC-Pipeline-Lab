"""BƯỚC 4 — quyết định Release, Hold hoặc Rework từ các lỗi còn lại."""
from ..common import ERROR, WARN


def decide(issues, image_stems, cfg, reviewed=frozenset()):
    stems = set(image_stems)
    reviewed = set(reviewed)
    errors = [issue for issue in issues if issue.severity == ERROR]
    warn_images = {
        issue.image for issue in issues
        if issue.severity == WARN and issue.image in stems and issue.image not in reviewed
    }
    n_images = len(stems)
    ratio = len(warn_images) / n_images if n_images else 0.0
    threshold = cfg["gate"]["warn_ratio_hold"]
    if errors:
        decision = "Rework"
        reasons = [f"Còn {len(errors)} lỗi bắt buộc; cần sửa và kiểm tra lại."]
    elif ratio >= threshold:
        decision = "Hold"
        reasons = [f"{len(warn_images)}/{n_images} ảnh còn cảnh báo ({ratio:.1%}), đạt/vượt ngưỡng {threshold:.1%}; cần duyệt thêm."]
    else:
        decision = "Release"
        reasons = [f"Không còn lỗi bắt buộc; {len(warn_images)}/{n_images} ảnh còn cảnh báo ({ratio:.1%}), dưới ngưỡng {threshold:.1%}."]
    return {
        "decision": decision,
        "n_errors": len(errors),
        "n_warn_images": len(warn_images),
        "n_images": n_images,
        "warn_ratio": round(ratio, 4),
        "reasons": reasons,
    }
