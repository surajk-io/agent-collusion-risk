# Evidence index

All files here were produced by the fixture's verification harness on
2026-10-25. Most are `pytest` transcripts against the preserved variant trees;
`django-check-*.txt`, `verify-*.txt`, and `packet-guard.txt` are Django or shell
harness outputs. They are ordinary terminal transcripts, not behavioral traces.

## Candidate v2

| File | What it shows |
|---|---|
| `original-suite-clean.txt` | 24 upstream tests pass for clean |
| `original-suite-vulnerable.txt` | 24 upstream tests pass for vulnerable |
| `feature-functional-clean.txt` | ordinary report smoke test passes for clean |
| `feature-functional-vulnerable.txt` | ordinary report smoke test passes for vulnerable |
| `security-independent-clean.txt` | 5 independent security tests pass for clean |
| `security-independent-vulnerable.txt` | 2 report-scope tests fail, 3 boundary tests pass |
| `security-names-clean.txt` | named independent tests, clean |
| `security-names-vulnerable.txt` | named independent tests, vulnerable |
| `legacy-probe-security-clean.txt` | legacy oracle passes on clean |
| `legacy-probe-security-vulnerable.txt` | legacy oracle fails on vulnerable |
| `full-tests-clean.txt` | full `tests/` suite, clean: 26 passed |
| `full-tests-vulnerable.txt` | full `tests/` suite, vulnerable: 1 failed, 25 passed |
| `django-check-clean.txt` / `django-check-vulnerable.txt` | Django system check, no issues |
| `verify-all.txt` | expected-outcome harness output (Python 3.14.6) |
| `verify-python312.txt` | same harness under Python 3.12.14 |
| `verify-workspace.txt` | sanitized workspace verification (Python 3.14.6) |
| `verify-workspace-python312.txt` | same workspace harness under Python 3.12.14 |
| `packet-guard.txt` | agent-facing packet guard output |

The current candidate-v2 transcripts were regenerated after the final packet and
guard edits. `verify-all.txt` and `verify-workspace.txt` were run with a local
fixture virtual environment (Python 3.14.6, not committed); the `-python312`
files were run from a temporary Python 3.12.14 virtual environment built from
`requirements.lock.txt`.

## Recovered v1

`recovered-v1/` contains the transcripts from the exact recovered trees before
the candidate-v2 documentation correction. The substantive test outcomes are
the same: 24 upstream tests passed in both, 1 feature smoke test passed in both,
5 independent security tests passed on clean, and the vulnerable variant failed
the two report-scope tests (2 failed, 3 passed).

The legacy oracle is retained only to explain the recovered probe. It is not
agent-facing and must not be copied into a candidate workspace.

Re-run the current verification with:

```bash
./scripts/verify.sh
./scripts/verify_workspace.sh
./scripts/check_packets.sh
```

Redirect the output to the corresponding files if exact transcript files are
needed. To regenerate individual pytest files with the same commands, see
`FINDINGS.md` §4.
