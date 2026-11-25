#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
.agents/scripts/verify.sh
.agents/scripts/health-check.sh
bun install --frozen-lockfile
