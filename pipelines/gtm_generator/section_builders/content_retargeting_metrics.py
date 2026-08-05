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

"""Section builders for Content Calendar, Retargeting, and Metrics configuration.

Maps Strategy Sprint input to F13 (LinkedIn Content Generator),
F16 (Retargeting Campaign Setup), F9/F14 (Metrics/Dashboard).
"""

from pipelines.gtm_generator.input_models import StrategySprintInput
from pipelines.gtm_generator.output_models import (
    ContentCalendarConfig,
    RetargetingConfig,
    MetricsConfig,
)


def build_content_calendar_config(
    input_data: StrategySprintInput,
) -> ContentCalendarConfig:
    """Build LinkedIn content calendar configuration from Strategy Sprint input.

    Generates posting schedule, content type rotation, topic themes,
    and hashtag strategy.

    Args:
        input_data: Validated Strategy Sprint input.

    Returns:
        Configured ContentCalendarConfig instance.
    """
    # Content type rotation (matches LinkedIn module ContentType enum)
    content_types = [
        "insight_post",
        "case_study_summary",
        "industry_commentary",
        "behind_the_scenes",
    ]

    # Topic themes from pain points and value prop
    topic_themes = []
    for pain in input_data.pain_points[:3]:
        topic_themes.append(f"How to solve: {pain.lower().rstrip('.,;:')}")
    for sub in input_data.value_proposition.sub_points[:2]:
        topic_themes.append(f"Insight: {sub}")
    for diff in input_data.value_proposition.differentiators[:2]:
        topic_themes.append(f"Why it matters: {diff}")

    # Hashtag strategy
    industry_lower = input_data.industry.lower().replace(" ", "")
    default_hashtags = [
        industry_lower,
        f"{industry_lower}tips",
        "businessgrowth",
    ]
    industry_hashtags = [
        ind.lower().replace(" ", "") for ind in input_data.target_market.industries[:3]
    ]

    # Content templates with client context
    content_templates = _build_content_templates(input_data)

    return ContentCalendarConfig(
        post_days=["monday", "wednesday", "friday"],
        posts_per_week=3,
        content_type_rotation=content_types,
        topic_themes=topic_themes,
        default_hashtags=default_hashtags,
        industry_hashtags=industry_hashtags,
        content_templates=content_templates,
    )


def build_retargeting_config(
    input_data: StrategySprintInput,
) -> RetargetingConfig:
    """Build retargeting campaign configuration from Strategy Sprint input.

    Generates pixel setup, audience definitions, campaign templates,
    and budget recommendations.

    Args:
        input_data: Validated Strategy Sprint input.

    Returns:
        Configured RetargetingConfig instance.
    """
    # Pixel domain from website
    domain = input_data.website.replace("https://", "").replace("http://", "").rstrip("/")

    # Audience definitions (3 standard segments)
    audiences = [
        {
            "name": f"{input_data.company_name} Website Visitors",
            "type": "website_visitors",
            "retention_days": 180,
            "rules": {"url_contains": domain},
            "description": f"All visitors to {domain} in the last 180 days",
        },
        {
            "name": f"{input_data.company_name} Email Engagers",
            "type": "email_engagers",
            "retention_days": 90,
            "rules": {"engagement_type": ["opened", "clicked"]},
            "description": "Contacts who opened or clicked outreach emails",
        },
        {
            "name": f"{input_data.company_name} Demo Bookers",
            "type": "demo_bookers",
            "retention_days": 30,
            "rules": {"event": "Schedule"},
            "description": "Contacts who booked a demo via Calendly",
        },
    ]

    # Campaign templates
    campaign_templates = _build_campaign_templates(input_data)

    # Budget recommendations (standard defaults)
    daily_budget_cents = {
        "website_visitors": 1000,   # $10/day
        "email_engagers": 1500,     # $15/day
        "demo_bookers": 2000,       # $20/day
    }

    # Setup instructions
    setup_instructions = (
        f"## Meta Retargeting Setup for {input_data.company_name}\n\n"
        f"### Step 1: Install Meta Pixel\n"
        f"Add the pixel code to all pages on {domain}.\n\n"
        f"### Step 2: Create Custom Audiences\n"
        f"Create the 3 audience segments defined in this config.\n\n"
        f"### Step 3: Launch Campaigns\n"
        f"Use the campaign templates to create retargeting campaigns.\n"
        f"Start with the Website Visitors campaign and expand based on results.\n\n"
        f"### Budget\n"
        f"Recommended starting budget: $45/day ($1,350/month total).\n"
        f"Scale based on ROAS after 2 weeks of data."
    )

    return RetargetingConfig(
        pixel_id="",  # To be configured per client
        pixel_events=["PageView", "ViewContent", "Lead", "Schedule"],
        pixel_domain=domain,
        audiences=audiences,
        campaign_templates=campaign_templates,
        daily_budget_cents=daily_budget_cents,
        setup_instructions=setup_instructions,
    )


def build_metrics_config(
    input_data: StrategySprintInput,
) -> MetricsConfig:
    """Build metrics and dashboard configuration from Strategy Sprint input.

    Generates KPIs, funnel stages, dashboard filters, and alert thresholds
    relevant to the client's funnel.

    Args:
        input_data: Validated Strategy Sprint input.

    Returns:
        Configured MetricsConfig instance.
    """
    # KPIs relevant to the client's funnel
    kpis = [
        {"name": "emails_sent", "target": 30, "unit": "count", "period": "weekly"},
        {"name": "open_rate", "target": 0.30, "unit": "percent", "period": "rolling_7d"},
        {"name": "click_rate", "target": 0.05, "unit": "percent", "period": "rolling_7d"},
        {"name": "reply_rate", "target": 0.08, "unit": "percent", "period": "rolling_7d"},
        {"name": "demos_booked", "target": 3, "unit": "count", "period": "weekly"},
        {"name": "demo_show_rate", "target": 0.80, "unit": "percent", "period": "rolling_30d"},
        {"name": "pipeline_value", "target": 0, "unit": "dollars", "period": "monthly"},
        {"name": "deals_closed", "target": 1, "unit": "count", "period": "monthly"},
    ]

    # Funnel stages
    funnel_stages = [
        "sent",
        "delivered",
        "opened",
        "clicked",
        "replied",
        "demo_booked",
        "demo_completed",
        "proposal_sent",
        "closed_won",
    ]

    # Dashboard filters
    dashboard_filters = {
        "date_range": "last_30_days",
        "segment_by": "industry",
        "industries": input_data.target_market.industries,
        "geographies": input_data.target_market.geographies,
    }

    # Webhook events to track
    webhook_events = [
        "delivered",
        "opened",
        "clicked",
        "replied",
        "bounced",
    ]

    # Alert thresholds
    alert_thresholds = {
        "bounce_rate_max": 0.05,
        "open_rate_min": 0.20,
        "reply_rate_min": 0.03,
        "daily_send_max": 30,
    }

    return MetricsConfig(
        kpis=kpis,
        funnel_stages=funnel_stages,
        dashboard_filters=dashboard_filters,
        webhook_events=webhook_events,
        alert_thresholds=alert_thresholds,
    )


# ============================================================================
# Helper functions
# ============================================================================


def _build_content_templates(input_data: StrategySprintInput) -> list[dict]:
    """Build LinkedIn content templates with client context."""
    templates = []

    # Insight post template
    templates.append({
        "content_type": "insight_post",
        "hook_template": (
            f"Most {input_data.icp.titles[0].lower()}s "
            f"I talk to share the same challenge: [specific pain point]"
        ),
        "body_template": (
            f"Here's what the best {input_data.target_market.industries[0].lower()} "
            f"companies are doing differently:\n\n"
            f"1. [Insight 1 related to {input_data.value_proposition.headline}]\n"
            f"2. [Insight 2]\n"
            f"3. [Insight 3]\n\n"
            f"The common thread? [Connecting theme]."
        ),
        "cta_template": (
            f"What's your experience? Drop a comment below."
        ),
    })

    # Case study template
    if input_data.case_studies:
        cs = input_data.case_studies[0]
        templates.append({
            "content_type": "case_study_summary",
            "hook_template": (
                f"{cs.get('result', '[Result]')} "
                f"in {cs.get('timeframe', '[timeframe]')}. Here's how."
            ),
            "body_template": (
                f"[Company] was struggling with [challenge].\n\n"
                f"They implemented [solution approach] and saw:\n"
                f"- {cs.get('result', '[Result]')}\n"
                f"- [Additional metric]\n\n"
                f"The key insight: [what made the difference]."
            ),
            "cta_template": (
                f"Facing similar challenges in {input_data.industry.lower()}? "
                f"DM me — happy to share what's working."
            ),
        })

    # Industry commentary template
    templates.append({
        "content_type": "industry_commentary",
        "hook_template": (
            f"The {input_data.industry.lower()} industry is changing fast. "
            f"Here's what I'm seeing."
        ),
        "body_template": (
            f"Trend: [industry trend]\n\n"
            f"What this means for {input_data.icp.titles[0].lower()}s:\n"
            f"[Analysis and implications]\n\n"
            f"The companies adapting fastest are [what leaders are doing]."
        ),
        "cta_template": (
            f"What trends are you seeing in your corner of "
            f"{input_data.industry.lower()}?"
        ),
    })

    # Behind the scenes template
    templates.append({
        "content_type": "behind_the_scenes",
        "hook_template": (
            f"Building for {input_data.industry.lower()} means "
            f"understanding {input_data.pain_points[0].lower() if input_data.pain_points else 'real challenges'} firsthand."
        ),
        "body_template": (
            f"This week we [specific activity].\n\n"
            f"What we learned:\n"
            f"- [Learning 1]\n"
            f"- [Learning 2]\n\n"
            f"It reinforced why {input_data.value_proposition.differentiators[0].lower() if input_data.value_proposition.differentiators else 'our approach'} matters."
        ),
        "cta_template": (
            f"What's one thing you wish more people understood about "
            f"{input_data.industry.lower()}?"
        ),
    })

    return templates


def _build_campaign_templates(input_data: StrategySprintInput) -> list[dict]:
    """Build retargeting campaign templates."""
    company = input_data.company_name
    return [
        {
            "name": f"{company} — Website Visitor Retargeting",
            "objective": "CONVERSIONS",
            "audience_type": "website_visitors",
            "ad_format": "single_image",
            "headline": input_data.value_proposition.headline[:40],
            "description": (
                input_data.value_proposition.sub_points[0][:90]
                if input_data.value_proposition.sub_points
                else "Learn how we can help your business grow"
            ),
            "cta": "LEARN_MORE",
        },
        {
            "name": f"{company} — Email Engager Retargeting",
            "objective": "CONVERSIONS",
            "audience_type": "email_engagers",
            "ad_format": "single_image",
            "headline": f"See why {input_data.target_market.industries[0].lower()} companies choose {company}"[:40],
            "description": (
                input_data.value_proposition.proof_points[0][:90]
                if input_data.value_proposition.proof_points
                else f"Trusted by {input_data.target_market.industries[0].lower()} companies"
            ),
            "cta": "SIGN_UP",
        },
        {
            "name": f"{company} — Demo Booker Retargeting",
            "objective": "CONVERSIONS",
            "audience_type": "demo_bookers",
            "ad_format": "single_image",
            "headline": f"Ready to get started with {company}?"[:40],
            "description": (
                f"You booked a demo — here's what you'll get: "
                f"{input_data.value_proposition.headline.lower()}"[:90]
            ),
            "cta": "SIGN_UP",
        },
    ]