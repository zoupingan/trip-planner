from __future__ import annotations

import json
import os
import posixpath
import socket
import sys
import time
from pathlib import Path

import paramiko


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend-learn"
FRONTEND_DIST = ROOT / "frontend" / "dist"
DEPLOY_DIR = ROOT / "deploy"

SERVER_HOST = os.environ.get("DEPLOY_HOST", "")
SERVER_USER = os.environ.get("DEPLOY_USER", "root")
PUBLIC_HOST = os.environ.get("PUBLIC_HOST", SERVER_HOST)
REMOTE_ROOT = "/app/trip-planner"
COMPOSE_PATH = "/root/docker-compose.yml"

BLOCK_START = "# trip-planner managed block start"
BLOCK_END = "# trip-planner managed block end"


def read_dotenv(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
            value = value[1:-1]
        values[key.strip()] = value
    return values


def run_remote(
    client: paramiko.SSHClient,
    command: str,
    *,
    timeout: int = 60,
    show_output: bool = False,
) -> str:
    _, stdout, stderr = client.exec_command(command, timeout=timeout)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    status = stdout.channel.recv_exit_status()
    if show_output:
        combined = (out + err).strip()
        if combined:
            print(combined)
    if status != 0:
        raise RuntimeError(f"Remote command failed ({status}): {command}\n{err.strip()}")
    return out


def ensure_remote_dir(sftp: paramiko.SFTPClient, path: str) -> None:
    current = ""
    for part in path.strip("/").split("/"):
        current += f"/{part}"
        try:
            sftp.stat(current)
        except FileNotFoundError:
            sftp.mkdir(current)


def upload_tree(
    sftp: paramiko.SFTPClient,
    local_root: Path,
    remote_root: str,
) -> None:
    ignored = {".git", ".idea", ".venv", "__pycache__", ".pytest_cache"}
    ensure_remote_dir(sftp, remote_root)
    for local_path in local_root.rglob("*"):
        if any(part in ignored for part in local_path.parts):
            continue
        relative = local_path.relative_to(local_root)
        remote_path = posixpath.join(remote_root, *relative.parts)
        if local_path.is_dir():
            ensure_remote_dir(sftp, remote_path)
        elif local_path.is_file():
            ensure_remote_dir(sftp, posixpath.dirname(remote_path))
            sftp.put(str(local_path), remote_path)


def make_runtime_env() -> str:
    backend_env = read_dotenv(BACKEND / ".env")
    values = {
        "APP_NAME": backend_env.get("APP_NAME", "旅行规划后端"),
        "APP_VERSION": backend_env.get("APP_VERSION", "1.0.0"),
        "DEBUG": "false",
        "HOST": "0.0.0.0",
        "PORT": "8001",
        "CORS_ORIGINS": (
            f"http://{PUBLIC_HOST}:82,http://{PUBLIC_HOST},"
            "http://localhost:5173,http://127.0.0.1:5173"
        ),
        "AMAP_API_KEY": backend_env.get("AMAP_API_KEY", ""),
        "UNSPLASH_ACCESS_KEY": backend_env.get("UNSPLASH_ACCESS_KEY", ""),
        "UNSPLASH_SECRET_KEY": backend_env.get("UNSPLASH_SECRET_KEY", ""),
        "LLM_API_KEY": os.environ.get("LLM_API_KEY", ""),
        "LLM_BASE_URL": os.environ.get(
            "LLM_BASE_URL",
            "https://dashscope.aliyuncs.com/compatible-mode/v1",
        ),
        "LLM_MODEL_ID": os.environ.get("LLM_MODEL_ID", "qwen3.6-flash"),
        "NO_PROXY": "localhost,127.0.0.1,::1",
    }
    required = [
        "AMAP_API_KEY",
        "UNSPLASH_ACCESS_KEY",
        "LLM_API_KEY",
        "LLM_BASE_URL",
        "LLM_MODEL_ID",
    ]
    missing = [key for key in required if not values[key]]
    if missing:
        raise RuntimeError("Missing required environment variables: " + ", ".join(missing))
    return "\n".join(
        f"{key}={json.dumps(value, ensure_ascii=False)}"
        for key, value in values.items()
    ) + "\n"


def make_compose_block() -> str:
    return f"""\
{BLOCK_START}
  trip-backend-learn:
    build:
      context: /app/trip-planner/backend
      dockerfile: Dockerfile
    container_name: trip-backend-learn
    ports:
      - "8001:8001"
    env_file:
      - /app/trip-planner/backend/.env
    networks:
      - pet-network
    restart: unless-stopped

  trip-frontend:
    image: nginx:alpine
    container_name: trip-frontend
    ports:
      - "82:80"
    volumes:
      - /app/trip-planner/frontend/dist:/usr/share/nginx/html:ro
      - /app/trip-planner/frontend/nginx.conf:/etc/nginx/nginx.conf:ro
    networks:
      - pet-network
    depends_on:
      - trip-backend-learn
    restart: unless-stopped
{BLOCK_END}
"""


def update_compose(compose: str) -> str:
    block = make_compose_block()
    if BLOCK_START in compose and BLOCK_END in compose:
        before, remainder = compose.split(BLOCK_START, 1)
        _, after = remainder.split(BLOCK_END, 1)
        return before.rstrip() + "\n\n" + block + after.lstrip("\n")
    marker = "\nnetworks:"
    if marker not in compose:
        raise RuntimeError("Could not find the top-level networks section in docker-compose.yml")
    return compose.replace(marker, "\n\n" + block + "\nnetworks:", 1)


def main() -> None:
    password = os.environ.get("DEPLOY_PASSWORD")
    if not password:
        raise RuntimeError("DEPLOY_PASSWORD is not set")
    if not SERVER_HOST:
        raise RuntimeError("DEPLOY_HOST is not set")
    if not FRONTEND_DIST.joinpath("index.html").exists():
        raise RuntimeError("Frontend dist is missing; run npm build first")

    print("Connecting to server...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=SERVER_HOST,
        username=SERVER_USER,
        password=password,
        timeout=20,
        banner_timeout=20,
        auth_timeout=20,
    )

    try:
        sftp = client.open_sftp()
        timestamp = time.strftime("%Y%m%d%H%M%S")
        run_remote(
            client,
            f"cp {COMPOSE_PATH} {COMPOSE_PATH}.bak-trip-{timestamp} && "
            f"rm -rf -- {REMOTE_ROOT}/backend {REMOTE_ROOT}/frontend && "
            f"mkdir -p {REMOTE_ROOT}/backend {REMOTE_ROOT}/frontend/dist",
        )

        print("Uploading backend...")
        upload_tree(sftp, BACKEND / "app", f"{REMOTE_ROOT}/backend/app")
        for filename in ("requirements.txt", "run.py"):
            sftp.put(str(BACKEND / filename), f"{REMOTE_ROOT}/backend/{filename}")
        sftp.put(
            str(DEPLOY_DIR / "trip-backend.Dockerfile"),
            f"{REMOTE_ROOT}/backend/Dockerfile",
        )

        print("Uploading frontend...")
        upload_tree(sftp, FRONTEND_DIST, f"{REMOTE_ROOT}/frontend/dist")
        sftp.put(
            str(DEPLOY_DIR / "trip-frontend.nginx.conf"),
            f"{REMOTE_ROOT}/frontend/nginx.conf",
        )

        with sftp.open(f"{REMOTE_ROOT}/backend/.env", "w") as env_file:
            env_file.write(make_runtime_env())
        sftp.chmod(f"{REMOTE_ROOT}/backend/.env", 0o600)

        with sftp.open(COMPOSE_PATH, "r") as compose_file:
            current_compose = compose_file.read().decode("utf-8")
        updated_compose = update_compose(current_compose)
        with sftp.open(COMPOSE_PATH, "w") as compose_file:
            compose_file.write(updated_compose)
        sftp.close()

        print("Validating Docker Compose...")
        run_remote(
            client,
            f"docker compose -f {COMPOSE_PATH} config --quiet",
            timeout=60,
        )

        print("Building and starting trip services...")
        run_remote(
            client,
            f"docker compose -f {COMPOSE_PATH} up -d --build "
            "trip-backend-learn trip-frontend",
            timeout=1800,
            show_output=True,
        )

        print("Waiting for services...")
        time.sleep(8)
        health = run_remote(
            client,
            "curl -fsS --max-time 15 http://127.0.0.1:8001/health",
            timeout=30,
        )
        frontend_status = run_remote(
            client,
            "curl -sS -o /dev/null -w '%{http_code}' --max-time 15 "
            "http://127.0.0.1:82/",
            timeout=30,
        )
        containers = run_remote(
            client,
            "docker ps --filter name=trip- --format "
            "'{{.Names}}|{{.Status}}|{{.Ports}}'",
            timeout=30,
        )

        print(f"Backend health: {health.strip()}")
        print(f"Frontend HTTP status: {frontend_status.strip()}")
        print("Containers:")
        print(containers.strip())
    finally:
        client.close()


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, socket.error, paramiko.SSHException) as exc:
        print(f"Deployment failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
