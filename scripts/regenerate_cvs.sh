#!/usr/bin/env bash
# ==============================================================================
# scripts/regenerate_cvs.sh
#
# Convenient bash wrapper to regenerate CV PDF(s) from cv.json.
# Examples:
#   ./scripts/regenerate_cvs.sh cvs/general-ai-engineer
#   ./scripts/regenerate_cvs.sh --all
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="${SCRIPT_DIR}/render_cv.py"

chmod +x "${PYTHON_SCRIPT}"
exec python3 "${PYTHON_SCRIPT}" "$@"
