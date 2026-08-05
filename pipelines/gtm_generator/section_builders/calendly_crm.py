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

"""Section builders for Calendly and CRM configuration.

Maps Strategy Sprint input to F8 (Calendly Integration)
and F10 (CRM Activity Logger).
"""

from pipelines.gtm_generator.input_models import StrategySprintInput
from pipelines.gtm_generator.output_models import CalendlyConfig, CRMConfig


def build_calendly_config(input_data: StrategySprintInput) -> CalendlyConfig:
    """Build Calendly scheduling configuration from Strategy Sprint input.

    Generates event type, branding messages, and UTM tracking setup
    customized for the client.

    Args:
        input_data: Validated Strategy Sprint input.

    Returns:
        Configured CalendlyConfig instance.
    """
    company = input_data.company_name
    industry = input_data.industry

    # Event type name based on pricing positioning
    if input_data.pricing_context.positioning == "premium":
        event_name = f"Strategy Session with {company}"
        duration = 30
    else:
        event_name = f"15-Minute {industry} Demo"
        duration = 15

    # Confirmation message
    confirmation = (
        f"Thanks for booking! Looking forward to showing you how "
        f"{company} can help with "
        f"{input_data.pain_points[0].lower() if input_data.pain_points else 'your challenges'}. "
        f"You'll receive a calendar invite shortly."
    )

    # Reminder message
    reminder = (
        f"Quick reminder about your upcoming call with {company}. "
        f"We'll be covering how to "
        f"{input_data.value_proposition.headline.lower()} "
        f"for companies like yours."
    )

    # UTM campaign based on company name
    utm_campaign = (
        input_data.company_name.lower()
        .replace(" ", "_")
        .replace(".", "")
        .replace(",", "")
    )

    return CalendlyConfig(
        event_type_name=event_name,
        event_duration_minutes=duration,
        booking_url_template=f"https://calendly.com/{utm_campaign}",
        confirmation_message=confirmation,
        reminder_message=reminder,
        utm_source="cold_outreach",
        utm_medium="email",
        utm_campaign=utm_campaign,
        webhook_events=["invitee.created", "invitee.canceled"],
    )


def build_crm_config(input_data: StrategySprintInput) -> CRMConfig:
    """Build CRM and activity tracking configuration from Strategy Sprint input.

    Generates Notion database schema, activity types, status transitions,
    and pipeline stages customized for the client's sales process.

    Args:
        input_data: Validated Strategy Sprint input.

    Returns:
        Configured CRMConfig instance.
    """
    # Database schema properties
    database_schema = _build_database_schema(input_data)

    # Activity types (standard + client-specific)
    activity_types = _build_activity_types(input_data)

    # Status flow
    status_flow = _build_status_flow(input_data)

    # Pipeline stages based on sales cycle
    pipeline_stages = _build_pipeline_stages(input_data)

    # Custom properties
    custom_properties = _build_custom_properties(input_data)

    return CRMConfig(
        database_schema=database_schema,
        activity_types=activity_types,
        status_flow=status_flow,
        pipeline_stages=pipeline_stages,
        custom_properties=custom_properties,
    )


# ============================================================================
# CRM helper builders
# ============================================================================


def _build_database_schema(input_data: StrategySprintInput) -> dict:
    """Build Notion database property schema."""
    schema = {
        "Name": {"type": "title"},
        "Company": {"type": "rich_text"},
        "Email": {"type": "email"},
        "Phone": {"type": "phone_number"},
        "Title": {"type": "rich_text"},
        "Status": {
            "type": "select",
            "options": [
                {"name": "Prospect", "color": "gray"},
                {"name": "Contacted", "color": "blue"},
                {"name": "Engaged", "color": "yellow"},
                {"name": "Demo Scheduled", "color": "orange"},
                {"name": "Demo Completed", "color": "purple"},
                {"name": "Proposal Sent", "color": "pink"},
                {"name": "Closed Won", "color": "green"},
                {"name": "Closed Lost", "color": "red"},
                {"name": "Nurture", "color": "default"},
            ],
        },
        "Source": {
            "type": "select",
            "options": [
                {"name": "Cold Outreach", "color": "blue"},
                {"name": "Inbound", "color": "green"},
                {"name": "Referral", "color": "purple"},
                {"name": "Event", "color": "orange"},
            ],
        },
        "Industry": {
            "type": "select",
            "options": [
                {"name": ind, "color": "default"}
                for ind in input_data.target_market.industries
            ],
        },
        "Qualification Score": {"type": "number"},
        "Last Activity": {"type": "date"},
        "Next Follow Up": {"type": "date"},
        "Notes": {"type": "rich_text"},
    }

    # Add technology property if platforms are tracked
    if input_data.technology_focus.platforms:
        schema["Technology"] = {
            "type": "multi_select",
            "options": [
                {"name": platform, "color": "default"}
                for platform in input_data.technology_focus.platforms
            ],
        }

    return schema


def _build_activity_types(input_data: StrategySprintInput) -> list[str]:
    """Build the list of CRM activity types to track."""
    # Standard activity types from the existing system
    activity_types = [
        "email_sent",
        "email_opened",
        "email_clicked",
        "email_replied",
        "email_bounced",
        "phone_call_attempted",
        "phone_call_connected",
        "phone_call_voicemail",
        "demo_scheduled",
        "demo_completed",
        "demo_no_show",
        "demo_canceled",
        "follow_up_sent",
        "proposal_sent",
        "deal_closed_won",
        "deal_closed_lost",
        "reengagement_30_sent",
        "reengagement_60_sent",
        "reengagement_90_sent",
        "linkedin_post_published",
    ]

    return activity_types


def _build_status_flow(input_data: StrategySprintInput) -> list[dict]:
    """Build status transition rules."""
    return [
        {"from": "prospect", "to": "contacted", "trigger": "first_email_sent"},
        {"from": "contacted", "to": "engaged", "trigger": "email_opened_or_clicked"},
        {"from": "engaged", "to": "demo_scheduled", "trigger": "calendly_booking"},
        {"from": "demo_scheduled", "to": "demo_completed", "trigger": "demo_occurred"},
        {"from": "demo_completed", "to": "proposal_sent", "trigger": "proposal_sent"},
        {"from": "proposal_sent", "to": "closed_won", "trigger": "deal_signed"},
        {"from": "proposal_sent", "to": "closed_lost", "trigger": "deal_lost"},
        {"from": "contacted", "to": "nurture", "trigger": "no_response_after_sequence"},
        {"from": "demo_scheduled", "to": "nurture", "trigger": "demo_no_show_twice"},
        {"from": "nurture", "to": "contacted", "trigger": "reengagement_reply"},
    ]


def _build_pipeline_stages(input_data: StrategySprintInput) -> list[str]:
    """Build pipeline stages based on sales process."""
    stages = [
        "prospect",
        "contacted",
        "engaged",
        "demo_scheduled",
        "demo_completed",
    ]

    # Add proposal stage if sales cycle warrants it
    if input_data.sales_cycle_days > 14:
        stages.append("proposal_sent")

    stages.extend(["closed_won", "closed_lost", "nurture"])
    return stages


def _build_custom_properties(input_data: StrategySprintInput) -> dict:
    """Build client-specific custom CRM properties."""
    custom = {}

    # Add company size property if relevant
    if input_data.target_market.company_sizes:
        custom["Company Size"] = {
            "type": "select",
            "options": [
                {"name": size, "color": "default"}
                for size in input_data.target_market.company_sizes
            ],
        }

    # Add geography property
    if input_data.target_market.geographies:
        custom["Region"] = {
            "type": "select",
            "options": [
                {"name": geo, "color": "default"}
                for geo in input_data.target_market.geographies
            ],
        }

    # Add pain point tracking
    custom["Primary Pain Point"] = {
        "type": "select",
        "options": [
            {"name": pain[:50], "color": "default"}  # Truncate long pain points
            for pain in input_data.pain_points
        ],
    }

    return custom