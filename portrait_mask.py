"""Batch human masks: white people, black background."""
from pathlib import Path
import argparse
import os
import sys

# Only hard masks are used; matting's JIT kernels are unnecessary in a frozen app.
if getattr(sys, "frozen", False):
    os.environ.setdefault("NUMBA_DISABLE_JIT", "1")


def main():
    parser = argparse.ArgumentParser(description="生成人像黑白蒙版")
    parser.add_argument("folder", nargs="?")
    parser.add_argument("--threshold", type=int, default=127)
    parser.add_argument("--model", choices=["birefnet-portrait", "u2net_human_seg"],
                        default="birefnet-portrait")
    parser.add_argument("--self-test", action="store_true", help="检查运行依赖，不下载模型")
    parser.add_argument("--test-inference", action="store_true", help="使用所选模型进行推理自检")
    args = parser.parse_args()
    if not 1 <= args.threshold <= 254:
        parser.error("threshold 必须在 1 到 254 之间")
    if args.self_test or args.test_inference:
        return self_test(args.model if args.test_inference else None)
    folder = args.folder
    if not folder:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        folder = filedialog.askdirectory(title="选择需要生成人像蒙版的图片文件夹")
        root.destroy()
    if not folder:
        print("已取消。")
        return 0
    source = Path(folder).expanduser().resolve()
    if not source.is_dir():
        raise ValueError(f"不是有效文件夹：{source}")
    extensions = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}
    files = sorted(p for p in source.rglob("*") if p.is_file()
                   and p.suffix.lower() in extensions
                   and not p.name.lower().endswith(".mask.png")
                   and not any(part.startswith("人像蒙版_") for part in p.relative_to(source).parts[:-1]))
    if not files:
        print("该文件夹中没有支持的图片。")
        return 0
    from datetime import datetime
    output = source / ("人像蒙版_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f"))
    output.mkdir()
    from PIL import Image, ImageOps
    from rembg import new_session, remove
    print(f"正在加载 {args.model} 人像模型，首次使用需要联网下载，请耐心等待……", flush=True)
    session = new_session(args.model, providers=["CPUExecutionProvider"])
    errors = []
    for index, path in enumerate(files, 1):
        try:
            with Image.open(path) as original:
                picture = ImageOps.exif_transpose(original).convert("RGB")
                mask = remove(picture, session=session, only_mask=True).convert("L")
                mask = mask.point(lambda pixel: 255 if pixel > args.threshold else 0)
                target = output / path.relative_to(source)
                target = target.with_name(target.name + ".mask.png")
                target.parent.mkdir(parents=True, exist_ok=True)
                mask.save(target)
            print(f"[{index}/{len(files)}] 完成：{path.name}", flush=True)
        except Exception as exc:
            errors.append(f"{path}: {exc}")
            print(f"[{index}/{len(files)}] 失败：{path.name}：{exc}", flush=True)
    print(f"\n完成 {len(files) - len(errors)} 张，失败 {len(errors)} 张。\n保存位置：{output}")
    if errors:
        (output / "失败记录.txt").write_text("\n".join(errors), encoding="utf-8")
    return 1 if errors else 0


def self_test(model=None):
    import tkinter as tk
    import numpy as np
    import onnxruntime as ort
    from PIL import Image, features
    from rembg import new_session, remove
    assert tk.Tcl().eval("info patchlevel")
    assert features.check("webp"), "缺少 WebP 支持"
    assert "CPUExecutionProvider" in ort.get_available_providers()
    if model:
        session = new_session(model, providers=["CPUExecutionProvider"])
        sample = Image.fromarray(np.random.default_rng(42).integers(0, 256, (96, 64, 3), dtype=np.uint8))
        mask = remove(sample, session=session, only_mask=True).convert("L")
        mask = mask.point(lambda p: 255 if p > 127 else 0)
        assert mask.size == sample.size
        assert set(np.unique(np.asarray(mask))) <= {0, 255}
    print("SELF-TEST OK" + (f" ({model})" if model else ""), flush=True)
    return 0


if __name__ == "__main__":
    code = 1
    try:
        code = main()
    except Exception as exc:
        print(f"运行失败：{exc}", file=sys.stderr)
    if getattr(sys, "frozen", False) and (len(sys.argv) == 1 or len(sys.argv) == 2 and not sys.argv[1].startswith("--")):
        try:
            input("\n按回车关闭窗口……")
        except EOFError:
            pass
    sys.exit(code)
