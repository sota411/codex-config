#!/usr/bin/env bash
set -euo pipefail

if ! command -v npx >/dev/null 2>&1; then
  echo "Error: npx is required but not found on PATH." >&2
  exit 1
fi

has_session_flag="false"
for arg in "$@"; do
  case "$arg" in
    --)
      break
      ;;
    -s|-s=*|--session|--session=*)
      has_session_flag="true"
      break
      ;;
  esac
done

cmd=(npx --yes --package @playwright/cli playwright-cli)
default_session="${PLAYWRIGHT_CLI_SESSION:-${CODEX_THREAD_ID:-}}"
if [[ "${has_session_flag}" != "true" && -n "${default_session}" ]]; then
  cmd+=(--session "${default_session}")
fi
cmd+=("$@")

exec "${cmd[@]}"
