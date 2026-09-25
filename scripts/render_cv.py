#!/usr/bin/env python3
"""
scripts/render_cv.py

Regenerate CV PDF(s) from cv.json using the cv-writer MCP server over JSON-RPC (stdio),
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
from pathlib import Path


def find_binary(repo_root: Path) -> Path:
    bin_path = repo_root / "bin" / "cv-writer-mcp"
    if not bin_path.is_file():
        # Check windows executable
        bin_path_exe = repo_root / "bin" / "cv-writer-mcp.exe"
        if bin_path_exe.is_file():
            return bin_path_exe
        print(f"[-] Error: cv-writer-mcp binary not found at {bin_path}.", file=sys.stderr)
        print("[-] Run `./scripts/install_or_update_mcps.sh` first.", file=sys.stderr)
        sys.exit(1)
    if not os.access(bin_path, os.X_OK):
        print(f"[-] Error: {bin_path} is not executable. Run `chmod +x {bin_path}`.", file=sys.stderr)
        sys.exit(1)
    return bin_path


class McpClient:
    def __init__(self, binary_path: Path):
        self.process = subprocess.Popen(
            [str(binary_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        self._request_id = 0

    def send_request(self, method: str, params: dict | None = None) -> dict:
        self._request_id += 1
        req = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": method,
        }
        if params is not None:
            req["params"] = params

        payload = json.dumps(req)
        assert self.process.stdin is not None
        self.process.stdin.write(payload + "\n")
        self.process.stdin.flush()

        assert self.process.stdout is not None
        while True:
            line = self.process.stdout.readline()
            if not line:
                stderr_output = ""
                if self.process.stderr:
                    stderr_output = self.process.stderr.read()
                raise RuntimeError(
                    f"cv-writer-mcp terminated unexpectedly (code {self.process.poll()}). Stderr: {stderr_output}"
                )
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                if isinstance(data, dict) and data.get("id") == self._request_id:
                    return data
            except json.JSONDecodeError:
                # Ignore non-json logging lines on stdout if any
                continue

    def initialize(self):
        self.send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "render_cv_cli", "version": "1.0.0"}
        })
        # Send initialized notification
        notif = {"jsonrpc": "2.0", "method": "notifications/initialized"}
        assert self.process.stdin is not None
        self.process.stdin.write(json.dumps(notif) + "\n")
        self.process.stdin.flush()

    def render_cv(self, cv_profile: dict, output_path: str) -> dict:
        res = self.send_request("tools/call", {
            "name": "render_cv",
            "arguments": {
                "profile": cv_profile,
                "output_path": output_path
            }
        })
        return res

    def close(self):
        try:
            if self.process.stdin and not self.process.stdin.closed:
                self.process.stdin.close()
            self.process.terminate()
            self.process.wait(timeout=2)
        except Exception:
            self.process.kill()


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


def render_single_cv(client: McpClient, json_path: Path, output_pdf_path: Path):
    print(f"[*] Reading CV data: {json_path}")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # In case payload is wrapped under {"cv_profile": ...} or directly CvProfile
    profile = data.get("cv_profile", data)

    output_pdf_path.parent.mkdir(parents=True, exist_ok=True)
    abs_out_str = str(output_pdf_path.resolve())

    print(f"[*] Rendering to PDF: {abs_out_str} ...")
    resp = client.render_cv(profile, abs_out_str)

    if "error" in resp:
        print(f"[-] MCP Error: {resp['error']}", file=sys.stderr)
        return False

    result = resp.get("result", {})
    if result.get("isError"):
        content = result.get("content", [])
        msgs = [c.get("text", "") for c in content if isinstance(c, dict)]
        print(f"[-] Tool execution failed:\n" + "\n".join(msgs), file=sys.stderr)
        return False

    # Extract success text
    content = result.get("content", [])
    success_text = "\n".join(c.get("text", "") for c in content if isinstance(c, dict) and "text" in c)
    if success_text:
        print(f"[✓] {success_text.strip()}")
    else:
        print(f"[✓] Successfully compiled: {abs_out_str}")

    if output_pdf_path.exists():
        size_kb = output_pdf_path.stat().st_size / 1024
        print(f"    File size: {size_kb:.1f} KB")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Regenerate CV PDF(s) directly from cv.json via cv-writer-mcp."
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

    print(f"[+] Starting cv-writer-mcp from {binary_path} ...")
    client = McpClient(binary_path)
    client.initialize()

    all_ok = True
    try:
        for json_p, pdf_p in targets:
            print("-" * 50)
            ok = render_single_cv(client, json_p, pdf_p)
            if not ok:
                all_ok = False
    finally:
        client.close()

    print("=" * 50)
    if all_ok:
        print("[✓] All requested CVs successfully regenerated.")
        sys.exit(0)
    else:
        print("[-] One or more CVs failed to regenerate.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
