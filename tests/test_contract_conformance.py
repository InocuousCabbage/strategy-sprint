"""Contract conformance across the producer/consumer seam.

WHY THIS FILE EXISTS. The GTM contract has three parts that are each tested in
isolation and were, until now, never checked against each other:

  producer  the exercise skills, which are supposed to write sidecars
  contract  schema/strategy_sprint_input.schema.json
  consumer  pipelines/gtm_generator/loader.py, which reads payload keys

Every existing suite validates one part against fixtures written by whoever
wrote that part. A fixture authored by the contract's author always matches the
contract, so all of them stay green while the parts disagree with each other.
That is exactly what happened: on 2026-08-05 a hand-authored, schema-valid
sprint artifact was fed to the generator for the first time and it could not
produce a plan, because the loader reads keys the schema forbids. Neither test
suite went red, and neither was wrong.

These checks compare the parts to EACH OTHER rather than to fixtures. They are
deliberately mechanical: read the enum, grep the skills, walk the loader.

The failing ones are marked xfail(strict=True) rather than left red, because
turning main red is not this file's call to make. strict=True matters: if a
gap is partially closed the xfail becomes an unexpected pass and the suite
fails, so these cannot quietly rot into decoration. Delete the marker, do not
loosen it, when the underlying gap is closed.
"""
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schema" / "strategy_sprint_input.schema.json").read_text())
SKILLS = ROOT / ".claude" / "skills"
LOADER = ROOT / "pipelines" / "gtm_generator" / "loader.py"

EXERCISE_IDS = SCHEMA["$defs"]["exerciseId"]["enum"]
PAYLOADS = SCHEMA["$defs"]["payloads"]


def _skill_body(exercise_id):
    p = SKILLS / exercise_id / "SKILL.md"
    return p.read_text() if p.exists() else ""


def test_every_exercise_id_has_a_skill():
    """An enum entry with no skill is a contract naming something that cannot exist."""
    missing = [e for e in EXERCISE_IDS if not (SKILLS / e / "SKILL.md").exists()]
    assert not missing, f"exerciseId enum names skills that do not exist: {missing}"


@pytest.mark.xfail(
    strict=True,
    reason="KNOWN GAP 2026-08-05: only tool-inventory writes a sidecar. The other "
           "exercises produce no machine-readable output at all, so the generator "
           "reads a manifest and sidecars that nothing writes. Remove this marker "
           "when the producing side lands; do not loosen it.",
)
def test_every_exercise_instructs_writing_its_sidecar():
    """The contract is only real if something produces it.

    A payload schema describes what an exercise MUST emit. It cannot make the
    exercise emit anything. Without this check the gap reopens silently every
    time an exercise is added, because a new enum entry needs no producer to
    pass any other test.
    """
    # Require the skill to name ITS OWN sidecar path next to a write verb.
    # A first version matched the bare word "sidecar" and passed channel-strategy,
    # whose only mention is "once the sidecar is written" in a step that consumes
    # one. A precondition is not an instruction, and a check that accepts prose
    # about a thing as evidence the thing happens is the exact defect being
    # looked for here, committed by the instrument looking for it.
    silent = []
    for e in EXERCISE_IDS:
        body = _skill_body(e)
        names_own_path = re.search(rf"output/{re.escape(e)}\.yaml", body)
        write_verb = re.search(r"\b(write|save|emit|create)\b", body, re.I)
        if not (names_own_path and write_verb):
            silent.append(e)
    assert not silent, (
        "these exercises never mention writing a sidecar or updating the manifest, "
        f"so nothing produces their payload: {silent}"
    )


@pytest.mark.xfail(
    strict=True,
    reason="KNOWN GAP 2026-08-05: the orchestrator reads the manifest as a backstop "
           "but never creates it. An absent manifest is the exact state the "
           "two-level design exists to make impossible.",
)
def test_orchestrator_creates_the_manifest():
    body = _skill_body("strategy-sprint")
    creates = re.search(r"creat\w*[^.]{0,80}sprint-manifest|sprint-manifest[^.]{0,80}creat\w*",
                        body, re.I)
    assert creates, (
        "the orchestrator never creates output/sprint-manifest.yaml. Nothing does, "
        "so every consumer starts from a missing entry point."
    )


def _loader_payload_reads():
    """Keys the loader pulls out of exercise payloads, as (exercise_id, path).

    `path` is a tuple, because reads nest: `company = payload("company-overview")
    .get("company")` then `company.get("name")` is company-overview at
    ("company", "name"), NOT at ("name"). A first version flattened that and
    reported company.name and company.url as unreachable when both are perfectly
    well defined one level down. Out-of-domain hits are instrument bugs, so the
    instrument models the nesting rather than the report being caveated.

    Reads the source rather than importing, so this still reports when the module
    cannot import for an unrelated reason.
    """
    src = LOADER.read_text()
    # variable -> (exercise_id, path-prefix)
    origins = {}
    # v = payload("x")  -- the trailing (?!\s*\.) matters: without it this also
    # matches the PREFIX of `v = payload("x").get("k")` and registers v as the
    # payload root, which silently flattens one level of nesting and reports
    # perfectly reachable sub-keys as forbidden.
    for var, ex in re.findall(r'(\w+)\s*=\s*payload\(\s*["\']([a-z-]+)["\']\s*\)(?!\s*\.)', src):
        origins[var] = (ex, ())
    # v = payload("x").get("k")
    for var, ex, key in re.findall(
            r'(\w+)\s*=\s*payload\(\s*["\']([a-z-]+)["\']\s*\)\s*\.get\(\s*["\'](\w+)["\']', src):
        origins[var] = (ex, (key,))
    # v = <known>.get("k")
    for var, src_var, key in re.findall(r'(\w+)\s*=\s*(\w+)\s*\.get\(\s*["\'](\w+)["\']', src):
        if src_var in origins and var not in origins:
            ex, prefix = origins[src_var]
            origins[var] = (ex, prefix + (key,))

    reads = set()
    for var, key in re.findall(r'(\w+)\s*\.get\(\s*["\'](\w+)["\']', src):
        if var in origins:
            ex, prefix = origins[var]
            reads.add((ex, prefix + (key,)))
    for ex, key in re.findall(r'payload\(\s*["\']([a-z-]+)["\']\s*\)\s*\.get\(\s*["\'](\w+)["\']', src):
        reads.add((ex, (key,)))
    return sorted(reads)


def _reachable(spec, path):
    """Walk a payload schema down `path`. Unreachable only if a CLOSED object
    on the way lacks the key: an open object may legitimately carry anything."""
    node = spec
    for key in path:
        props = node.get("properties") or {}
        if key not in props:
            return node.get("additionalProperties") is not False
        node = props[key]
    return True


def test_every_payload_key_the_loader_reads_is_reachable_under_the_schema():
    """The seam that no fixture can test.

    Both sides pass their own suites while disagreeing, because each side's
    fixtures were written by that side. Only a comparison of the two artifacts
    catches it.

    This began as xfail(strict=True) describing seven unsatisfiable reads. The
    translation layer in the same PR closed them, the marker became an
    unexpected pass, and the suite failed until it was removed. That is the
    intended lifecycle: the marker cannot outlive the gap it documents.
    """
    unreachable = []
    for exercise_id, path in _loader_payload_reads():
        spec = PAYLOADS.get(exercise_id)
        if spec is None:
            continue  # open payload at this schema version, anything is allowed
        if not _reachable(spec, path):
            unreachable.append(exercise_id + "." + ".".join(path))
    assert not unreachable, (
        "the loader reads payload keys the schema forbids, so these can never be "
        f"populated no matter what an exercise writes: {unreachable}"
    )
