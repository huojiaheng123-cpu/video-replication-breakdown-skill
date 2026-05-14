from __future__ import annotations

from pathlib import Path
import os
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()


def run(args: list[str], cwd: Path) -> int:
    print("\n$ " + " ".join(str(arg) for arg in args))
    return subprocess.run(args, cwd=cwd, check=False).returncode


def command(names: list[str]) -> str | None:
    for name in names:
        found = shutil.which(name)
        if found:
            return found
    return None


def candidate_codex_homes() -> list[Path]:
    values: list[Path] = []
    env_home = os.environ.get("CODEX_HOME")
    if env_home:
        values.append(Path(env_home).expanduser())
    values.extend([HOME / ".codex", HOME / ".agents"])
    seen: set[str] = set()
    result: list[Path] = []
    for path in values:
        key = str(path.resolve()) if path.exists() else str(path)
        if key not in seen:
            seen.add(key)
            result.append(path)
    return result


def find_watch_video() -> Path | None:
    for codex_home in candidate_codex_homes():
        path = codex_home / "skills" / "watch-video"
        if (path / "SKILL.md").exists():
            return path
    for name in ["watch-video-skill", "watch-video"]:
        path = ROOT.parent / name
        if (path / "SKILL.md").exists():
            return path
    return None


def main() -> int:
    print("Setting up local dependencies for video-replication-breakdown full mode.")
    print("This script can install local Python/Node dependencies and delegate to watch-video setup.")
    print("It cannot silently install Codex plugins, FFmpeg, Chrome/Edge, or other system apps.")

    failures = 0

    if (ROOT / "requirements.txt").exists():
        failures += run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], ROOT) != 0

    if (ROOT / "package.json").exists():
        npm = command(["npm", "npm.cmd"])
        if npm:
            failures += run([npm, "install"], ROOT) != 0
        else:
            print("\nNode/npm was not found. Install Node.js LTS, restart the terminal, then rerun this script.")
            failures += 1

    watch_path = find_watch_video()
    if watch_path:
        setup = watch_path / "scripts" / "setup_full.py"
        if setup.exists():
            print(f"\nFound watch-video at: {watch_path}")
            failures += run([sys.executable, str(setup)], watch_path) != 0
        else:
            print(f"\nwatch-video found at {watch_path}, but scripts/setup_full.py is missing.")
            failures += 1
    else:
        print("\nwatch-video is not installed.")
        print("Install it with skill-installer from:")
        print("https://github.com/huojiaheng123-cpu/watch-video-skill")
        print("Then restart Codex and rerun this setup script.")
        failures += 1

    run([sys.executable, "scripts/check_capabilities.py"], ROOT)

    if failures:
        print("\nSome setup steps still need manual action. Follow the missing-item fixes above.")
        return 1
    print("\nLocal dependencies are ready. If Browser plugin or system tools are missing, install/enable them manually and rerun the check.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
