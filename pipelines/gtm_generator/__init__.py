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

"""GTM Plan Generator — the crown jewel of the GTM Execution Engine.

Takes Strategy Sprint output and generates complete, executable GTM plans
configuring all 15 features from Sprints 1-5 for a specific client.
"""

from pipelines.gtm_generator.input_models import StrategySprintInput, validate_strategy_input
from pipelines.gtm_generator.output_models import GTMPlan
from pipelines.gtm_generator.generator import GTMPlanGenerator
from pipelines.gtm_generator.validators import PlanValidator
from pipelines.gtm_generator.plan_writer import PlanWriter

__all__ = [
    "StrategySprintInput",
    "validate_strategy_input",
    "GTMPlan",
    "GTMPlanGenerator",
    "PlanValidator",
    "PlanWriter",
]