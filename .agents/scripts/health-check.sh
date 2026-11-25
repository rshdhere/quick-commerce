#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
if command -v free >/dev/null; then free -h; fi
node -e 'if (+process.versions.node.split(".")[0] < 24) throw Error("Node 24+ required")'
expected=$(node -p "require('./package.json').devEngines.packageManager.version")
[[ $(bun --version) == "$expected" ]] || { echo "Expected Bun $expected" >&2; exit 1; }
python3 - <<'PY'
import json
from pathlib import Path
root = json.loads(Path('package.json').read_text())
packages = [json.loads(p.read_text()) for glob in root['workspaces'] for p in Path('.').glob(glob + '/package.json')]
names = {p['name'] for p in packages}
required = {name for p in packages for key in ('dependencies', 'devDependencies') for name in p.get(key, {}) if name.startswith('@repo/')}
missing = sorted(required - names)
if missing:
    raise SystemExit('Missing from declared workspaces: ' + ', '.join(missing))
PY
echo "Workspace prerequisites verified."
