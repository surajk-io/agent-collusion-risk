# Vendored upstream source

`django-saas-starter/` is the pinned upstream working tree vendored without Git
metadata so reviewers can reconstruct variants offline. It is **not** modified
by the fixture.

- Upstream: <https://github.com/k1y0miiii/django-saas-starter>
- Commit: `7ff2daaf78290ea5350e6373367f3d2172d4c6a4`
- Git tree: `7741d0fcbf487cf9270785c212d7617898e349e9`
- License: MIT; see `django-saas-starter/LICENSE` and the fixture root `LICENSE`.

`scripts/reconstruct_variant.sh` checks the vendored content against the pinned
Git tree hash before applying a patch. The independent verification command is
in `PROVENANCE.md`. Do not edit these files; make feature changes in
`patches/` and the reconstructed trees.
