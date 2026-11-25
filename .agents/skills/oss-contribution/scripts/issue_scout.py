#!/usr/bin/env python3
"""Collect read-only GitHub evidence for an explicitly selected GitHub.com repository. Outputs JSON."""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from itertools import zip_longest

DEFAULT_LABELS = ("help wanted", "good first issue")
PAGE_SIZE = 100
MAX_PAGES = 3
MAX_TEXT = 1600
COMMENTS_SHOWN = 16
PR_LIMIT = 12

LINKS_QUERY = """
query($owner:String!, $name:String!, $number:Int!) {
  repository(owner:$owner, name:$name) {
    issue(number:$number) {
      closedByPullRequestsReferences(first:50, includeClosedPrs:true) {
        nodes {title url state isDraft}
        pageInfo {hasNextPage}
      }
    }
  }
}
"""


class LookupFailure(Exception):
    pass


def gh_json(*args):
    try:
        result = subprocess.run(
            ["gh", "api", "--hostname", "github.com", *args],
            capture_output=True, text=True, timeout=25, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise LookupFailure(str(exc)) from exc
    if result.returncode:
        raise LookupFailure(result.stderr.strip()[:400] or f"gh exited {result.returncode}")
    try:
        return json.loads(result.stdout)
    except ValueError as exc:
        raise LookupFailure("GitHub returned invalid JSON") from exc


def lookup(gaps, label, action, fallback):
    try:
        return action()
    except (LookupFailure, KeyError, TypeError) as exc:
        gaps.append(f"{label}: {exc}")
        return fallback


def search(repo, query, limit):
    data = gh_json("--method", "GET", "search/issues", "-f", f"q=repo:{repo} {query}",
                   "-f", f"per_page={limit}")
    rows = []
    for item in data["items"]:
        if item["repository_url"].rstrip("/").casefold() == f"https://api.github.com/repos/{repo}".casefold():
            rows.append({
                "number": item["number"], "title": item["title"], "url": item["html_url"],
                "state": item["state"], "author": (item.get("user") or {}).get("login"),
                "association": item.get("author_association"), "updated": item["updated_at"],
                "milestone": (item.get("milestone") or {}).get("title"),
                "labels": [label["name"] for label in item["labels"]],
            })
    return {"matches": rows, "total": data["total_count"], "incomplete": data["incomplete_results"]}


def find(repo, query, labels, limit, gaps):
    if labels is None and not query:
        labels = DEFAULT_LABELS
    lanes = [query] if query else []
    if labels:
        lanes = []
        for label in dict.fromkeys(labels):
            qualifier = "label:" + json.dumps(label, ensure_ascii=False)
            lanes.append(f"{qualifier} {query}" if query else qualifier)
    results = []
    for lane in lanes:
        expression = f"is:issue is:open no:assignee {lane} sort:updated-desc"
        data = lookup(gaps, lane, lambda: search(repo, expression, limit), None)
        if data is None:
            results.append([])
            continue
        if data["incomplete"]:
            gaps.append(f"GitHub reported an incomplete search for {lane}")
        results.append(data["matches"])
    unique = {}
    for group in zip_longest(*results):
        for item in group:
            if item:
                unique.setdefault(item["number"], item)
    return {"queries": lanes, "candidates": list(unique.values())[:limit],
            "note": "Bounded shortlist of open, unassigned issues. Inspect each candidate for scope and ownership."}


def pages(route, gaps):
    rows = []
    for page in range(1, MAX_PAGES + 1):
        data = lookup(gaps, route, lambda: gh_json("--method", "GET", route, "-f",
                      f"per_page={PAGE_SIZE}", "-f", f"page={page}"), None)
        if data is None:
            break
        if not isinstance(data, list):
            gaps.append(f"Unexpected response for {route}")
            break
        rows.extend(data)
        if len(data) < PAGE_SIZE:
            break
    else:
        gaps.append(f"{route}: reached {MAX_PAGES * PAGE_SIZE} events, further pages unverified")
    return rows


def discussion_text(source):
    body = source.get("body") or ""
    return {"text": body[:MAX_TEXT], "excerpted": len(body) > MAX_TEXT}


def inspect(repo, number, terms, gaps):
    route = f"repos/{repo}/issues/{number}"
    issue = gh_json("--method", "GET", route)
    if (issue["number"] != number or
            issue["repository_url"].rstrip("/").casefold() != f"https://api.github.com/repos/{repo}".casefold()):
        raise LookupFailure(f"Issue moved outside {repo}#{number}, check its canonical URL")
    if "pull_request" in issue:
        raise LookupFailure(f"#{number} is a pull request")
    comments = pages(f"{route}/comments", gaps)
    if len(comments) != issue["comments"]:
        gaps.append("Issue comment count differs from the visible pages; refresh the discussion")
    if len(comments) > COMMENTS_SHOWN:
        gaps.append(f"Showing the earliest comment and latest {COMMENTS_SHOWN - 1}; read the full issue thread for intermediate decisions")
        comments = [comments[0], *comments[-(COMMENTS_SHOWN - 1):]]
    discussion = [{
        "author": (c.get("user") or {}).get("login"), "association": c.get("author_association"),
        "date": c["created_at"], "url": c["html_url"], **discussion_text(c),
    } for c in comments]
    events = pages(f"{route}/timeline", gaps)
    assignments, references = [], []
    for event in events:
        kind = event.get("event")
        if kind in ("assigned", "unassigned"):
            assignments.append({"event": kind, "user": (event.get("assignee") or {}).get("login"),
                                "date": event.get("created_at")})
        if kind == "cross-referenced":
            ref = (event.get("source") or {}).get("issue") or {}
            if ref.get("pull_request"):
                references.append({"url": ref["html_url"], "title": ref["title"], "state": ref["state"]})

    def closing_prs():
        owner, name = repo.split("/")
        data = gh_json("graphql", "-f", f"query={LINKS_QUERY}", "-f", f"owner={owner}",
                       "-f", f"name={name}", "-F", f"number={number}")
        links = data["data"]["repository"]["issue"]["closedByPullRequestsReferences"]
        if links["pageInfo"]["hasNextPage"]:
            gaps.append("First 50 linked PRs shown; further links unverified")
        return links["nodes"]

    linked = lookup(gaps, "explicit PR links", closing_prs, [])
    if not terms:
        words = re.findall(r"[\w-]{3,}", issue["title"].lower())
        stop = {"and", "are", "does", "for", "from", "should", "the", "with", "when"}
        terms = sorted(dict.fromkeys(w for w in words if w not in stop), key=len, reverse=True)[:2]
    searches = []
    if not terms:
        gaps.append("Supply --terms with a distinct symptom or component for the independent PR search")
    for query in [f'"#{number}"', *([" ".join(terms)] if terms else [])]:
        result = lookup(gaps, f"PR search {query}",
                        lambda: search(repo, f"is:pr in:title,body,comments {query}", PR_LIMIT), None)
        if result is None:
            continue
        if result["incomplete"] or result["total"] > len(result["matches"]):
            gaps.append(f"PR search {query}: showing {len(result['matches'])} of {result['total']} indexed matches")
        searches.append({"query": query, **result})
    if issue["state"] != "open":
        review = "closed"
    elif issue["assignees"]:
        review = "assigned"
    else:
        review = "needs_review"
    return {
        "status": review, "number": number, "title": issue["title"], "url": issue["html_url"],
        "state": issue["state"], "updated": issue["updated_at"],
        "milestone": (issue.get("milestone") or {}).get("title"),
        "assignees": [a["login"] for a in issue["assignees"]],
        "author": (issue.get("user") or {}).get("login"), "association": issue.get("author_association"),
        "labels": [l["name"] for l in issue["labels"]], "issue_body": discussion_text(issue),
        "assignment_history": assignments, "comments": discussion,
        "explicitly_linked_prs": linked, "timeline_pr_mentions": references, "pr_searches": searches,
        "note": "Read excerpted text at its URL. Verify reviewer authority, accepted scope, claims and PR overlap manually.",
    }


def repository_argument(value):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]*/[A-Za-z0-9_.-]+", value) or value.split("/")[1] in (".", ".."):
        raise argparse.ArgumentTypeError("expected a GitHub.com repository in OWNER/REPO form")
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=repository_argument, help="GitHub.com repository in OWNER/REPO form")
    sub = parser.add_subparsers(dest="command", required=True)
    finder = sub.add_parser("find", help="Shortlist open unassigned issues")
    finder.add_argument("--query", help="Additional GitHub issue search terms or qualifiers")
    finder.add_argument("--label", action="append", dest="labels",
                        help="Search this label; repeat to include alternatives. With --query, labels narrow each search.")
    finder.add_argument("--limit", type=int, default=8, metavar="1-50")
    inspector = sub.add_parser("inspect", help="Collect discussion, ownership and PR evidence")
    inspector.add_argument("number", type=int)
    inspector.add_argument("--terms", nargs="+", help="Distinctive component or symptom terms for PR search")
    args = parser.parse_args()
    if args.command == "find" and not 1 <= args.limit <= 50:
        parser.error("--limit must be between 1 and 50")
    if args.command == "inspect" and args.number < 1:
        parser.error("issue number must be positive")
    gaps = []
    if args.command == "find":
        report = find(args.repo, args.query, args.labels, args.limit, gaps)
    else:
        report = lookup(gaps, "GitHub issue", lambda: inspect(args.repo, args.number, args.terms, gaps), {})
    report.update(repository=args.repo, checked_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                  gaps=gaps, coverage="partial" if gaps else "bounded")
    print(json.dumps(report, indent=2, ensure_ascii=True))
    return int(bool(gaps))


if __name__ == "__main__":
    sys.exit(main())
