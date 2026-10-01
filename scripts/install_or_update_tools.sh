#!/usr/bin/env bash
# ==============================================================================
# scripts/install_or_update_tools.sh
#
# Pulls the platform-appropriate release binaries from:
#   - git@github.com:ahndunn/cv-writer.git (or ahndunn/cv-writer)
#   - git@github.com:ahndunn/profile-curator.git (or ahndunn/profile-curator)
# Checks the latest release version on GitHub, compares with local version,
# and downloads / updates the stateless CLI binaries in bin/.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
BIN_DIR="${REPO_ROOT}/bin"
VERSIONS_FILE="${BIN_DIR}/.versions.json"

mkdir -p "${BIN_DIR}"

# 1. Detect OS and Architecture for GitHub release asset matching
detect_platform() {
  local os_name arch_name
  os_name="$(uname -s)"
  arch_name="$(uname -m)"

  case "${os_name}" in
    Linux)
      case "${arch_name}" in
        x86_64)  TARGET_TRIPLE="x86_64-unknown-linux-gnu" ;;
        aarch64|arm64) TARGET_TRIPLE="aarch64-unknown-linux-gnu" ;;
        *) echo "[-] Unsupported Linux architecture: ${arch_name}" >&2; exit 1 ;;
      esac
      EXT="tar.xz"
      EXE_SUFFIX=""
      ;;
    Darwin)
      # macOS builds if available, fallback notice
      case "${arch_name}" in
        x86_64)  TARGET_TRIPLE="x86_64-apple-darwin" ;;
        arm64)   TARGET_TRIPLE="aarch64-apple-darwin" ;;
        *) echo "[-] Unsupported macOS architecture: ${arch_name}" >&2; exit 1 ;;
      esac
      EXT="tar.xz"
      EXE_SUFFIX=""
      ;;
    MINGW*|MSYS*|CYGWIN*)
      case "${arch_name}" in
        x86_64)  TARGET_TRIPLE="x86_64-pc-windows-msvc" ;;
        aarch64|arm64) TARGET_TRIPLE="aarch64-pc-windows-msvc" ;;
        *) echo "[-] Unsupported Windows architecture: ${arch_name}" >&2; exit 1 ;;
      esac
      EXT="zip"
      EXE_SUFFIX=".exe"
      ;;
    *)
      echo "[-] Unsupported operating system: ${os_name}" >&2
      exit 1
      ;;
  esac
  echo "[+] Detected platform target: ${TARGET_TRIPLE} (${EXT})"
}

# 2. Get latest release tag using GitHub CLI (gh) or fallback to GitHub API
get_latest_release_tag() {
  local repo="$1"
  local tag=""
  if command -v gh >/dev/null 2>&1; then
    tag="$(gh release list --repo "${repo}" --limit 1 --json tagName --jq '.[0].tagName' 2>/dev/null || true)"
  fi
  if [ -z "${tag}" ]; then
    tag="$(curl -sSL "https://api.github.com/repos/${repo}/releases/latest" 2>/dev/null | grep '"tag_name":' | head -n 1 | sed -E 's/.*"([^"]+)".*/\1/' || true)"
  fi
  if [ -z "${tag}" ]; then
    echo "[-] Failed to fetch latest release tag for ${repo}" >&2
    exit 1
  fi
  echo "${tag}"
}

# 3. Read recorded local version
get_local_version() {
  local binary_name="$1"
  if [ -f "${VERSIONS_FILE}" ]; then
    grep -o "\"${binary_name}\": *\"[^\"]*\"" "${VERSIONS_FILE}" 2>/dev/null | sed -E 's/.*"([^"]+)".*/\1/' || echo "none"
  else
    echo "none"
  fi
}

# 4. Save recorded local version
set_local_version() {
  local binary_name="$1"
  local version="$2"
  python3 -c "
import json, os
path = '${VERSIONS_FILE}'
data = {}
if os.path.exists(path):
    try:
        with open(path, 'r') as f:
            data = json.load(f)
    except Exception:
        data = {}
data['${binary_name}'] = '${version}'
with open(path, 'w') as f:
    json.dump(data, f, indent=2)
"
}

# 5. Download and extract binary
install_or_update_tool() {
  local repo="$1"
  local binary_name="$2"
  local force="${3:-false}"

  echo "=================================================="
  echo "[*] Processing ${binary_name} (${repo})..."
  local latest_tag
  latest_tag="$(get_latest_release_tag "${repo}")"
  local local_tag
  local_tag="$(get_local_version "${binary_name}")"

  echo "    Current local:  ${local_tag}"
  echo "    Latest release: ${latest_tag}"

  local target_bin="${BIN_DIR}/${binary_name}${EXE_SUFFIX}"
  if [ "${force}" != "true" ] && [ "${local_tag}" = "${latest_tag}" ] && [ -x "${target_bin}" ]; then
    echo "[✓] ${binary_name} is already up to date (${latest_tag})."
    return 0
  fi

  echo "[i] Updating ${binary_name} to ${latest_tag}..."

  local asset_name="${binary_name}-${TARGET_TRIPLE}.${EXT}"
  local tmp_work
  tmp_work="$(mktemp -d "/tmp/${binary_name}_dl_XXXXXX")"
  trap 'rm -rf "${tmp_work}"' RETURN

  echo "    Downloading asset: ${asset_name}"
  if command -v gh >/dev/null 2>&1; then
    gh release download "${latest_tag}" --repo "${repo}" -p "${asset_name}" --dir "${tmp_work}"
  else
    local download_url="https://github.com/${repo}/releases/download/${latest_tag}/${asset_name}"
    curl -sSL -f "${download_url}" -o "${tmp_work}/${asset_name}"
  fi

  echo "    Extracting binary..."
  if [ "${EXT}" = "tar.xz" ]; then
    tar -xf "${tmp_work}/${asset_name}" -C "${tmp_work}"
  elif [ "${EXT}" = "zip" ]; then
    unzip -q "${tmp_work}/${asset_name}" -d "${tmp_work}"
  fi

  # Find extracted binary executable
  local extracted_bin
  extracted_bin="$(find "${tmp_work}" -type f -name "${binary_name}${EXE_SUFFIX}" | head -n 1)"

  if [ -z "${extracted_bin}" ]; then
    echo "[-] Error: Executable ${binary_name}${EXE_SUFFIX} not found in archive" >&2
    exit 1
  fi

  chmod +x "${extracted_bin}"
  mv "${extracted_bin}" "${target_bin}"
  set_local_version "${binary_name}" "${latest_tag}"
  echo "[✓] Successfully installed ${binary_name} (${latest_tag}) -> ${target_bin}"
}

# --- Main Entry ---
detect_platform

FORCE_UPDATE="false"
if [ "${1:-}" = "--force" ] || [ "${1:-}" = "-f" ]; then
  FORCE_UPDATE="true"
fi

install_or_update_tool "ahndunn/cv-writer" "cv-writer" "${FORCE_UPDATE}"
install_or_update_tool "ahndunn/profile-curator" "profile-curator" "${FORCE_UPDATE}"

echo "=================================================="
echo "[✓] All CLI tool binaries verified in ${BIN_DIR}:"
ls -la "${BIN_DIR}"
