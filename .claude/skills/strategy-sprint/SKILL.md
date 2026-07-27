---
name: strategy-sprint
description: "Top-level Strategy Sprint orchestrator. Runs an 8-skill marketing strategy sprint against a per-client artifact folder — company-overview, ICP prioritization, marketing advantages, perceptions, positioning, revenue levers, big-bet campaigns, and brand voice. Reads client input from artifacts/<client>/input/, produces strategy sections in artifacts/<client>/output/. Extracted from marketing-agent-team; standalone + portable."
metadata:
  version: 1.0.0
---

# Strategy Sprint Orchestrator

You are running a complete Strategy Sprint for a client. This orchestrator chains the 7 core Sprint exercises + 1 companion brand-voice skill, producing a full marketing strategy document with per-client customization.

## Per-Client Artifact Folder Convention

Every Sprint run targets ONE client, whose inputs and outputs live under a dedicated per-client artifact folder:

```
artifacts/<client-slug>/
├── input/
│   ├── client-brief.md          # required — company description, goals, current state
│   ├── prior-research.md        # optional — any research the operator already did
│   └── brand-voice.md           # optional — client's brand-voice override (falls back to defaults if absent)
└── output/
    ├── marketing-strategy.md    # the master strategy doc, populated section-by-section
    ├── product.md               # deeper product context (populated by company-overview)
    ├── icp.md                   # ICP tier details (populated by icp-prioritization)
    ├── competitors.md           # competitive map (populated by positioning)
    ├── notes.md                 # cross-exercise operator notes
    └── campaigns/               # one file per big-bet campaign (populated by big-bets)
```

Every exercise skill in this repo references `${ARTIFACT_DIR}` as its per-client root. When the orchestrator runs, it sets `ARTIFACT_DIR` to the chosen client's folder. When an exercise skill runs standalone, the operator must set `ARTIFACT_DIR` before invocation (see "Single-phase mode" below).

## How to Run

### Full sprint (all 8 phases)

Invoke with the client slug:

```
/strategy-sprint <client-slug>
```

The orchestrator will:

1. Verify `artifacts/<client-slug>/input/client-brief.md` exists (fail loud if not — the client brief is the single source of truth for the run).
2. Create `artifacts/<client-slug>/output/` if it doesn't exist, seed `marketing-strategy.md` from the template if new.
3. Set `ARTIFACT_DIR=artifacts/<client-slug>` for the run.
4. Execute the 7 core exercises in order (each writes its section to `output/marketing-strategy.md`):
   - Phase 1: `/company-overview`
   - Phase 2: `/icp-prioritization`
   - Phase 3: `/marketing-advantages`
   - Phase 4: `/perceptions`
   - Phase 5: `/positioning`
   - Phase 6: `/revenue-levers`
   - Phase 7: `/big-bets`
5. Execute the companion `/brand-voice` skill last, populating `artifacts/<client-slug>/output/brand-voice.md` from either the client's `input/brand-voice.md` override or the built-in defaults.
6. Read back `output/marketing-strategy.md` to confirm all 7 sections are populated (no `*Not yet completed.*` placeholders remain).
7. Announce completion + summarize what was produced.

### Single-phase mode

Any exercise skill is individually runnable. The operator sets `ARTIFACT_DIR` as an env var or explicitly in the prompt, then invokes just that exercise:

```
ARTIFACT_DIR=artifacts/acme /company-overview
```

Or in-prompt: "Run /positioning against artifacts/acme."

Individual runs are useful for iterating on ONE section after the full sprint has run once, or for updating the strategy as it evolves (quarterly reviews, new competitor entrant, ICP shift, etc.).

## Prerequisites (before running)

- The client folder must exist at `artifacts/<client-slug>/` with an `input/client-brief.md`. If not, either seed from `artifacts/example-client/` or refuse to run.
- The operator (human) should be available for the Step 4 client-confirmation questions in each exercise. This is NOT a fully-autonomous run — every exercise pauses for operator/client confirmation before saving to marketing-strategy.md.

## Data flow (why the order matters)

Each exercise depends on the outputs of the ones before it:

```
company-overview   → foundational context; everything else references it
    ↓
icp-prioritization → who we serve; positioning + big-bets both need this
    ↓
marketing-advantages → what strengths we have; big-bets should leverage these
    ↓
perceptions        → the storylines; big-bets should reinforce these
    ↓
positioning        → the market position; competitors.md + big-bets both depend on this
    ↓
revenue-levers     → where to invest; big-bets should activate the top 1-2 levers
    ↓
big-bets           → concrete campaigns that ladder up to everything above
    ↓
brand-voice        → applies across all campaigns produced by big-bets
```

Skipping or reordering breaks the dependency chain. If a client already has some sections (e.g. positioning already exists from a prior sprint), the orchestrator should ask which phases to skip vs re-run.

## Product / competitors — where they live

Neither `product` nor `competitors` is a standalone Sprint exercise. Both are covered as SECTIONS within existing exercises:

- **Product overview**: written into `output/product.md` by `/company-overview` Step 6.
- **Competitors table + positioning map**: written into `output/competitors.md` by `/positioning` Step 6.

Do not create standalone product or competitors skills. They are already covered.

## Output verification

After a full sprint, the operator should be able to:

1. Read `artifacts/<client-slug>/output/marketing-strategy.md` end-to-end and see all 7 sprint sections populated with client-specific content (not `*Not yet completed.*` placeholders).
2. Find deeper per-topic files at `output/product.md`, `output/icp.md`, `output/competitors.md`.
3. Find one file per big-bet campaign in `output/campaigns/`.
4. Find `output/brand-voice.md` with either the client's overrides or the defaults from `brand-voice/SKILL.md`.

## Related skills

- Each of the 8 individual exercise skills at `.claude/skills/<exercise>/SKILL.md`.
- Source lineage: extracted 2026-07-27 from `marketing-agent-team/orgs/lever/agents/boss/.claude/skills/` (7 exercises) and `marketing-agent-team/templates/content-creator/.claude/skills/brand-voice/` (brand-voice). Marketing-agent-team-specific paths were rewritten to the `${ARTIFACT_DIR}` per-client convention. See README for the extraction discipline.
