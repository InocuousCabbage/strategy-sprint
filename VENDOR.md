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

Run before any commit that moves content from a private repo into this
one:

    python3 path/to/private_scan.py --terms <your-team's-canonical-list>

Exits 1 on any error. The tool lives at
InocuousCabbage/copy-audit-stack (`scripts/private_scan.py`). The
terms list is NOT in this repo and must not be: an enumeration of
what you must not publish is itself a thing you must not publish.
See the scanner's `data/private-terms.example.txt` for the format.

## Sync changelog

| Date | Upstream SHA | Notes |
|------|--------------|-------|
| 2026-08-05 | ce73ca84f7462b2ca2d701e0c413dec62e94445f | Initial vendor. Includes upstream genericization of a "Sender Name" example placeholder that had a name colliding with the copy-up gate's private-terms enumeration. |
