from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid


ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()


def find_command(names: list[str]) -> str | None:
    for name in names:
        found = shutil.which(name)
        if found:
            return found
    return None


def try_command(args: list[str], cwd: Path | None = None, timeout: int = 20) -> tuple[bool, str]:
    try:
        proc = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout, check=False)
    except Exception as exc:
        return False, str(exc)
    lines = (proc.stdout or proc.stderr or "").strip().splitlines()
    detail = lines[0] if lines else f"exit code {proc.returncode}"
    return proc.returncode == 0, detail


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


def find_skill(skill_name: str, repo_name: str | None = None) -> Path | None:
    for codex_home in candidate_codex_homes():
        path = codex_home / "skills" / skill_name
        if (path / "SKILL.md").exists():
            return path

    sibling_names = [repo_name, skill_name] if repo_name else [skill_name]
    for name in sibling_names:
        if not name:
            continue
        path = ROOT.parent / name
        if (path / "SKILL.md").exists():
            return path

    return None


def find_browser_plugin() -> tuple[bool | None, str]:
    hits: list[str] = []
    for codex_home in candidate_codex_homes():
        skills = codex_home / "skills"
        for name in ["browser-use", "browser-operator"]:
            if (skills / name / "SKILL.md").exists():
                hits.append(str(skills / name))
        cache = codex_home / "plugins" / "cache"
        if cache.exists():
            for pattern in ["**/browser-use*/**/SKILL.md", "**/browser*/**/SKILL.md"]:
                for skill_file in cache.glob(pattern):
                    hits.append(str(skill_file.parent))
    if hits:
        return True, hits[0]
    return None, "cannot reliably detect active Codex Browser plugin from a standalone script"


def run_watch_video_check(watch_path: Path | None) -> tuple[str | None, str]:
    if not watch_path:
        return None, "watch-video skill not found"
    script = watch_path / "scripts" / "check_capabilities.py"
    if not script.exists():
        return None, f"missing {script}"
    try:
        proc = subprocess.run(
            [sys.executable, str(script), "--json"],
            cwd=watch_path,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except Exception as exc:
        return None, str(exc)
    output = proc.stdout.strip()
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip().splitlines()
        return None, detail[0] if detail else f"exit code {proc.returncode}"
    try:
        report = json.loads(output)
    except json.JSONDecodeError:
        return None, "watch-video check did not return valid JSON"
    return str(report.get("level") or "unknown"), f"{watch_path}"


def is_writable(path: Path) -> tuple[bool, str]:
    try:
        path.mkdir(parents=True, exist_ok=True)
        test = path / f".write-test-{uuid.uuid4().hex}"
        test.write_text("ok", encoding="utf-8")
        test.unlink(missing_ok=True)
    except Exception as exc:
        return False, str(exc)
    return True, str(path)


def collect() -> dict[str, object]:
    watch_path = find_skill("watch-video", "watch-video-skill")
    watch_level, watch_detail = run_watch_video_check(watch_path)
    browser_state, browser_detail = find_browser_plugin()
    node = find_command(["node", "node.exe"])
    npm = find_command(["npm", "npm.cmd"])
    npx = find_command(["npx", "npx.cmd"])

    html_template = ROOT / "assets" / "html-report-template.html"
    report_ref = ROOT / "references" / "report-structure.md"
    output_ok, output_detail = is_writable(Path.cwd() / "00_工作台")

    node_ok, node_detail = try_command([node, "--version"]) if node else (False, "not found")
    npm_ok, npm_detail = try_command([npm, "--version"]) if npm else (False, "not found")
    npx_ok, npx_detail = try_command([npx, "--version"]) if npx else (False, "not found")

    checks = [
        {
            "name": "watch-video skill",
            "available": watch_path is not None,
            "detail": watch_detail,
            "use": "Provides the evidence base: playback, frame extraction, media probing, audio extraction, and ASR.",
            "fix": "Install https://github.com/huojiaheng123-cpu/watch-video-skill with skill-installer, then restart Codex.",
        },
        {
            "name": "watch-video capability level",
            "available": watch_level == "full",
            "detail": watch_level or watch_detail,
            "use": "Full replication reports need the same evidence depth as the original local environment.",
            "fix": "Run watch-video scripts/check_capabilities.py and scripts/setup_full.py until it reaches full or explains the remaining manual steps.",
        },
        {
            "name": "HTML report template",
            "available": html_template.exists(),
            "detail": str(html_template),
            "use": "Base template for the visual case asset page.",
            "fix": "Reinstall this skill from GitHub.",
        },
        {
            "name": "Report structure reference",
            "available": report_ref.exists(),
            "detail": str(report_ref),
            "use": "Defines the required sections and quality bar for the HTML report.",
            "fix": "Reinstall this skill from GitHub.",
        },
        {
            "name": "00_工作台 writable",
            "available": output_ok,
            "detail": output_detail,
            "use": "Stores evidence, extracted frames, transcripts, scripts, prompts, and HTML reports.",
            "fix": "Run Codex from a workspace where it can write files, or create 00_工作台 manually.",
        },
        {
            "name": "Node.js",
            "available": node_ok,
            "detail": node_detail,
            "use": "Supports browser automation and optional HTML/report tooling.",
            "fix": "Install Node.js LTS, then rerun setup.",
        },
        {
            "name": "npm/npx",
            "available": npm_ok and npx_ok,
            "detail": f"npm={npm_detail}; npx={npx_detail}",
            "use": "Installs Playwright/browser dependencies when watch-video needs them.",
            "fix": "Install Node.js LTS, then rerun setup.",
        },
        {
            "name": "Codex Browser plugin",
            "available": browser_state,
            "detail": browser_detail,
            "use": "Lets Codex inspect local HTML reports and interactively verify webpage/video evidence.",
            "fix": "Enable the Browser/browser-use plugin in Codex. GitHub skills cannot silently install plugins.",
        },
    ]

    required_full = [
        checks[0]["available"] is True,
        checks[1]["available"] is True,
        checks[2]["available"] is True,
        checks[3]["available"] is True,
        checks[4]["available"] is True,
    ]
    if all(required_full):
        level = "full"
    elif watch_path is not None and html_template.exists() and output_ok:
        level = "recommended"
    else:
        level = "minimal"

    return {"level": level, "checks": checks, "watch_video_path": str(watch_path) if watch_path else None}


def print_human(report: dict[str, object]) -> None:
    print(f"Current video-replication-breakdown capability level: {report['level']}")
    print("\nAvailable / missing:")
    for item in report["checks"]:
        state = "unknown" if item["available"] is None else ("ok" if item["available"] else "missing")
        print(f"- {item['name']}: {state}")
        print(f"  use: {item['use']}")
        print(f"  detail: {item['detail']}")
        if item["available"] is not True:
            print(f"  fix: {item['fix']}")

    print("\nFast path to same effect as the original local setup:")
    print("1. Install both skills: video-replication-breakdown-skill and watch-video-skill.")
    print("2. Run this script, then run scripts/setup_full.py in this skill folder.")
    print("3. Run watch-video/scripts/check_capabilities.py until watch-video is full.")
    print("4. Enable Browser/browser-use in Codex if interactive webpage/video verification is needed.")
    print("5. Restart Codex after installing skills, plugins, or system tools.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check whether this computer can run video-replication-breakdown like the source setup.")
    parser.add_argument("--json", action="store_true", help="Print JSON only.")
    args = parser.parse_args()
    report = collect()
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_human(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
