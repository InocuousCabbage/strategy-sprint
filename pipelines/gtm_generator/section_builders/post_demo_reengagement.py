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

"""Section builders for Post-Demo and Re-engagement configuration.

Maps Strategy Sprint input to F11 (Post-Demo Sequence Generator)
and F12 (Re-engagement Triggers).
"""

from pipelines.gtm_generator.input_models import StrategySprintInput
from pipelines.gtm_generator.output_models import PostDemoConfig, ReengagementConfig


# Default post-demo day offsets (matching Sprint 4 constants)
_POST_DEMO_DAY_OFFSETS = {
    "interested": [1, 3, 7],
    "not_interested": [3, 14, 30],
    "no_show": [0, 3],
    "canceled": [1, 7],
}


def build_post_demo_config(input_data: StrategySprintInput) -> PostDemoConfig:
    """Build post-demo follow-up configuration from Strategy Sprint input.

    Generates 4 outcome-based follow-up sequences with client-specific
    context pre-filled.

    Args:
        input_data: Validated Strategy Sprint input.

    Returns:
        Configured PostDemoConfig instance.
    """
    sequences = {
        "interested": _build_interested_sequence(input_data),
        "not_interested": _build_not_interested_sequence(input_data),
        "no_show": _build_no_show_sequence(input_data),
        "canceled": _build_canceled_sequence(input_data),
    }

    # Demo talking points from value prop and differentiators
    talking_points = []
    talking_points.append(input_data.value_proposition.headline)
    talking_points.extend(input_data.value_proposition.sub_points[:3])
    talking_points.extend(input_data.value_proposition.differentiators[:2])

    # Case study references
    case_study_refs = [
        {"company": cs.get("company", ""), "result": cs.get("result", "")}
        for cs in input_data.case_studies[:3]
    ]

    # Proposal template notes
    proposal_notes = (
        f"Pricing: {input_data.pricing_context.range} "
        f"({input_data.pricing_context.model}). "
        f"Positioning: {input_data.pricing_context.positioning}."
    )
    if input_data.pricing_context.free_trial:
        proposal_notes += " Free trial available."

    return PostDemoConfig(
        sequences=sequences,
        day_offsets=dict(_POST_DEMO_DAY_OFFSETS),
        demo_talking_points=talking_points,
        case_study_references=case_study_refs,
        proposal_template_notes=proposal_notes,
    )


def build_reengagement_config(input_data: StrategySprintInput) -> ReengagementConfig:
    """Build re-engagement configuration from Strategy Sprint input.

    Adjusts trigger intervals based on the client's sales cycle length
    and generates template customizations with client context.

    Args:
        input_data: Validated Strategy Sprint input.

    Returns:
        Configured ReengagementConfig instance.
    """
    sales_cycle = input_data.sales_cycle_days

    # Adjust intervals based on sales cycle
    # Shorter sales cycles get tighter intervals
    intervals, adjusted = _adjust_intervals_for_sales_cycle(sales_cycle)

    # Build template customizations per interval
    templates = {
        "day_30": _build_reengagement_template(
            input_data, "value_add", intervals["day_30"]
        ),
        "day_60": _build_reengagement_template(
            input_data, "re_introduction", intervals["day_60"]
        ),
        "day_90": _build_reengagement_template(
            input_data, "breakup", intervals["day_90"]
        ),
    }

    return ReengagementConfig(
        intervals=intervals,
        templates=templates,
        sales_cycle_days=sales_cycle,
        adjusted_intervals=adjusted,
        eligible_statuses=["sent", "no_response", "engaged"],
    )


# ============================================================================
# Post-demo sequence builders
# ============================================================================


def _build_interested_sequence(input_data: StrategySprintInput) -> list[dict]:
    """Build the interested-outcome follow-up sequence."""
    proof = (
        input_data.value_proposition.proof_points[0]
        if input_data.value_proposition.proof_points
        else "[Proof Point]"
    )
    return [
        {
            "position": 1,
            "subject": "[Company Name] next steps",
            "body": (
                f"Hi [First Name],\n\n"
                f"Thanks for the conversation [demo_day_reference]. "
                f"As discussed, here's what we covered:\n\n"
                f"- {input_data.value_proposition.headline}\n"
                f"- [Key takeaway from demo]\n\n"
                f"For next steps, [specific action]. "
                f"Worth a quick call [Proposed Day] to walk through the details?\n\n"
                f"[Sender Name]"
            ),
            "purpose": "next_steps",
        },
        {
            "position": 2,
            "subject": f"how similar companies tackled this",
            "body": (
                f"Hi [First Name],\n\n"
                f"Following up on our conversation — wanted to share: "
                f"{proof}\n\n"
                f"The parallels to [Company Name] are clear. "
                f"Happy to walk through the specifics.\n\n"
                f"[Sender Name]"
            ),
            "purpose": "case_study",
        },
        {
            "position": 3,
            "subject": "moving forward?",
            "body": (
                f"Hi [First Name],\n\n"
                f"Checking in on next steps. "
                f"Based on our conversation, {input_data.value_proposition.sub_points[0].lower() if input_data.value_proposition.sub_points else '[key benefit]'}.\n\n"
                f"Would it help to set up a follow-up with your team?\n\n"
                f"[Sender Name]"
            ),
            "purpose": "proposal_follow_up",
        },
    ]


def _build_not_interested_sequence(input_data: StrategySprintInput) -> list[dict]:
    """Build the not-interested-outcome follow-up sequence."""
    return [
        {
            "position": 1,
            "subject": "thought you might find this useful",
            "body": (
                f"Hi [First Name],\n\n"
                f"Thanks for your time on the demo. Even though the timing "
                f"may not be right, I wanted to share something relevant:\n\n"
                f"[Industry insight or resource related to "
                f"{input_data.pain_points[0].lower() if input_data.pain_points else 'their challenge'}]\n\n"
                f"No agenda — just thought it might be useful.\n\n"
                f"[Sender Name]"
            ),
            "purpose": "value_add_nurture",
        },
        {
            "position": 2,
            "subject": f"update on {input_data.industry.lower()}",
            "body": (
                f"Hi [First Name],\n\n"
                f"Quick update — [industry trend or new capability "
                f"relevant to {input_data.industry.lower()}].\n\n"
                f"Worth revisiting if circumstances have changed?\n\n"
                f"[Sender Name]"
            ),
            "purpose": "check_back",
        },
        {
            "position": 3,
            "subject": "one last thought",
            "body": (
                f"Hi [First Name],\n\n"
                f"Last reach-out from me. "
                f"If {input_data.pain_points[0].lower() if input_data.pain_points else '[their challenge]'} "
                f"becomes a priority, I'm here.\n\n"
                f"All the best,\n[Sender Name]"
            ),
            "purpose": "soft_close",
        },
    ]


def _build_no_show_sequence(input_data: StrategySprintInput) -> list[dict]:
    """Build the no-show follow-up sequence."""
    return [
        {
            "position": 1,
            "subject": "missed you today — easy reschedule",
            "body": (
                f"Hi [First Name],\n\n"
                f"Looks like we missed each other. No worries — "
                f"things come up.\n\n"
                f"Here's a quick link to grab another time: [Booking URL]\n\n"
                f"[Sender Name]"
            ),
            "purpose": "reschedule",
        },
        {
            "position": 2,
            "subject": "still open if you are",
            "body": (
                f"Hi [First Name],\n\n"
                f"Just circling back on the call we had scheduled. "
                f"If you're still interested in exploring how to "
                f"{input_data.value_proposition.headline.lower()}, "
                f"happy to find a time that works better.\n\n"
                f"[Sender Name]"
            ),
            "purpose": "second_attempt",
        },
    ]


def _build_canceled_sequence(input_data: StrategySprintInput) -> list[dict]:
    """Build the canceled follow-up sequence."""
    return [
        {
            "position": 1,
            "subject": "no worries — rain check?",
            "body": (
                f"Hi [First Name],\n\n"
                f"Saw the demo got canceled — totally understand. "
                f"Happy to reschedule whenever works: [Booking URL]\n\n"
                f"[Sender Name]"
            ),
            "purpose": "acknowledge_reschedule",
        },
        {
            "position": 2,
            "subject": "quick resource instead",
            "body": (
                f"Hi [First Name],\n\n"
                f"Since we haven't connected yet, I put together a quick "
                f"overview of how we help {input_data.industry.lower()} companies "
                f"with {input_data.pain_points[0].lower() if input_data.pain_points else '[their challenge]'}.\n\n"
                f"Worth a look when you have 2 minutes.\n\n"
                f"[Sender Name]"
            ),
            "purpose": "alternative_offer",
        },
    ]


# ============================================================================
# Re-engagement helpers
# ============================================================================


def _adjust_intervals_for_sales_cycle(sales_cycle_days: int) -> tuple[dict, bool]:
    """Adjust re-engagement intervals based on sales cycle length.

    Shorter sales cycles (< 30 days) use tighter intervals.
    Longer sales cycles (> 60 days) use wider intervals.
    Standard (30-60 days) uses defaults.

    Args:
        sales_cycle_days: Average sales cycle length in days.

    Returns:
        Tuple of (intervals_dict, whether_adjusted).
    """
    if sales_cycle_days < 30:
        # Short sales cycle — tighter touchpoints
        return {
            "day_30": 21,
            "day_60": 42,
            "day_90": 63,
        }, True
    elif sales_cycle_days > 60:
        # Long sales cycle — wider touchpoints
        return {
            "day_30": 45,
            "day_60": 90,
            "day_90": 120,
        }, True
    else:
        # Standard intervals
        return {
            "day_30": 30,
            "day_60": 60,
            "day_90": 90,
        }, False


def _build_reengagement_template(
    input_data: StrategySprintInput,
    approach: str,
    days: int,
) -> dict:
    """Build a re-engagement template for a specific interval.

    Args:
        input_data: Strategy Sprint input.
        approach: Template approach (value_add, re_introduction, breakup).
        days: Days of inactivity for this trigger.

    Returns:
        Template configuration dict.
    """
    templates = {
        "value_add": {
            "subject": f"thought of [Company Name]",
            "approach": "value_add",
            "tone": "helpful",
            "body_hint": (
                f"Share an industry insight about "
                f"{input_data.industry.lower()} or a relevant resource. "
                f"No hard sell."
            ),
            "days": days,
        },
        "re_introduction": {
            "subject": f"update since we last connected",
            "approach": "re_introduction",
            "tone": "warm",
            "body_hint": (
                f"Re-introduce with new value: "
                f"{input_data.value_proposition.differentiators[0] if input_data.value_proposition.differentiators else 'new capability'}. "
                f"Soft CTA to reconnect."
            ),
            "days": days,
        },
        "breakup": {
            "subject": f"closing the loop on [Company Name]",
            "approach": "breakup",
            "tone": "respectful",
            "body_hint": (
                f"Final outreach. Acknowledge silence. "
                f"Offer to reconnect if "
                f"{input_data.pain_points[0].lower() if input_data.pain_points else 'their challenge'} "
                f"becomes a priority. No pressure."
            ),
            "days": days,
        },
    }
    return templates.get(approach, templates["value_add"])