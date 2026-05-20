#!/usr/bin/env bash
# Mint Street — production preview
# Builds the frontend (if missing/stale) and serves backend + frontend
# from a single uvicorn process on port 8000.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="$REPO_ROOT/frontend"
BACKEND_DIR="$REPO_ROOT/backend"
BUILD_DIR="$FRONTEND_DIR/build"
INDEX_HTML="$BUILD_DIR/index.html"

needs_build=0
if [[ ! -f "$INDEX_HTML" ]]; then
    needs_build=1
else
    # Rebuild if any frontend source is newer than the built index.html.
    if [[ -n "$(find "$FRONTEND_DIR/src" "$FRONTEND_DIR/public" -newer "$INDEX_HTML" -print -quit 2>/dev/null)" ]]; then
        needs_build=1
    fi
fi

if [[ "$needs_build" == "1" ]]; then
    echo "[mint-street] Building frontend bundle…"
    cd "$FRONTEND_DIR"
    DISABLE_ESLINT_PLUGIN=true CI=true npm run build
else
    echo "[mint-street] Frontend bundle is up to date; skipping build."
fi

cd "$BACKEND_DIR"

# Activate venv if present.
if [[ -f "$BACKEND_DIR/.venv/bin/activate" ]]; then
    # shellcheck disable=SC1091
    source "$BACKEND_DIR/.venv/bin/activate"
fi

echo "Mint Street running at http://localhost:8000"
exec uvicorn server:app --host 0.0.0.0 --port 8000
