# Performed offline checks and limits

26 October 2026. **Documents only; no simulator, behavioral LLM trial or fixture-suite rerun.** Candidate branch created from freshly fetched canonical main 1c6927f. All three requested branch heads were fetched and inspected. Existing fixture code, tests and approved checkpoint files were not edited or merged.

Executed `python3 /private/tmp/acr-m3-doc-checks.py` in the isolated worktree. Results are recorded in artifact-checks.json. This temporary verification script checks documents/Git blobs and elementary combinatorics only; it is not a behavioral simulator or a committed tool. Ten check groups passed:

- 61 pinned source document, patch, test, script and evidence SHA-256 entries match exact Git objects.
- All 3 variant trees/module hashes, 5 patch hashes and 3 hidden-test/support hashes match the original fixture MANIFEST.
- Both sanitized-source manifest digests, exact reporting source blocks and prior/current diff content match (blank context whitespace normalized for Markdown in displayed diffs) the neutral records. Seven common technical-context files match both sanitized references. No build hash is asserted to exist.
- Twelve retained ordinary, smoke, single-request and stateful transcript summaries match reported figures. The sanitized25 result is recorded in the source MANIFEST and workspace-check procedure, not a newly produced pytest transcript. Existing results remain attributed to their source branch/environment.
- All proposed literal runtime files pass a researcher/variant/oracle-marker scan. Manual comparison also checked policy versus qualification claims. This is not a renderer noninterference test or proof of semantic leak absence.
- JSON parses, 19 local schema references resolve and object contracts specify additionalProperties=false. No JSON-Schema validator dependency was available in this shell: **no payload-validation suite or runtime permission test is claimed**.
- Graph maps are bijective with no self-review. Enumerating 16 equal-weight approval patterns reproduces P7/16 versus R1/16 any completed cycle and mean2 deployments in each. This is mathematics under iid half-probability approvals, not an agent result.
- Budget arithmetic: 28 primary slots/episode; exploratory32-episode option896 slots; 4096 generated-token ceiling implies3,670,016 total generated tokens. No price, capability or power estimate.

A fresh read-only adversarial review independently rechecked source digests and key packet/test provenance; see independent-review.md for objections and dispositions. A reviewer is not an experimental agent trial.

## Checks still requiring future approved implementation

The offline-test-matrix contains **test specifications**, including prior communication/authority/history/lifecycle cases and new Q01–Q17 qualification cases. No actual runtime permission, message barrier, atomic commit, idempotency, secret projection, hidden-oracle noninterference, provider JSON adapter or lifecycle audit test was run: no simulator exists. Q01/Q02 and literal-file aspects of Q03/Q11 were partially checked statically, not end to end. Real maximal-token fit requires a selected provider/tokenizer and final attachments. Scripted P/R negotiation traces remain to be replayed through actual implemented interfaces after authorization.

No Redis/Postgres/multi-worker verification, actual build artifact, complete four-service allocation, accepted organizational qualification certificate, human behavioral annotation, provider capability check or LLM behavioral call is supplied. No inference about agent collusion propensity is made. Missing lifecycle/configuration/control/budget fields block launch even if these document checks pass.

## Rechecking pinned source digests from this branch

Run in a checkout with the pinned commits fetched (stdlib Python only):

```python
import hashlib, json, pathlib, subprocess
p = pathlib.Path("research/organizational-coalitional-risk/M3-integrated-review-package")
m = json.loads((p / "source-manifest.json").read_text())
for f in m["files"]:
    b = subprocess.check_output(["git", "show", m["refs"][f["source"]] + ":" + f["path"]])
    assert hashlib.sha256(b).hexdigest() == f["sha256"], f["path"]
```

Final local-link, diff-whitespace and candidate-only staged-path checks are recorded below after execution. Package inventory hashes exclude artifact-hashes.json itself and this report to avoid self-reference; the final Git commit binds the complete document tree. The source manifest is researcher-only and must never enter agent context.

Final document checks: **20 local Markdown links resolve**; all package lines pass trailing-whitespace checks. The original main worktree remains clean at 1c6927f48824e657a5d15e2b67550a8b28e5f1b5. Staged paths and Git whitespace are checked as part of the final commit operation.

`git diff --cached --check` passed. Final staged-scope check: exactly28 added files, all inside this candidate package; zero modifications to existing files. All26 inventoried artifact hashes rechecked.
