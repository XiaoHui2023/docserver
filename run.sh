#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
exec release/bin/docserver-sync --watch
