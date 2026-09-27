"""Install an isolated Python 3.12 runtime and launch the mask tool."""
from pathlib import Path
import os
import subprocess
import sys

BASE = Path(__file__).resolve().parent


def run(command, **kwargs):
    subprocess.run(command, check=True, cwd=BASE, **kwargs)


def ensure_environment(build=False):
    runtime = BASE / ".portrait_env"
    python = runtime / "Scripts" / "python.exe"
    ready = runtime / ".ready-v2"
    if not ready.exists():
        bootstrap = BASE / ".portrait_bootstrap"
        env = os.environ.copy()
        env["PYTHONPATH"] = str(bootstrap)
        env["UV_PYTHON_INSTALL_DIR"] = str(BASE / ".portrait_python")
        if not (bootstrap / "uv").is_dir():
            print("首次运行：正在安装环境管理工具……", flush=True)
            run([sys.executable, "-m", "pip", "install", "--target", str(bootstrap), "uv"])
        uv = [sys.executable, "-m", "uv"]
        if not python.exists():
            run(uv + ["venv", "--python", "3.12", str(runtime)], env=env)
        run(uv + ["pip", "install", "--python", str(python), "-r", str(BASE / "requirements.txt")], env=env)
        ready.write_text("ready", encoding="ascii")
    if build:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(BASE / ".portrait_bootstrap")
        run([sys.executable, "-m", "uv", "pip", "install", "--python", str(python),
             "-r", str(BASE / "requirements-build.txt")], env=env)
    return python


def main():
    if sys.argv[1:] == ["--build-exe"]:
        python = ensure_environment(build=True)
        run([str(python), str(BASE / "build_exe.py")])
        return 0
    python = ensure_environment()
    result = subprocess.run([str(python), str(BASE / "portrait_mask.py"), *sys.argv[1:]], cwd=BASE)
    return result.returncode


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"环境安装失败，请检查网络后重试：{exc}", file=sys.stderr)
        sys.exit(1)
