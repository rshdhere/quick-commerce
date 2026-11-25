---
name: oss-contribution
description: Find worthwhile issues in an upstream GitHub repository, evaluate a candidate or tracking-issue slice, and take selected work through reproduction, implementation, PR preparation and review. Use for the contribution stage the user requests.
---

# Open-source contributions

Identify the upstream repository, default branch, issue tracker and local project instructions. A fork's origin can point to a personal copy. Read the project's contribution guide, issue and PR templates, ownership rules and AI policy. Apply project-specific skills when available. The commands below assume GitHub and an authenticated `gh`. For another tracker use its equivalent issue and review evidence.

## Find work with a demonstrable outcome

1. Start from the user's component or the project's current invitation to contribute. A triaged bug carrying a clear impact and a reproducible example often makes a better first change than a popular proposal awaiting a design decision. Verify the local meaning of labels, the active milestone and whether anyone has taken the work.
2. Use the bundled [issue scout](scripts/issue_scout.py). Set `repo` to the upstream `OWNER/REPO`, and `scout` to the installed script's path. The default search covers unassigned open issues labeled `help wanted` or `good first issue`. Supply the project's own labels or a topic when appropriate.

   ```sh
   python3 "$scout" --repo "$repo" find --limit 8
   python3 "$scout" --repo "$repo" find --query 'label:bug pagination'
   python3 "$scout" --repo "$repo" inspect "$issue_number" --terms pagination cursor
   ```

3. Read the most recent decision on the *specific change*. Look for an assignee, a claim or withdrawal in comments, a linked PR and unlinked work described in different terms. Check the reason an earlier attempt closed. On tracking issues, evaluate the proposed slice. Read full discussions when results are truncated. An incomplete search leaves availability unresolved.
4. For each recommendation give the issue link, who is affected, evidence that the work is wanted and available, the owning code path, and the first test or experiment. Distinguish a reported symptom from one reproduced on the current upstream revision. If the evidence rules out all candidates, report why. A request for a shortlist ends with those findings.

## Deliver the selected change

- Agree on a concrete acceptance criterion from the issue and its discussion. Preserve unrelated work. Start selected changes on an isolated branch or worktree based on the current target revision. Trace the behavior from its normal entry point and look for an existing implementation or test that establishes the expected contract.
- For a bug, run the same regression on the base and the proposed fix. Capture the expected failure and passing result. For new behavior cover the acceptance criterion and one realistic edge or compatibility case. For performance work compare like workloads. Use the project's actual checks, and record the exact revision tested and any gap.
- Give an independent reviewer the issue or slice, base and head, affected paths and verification evidence. Focus review on behavior, compatibility, rollout and the most likely regression. Resolve blockers and rerun affected checks on the final head.

## Prepare and follow up on a PR

Use the [PR brief helper](scripts/pr_brief.py) from the target checkout. Set `brief` to the installed script's path and `base` to the verified target ref. The local report identifies the compared commits, affected paths, checkout state and author sign-off trailers. Apply the project's actual DCO policy.

```sh
python3 "$brief" --base "$base" --head HEAD
python3 "$brief" --base "$base" --head HEAD --body --issue "$issue_number"
```

Fill the draft with the user-visible outcome, cause or design decision, actual verification and any upgrade or backport implications. A partial tracking issue uses `--partial`. A separately resolved issue can reference its tracker with `--umbrella`. Complete the target project's checklist and disclose assistance according to its policy.

Keep the draft local until publication is requested. When publishing, recheck upstream scope, duplicate work, authorization and branch head. Reuse an existing PR for the same change. Follow review threads and CI on the latest head and explain what each follow-up fixed. Record durable maintainer decisions with their date and source in the project's own contribution notes.
