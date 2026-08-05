# Vendor manifest — pipelines/gtm_generator/

This document explains where the vendored GTM plan generator lives, why
it lives here rather than being imported, and how to sync it forward
without silently reintroducing private data into this public repo.

## What's vendored

`pipelines/gtm_generator/` is copied from an upstream private generator
repo. Every `.py` file in that tree carries a provenance header naming
the upstream source SHA and pointing at this sync script.

`pipelines/gtm_generator/cli.py` is **not vendored** — it is
strategy-sprint's own wrapper around the vendored modules. Edit it
directly.

## Why vendor rather than import

The generator is not yet published as a package. Vendoring gives us:

- A pinned SHA (in each file's header) so behaviour cannot drift between
  the generator and this repo without the sync being explicit.
- No network dependency at test or run time (fixtures + generator all
  live in the tree).
- Ability to ship strategy-sprint as a self-contained repo that
  contributors can clone + run without needing access to the private
  upstream.

The trade-off is that fixes reach here only through explicit sync. That
is a feature: an unaudited upstream cannot silently change the shape of
generated GTM plans.

## Sync procedure

1. Set the environment variable pointing at your local upstream checkout:

       export UPSTREAM_GTM_GENERATOR_PATH=/absolute/path/to/upstream/checkout

   The path itself is deliberately not stored in this repo. Different
   maintainers keep the upstream at different paths on disk, and the
   private repo name stays out of public files.

2. Run the sync script:

       ./scripts/sync-from-upstream.sh

   It will rsync the module tree in, reapply the vendor-provenance
   header with the fresh upstream SHA, and print the SHA to stdout.

3. **Run the copy-up private-data gate before committing** (see next
   section). This is not optional. The sync script does not run it for
   you.

4. Run tests:

       pytest tests/gtm_generator/

5. Update the changelog below with the new SHA + a one-line note on
   what was different.

6. Commit only after all four preceding steps pass.

## Copy-up gate (run before every commit that includes a sync)

The copy-up gate verifies no private terms slipped through in the diff
before the sync is committed to this public repo.

**Automation state (accurate as of 2026-08-05):** the gate is NOT
automated as a runnable script yet. Before any commit that vendors or
re-syncs content from a private upstream into this repo, ask the
canonical gate-runner to sweep the staged diff manually. A runnable
script is planned at the copy-audit-stack repo
(InocuousCabbage/copy-audit-stack); when it lands, this section
becomes a pointer to it and this manual step goes away.

**Why the enumeration doesn't live here:** the private-terms list has
to live in exactly one place. Restating it in every consuming repo
guarantees drift as new client names are added over time. When the
runnable script exists, the enumeration will live in the scanner's
own `data/` directory and every repo that pulls the script picks up
the same enumeration.

**What to expect from a sweep, whether manual or scripted:**

- Scan runs against the **added lines** of the staged diff (not the
  whole file), so pre-existing exposure doesn't drown the signal on
  its first run in an established repo.
- Positive-control fixture must fire on all gates before a clean run
  is trusted. A "clean" report with no positive control is exactly
  the false-green pattern the scan exists to prevent.
- If a gate fires, either (a) the added content is genuinely private
  and should not go public (fix at source or leave unstaged), or (b)
  the enumeration incorrectly flags a legitimate term (file an issue
  at the scanner repo — do NOT silence the gate locally, since a
  locally-silenced gate is how canonical-drift-with-different-numbers
  starts).

## Sync changelog

| Date | Upstream SHA | Notes |
|------|--------------|-------|
| 2026-08-05 | ce73ca84f7462b2ca2d701e0c413dec62e94445f | Initial vendor. Includes upstream genericization of a "Sender Name" example placeholder that had a name colliding with the copy-up gate's private-terms enumeration. |
