# Strategy Sprint

A standalone Claude Code skills repo that runs Emily Kramer-inspired Strategy Sprint exercises against any client. Extracted 2026-07-27 from a private multi-agent marketing framework, as a portable, orchestrator-driven, per-client workflow.

The sprint takes ~3-5 hours end-to-end with a knowledgeable operator and produces a complete marketing strategy document (positioning, ICP, revenue levers, big-bet campaigns, brand voice, etc.) for one client.

## What's inside

Ten skills: eight numbered exercises, one companion, one prerequisite. Chained by the top-level orchestrator.

| Skill | Purpose |
|-------|---------|
| `strategy-sprint` | Top-level orchestrator. Chains all 8 exercises + the tool-inventory prerequisite + brand-voice against one client. |
| `company-overview` | Exercise 1. Foundational company context, product, metrics, differentiators. |
| `icp-prioritization` | Exercise 2. Prioritized ICP tiers (Core / Scaling / Testing / Not a Priority). |
| `marketing-advantages` | Exercise 3. Unfair marketing advantages across MKT1 categories. |
| `perceptions` | Exercise 4. 3-5 storylines the client wants to be known for. |
| `positioning` | Exercise 5. Positioning statement + competitive map + category strategy. |
| `revenue-levers` | Exercise 6. Which of the 4 revenue levers to invest in and how. |
| `channel-strategy` | Exercise 7. Weighted channel scoring, tiers, budget allocation. |
| `big-bets` | Exercise 8. 1-3 major campaigns that ladder up to everything above. |
| `brand-voice` | Companion. Per-client voice guide, overrides built-in defaults from `input/brand-voice.md`. |
| `tool-inventory` | Prerequisite to Exercise 7. What the client can actually operate, as opposed to what they pay for. |

## How to run

### Prerequisites

- Claude Code with skills support
- A per-client artifact folder at `artifacts/<client-slug>/` (copy `artifacts/example-client/` as a starter)
- `artifacts/<client-slug>/input/client-brief.md` filled in with baseline client context

### Full sprint

Invoke the orchestrator with the client slug:

```
/strategy-sprint acme
```

The orchestrator:
1. Verifies `artifacts/acme/input/client-brief.md` exists.
2. Sets `ARTIFACT_DIR=artifacts/acme` for the run.
3. Runs the 8 exercises in dependency order, each pausing for operator/client confirmation before saving.
4. Runs `/brand-voice` last, applying `input/brand-voice.md` overrides if present.
5. Verifies `output/marketing-strategy.md` has no `*Not yet completed.*` placeholders left.

Expected wall-clock: 3-5 hours with a knowledgeable operator running the client-facing conversations.

### Single-phase

Any exercise runs on its own. Useful for iterating one section after a full sprint has already run, or for updating the strategy as things change:

```
ARTIFACT_DIR=artifacts/acme /positioning
```

Or in-prompt: "Run /positioning against artifacts/acme."

## Per-client artifact folder shape

```
artifacts/<client-slug>/
├── input/
│   ├── client-brief.md          # REQUIRED: company snapshot, goals, current state
│   ├── prior-research.md        # optional: anything already researched
│   └── brand-voice.md           # optional: client voice override
└── output/
    ├── marketing-strategy.md    # master strategy doc, populated section-by-section
    ├── product.md               # deeper product context (by /company-overview)
    ├── icp.md                   # ICP tier details (by /icp-prioritization)
    ├── competitors.md           # competitive map (by /positioning)
    ├── notes.md                 # cross-exercise operator notes
    └── campaigns/               # one file per big-bet campaign (by /big-bets)
```

Copy `artifacts/example-client/` as a starter. Delete the placeholder preambles, replace with real content.

## Data dependencies (why the phase order matters)

```
company-overview → icp-prioritization → marketing-advantages
     ↓                     ↓                       ↓
perceptions ← positioning ← ── ── ── ── ── ── ── ─┘
     ↓             ↓
revenue-levers → channel-strategy → big-bets → brand-voice
                       ↑
                 tool-inventory
```

**channel-strategy runs BEFORE big-bets, and swapping them breaks the sprint.** The
dependency is one-directional: channel-strategy consumes ICP, positioning, advantages
and budget from exercises 1 through 6 and consumes nothing from big-bets, while
big-bets consumes channels, since the Engine of every campaign is a distribution
choice. Run the channel analysis afterwards and campaigns pick their channels before
the exercise that ranks channels has run, which is the problem the exercise exists to
solve. This is recorded here because "add the new exercise at the end" is the obvious
guess and it produces eight exercises with no change in output.

`tool-inventory` is a prerequisite rather than a numbered exercise: it gathers input
instead of producing strategy, and writes no section to `marketing-strategy.md`. It
feeds the Team Capability dimension, which is 20% of every channel's weighted score.

Skipping earlier phases breaks downstream context. If the client already has some sections (from a prior sprint), the orchestrator asks which to skip vs re-run.

## Design notes

- **Standalone + portable.** Skills reference `${ARTIFACT_DIR}` as their per-client root. No framework-specific paths remain.
- **Product + competitors are NOT standalone skills.** They live as SECTIONS within `/company-overview` (product) and `/positioning` (competitors), matching how the source Sprint methodology structures them. Adding standalone product/competitors skills would duplicate work already covered.
- **Not fully autonomous.** Every exercise pauses at Step 4 for operator/client confirmation. This is a human-in-the-loop workflow, not a fire-and-forget agent.
- **The core methodology comes from Emily Kramer's MKT1 framework.** This repo is a Claude-Code-native re-implementation for personal / small-team consulting use. Seven exercises came across from it; channel-strategy joined 2026-08-05 and tool-inventory was written for this repo.
- **Machine-readable output alongside the human document.** Each exercise writes a typed sidecar to `output/<exercise>.yaml`, indexed by a run manifest at `output/sprint-manifest.yaml`. The contract is `schema/strategy_sprint_input.schema.json`.

  The manifest exists because completion status cannot live only in the sidecar: a sidecar that was never written has nowhere to say it was expected, so "complete but absent" would be indistinguishable from "never ran". The manifest lists every step including unrun ones, which is what lets a consumer tell those apart.

  Payload schemas require only what an exercise exists to produce. Everything else is optional and nullable on purpose, because a required field with no available value does not produce an error, it produces a fabrication.

## Generating a GTM plan from a finished sprint

Once a sprint has run and its sidecars are written, `pipelines/gtm_generator/` turns
that typed output into a GTM plan.

```
pipelines/gtm_generator/     vendored generator modules
pipelines/gtm_generator/cli.py   this repo's own wrapper, not vendored
schema/                      the contract the generator reads against
tests/                       fixtures and tests, run in CI on pushes to main and on PRs against it
requirements.txt             pinned deps for both
```

The generator consumes the manifest and sidecars described above, not the prose
document, which is why the schema work came first. An exercise that has not run is
readable as unrun rather than as empty.

**The generator tree is vendored, not imported, and syncing it forward has a required
pre-commit gate. Both are documented in [`VENDOR.md`](VENDOR.md), which is the
authority.** That procedure is deliberately not restated here: it is an enumeration
that goes stale, and a second copy of it would drift from the first without either
copy looking wrong.

## License

`LICENSE`: All Rights Reserved. Private consulting methodology; not distributed for reuse.

## Lineage

- Extracted 2026-07-27 from a private multi-agent marketing framework: 7 exercises from one agent's skills directory, joined 2026-08-05 by channel-strategy from the same directory, plus brand-voice from a content-creator agent template.
- Marketing-agent-team-specific paths (`contexts/*.md`, `.claude/skills/marketing-strategy/`, `USER.md`, `tasks/strategy/`) rewritten to the `${ARTIFACT_DIR}` per-client convention.
- Extraction was read-only on the source framework; the source was not modified.
