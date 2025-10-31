#!/usr/bin/env python3
"""Convenience launcher for the AI Trading scaffold.

Running this script automates the most common development workflows so
new contributors only have to execute a single command instead of
manually creating virtual environments, installing dependencies, and
starting multiple processes.

Usage examples
--------------

- ``python run.py`` → set up local virtualenv + npm deps and launch the
  FastAPI backend with the Next.js dashboard in watch mode.
- ``python run.py --mode docker`` → ensure ``infra/.env`` exists and
  start the Docker Compose stack.

The script is intentionally lightweight and safe: it only copies
``infra/.env.example`` when an environment file is missing and records
simple timestamps to avoid reinstalling dependencies unless required.
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
    """Copy ``template`` to ``target`` when the latter is absent.

    Returns ``True`` if a copy happened so the caller can surface a
    helpful message.
    """
    if target.exists():
        return False
    if not template.exists():
        raise FileNotFoundError(f"Environment template not found: {template}")
    target.write_text(template.read_text())
    return True


def venv_executable(name: str) -> Path:
    """Return the path of an executable inside the managed virtualenv."""
    if os.name == "nt":
        extension = ".exe"
        return VENV_DIR / "Scripts" / f"{name}{extension}"
    return VENV_DIR / "bin" / name


def ensure_virtualenv() -> Path:
    """Create the local virtual environment if it does not exist."""
    if not VENV_DIR.exists():
        print("[setup] Creating Python virtual environment (.venv)")
        subprocess.check_call([sys.executable, "-m", "venv", str(VENV_DIR)])
    python_path = venv_executable("python")
    if not python_path.exists():
        raise RuntimeError("Virtualenv creation failed: python executable missing")
    return python_path


def ensure_backend_dependencies(python_path: Path) -> None:
    """Install backend dependencies when requirements change."""
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


def ensure_frontend_dependencies() -> None:
    """Install npm dependencies when missing or package definitions change."""
    if not FRONTEND_PACKAGE_JSON.exists():
        print("[setup] No frontend package.json found; skipping npm deps")
        return
    if shutil.which("npm") is None:
        raise RuntimeError("npm executable not found. Install Node.js or use --mode docker")
    marker = FRONTEND_DIR / ".deps.stamp"
    package_mtime = str(max(FRONTEND_PACKAGE_JSON.stat().st_mtime,
                             FRONTEND_PACKAGE_LOCK.stat().st_mtime if FRONTEND_PACKAGE_LOCK.exists() else 0.0))
    dependencies_present = FRONTEND_NODE_MODULES.exists()
    if dependencies_present and marker.exists() and marker.read_text() == package_mtime:
        return
    print("[setup] Installing frontend dependencies (npm install)")
    subprocess.check_call(["npm", "install"], cwd=str(FRONTEND_DIR))
    marker.write_text(package_mtime)


def run_processes(defs: Iterable[ProcessDef]) -> None:
    """Launch multiple long-running processes and keep them alive."""
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
    ensure_frontend_dependencies()

    backend_env = os.environ.copy()
    backend_env.setdefault("PYTHONPATH", str(ROOT))

    backend_cmd = [str(python_path), "-m", "uvicorn", "backend.main:app", "--reload"]
    frontend_cmd = ["npm", "run", "dev"]

    run_processes([
        ("backend", backend_cmd, ROOT, backend_env),
        ("frontend", frontend_cmd, FRONTEND_DIR, None),
    ])


def detect_compose_command() -> Sequence[str]:
    """Select docker compose CLI compatible with the host environment."""
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
