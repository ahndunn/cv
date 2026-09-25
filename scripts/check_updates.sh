#!/usr/bin/env bash
# ==============================================================================
# scripts/check_updates.sh
#
# Inspects current installed versions versus latest GitHub releases for:
#   - git@github.com:ahndunn/cv-writer.git
#   - git@github.com:ahndunn/profile-curator.git
# Returns exit code 0 if everything is up to date, or exit code 1 if updates available.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
BIN_DIR="${REPO_ROOT}/bin"
VERSIONS_FILE="${BIN_DIR}/.versions.json"

get_latest_tag() {
  local repo="$1"
  local tag=""
  if command -v gh >/dev/null 2>&1; then
    tag="$(gh release list --repo "${repo}" --limit 1 --json tagName --jq '.[0].tagName' 2>/dev/null || true)"
  fi
  if [ -z "${tag}" ]; then
    tag="$(curl -sSL "https://api.github.com/repos/${repo}/releases/latest" 2>/dev/null | grep '"tag_name":' | head -n 1 | sed -E 's/.*"([^"]+)".*/\1/' || true)"
  fi
  echo "${tag}"
}

get_local_version() {
  local binary_name="$1"
  if [ -f "${VERSIONS_FILE}" ]; then
    grep -o "\"${binary_name}\": *\"[^\"]*\"" "${VERSIONS_FILE}" 2>/dev/null | sed -E 's/.*"([^"]+)".*/\1/' || echo "none"
  else
    echo "none"
  fi
}

echo "=== Checking MCP Binary Versions ==="
UPDATES_AVAILABLE=0

check_binary() {
  local repo="$1"
  local binary_name="$2"

  local local_tag
  local_tag="$(get_local_version "${binary_name}")"
  local latest_tag
  latest_tag="$(get_latest_tag "${repo}")"

  printf "%-22s: Local [%-8s]  Latest [%-8s]  Status: " "${binary_name}" "${local_tag}" "${latest_tag}"
  if [ "${local_tag}" = "none" ]; then
    echo "NOT INSTALLED"
    UPDATES_AVAILABLE=1
  elif [ "${local_tag}" != "${latest_tag}" ]; then
    echo "UPDATE AVAILABLE (${local_tag} -> ${latest_tag})"
    UPDATES_AVAILABLE=1
  else
    echo "UP TO DATE"
  fi
}

check_binary "ahndunn/cv-writer" "cv-writer-mcp"
check_binary "ahndunn/profile-curator" "profile-curator-mcp"

echo "===================================="
if [ "${UPDATES_AVAILABLE}" -eq 1 ]; then
  echo "Updates or missing binaries detected! Run: ./scripts/install_or_update_mcps.sh"
  exit 1
else
  echo "All MCP binaries are up to date."
  exit 0
fi
