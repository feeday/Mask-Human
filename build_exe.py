"""Build a standalone Windows executable from the current environment."""
from pathlib import Path
import os
import subprocess
import sys

BASE = Path(__file__).resolve().parent


def main():
    if sys.platform != "win32":
        raise SystemExit("Windows EXE 必须在 Windows 上打包。")
    env = os.environ.copy()
    env["NUMBA_DISABLE_JIT"] = "1"
    command = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean",
               "--onefile", "--console", "--name", "Mask-Human",
               "--distpath", str(BASE / "dist"), "--workpath", str(BASE / "build"),
               "--specpath", str(BASE / "build"),
               "--collect-all", "rembg", "--collect-all", "pymatting",
               "--collect-all", "onnxruntime", "--copy-metadata", "rembg",
               str(BASE / "portrait_mask.py")]
    subprocess.run(command, check=True, cwd=BASE, env=env)
    executable = BASE / "dist" / "Mask-Human.exe"
    subprocess.run([str(executable), "--self-test"], check=True, cwd=BASE, env=env)
    print(f"\n打包并通过运行检查：{executable}", flush=True)


if __name__ == "__main__":
    main()
