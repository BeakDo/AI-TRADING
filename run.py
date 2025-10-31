#!/usr/bin/env python3
"""AI Trading 스캐폴드를 위한 편의 런처.

이 스크립트는 가장 일반적인 개발 워크플로를 자동화하여, 새 기여자가
가상환경 생성·의존성 설치·다중 프로세스 기동을 직접 수행하는 대신 한 번의
명령으로 시작할 수 있게 한다.

사용 예시
---------

- ``python run.py`` → 로컬 가상환경과 npm 의존성을 준비하고 FastAPI 백엔드와
  Next.js 대시보드를 감시 모드로 실행한다.
- ``python run.py --mode docker`` → ``infra/.env``를 확인한 뒤 Docker Compose
  스택을 기동한다.

스크립트는 의도적으로 가볍고 안전하게 설계되었다. 환경 파일이 없을 때만
``infra/.env.example``을 복사하며, 필요할 때에만 의존성을 다시 설치하도록
간단한 타임스탬프를 기록한다.
"""
from __future__ import annotations

import argparse
import os
import shutil
import signal
import subprocess
import sys
import textwrap
import time
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parent
INFRA_DIR = ROOT / "infra"
FRONTEND_DIR = ROOT / "frontend"
BACKEND_DIR = ROOT / "backend"
DEFAULT_ENV = ROOT / ".env"
DOCKER_ENV = INFRA_DIR / ".env"
ENV_TEMPLATE = INFRA_DIR / ".env.example"
VENV_DIR = ROOT / ".venv"
BACKEND_REQ = BACKEND_DIR / "requirements.txt"
FRONTEND_NODE_MODULES = FRONTEND_DIR / "node_modules"
FRONTEND_PACKAGE_LOCK = FRONTEND_DIR / "package-lock.json"
FRONTEND_PACKAGE_JSON = FRONTEND_DIR / "package.json"

ProcessDef = Tuple[str, Sequence[str], Path, Optional[dict]]


def copy_env_if_missing(target: Path, template: Path) -> bool:
    """``target``이 없을 때 ``template``을 복사한다.

    복사가 수행되면 ``True``를 반환해 호출자가 안내 메시지를 보여줄 수 있게 한다.
    """
    if target.exists():
        return False
    if not template.exists():
        raise FileNotFoundError(f"Environment template not found: {template}")
    target.write_text(template.read_text())
    return True


def venv_executable(name: str) -> Path:
    """관리되는 가상환경 내부 실행 파일 경로를 반환한다."""
    if os.name == "nt":
        extension = ".exe"
        return VENV_DIR / "Scripts" / f"{name}{extension}"
    return VENV_DIR / "bin" / name


def ensure_virtualenv() -> Path:
    """로컬 가상환경이 없으면 생성한다."""
    if not VENV_DIR.exists():
        print("[setup] Creating Python virtual environment (.venv)")
        subprocess.check_call([sys.executable, "-m", "venv", str(VENV_DIR)])
    python_path = venv_executable("python")
    if not python_path.exists():
        raise RuntimeError("Virtualenv creation failed: python executable missing")
    return python_path


def ensure_backend_dependencies(python_path: Path) -> None:
    """요구 사항이 바뀌면 백엔드 의존성을 설치한다."""
    if not BACKEND_REQ.exists():
        print("[setup] No backend requirements.txt found; skipping Python deps")
        return
    marker = VENV_DIR / ".requirements.stamp"
    requirements_mtime = str(BACKEND_REQ.stat().st_mtime)
    if marker.exists() and marker.read_text() == requirements_mtime:
        return
    pip_path = venv_executable("pip")
    print("[setup] Installing backend dependencies (pip install -r backend/requirements.txt)")
    subprocess.check_call([str(pip_path), "install", "-r", str(BACKEND_REQ)])
    marker.write_text(requirements_mtime)


def ensure_frontend_dependencies() -> Optional[str]:
    """npm 의존성이 없거나 패키지 정의가 변경되면 설치한다.

    프런트엔드 실행 준비가 완료되면 ``npm`` 실행 파일 경로를 반환하고,
    준비가 되지 않았으면 ``None``을 반환한다.
    """
    if not FRONTEND_PACKAGE_JSON.exists():
        print("[setup] 프런트엔드 package.json을 찾을 수 없어 npm 설치를 건너뜁니다.")
        return None
    npm_path = shutil.which("npm")
    if npm_path is None:
        print(
            "[setup] npm 실행 파일을 찾지 못했습니다. 프런트엔드 준비를 건너뜁니다. "
            "Node.js를 설치하거나 --mode docker를 사용하세요."
        )
        return None
    marker = FRONTEND_DIR / ".deps.stamp"
    package_mtime = str(max(FRONTEND_PACKAGE_JSON.stat().st_mtime,
                             FRONTEND_PACKAGE_LOCK.stat().st_mtime if FRONTEND_PACKAGE_LOCK.exists() else 0.0))
    dependencies_present = FRONTEND_NODE_MODULES.exists()
    if dependencies_present and marker.exists() and marker.read_text() == package_mtime:
        return npm_path
    print("[setup] 프런트엔드 의존성을 설치합니다 (npm install)")
    subprocess.check_call([npm_path, "install"], cwd=str(FRONTEND_DIR))
    marker.write_text(package_mtime)
    return npm_path


def run_processes(defs: Iterable[ProcessDef]) -> None:
    """여러 장기 실행 프로세스를 띄우고 생존 상태를 유지한다."""
    processes: List[Tuple[str, subprocess.Popen[str]]] = []
    try:
        for name, cmd, cwd, env in defs:
            print(f"[run] Starting {name}: {' '.join(cmd)}")
            proc = subprocess.Popen(cmd, cwd=str(cwd), env=env)
            processes.append((name, proc))
        while True:
            for name, proc in processes:
                ret = proc.poll()
                if ret is not None:
                    raise RuntimeError(f"Process '{name}' exited with code {ret}")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n[run] Received keyboard interrupt, shutting down...")
    finally:
        for name, proc in processes:
            if proc.poll() is None:
                try:
                    print(f"[run] Terminating {name}")
                    proc.send_signal(signal.SIGINT)
                    try:
                        proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        proc.terminate()
                except Exception:  # pragma: no cover - best effort shutdown
                    proc.kill()


def launch_local() -> None:
    copied_root_env = copy_env_if_missing(DEFAULT_ENV, ENV_TEMPLATE)
    if copied_root_env:
        print(textwrap.dedent(
            """
            [setup] Created .env from infra/.env.example. Remember to update
            credentials before connecting to real broker endpoints.
            """.strip()
        ))
    python_path = ensure_virtualenv()
    ensure_backend_dependencies(python_path)
    npm_path = ensure_frontend_dependencies()

    backend_env = os.environ.copy()
    backend_env.setdefault("PYTHONPATH", str(ROOT))

    backend_cmd = [str(python_path), "-m", "uvicorn", "backend.main:app", "--reload"]
    processes: List[ProcessDef] = [("backend", backend_cmd, ROOT, backend_env)]
    if npm_path:
        processes.append(("frontend", [npm_path, "run", "dev"], FRONTEND_DIR, None))
    else:
        print(
            "[run] 프런트엔드를 건너뜁니다. 백엔드 API만 실행됩니다."
        )

    run_processes(processes)


def detect_compose_command() -> Sequence[str]:
    """호스트 환경과 호환되는 docker compose CLI를 선택한다."""
    if shutil.which("docker") and shutil.which("docker-compose"):
        # Prefer new plugin when available but fall back to docker-compose explicitly if needed.
        return ["docker", "compose"]
    if shutil.which("docker"):
        return ["docker", "compose"]
    if shutil.which("docker-compose"):
        return ["docker-compose"]
    raise RuntimeError("Neither 'docker compose' nor 'docker-compose' is available")


def launch_docker(no_build: bool) -> None:
    copied_root_env = copy_env_if_missing(DEFAULT_ENV, ENV_TEMPLATE)
    copied_docker_env = copy_env_if_missing(DOCKER_ENV, ENV_TEMPLATE)
    if copied_root_env or copied_docker_env:
        print(textwrap.dedent(
            """
            [setup] Created missing environment files from infra/.env.example.
            Update credentials before switching to live trading.
            """.strip()
        ))
    compose_cmd = list(detect_compose_command())
    args = compose_cmd + ["up"]
    if not no_build:
        args.append("--build")
    print(f"[run] Executing {' '.join(args)} in {INFRA_DIR}")
    subprocess.check_call(args, cwd=str(INFRA_DIR))


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the AI Trading scaffold with a single command")
    parser.add_argument(
        "--mode",
        choices=("local", "docker"),
        default="local",
        help="Execution mode: 'local' (default) or 'docker'",
    )
    parser.add_argument(
        "--no-build",
        action="store_true",
        help="Skip docker compose build step when using --mode docker",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)
    if args.mode == "local":
        launch_local()
    else:
        launch_docker(no_build=args.no_build)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover - top level safety net
        print(f"[error] {exc}")
        sys.exit(1)
