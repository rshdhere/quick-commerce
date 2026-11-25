#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
for script in .agents/scripts/*.sh; do bash -n "$script"; done
python3 - <<'PY'
from pathlib import Path
import tomllib

def check(path):
    assert path.is_file() and path.read_text().strip(), f"Missing or empty: {path}"

for group, names in {
    'context': 'architecture product tech-stack database decisions',
    'rules': 'coding security testing performance git',
    'templates': 'implementation-plan adr pull-request incident-report',
    'workflows': 'feature-development bug-fixing parallel-execution release-management',
}.items():
    for name in names.split():
        check(Path('.agents', group, name + '.md'))
for name in 'implement-feature fix-bug code-review database-migration security-audit release'.split():
    path = Path('.agents/skills', name, 'SKILL.md')
    check(path)
    metadata = path.read_text().split('---', 2)[1].splitlines()
    assert f'name: {name}' in metadata and any(line.startswith('description: ') for line in metadata), path
for name in 'architect backend frontend database devops security reviewer tester researcher'.split():
    role = tomllib.loads(Path('.codex/agents', name + '.toml').read_text())
    assert role['name'] == name and role['description'] and role['developer_instructions'], name
assert tomllib.loads(Path('.codex/config.toml').read_text())['agents']['max_threads'] > 0
check(Path('AGENTS.md'))
check(Path('.codex/rules/default.rules'))
PY
if command -v codex >/dev/null; then
  codex execpolicy check --rules .codex/rules/default.rules git push --force |
    python3 -c 'import json,sys; assert json.load(sys.stdin)["decision"] == "prompt"'
fi
echo "Project agent setup verified."
