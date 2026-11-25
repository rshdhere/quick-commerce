#!/usr/bin/env python3
"""Inspect a proposed Git revision range or draft a local GitHub PR body."""

import argparse
import json
import os
import subprocess
import sys


def git(*args):
    result = subprocess.run(
        ["git", "--no-optional-locks", *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    if result.returncode:
        raise ValueError(result.stderr.decode(errors="replace").strip() or "Git command failed")
    return result.stdout


def revision(ref):
    return git("rev-parse", "--verify", "--end-of-options", ref + "^{commit}").decode().strip()


def positive_issue(value):
    if not value.isascii() or not value.isdecimal() or int(value) < 1:
        raise argparse.ArgumentTypeError("expected a positive GitHub issue number")
    return int(value)


def entries(base, directory):
    tree = base + ":" + directory
    rows = git("ls-tree", "--full-tree", "-z", tree).split(b"\0")
    for row in filter(None, rows):
        metadata, name = row.split(b"\t", 1)
        yield metadata.split()[0], os.fsdecode(name)


def default_templates(base):
    """Check root, .github and docs without walking the full source tree."""
    templates = []
    directories = [""]
    for directory in directories:
        prefix = directory + "/" if directory else ""
        for mode, name in entries(base, directory):
            path = prefix + name
            lower = name.casefold()
            if mode == b"040000":
                if not directory and lower in (".github", "docs"):
                    directories.append(path)
                elif lower == "pull_request_template" and directory.casefold() in ("", "docs", ".github"):
                    directories.append(path)
            elif mode in (b"100644", b"100755"):
                if directory.casefold().split("/")[-1] == "pull_request_template":
                    if lower.endswith((".md", ".txt")):
                        templates.append(path)
                elif lower in ("pull_request_template", "pull_request_template.md", "pull_request_template.txt"):
                    templates.append(path)
    return sorted(templates)


def draft(base, args):
    path = args.template
    if path is None:
        templates = default_templates(base)
        if len(templates) > 1:
            options = ", ".join(json.dumps(name) for name in templates)
            raise ValueError(f"select a target template with --template PATH. Available paths: {options}")
        path = next(iter(templates), None)
    if path:
        entry = base + ":" + path
        template = git("cat-file", "blob", entry)
    else:
        template = b"""## Summary

<!-- Describe who is affected and what changes for them. -->

## Verification

<!-- Record the checks you ran, their results, and any pending verification. -->
"""
    links = []
    if args.issue:
        links.append(f"{'Refs' if args.partial else 'Fixes'} #{args.issue}")
    if args.umbrella:
        links.append(f"Refs #{args.umbrella}")
    if links:
        sys.stdout.buffer.write(("\n".join(links) + "\n\n").encode())
    sys.stdout.buffer.write(template)


def report(base, head, merge_base, paths):
    dirty = bool(git("status", "--porcelain=v1", "-z", "--untracked-files=normal"))
    print(f"Target base  {base}\nProposed head  {head}\nMerge base  {merge_base}")
    print(f"Current checkout  {'has uncommitted changes' if dirty else 'clean'}")
    print("Commits and exact author sign-offs (informational local trailer check)")
    fmt = "%H%x00%an%x00%ae%x00%s%x00%(trailers:key=Signed-off-by,valueonly,unfold)"
    fields = git("log", "--reverse", "-z", "--format=" + fmt, base + ".." + head).split(b"\0")
    for i in range(0, len(fields) - 1, 5):
        sha, name, email, subject, trailers = fields[i:i + 5]
        author = name + b" <" + email + b">"
        signed = author in (line.strip() for line in trailers.splitlines())
        status = "signed by author" if signed else "no exact author sign-off"
        print(f"  {sha[:12].decode()}  {status}  {json.dumps(subject.decode(errors='replace'))}")
    print("Changed paths (committed changes since the merge base)")
    for path in paths:
        print("  " + json.dumps(os.fsdecode(path)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, help="actual PR target commit or local remote-tracking ref")
    parser.add_argument("--head", default="HEAD", help="proposed commit or branch (default HEAD)")
    parser.add_argument("--body", action="store_true", help="print a local draft using the base's PR template")
    parser.add_argument("--template", help="exact repository-relative template path on the base for --body")
    parser.add_argument("--issue", type=positive_issue, help="issue fully resolved by the PR")
    parser.add_argument("--partial", action="store_true", help="reference --issue without closing it")
    parser.add_argument("--umbrella", type=positive_issue, help="additional tracking issue to reference")
    args = parser.parse_args()
    if not args.body and (args.issue or args.umbrella or args.partial or args.template is not None):
        parser.error("--template, --issue, --partial and --umbrella require --body")
    if args.partial and not args.issue:
        parser.error("--partial requires --issue")
    if args.umbrella and args.umbrella == args.issue:
        parser.error("use --partial to reference the primary issue as a tracking issue")
    if args.template is not None and any(part in ("", ".", "..") for part in args.template.split("/")):
        parser.error("--template must be a repository-relative file path")
    try:
        base, head = revision(args.base), revision(args.head)
        merge_bases = git("merge-base", "--all", base, head).decode().splitlines()
        if len(merge_bases) != 1:
            raise ValueError("the selected commits need a single merge base")
        merge_base = merge_bases[0]
        paths = git("diff", "--no-ext-diff", "--no-renames", "--no-relative", "--name-only", "-z",
                    merge_base, head, "--").split(b"\0")[:-1]
        if not paths:
            raise ValueError("the selected head has no committed changes relative to the merge base")
        if args.body:
            draft(base, args)
        else:
            report(base, head, merge_base, paths)
    except (ValueError, OSError) as error:
        parser.exit(1, f"pr_brief: {error}\n")


if __name__ == "__main__":
    main()
