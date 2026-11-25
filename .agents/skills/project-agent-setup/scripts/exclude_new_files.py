#!/usr/bin/env python3
"""Locally exclude individual new Codex files, before creating them."""

import argparse
from pathlib import Path
import subprocess


def git(*args):
    return subprocess.run(["git", "--literal-pathspecs", *args], capture_output=True, check=True)


def exclude_files(names):
    root = Path(git("rev-parse", "--show-toplevel").stdout.decode().strip()).resolve()
    if root != Path.cwd().resolve():
        raise ValueError("run from the repository root")
    entries = []
    for name in dict.fromkeys(names):
        path = Path(name)
        if not (name in {"AGENTS.md", "AGENTS.override.md"} or
                (len(path.parts) >= 2 and path.parts[0] in {".agents", ".codex"})):
            raise ValueError(f"expected a project instruction, skill or role file: {name!r}")
        if str(path) != name or ".." in path.parts or any(ord(c) < 32 for c in name):
            raise ValueError(f"expected a normalized relative file path: {name!r}")
        target = root / path
        if target.resolve() != target or target.is_symlink() or target.is_dir():
            raise ValueError(f"expected a file path without symlinks: {name!r}")
        if any(p.exists() and not p.is_dir() for p in target.parents):
            raise ValueError(f"a parent is already a file: {name!r}")
        if git("ls-files", "-z", "--", name).stdout:
            raise ValueError(f"already tracked: {name!r}")
        match = subprocess.run(["git", "check-ignore", "-v", "-z", "--stdin"],
                               input=name.encode() + b"\0", capture_output=True)
        if match.returncode == 0:
            pattern = match.stdout.split(b"\0")[2]
            if pattern.startswith(b"!"):
                raise ValueError(f"an existing Git rule explicitly includes {name!r}")
            continue
        if match.returncode != 1:
            raise ValueError(f"could not check ignore status: {name!r}")
        if target.exists():
            raise ValueError(f"already exists and is visible to Git: {name!r}")
        literal = "".join("\\" + c if c in "\\*?[] " else c for c in name)
        entries.append("/" + literal)

    if entries:
        exclude = Path(git("rev-parse", "--path-format=absolute", "--git-path", "info/exclude")
                       .stdout.decode().strip())
        if exclude.resolve() != exclude or exclude.is_symlink():
            raise ValueError("the local exclude path contains a symlink")
        exclude.parent.mkdir(exist_ok=True)
        with exclude.open("ab+") as stream:
            stream.seek(0, 2)
            separator = b""
            if stream.tell():
                stream.seek(-1, 2)
                if stream.read(1) != b"\n":
                    separator = b"\n"
            stream.write(separator + ("\n".join(entries) + "\n").encode())
    print(f"Added {len(entries)} local exclude entries.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="new private file paths relative to the project root")
    args = parser.parse_args()
    try:
        exclude_files(args.paths)
    except subprocess.CalledProcessError as exc:
        parser.exit(1, exc.stderr.decode(errors="replace") or f"git exited {exc.returncode}\n")
    except (OSError, ValueError) as exc:
        parser.exit(1, f"{exc}\n")


if __name__ == "__main__":
    main()
