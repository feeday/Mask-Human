# Mask-Human

Windows 批量人像黑白蒙版工具。人物（包括头发、衣服和可见身体）为纯白色 255，背景为纯黑色 0，输出 PNG，保留原图。

## 直接运行

- **EXE**：双击 `Mask-Human.exe` 选择图片文件夹，或将一个文件夹拖到 EXE 上。不需要安装 Python。
- **源码**：已有 Python 的 Windows 电脑可双击 `run_portrait_mask.bat`，首次自动安装独立 Python 3.12 环境和依赖。
- 自动处理子文件夹，在所选目录内生成 `人像蒙版_时间` 文件夹，并保留子目录结构。
- 原有 `.mask.png` 和此前生成的 `人像蒙版_` 目录会跳过。同一张图的所有人物合并在一张蒙版中。

支持 JPG、JPEG、PNG、WebP、BMP、TIF、TIFF；动图/多页图只处理第一帧。自动校正 EXIF 方向，输出尺寸与校正后的图片一致。

## 一键打包 EXE

在 Windows 上双击 **`build_exe.bat`**。电脑需要已有 Python，脚本自动准备 Python 3.12 和 PyInstaller，打包后自动检查运行依赖。

输出：**`dist/Mask-Human.exe`**。将这个文件复制到其他 Windows x64 电脑即可运行。构建时需要联网，EXE 中包含运行环境，但不内嵌模型。

也可以用 Python 3.12 手动构建：

```powershell
python -m pip install -r requirements-build.txt
python build_exe.py
```

## GitHub 在线打包

打开仓库 **Actions → Build Windows EXE → Run workflow**。成功后进入该次运行，在 **Artifacts** 下载 `Mask-Human-Windows-x64`，解压即可得到 EXE。推送代码到 `main` 也会自动构建；构建产物保留 30 天。

## 模型与离线使用

默认 **BiRefNet Portrait**，1024×1024 推理，模型约 973 MB；首次使用联网下载到 `%USERPROFILE%\.u2net`，之后使用本机 CPU 离线处理，不上传图片。复杂背景和遮挡仍可能误分，请检查结果。

首次下载较慢时请等待控制台进度。若要在另一台电脑离线使用，把缓存的 `birefnet-portrait.onnx` 放到该电脑的 `%USERPROFILE%\.u2net` 目录，也可用 `U2NET_HOME` 环境变量指定模型目录。

旧模型 `u2net_human_seg` 约 176 MB，320×320 推理，可通过命令行选择：

```powershell
.\Mask-Human.exe "D:\照片" --model u2net_human_seg
.\Mask-Human.exe "D:\照片" --threshold 127
```

阈值范围 1～254，降低会扩大白色区域，提高会缩小。不要依靠阈值调整修复模型识别错误。

## 验证

```powershell
.\Mask-Human.exe --self-test
.\Mask-Human.exe --test-inference
```

前者检查打包依赖、Tk 和 WebP 支持，不下载模型；后者用默认模型进行一次合成输入推理，检查输出尺寸及纯黑白值，不代表真实照片的分割准确率。

## 使用的项目

- [rembg](https://github.com/danielgatis/rembg)
- [BiRefNet Portrait](https://huggingface.co/ZhengPeng7/BiRefNet-portrait)
- [U²-Net](https://github.com/xuebinqin/U-2-Net)
- [PyInstaller](https://pyinstaller.org/)

运行环境、模型、个人图片和打包产物不会提交到源码仓库。第三方软件及模型遵循各自许可证。
