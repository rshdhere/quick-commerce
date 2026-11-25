---
name: project-agent-setup
description: Set up or refresh Codex instructions, a codebase map, local workflows and review roles for a specific Git checkout when the user asks for project agent setup.
---

# Set up Codex for this project

Run this workflow on request in the target checkout. Installing the skill makes it available for later use. Setup ends after local verification.

## Learn the checkout

From the repository root, inspect the working tree, existing instruction files (including nested ones), installed project skills, README, contribution guide, manifests, build scripts and CI. Trace one representative user operation from its entry point to its implementation and tests. Record paths relative to the root, package and module boundaries, how sources become generated artifacts, and the focused checks that actually exist. For a monorepo identify each relevant working directory. Derive conventions from the current sources and preserve unrelated work.

When migrating existing Claude project guidance, read the relevant project instructions, commands and skills. Map the repository knowledge into the corresponding rules, roles or guides. Keep credentials, permission grants and private runtime settings out of shared material. Verify the migrated guidance against its sources before removing legacy files when the user explicitly requests cleanup.

## Choose the instruction entry point

Default to personal checkout files. For a requested team setup, use the project's tracked instruction conventions and review the resulting diff.

- If the repository has no root instruction file, create `AGENTS.md` with the map and task routing. If a local instruction file already serves this role, integrate only the missing context and preserve its existing directives.
- If the project supplies a root `AGENTS.md` and needs a personal layer, create an ignored `AGENTS.override.md`. Codex selects the override in place of the same-directory `AGENTS.md`. Start the override with an explicit instruction to read and apply the current root `AGENTS.md` in full before using the personal notes. When the project uses a configured fallback instruction filename, preserve it with the same explicit reference.
- If the effective root override is already tracked, leave it under project ownership. Put the personal map in a small project skill under `.agents/skills/` and give the user its invocation. Read existing nested directives in the scope where work will take place.
- Preserve existing files, symlinks and project roles. Reuse existing sections or pick a distinct local filename where a personal file would collide with team content. On repeat setup, update changed facts without duplicating entries.

## Write the useful parts

Keep the entry point short. Link to substantive material in the requested layout using paths relative to the project root.

| Location | Content to derive from this checkout |
| --- | --- |
| `.agents/context/` | Codebase map with actual entry points, subsystem ownership, data flow, test fixtures, and deployment or compatibility boundaries. Link existing architectural decisions. |
| `.agents/rules/` | Project-specific conventions that influence implementation, testing and contributions. Identify the authoritative source for each rule. |
| `.agents/workflows/` | Practical steps for recurring changes, with a first code path, a focused verification command, and an observable completion condition. |
| `.agents/templates/` | Drafting aids for the PR, issue or decision formats the project uses. Reuse official templates and their checklists. |
| `.agents/skills/` | Discoverable `<name>/SKILL.md` entry points for repeated tasks unique to this project. Reuse installed general skills. |
| `.codex/agents/` | A read-only reviewer or other requested roles. Use meaningful project boundary checks and the locally supported role configuration. |

Create files that carry verified project knowledge. When the user requests a particular tree, fill each requested guide or role for the project. Reuse an existing `.codex/config.toml` when configuration is needed. Project settings should contain only necessary overrides.

When `oss-contribution` is installed, route issue discovery and PR preparation to it by skill name in the chosen entry point. Record the verified upstream repository, how its contributors signal acceptance and ownership, and where to find its current PR template, as applicable. A search request ends with the findings. Start implementation or publication when requested for the chosen work.

## Keep personal files local

Before creating private files, run [the exclude helper](scripts/exclude_new_files.py) from the target repository root using its path in the installed skill. Pass the exact file paths the setup will create. For example:

```sh
python3 "$setup_skill_dir/scripts/exclude_new_files.py" \
  AGENTS.override.md .agents/context/codebase.md .agents/workflows/issue-search.md
```

Set `setup_skill_dir` to the directory containing this `SKILL.md`. The helper appends root-anchored entries to Git's local `info/exclude`. Git shares this file across linked worktrees. It checks for tracked paths, collisions and symlinks, and skips already ignored paths. If a proposed path collides, reuse the existing content appropriately or choose a new file. Exclude only files created for this personal setup. Leave repository `.gitignore` and existing team paths alone.

## Verify

Resolve the actual entry point and follow its links. Check that referenced commands, files and role names exist. For personal setup, run `git check-ignore -v -- <created-paths>` and compare `git status --short` with the initial status. Confirm tracked instructions and the index retained their original state. Report the entry point, one realistic invocation and any verification that the environment could not perform.
