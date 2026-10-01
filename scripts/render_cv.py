#!/usr/bin/env python3
"""
scripts/render_cv.py

Regenerate CV PDF(s) from cv.json directly using the stateless cv-writer CLI,
without needing an interactive AI agent session.

Usage:
    # Regenerate a specific variant
    ./scripts/render_cv.py cvs/general-ai-engineer
    ./scripts/render_cv.py cvs/general-ai-engineer/cv.json

    # Regenerate all variants in cvs/
    ./scripts/render_cv.py --all

    # Specify custom output path
    ./scripts/render_cv.py cvs/general-ai-engineer -o /path/to/output.pdf
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def find_binary(repo_root: Path) -> Path:
    bin_path = repo_root / "bin" / "cv-writer"
    if not bin_path.is_file():
        # Check windows executable
        bin_path_exe = repo_root / "bin" / "cv-writer.exe"
        if bin_path_exe.is_file():
            return bin_path_exe
        # Check PATH
        path_tool = subprocess.run(["which", "cv-writer"], capture_output=True, text=True)
        if path_tool.returncode == 0 and path_tool.stdout.strip():
            return Path(path_tool.stdout.strip())
        print(f"[-] Error: cv-writer binary not found at {bin_path}.", file=sys.stderr)
        print("[-] Run `./scripts/install_or_update_tools.sh` first.", file=sys.stderr)
        sys.exit(1)
    if not os.access(bin_path, os.X_OK):
        print(f"[-] Error: {bin_path} is not executable. Run `chmod +x {bin_path}`.", file=sys.stderr)
        sys.exit(1)
    return bin_path


def resolve_cv_paths(target: str, repo_root: Path) -> tuple[Path, Path]:
    p = Path(target)
    if not p.is_absolute():
        p = (repo_root / p).resolve()

    if p.is_dir():
        json_path = p / "cv.json"
        pdf_path = p / "cv.pdf"
    elif p.is_file() and p.name.endswith(".json"):
        json_path = p
        pdf_path = p.parent / "cv.pdf"
    else:
        # Check if user passed directory name without cvs/ prefix
        candidate = repo_root / "cvs" / target
        if candidate.is_dir():
            json_path = candidate / "cv.json"
            pdf_path = candidate / "cv.pdf"
        else:
            raise FileNotFoundError(f"Cannot locate cv.json from target: {target}")

    if not json_path.is_file():
        raise FileNotFoundError(f"cv.json does not exist: {json_path}")

    return json_path, pdf_path


def render_single_cv(
    binary_path: Path,
    json_path: Path,
    output_pdf_path: Path,
    changelog_dir: str | None = None,
    emit_tex: bool = False,
    dry_run: bool = False,
) -> bool:
    print(f"[*] Reading CV data: {json_path}")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # In case payload is wrapped under {"cv_profile": ...}
    profile_data = data.get("cv_profile", data)

    output_pdf_path.parent.mkdir(parents=True, exist_ok=True)
    abs_out_str = str(output_pdf_path.resolve())

    # Build command
    cmd = [
        str(binary_path),
        "compile",
        "--profile",
        "-",
        "--output",
        abs_out_str,
    ]

    if changelog_dir:
        cmd.extend(["--changelog-dir", changelog_dir])
    if emit_tex:
        cmd.append("--emit-tex")
    if dry_run:
        cmd.append("--dry-run")

    print(f"[*] Compiling to PDF: {abs_out_str} ...")
    proc = subprocess.run(
        cmd,
        input=json.dumps(profile_data),
        text=True,
        capture_output=True,
    )

    if proc.returncode != 0:
        print(f"[-] Compilation failed with exit code {proc.returncode}:", file=sys.stderr)
        if proc.stdout.strip():
            print(proc.stdout.strip(), file=sys.stderr)
        if proc.stderr.strip():
            print(proc.stderr.strip(), file=sys.stderr)
        return False

    if proc.stdout.strip():
        print(f"[✓] {proc.stdout.strip()}")
    else:
        print(f"[✓] Successfully compiled: {abs_out_str}")

    if output_pdf_path.exists():
        size_kb = output_pdf_path.stat().st_size / 1024
        print(f"    File size: {size_kb:.1f} KB")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Regenerate CV PDF(s) directly from cv.json via stateless cv-writer CLI."
    )
    parser.add_argument(
        "target",
        nargs="?",
        help="Path to cv.json or variant directory (e.g. cvs/general-ai-engineer)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Regenerate all CV variants located under cvs/",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Custom output PDF path (applicable only when targeting a single CV)",
    )
    parser.add_argument(
        "--changelog-dir",
        help="Directory to record timestamped profile snapshots and markdown changelogs",
    )
    parser.add_argument(
        "--emit-tex",
        action="store_true",
        help="Also emit raw LaTeX source alongside the PDF",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate schema and render template without running LuaLaTeX",
    )

    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    binary_path = find_binary(repo_root)

    if not args.all and not args.target:
        parser.print_help()
        sys.exit(1)

    targets: list[tuple[Path, Path]] = []

    if args.all:
        cvs_dir = repo_root / "cvs"
        if not cvs_dir.is_dir():
            print(f"[-] Directory not found: {cvs_dir}", file=sys.stderr)
            sys.exit(1)
        for item in sorted(cvs_dir.iterdir()):
            if item.is_dir() and (item / "cv.json").is_file():
                targets.append((item / "cv.json", item / "cv.pdf"))

        if not targets:
            print(f"[-] No variants containing cv.json found in {cvs_dir}")
            sys.exit(1)
    else:
        try:
            json_path, pdf_path = resolve_cv_paths(args.target, repo_root)
            if args.output:
                pdf_path = Path(args.output).resolve()
            targets.append((json_path, pdf_path))
        except Exception as e:
            print(f"[-] {e}", file=sys.stderr)
            sys.exit(1)

    print(f"[+] Using cv-writer CLI from {binary_path}")

    all_ok = True
    for json_p, pdf_p in targets:
        print("-" * 50)
        ok = render_single_cv(
            binary_path=binary_path,
            json_path=json_p,
            output_pdf_path=pdf_p,
            changelog_dir=args.changelog_dir,
            emit_tex=args.emit_tex,
            dry_run=args.dry_run,
        )
        if not ok:
            all_ok = False

    print("=" * 50)
    if all_ok:
        print("[✓] All requested CVs successfully regenerated.")
        sys.exit(0)
    else:
        print("[-] One or more CVs failed to regenerate.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
