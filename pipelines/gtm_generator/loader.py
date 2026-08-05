# -----------------------------------------------------------------------------
# Strategy Sprint artifact loader.
#
# NOT vendored — this file is strategy-sprint's own binding between a sprint's
# on-disk output layout (manifest + sidecars per the JSON Schema envelope) and
# the vendored generator's StrategySprintInput dataclass.
#
# Owned locally; edit here directly. Not affected by scripts/sync-from-upstream.sh.
#
# Loader contract (four-way state matrix, per schema envelope design):
#   manifest says unrun    + no sidecar    -> ExerciseNotYetRun
#   manifest says complete + no sidecar    -> SidecarMissingUnexpected
#   manifest says complete + empty payload -> PayloadFailedToWrite
#   manifest says complete + sidecar has confirmedByClient=false + strict mode
#                                          -> UnconfirmedPayloadRejected
#
# STRICT MODE is the only mode in V1: acting on unratified content downstream
# (outreach automation, CRM config) risks firing on drafted-but-not-confirmed
# data. Draft-generate is a separate CLI flag if it ever ships, not a weakening
# of the strict path.
# -----------------------------------------------------------------------------

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

from pipelines.gtm_generator.input_models import (
    BrandVoice,
    Competitor,
    ICPDefinition,
    PricingContext,
    StrategySprintInput,
    TargetMarket,
    TechnologyFocus,
    ValueProposition,
)

# Schema file lives at repo root under schema/. Absolute-path-relative-to-this
# file so tests running from arbitrary cwd still resolve.
_SCHEMA_PATH = Path(__file__).resolve().parents[2] / "schema" / "strategy_sprint_input.schema.json"


# ============================================================================
# Contract errors — hierarchy caught by cli.py + mapped to structured envelopes.
# ============================================================================


class ContractError(RuntimeError):
    """Base for anything a well-formed sprint contract would rule out.

    cli.py catches this and returns exit code 2 with a structured error
    envelope on stderr. Distinct from generator-internal errors (bugs),
    which get exit 3.
    """


class ManifestMissing(ContractError):
    """No output/sprint-manifest.yaml at the artifact dir.

    Recover: run the sprint through completion; the orchestrator writes
    the manifest at the end of the last exercise.
    """


class ManifestInvalid(ContractError):
    """The manifest file exists but doesn't validate against the schema.

    Recover: the sprint tool wrote a manifest the schema rejects. File
    an issue against the sprint tool; do NOT hand-edit the manifest
    (that just hides the writer bug).
    """


class ExerciseNotYetRun(ContractError):
    """A required exercise has status=unrun in the manifest.

    Recover: complete the named exercise via its /slash command; re-invoke
    the generator when the sprint is complete.
    """


class RequiredExerciseFailed(ContractError):
    """A required exercise has status=failed in the manifest.

    Recover: read the failureReason field, address the cause, re-run that
    exercise, re-invoke the generator.
    """


class SidecarMissingUnexpected(ContractError):
    """Manifest says a step is complete but its sidecar file is absent.

    Recover: the exercise reported success but the sidecar didn't reach
    disk — check for a write error (permissions, disk full, wrong
    working directory). Re-run the exercise to regenerate the sidecar.
    """


class SidecarInvalid(ContractError):
    """A sidecar file exists but doesn't validate against the schema.

    Recover: the exercise wrote a sidecar the schema rejects. File an
    issue; do not hand-edit.
    """


class PayloadFailedToWrite(ContractError):
    """Sidecar exists but payload is empty (schema requires minProperties: 1).

    Recover: the exercise's write path partially succeeded — envelope
    fields landed but the payload was empty. Re-run the exercise.
    """


class UnconfirmedPayloadRejected(ContractError):
    """Strict mode: sidecar has confirmedByClient=false.

    Recover: complete client confirmation on the named exercise, then
    re-invoke the generator. Do NOT weaken the strict check; downstream
    automation acting on unratified content is exactly the failure this
    is here to prevent.
    """


# ============================================================================
# Loader
# ============================================================================


@dataclass
class LoadedManifest:
    """Parsed + validated manifest, retained for downstream inspection."""

    raw: dict[str, Any]
    steps_by_id: dict[str, dict[str, Any]]

    @property
    def sprint_complete(self) -> bool:
        return bool(self.raw.get("sprintComplete", False))

    @property
    def client_slug(self) -> str:
        return str(self.raw["clientSlug"])


def _load_schema() -> dict[str, Any]:
    """Load the JSON Schema once; cached at module level would be a nice
    optimisation but we're loader-invoked-once-per-process so trivial."""
    if not _SCHEMA_PATH.is_file():
        raise ManifestInvalid(
            f"JSON Schema not found at {_SCHEMA_PATH}. This is a repo-level "
            f"defect: the schema file must be present at that path for the "
            f"loader to run at all."
        )
    return json.loads(_SCHEMA_PATH.read_text())


def _validator(schema: dict[str, Any], subschema_ref: str) -> Draft202012Validator:
    """Return a validator over one branch of the top-level oneOf.

    The top-level schema is oneOf[manifest, sidecar]; using it directly would
    let a manifest pass by accidentally matching the sidecar shape. Validators
    scoped to the specific $defs branch prevent that class of false-pass.
    """
    sub = schema["$defs"][subschema_ref]
    scoped = {**schema, **sub}
    scoped.pop("oneOf", None)
    return Draft202012Validator(scoped)


def load_from_artifact_dir(
    artifact_dir: Path | str,
    client_slug: str,
    *,
    strict: bool = True,
) -> StrategySprintInput:
    """Load + validate a completed sprint from its artifact directory.

    Args:
      artifact_dir: root of a client's sprint output, e.g.
        artifacts/acme-corp/. Must contain output/sprint-manifest.yaml.
      client_slug: expected client slug; must match manifest.clientSlug.
        Passed explicitly rather than derived so the caller commits to
        which client they think they're loading — a mismatch is a defect
        surfaced here instead of downstream.
      strict: if True (default and only supported mode in V1), rejects
        any confirmedByClient=false sidecar for a required step.

    Returns:
      Populated StrategySprintInput ready for GTMPlanGenerator.

    Raises:
      One of the ContractError subclasses. See each class docstring for
      the specific failure mode + recovery.
    """
    artifact_path = Path(artifact_dir)
    schema = _load_schema()
    manifest_validator = _validator(schema, "manifest")
    sidecar_validator = _validator(schema, "sidecar")

    manifest = _load_manifest(artifact_path, manifest_validator)
    if manifest.client_slug != client_slug:
        raise ManifestInvalid(
            f"Client slug mismatch: caller passed {client_slug!r}, "
            f"manifest at {artifact_path} declares {manifest.client_slug!r}. "
            f"Recover: correct one of the two so they agree."
        )

    sidecars = _load_sidecars(artifact_path, manifest, sidecar_validator, strict=strict)
    return _payloads_to_input(manifest, sidecars)


def _load_manifest(artifact_dir: Path, validator: Draft202012Validator) -> LoadedManifest:
    manifest_path = artifact_dir / "output" / "sprint-manifest.yaml"
    if not manifest_path.is_file():
        raise ManifestMissing(
            f"No sprint manifest at {manifest_path}. Recover: run the "
            f"sprint through its final exercise, which writes the manifest."
        )
    try:
        raw = yaml.safe_load(manifest_path.read_text())
    except yaml.YAMLError as exc:
        raise ManifestInvalid(
            f"Manifest at {manifest_path} is not valid YAML: {exc}"
        ) from exc

    if not isinstance(raw, dict):
        raise ManifestInvalid(
            f"Manifest at {manifest_path} must be a mapping at the top level; "
            f"got {type(raw).__name__}."
        )

    errors = sorted(validator.iter_errors(raw), key=lambda e: list(e.absolute_path))
    if errors:
        first = errors[0]
        raise ManifestInvalid(
            f"Manifest at {manifest_path} fails schema validation: "
            f"{first.message} (path: {'/'.join(str(p) for p in first.absolute_path)})"
        )

    steps_by_id = {step["exerciseId"]: step for step in raw["steps"]}
    return LoadedManifest(raw=raw, steps_by_id=steps_by_id)


def _load_sidecars(
    artifact_dir: Path,
    manifest: LoadedManifest,
    validator: Draft202012Validator,
    *,
    strict: bool,
) -> dict[str, dict[str, Any]]:
    """Load + validate each sidecar the manifest points at.

    Applies the four-way state matrix per step. Returns a dict keyed by
    exerciseId mapping to the validated sidecar body (envelope + payload).
    """
    loaded: dict[str, dict[str, Any]] = {}

    for step in manifest.raw["steps"]:
        exercise_id = step["exerciseId"]
        status = step["status"]
        required = step.get("required", True)
        sidecar_rel = step["sidecarPath"]
        sidecar_path = artifact_dir / sidecar_rel

        if status == "unrun":
            if required:
                raise ExerciseNotYetRun(
                    f"Required exercise {exercise_id!r} is unrun. Recover: "
                    f"complete it via /{exercise_id}, then re-invoke the "
                    f"generator."
                )
            continue  # optional + unrun is fine

        if status == "failed":
            if required:
                reason = step.get("failureReason") or "(no reason recorded)"
                raise RequiredExerciseFailed(
                    f"Required exercise {exercise_id!r} failed: {reason}. "
                    f"Recover: address the cause, re-run the exercise, re-invoke."
                )
            continue  # optional + failed is fine (surface, don't block)

        # status == "complete"
        if not sidecar_path.is_file():
            raise SidecarMissingUnexpected(
                f"Manifest says {exercise_id!r} is complete but its sidecar "
                f"at {sidecar_path} does not exist. Recover: re-run the "
                f"exercise (write likely partially succeeded)."
            )

        try:
            body = yaml.safe_load(sidecar_path.read_text())
        except yaml.YAMLError as exc:
            raise SidecarInvalid(
                f"Sidecar at {sidecar_path} is not valid YAML: {exc}"
            ) from exc

        if not isinstance(body, dict):
            raise SidecarInvalid(
                f"Sidecar at {sidecar_path} must be a mapping at the top level; "
                f"got {type(body).__name__}."
            )

        errors = sorted(validator.iter_errors(body), key=lambda e: list(e.absolute_path))
        if errors:
            first = errors[0]
            # PayloadFailedToWrite is a specific-shape of SidecarInvalid worth
            # distinguishing: an empty payload signals write-path partial-success
            # not "the payload had wrong fields", and its recovery is different
            # (re-run the exercise vs file an issue).
            path_str = "/".join(str(p) for p in first.absolute_path)
            if (
                path_str == "payload"
                and "minProperties" in first.message
            ):
                raise PayloadFailedToWrite(
                    f"Sidecar at {sidecar_path} has an empty payload. Recover: "
                    f"re-run the exercise; the write path partially succeeded."
                )
            raise SidecarInvalid(
                f"Sidecar at {sidecar_path} fails schema validation: "
                f"{first.message} (path: {path_str})"
            )

        if strict and required and not body.get("confirmedByClient", False):
            raise UnconfirmedPayloadRejected(
                f"Sidecar at {sidecar_path} has confirmedByClient=false. "
                f"Recover: complete client confirmation on the {exercise_id!r} "
                f"exercise, then re-invoke. Do not weaken the strict check."
            )

        loaded[exercise_id] = body

    return loaded


def _payloads_to_input(
    manifest: LoadedManifest,
    sidecars: dict[str, dict[str, Any]],
) -> StrategySprintInput:
    """Convert validated sidecar payloads into a StrategySprintInput.

    Payload schemas are being filled in additively (only company-overview
    is defined at schema version 0.1.0), so this mapping is defensive:
    extract known fields when present, fall through to dataclass defaults
    when absent. Adding stricter mappings as payload schemas land is
    additive-not-breaking, matching the schema's own evolution shape.
    """
    def payload(exercise_id: str) -> dict[str, Any]:
        sidecar = sidecars.get(exercise_id)
        if sidecar is None:
            return {}
        return dict(sidecar.get("payload") or {})

    company = payload("company-overview").get("company") or {}
    company_name = str(company.get("name", "") or "")
    industry = str(company.get("industry", "") or "")
    website = str(company.get("url", "") or "")

    # TRANSLATION LAYER. The sprint speaks the exercises' vocabulary and the
    # generator speaks GTM vocabulary, and until 2026-08-05 this function read
    # GTM key names straight out of sprint payloads. Those keys are not merely
    # absent, they are forbidden: the payload schemas are additionalProperties
    # false, so no exercise could ever have supplied them. Seven of ten reads
    # were unsatisfiable and the pipeline had never produced a plan from any
    # input, including this repo's own fixture. Both halves passed their own
    # suites throughout, because each side's fixtures were written by that side.
    #
    # Everything below maps from a field an exercise actually produces. Where
    # no such field existed, the fix was to add one to the payload schema so a
    # human states it, NOT to derive it here. A value inferred from free text
    # arrives wearing the same type as a stated one and nothing downstream can
    # tell them apart.
    icp_payload = payload("icp-prioritization")
    tiers = icp_payload.get("tiers") or []
    deep_dives = icp_payload.get("segmentDeepDives") or []

    target_market = TargetMarket(
        industries=[str(i) for i in (icp_payload.get("industries") or []) if i],
    )
    icp = ICPDefinition(
        # tiers[].role is the exercise's word for the buyer. Empty roles are
        # dropped rather than carried as "": a tier that named no role did not
        # name one, and a blank string would satisfy the generator's non-empty
        # check while telling a reader nothing.
        titles=[str(t.get("role")) for t in tiers if t.get("role")],
        criteria=[str(c) for d in deep_dives for c in (d.get("decisionCriteria") or []) if c],
    )

    # positioning.statement is described by the schema as the one sentence the
    # exercise exists to produce, which is exactly what a headline is.
    positioning_payload = payload("positioning")
    value_proposition = ValueProposition(
        headline=str(positioning_payload.get("statement", "") or ""),
    )

    # Competitors are named in two exercises and neither is authoritative alone:
    # company-overview lists who they are, positioning places them on spectrums.
    # Merged by name, first mention wins, so a competitor named in only one
    # place still arrives.
    seen: dict[str, Competitor] = {}
    for c in payload("company-overview").get("competitors") or []:
        name = str(c.get("name", "") or "").strip()
        if name and name not in seen:
            seen[name] = Competitor(name=name, weakness=str(c.get("howTheyDiffer", "") or ""))
    for row in positioning_payload.get("competitiveMap") or []:
        for c in row.get("competitors") or []:
            name = str(c.get("name", "") or "").strip()
            if name and name not in seen:
                seen[name] = Competitor(name=name)
    competitive_landscape = list(seen.values())

    pain_points = [
        str(p) for d in deep_dives for p in (d.get("painPoints") or []) if p
    ]

    # pricing_context has NO sprint source. revenue-levers defines rankedLevers
    # and leverByIcp; nothing anywhere states a pricing model, range or posture
    # in the shape PricingContext wants. The dead read that used to live here
    # (revenue_payload.get("pricing_context")) could never return anything, and
    # a read that cannot be satisfied is worse than an absent one: it reads as
    # wired.
    #
    # Deliberately NOT sourced from company-overview.company.pricing, which is
    # free text and explicitly documented as not reducing to structure.
    # Splitting a sentence into model/range/positioning is inference, and the
    # generator treats pricing_context as optional, so nothing is lost by
    # leaving it at defaults. If a plan ever needs it, the fix is a stated field
    # on revenue-levers, not a parser here.
    pricing_context = PricingContext()

    brand_voice_payload = payload("brand-voice")
    brand_voice = BrandVoice.from_dict(brand_voice_payload)

    tools_payload = payload("tool-inventory")
    technology_focus = TechnologyFocus.from_dict(tools_payload.get("technology_focus", {}))

    return StrategySprintInput(
        company_name=company_name,
        industry=industry,
        website=website,
        target_market=target_market,
        icp=icp,
        value_proposition=value_proposition,
        competitive_landscape=competitive_landscape,
        pain_points=pain_points,
        pricing_context=pricing_context,
        brand_voice=brand_voice,
        technology_focus=technology_focus,
    )
