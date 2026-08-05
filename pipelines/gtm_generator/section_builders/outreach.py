# -----------------------------------------------------------------------------
# VENDORED code. Do NOT edit here; edit upstream and re-sync.
#
# Upstream: GTM plan generator (private repo, path-parameterised via
# UPSTREAM_GTM_GENERATOR_PATH env var; see VENDOR.md).
# Source SHA: ce73ca84f7462b2ca2d701e0c413dec62e94445f
# Sync procedure: scripts/sync-from-upstream.sh
#
# Any change made directly to this file will be overwritten on the next
# sync. If you need to change behavior, change the upstream file first,
# then re-run the sync script.
# -----------------------------------------------------------------------------

"""Section builders for Outreach Sequence and Phone Script configuration.

Maps Strategy Sprint input to F6 (Platform-Specific Email Templates)
and F15 (Phone Script Generator).
"""

from pipelines.gtm_generator.input_models import StrategySprintInput
from pipelines.gtm_generator.output_models import OutreachSequenceConfig


# Day offsets for the 4-email + 1-phone cadence
_DEFAULT_CADENCE_OFFSETS = {
    "email_1": 0,
    "email_2": 3,
    "phone_call_1": 9,
    "email_3": 13,
    "email_4": 20,
}


def build_outreach_config(input_data: StrategySprintInput) -> OutreachSequenceConfig:
    """Build outreach sequence configuration from Strategy Sprint input.

    Generates 4 email templates and a phone script template with
    client-specific context pre-filled in bracket fields.

    Args:
        input_data: Validated Strategy Sprint input.

    Returns:
        Configured OutreachSequenceConfig instance.
    """
    # Build default field values from input
    default_fields = _build_default_fields(input_data)

    # Generate email templates
    email_templates = [
        _build_email_1(input_data, default_fields),
        _build_email_2(input_data, default_fields),
        _build_email_3(input_data, default_fields),
        _build_email_4(input_data, default_fields),
    ]

    # Generate phone script template
    phone_script = _build_phone_script(input_data, default_fields)

    return OutreachSequenceConfig(
        email_templates=email_templates,
        phone_script_template=phone_script,
        cadence_day_offsets=dict(_DEFAULT_CADENCE_OFFSETS),
        send_days=["tuesday", "wednesday", "thursday"],
        send_window_start=9,
        send_window_end=11,
        default_field_values=default_fields,
    )


# ============================================================================
# Email template builders
# ============================================================================


def _build_email_1(
    input_data: StrategySprintInput, defaults: dict
) -> dict:
    """Build Email 1 — Introduction / Pain Point Hook."""
    primary_pain = input_data.pain_points[0] if input_data.pain_points else "[Pain Point]"
    value_prop = input_data.value_proposition.headline

    return {
        "position": "email_1",
        "day_offset": 0,
        "subject": f"[First Name], quick question about [Company Name]",
        "body": (
            f"Hi [First Name],\n\n"
            f"I noticed [Company Name] is in the {input_data.industry.lower()} space "
            f"and wanted to reach out about something specific.\n\n"
            f"Many {_pluralize_title(input_data.icp.titles[0])} I talk to mention "
            f"that {primary_pain.lower()}\n\n"
            f"We help companies like [Company Name] {value_prop.lower()}\n\n"
            f"Worth a 15-minute call [Proposed Day] to see if this applies to your situation?\n\n"
            f"[Sender Name]"
        ),
        "purpose": "introduction_pain_hook",
    }


def _build_email_2(
    input_data: StrategySprintInput, defaults: dict
) -> dict:
    """Build Email 2 — Social Proof / Case Study."""
    proof = input_data.value_proposition.proof_points[0] if input_data.value_proposition.proof_points else "[Result]"

    return {
        "position": "email_2",
        "day_offset": 3,
        "subject": f"how similar companies tackled this",
        "body": (
            f"Hi [First Name],\n\n"
            f"Following up — wanted to share a quick result.\n\n"
            f"{proof}\n\n"
            f"The parallels to [Company Name] are clear: "
            f"[Research Brief Insight]\n\n"
            f"Happy to walk you through how they did it. "
            f"Free [Proposed Day]?\n\n"
            f"[Sender Name]"
        ),
        "purpose": "social_proof",
    }


def _build_email_3(
    input_data: StrategySprintInput, defaults: dict
) -> dict:
    """Build Email 3 — Value Add / Different Angle."""
    differentiator = (
        input_data.value_proposition.differentiators[0]
        if input_data.value_proposition.differentiators
        else "[Key Differentiator]"
    )

    return {
        "position": "email_3",
        "day_offset": 13,
        "subject": f"different angle on [Company Name]'s [Pain Area]",
        "body": (
            f"Hi [First Name],\n\n"
            f"One more thing I wanted to mention — "
            f"{differentiator.lower()}\n\n"
            f"This matters because [Industry Specific Reason].\n\n"
            f"If you're exploring options for [Pain Area], "
            f"I'd love to show you what we've built. "
            f"No pressure — just 15 minutes.\n\n"
            f"[Sender Name]"
        ),
        "purpose": "value_add_differentiator",
    }


def _build_email_4(
    input_data: StrategySprintInput, defaults: dict
) -> dict:
    """Build Email 4 — Breakup / Last Touch."""
    return {
        "position": "email_4",
        "day_offset": 20,
        "subject": f"closing the loop",
        "body": (
            f"Hi [First Name],\n\n"
            f"I've reached out a few times and haven't heard back — "
            f"totally understand if the timing isn't right.\n\n"
            f"If {input_data.pain_points[0].lower() if input_data.pain_points else '[pain point]'} "
            f"becomes a priority, I'm here.\n\n"
            f"Either way, no hard feelings. Would you like me to check back "
            f"in a few months?\n\n"
            f"[Sender Name]"
        ),
        "purpose": "breakup",
    }


# ============================================================================
# Phone script builder
# ============================================================================


def _build_phone_script(
    input_data: StrategySprintInput, defaults: dict
) -> dict:
    """Build phone script template from Strategy Sprint input."""
    primary_pain = input_data.pain_points[0] if input_data.pain_points else "[Pain Point]"
    proof = (
        input_data.value_proposition.proof_points[0]
        if input_data.value_proposition.proof_points
        else "[Result]"
    )

    return {
        "opening": (
            f"Hi [First Name], this is [Sender Name]. "
            f"I sent you an email recently about how we help "
            f"{_pluralize_title(input_data.icp.titles[0])} "
            f"with {_extract_pain_keyword(primary_pain)}."
        ),
        "hook": (
            f"The reason I'm calling — {primary_pain.lower()} "
            f"We've seen companies like [Company Name] "
            f"solve this and see results like {proof.lower()}"
        ),
        "bridge": (
            f"We work with {input_data.target_market.industries[0].lower()} companies "
            f"and what makes us different is "
            f"{input_data.value_proposition.differentiators[0].lower() if input_data.value_proposition.differentiators else '[differentiator]'}."
        ),
        "ask": (
            f"Would you be open to a 15-minute call this week "
            f"to see if this applies to [Company Name]?"
        ),
        "voicemail": (
            f"Hi [First Name], [Sender Name] here. "
            f"Quick message about {_extract_pain_keyword(primary_pain)} "
            f"for {input_data.industry.lower()} companies. "
            f"I'll send a quick email with details."
        ),
        "objections": _build_objection_responses(input_data),
    }


# ============================================================================
# Helper functions
# ============================================================================


def _build_default_fields(input_data: StrategySprintInput) -> dict:
    """Build default bracket field values from Strategy Sprint input."""
    fields = {
        "Industry": input_data.industry,
        "Value Proposition": input_data.value_proposition.headline,
        "Primary Pain Point": (
            input_data.pain_points[0] if input_data.pain_points else ""
        ),
    }

    # Add competitor-based fields
    if input_data.competitive_landscape:
        fields["Top Competitor"] = input_data.competitive_landscape[0].name
        fields["Competitor Weakness"] = input_data.competitive_landscape[0].weakness

    # Add proof points
    for i, proof in enumerate(input_data.value_proposition.proof_points[:3]):
        fields[f"Proof Point {i + 1}"] = proof

    return fields


def _build_objection_responses(input_data: StrategySprintInput) -> dict:
    """Build objection handling responses from competitive landscape."""
    objections = {
        "not_interested": (
            "I understand. Just curious — what's your current approach to "
            f"{_extract_pain_keyword(input_data.pain_points[0]) if input_data.pain_points else 'this'}? "
            "Even if we're not a fit, I might be able to share something useful."
        ),
        "already_have_solution": (
            f"Great to hear you have something in place. Many of our clients "
            f"were using {input_data.competitive_landscape[0].name if input_data.competitive_landscape else 'another solution'} "
            f"before switching. The main difference they found was "
            f"{input_data.value_proposition.differentiators[0].lower() if input_data.value_proposition.differentiators else 'our approach'}."
        ),
        "no_budget": (
            f"Totally understand budget constraints. Worth noting that "
            f"{input_data.value_proposition.proof_points[0] if input_data.value_proposition.proof_points else 'our clients typically see positive ROI within 60 days'}. "
            f"Would it help to see the numbers?"
        ),
        "send_info": (
            "Absolutely, I'll send that over right after this call. "
            "Quick question so I can tailor what I send — "
            f"what's your biggest challenge with "
            f"{_extract_pain_keyword(input_data.pain_points[0]) if input_data.pain_points else 'this area'} right now?"
        ),
    }
    return objections


def _pluralize_title(title: str) -> str:
    """Simple pluralization for job titles.

    Args:
        title: A job title like "Property Manager".

    Returns:
        Pluralized form like "property managers".
    """
    title_lower = title.lower()
    if title_lower.endswith("s"):
        return title_lower
    if title_lower.endswith("or"):
        return title_lower + "s"
    if title_lower.endswith("er"):
        return title_lower + "s"
    return title_lower + "s"


def _extract_pain_keyword(pain_point: str) -> str:
    """Extract a short keyword phrase from a pain point.

    Args:
        pain_point: Full pain point description.

    Returns:
        A 2-4 word keyword phrase.
    """
    # Remove common leading words
    pain = pain_point.lower().strip()
    for prefix in ["no ", "lack of ", "poor ", "slow ", "high ", "manual "]:
        if pain.startswith(prefix):
            return pain[:40].rstrip(".,;:")
    words = pain.split()[:4]
    return " ".join(words).rstrip(".,;:")