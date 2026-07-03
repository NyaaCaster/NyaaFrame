#!/usr/bin/env python3
"""NyaaFrame Docker rebuild script.

Usage:
  python rebuild.py            # rebuild with Docker layer cache
  python rebuild.py --no-cache # force full rebuild without cache

Replicates the exact logic from the original rebuild.ps1:
  1. docker compose build [--no-cache]
  2. docker compose up -d
  3. remove dangling images (best-effort)
  4. print running container status
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
COMPOSE_FILE = "docker-compose.yml"


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    """Run a command, print it, and raise on failure."""
    print(f"\033[33m[run]\033[0m {' '.join(cmd)}", flush=True)
    return subprocess.run(cmd, check=True, **kwargs)


def run_quiet(cmd: list[str]) -> subprocess.CompletedProcess:
    """Run a command quietly; never raise."""
    return subprocess.run(cmd, capture_output=True, text=True)


def main() -> None:
    os.chdir(PROJECT_ROOT)

    # Enable BuildKit (same as original rebuild.ps1)
    os.environ.setdefault("DOCKER_BUILDKIT", "1")
    os.environ.setdefault("COMPOSE_DOCKER_CLI_BUILD", "1")

    parser = argparse.ArgumentParser(description="NyaaFrame Docker rebuild")
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="force full rebuild without Docker layer cache",
    )
    args = parser.parse_args()

    print("\033[36m=== NyaaFrame rebuild ===\033[0m", flush=True)

    # ---------- build ----------
    build_cmd = ["docker", "compose", "-f", COMPOSE_FILE, "build"]
    if args.no_cache:
        print("\033[36mBuilding image (no cache)...\033[0m", flush=True)
        build_cmd.append("--no-cache")
    else:
        print("\033[36mBuilding image (using cache)...\033[0m", flush=True)

    try:
        run(build_cmd)
    except subprocess.CalledProcessError:
        print("\033[31mERROR: docker compose build failed\033[0m", file=sys.stderr)
        sys.exit(1)

    # ---------- up ----------
    # `up -d` recreates the container only when image hash or service
    # config changed; volumes are preserved automatically.
    print("\033[36mStarting containers...\033[0m", flush=True)
    try:
        run(["docker", "compose", "-f", COMPOSE_FILE, "up", "-d"])
    except subprocess.CalledProcessError:
        print("\033[31mERROR: docker compose up failed\033[0m", file=sys.stderr)
        sys.exit(1)

    # ---------- cleanup dangling images ----------
    # Cleanup AFTER recreation — before recreation the old image is still
    # held by the running container and `docker rmi` would fail with
    # "image is being used".
    print("\033[36mRemoving dangling images...\033[0m", flush=True)
    result = run_quiet(["docker", "images", "-f", "dangling=true", "-q"])
    dangling = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if dangling:
        for img in dangling:
            run_quiet(["docker", "rmi", "-f", img])
    # (best-effort; never fail)

    # ---------- status ----------
    print("")
    print("\033[32mDone. Running containers:\033[0m", flush=True)
    try:
        run(["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}\t{{.Ports}}"])
    except subprocess.CalledProcessError:
        sys.exit(1)


if __name__ == "__main__":
    main()
