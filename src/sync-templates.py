#!/usr/bin/env python3

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


REMOTE_DIR = "/usr/share/remarkable/templates"
REMOTE_JSON = f"{REMOTE_DIR}/templates.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync reMarkable templates.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--all", action="store_true", help="Sync all templates in templates/.")
    mode.add_argument("--tmp", dest="template", help="Sync a single template by name.")
    parser.add_argument("--host", default="remarkable_usb", help="SSH host alias.")
    parser.add_argument("--icon", default="\ue98c", help="Icon code string.")
    parser.add_argument("--category", default="Custom", help="Category name.")
    parser.add_argument("--no-restart", action="store_true", help="Skip UI restart.")
    return parser.parse_args()


def normalize_name(name: str) -> str:
    base = os.path.basename(name)
    if base.endswith(".template"):
        base = base[: -len(".template")]
    return base


def collect_templates(templates_dir: Path, args: argparse.Namespace) -> list[Path]:
    if args.all:
        files = sorted(templates_dir.glob("*.template"))
    else:
        base = normalize_name(args.template)
        file_path = templates_dir / f"{base}.template"
        if not file_path.is_file():
            raise SystemExit(f"Template not found: {file_path}")
        files = [file_path]

    if not files:
        raise SystemExit("No template files found.")
    return files


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def copy_templates(host: str, files: list[Path]) -> None:
    for file_path in files:
        run(["scp", str(file_path), f"{host}:{REMOTE_DIR}/"])


def update_templates_json(host: str, icon: str, category: str, files: list[Path]) -> list[Path]:
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp_path = Path(tmp.name)

    try:
        run(["scp", f"{host}:{REMOTE_JSON}", str(tmp_path)])

        with tmp_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            templates = data
            root_is_list = True
        elif isinstance(data, dict) and isinstance(data.get("templates"), list):
            templates = data["templates"]
            root_is_list = False
        else:
            raise SystemExit("Unsupported templates.json structure")

        existing_names = {
            entry.get("name")
            for entry in templates
            if isinstance(entry, dict) and isinstance(entry.get("name"), str)
        }

        added_files: list[Path] = []

        for file_path in files:
            with file_path.open("r", encoding="utf-8") as f:
                tmpl = json.load(f)

            display_name = tmpl.get("name") or file_path.stem
            filename = file_path.stem

            if display_name in existing_names:
                continue

            new_entry = {
                "name": display_name,
                "filename": filename,
                "iconCode": icon,
                "categories": [category],
            }
            templates.append(new_entry)
            added_files.append(file_path)

        output = templates if root_is_list else {**data, "templates": templates}

        if added_files:
            with tmp_path.open("w", encoding="utf-8") as f:
                json.dump(output, f, indent=2, ensure_ascii=True)
                f.write("\n")

            run(["scp", str(tmp_path), f"{host}:{REMOTE_JSON}"])
        return added_files
    finally:
        tmp_path.unlink(missing_ok=True)


def restart_ui(host: str) -> None:
    run(["ssh", host, "systemctl restart xochitl"])


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parent.parent
    templates_dir = repo_root / "templates"

    if not templates_dir.is_dir():
        raise SystemExit(f"Missing templates directory: {templates_dir}")

    files = collect_templates(templates_dir, args)
    new_files = update_templates_json(args.host, args.icon, args.category, files)
    if new_files:
        copy_templates(args.host, new_files)
        if not args.no_restart:
            restart_ui(args.host)
        print("Done.")
    else:
        print("No changes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
