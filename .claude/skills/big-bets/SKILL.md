---
name: big-bets
description: "Strategy Sprint Exercise 7: Big Bet Campaigns. Defines 1-3 major campaigns for the next quarter that bring the strategy to life — with specific audience, fuel, engine, goals, and timelines. Output is automatically saved to the /marketing-strategy skill."
metadata:
  version: 1.0.0
---

# Big Bet Campaigns Exercise

You are running the Big Bets exercise — the final Strategy Sprint exercise that translates all strategic work into concrete campaigns.

## Why This Exercise Matters

Strategy without execution is just theory. Big bets are the 1-3 major campaigns or initiatives that will consume the bulk of marketing resources over the next quarter. They're "big" because they require real investment (time, budget, effort) and they're "bets" because they're hypothesis-driven.

Each big bet should:
- Activate the #1 or #2 revenue lever
- Target a Core or Scaling ICP segment
- Reinforce at least one key perception
- Leverage a marketing advantage
- Have clear success metrics

This exercise is where all prior Strategy Sprint work comes together into action.

## Prerequisites

- Read `${ARTIFACT_DIR}/output/marketing-strategy.md` — ALL prior exercises should be completed:
  - Company Overview (context)
  - ICP Prioritization (who to target)
  - Marketing Advantages (what to leverage)
  - Perceptions (what stories to tell)
  - Positioning (how to frame it)
  - Revenue Levers (where to invest)

## Step 1: Research

1. **Synthesize prior exercises:**
   - What are the top 2 revenue levers?
   - Which ICP segments are Core/Scaling?
   - What advantages can we leverage?
   - What perceptions need reinforcing?
   - What's our positioning?

2. **Identify campaign opportunities:**
   - What seasonal or market timing matters?
   - What product launches or milestones are coming up?
   - What competitor movements create openings?
   - What content/assets already exist that we can build on?

3. **Assess resources:**
   - What's the budget?
   - What team capacity exists?
   - What tools/channels are already set up?

## Step 2: Conversational Discovery

### Campaign Ideation
1. "Given everything we've discussed in the sprint, what's the single most important marketing initiative for the next quarter?"
2. "Is there a product launch, event, or milestone coming up that we should build a campaign around?"
3. "What would you consider a 'big win' for marketing in the next 90 days?"

### Campaign Details (for each potential big bet)
4. "Who exactly is this campaign targeting?" (specific ICP segment + funnel stage)
5. "What's the goal — what metric are we trying to move?"
6. "What content or creative do we need to produce?" (fuel)
7. "What channels will we use to distribute it?" (engine)
8. "What's the timeline — when does this need to launch, and when do we measure?"
9. "Who's the DRI and who else needs to be involved?"

### Prioritization
10. "If you could only do ONE of these, which would it be?"
11. "Is there anything currently consuming marketing resources that we should stop to make room?"

## Step 3: Document

Compile into this format:

```markdown
### Big Bet Campaigns — Next Quarter

#### Big Bet 1: [Campaign Name]
- **Type:** [Content series / Product launch / Event / Outbound campaign / etc.]
- **Goal:** [Specific metric — e.g., "Generate 200 MQLs from Series A SaaS founders"]
- **Relevant OKR/KPI:** [What company goal this supports]
- **Revenue lever:** [Which lever this activates — #1 or #2]
- **Target audience:**
  - ICP segments: [Which ones]
  - Funnel stage: [Awareness / Consideration / Decision / Expansion]
- **Perception reinforced:** [Which perception(s) this campaign supports]
- **Advantage leveraged:** [Which marketing advantage this builds on]
- **Fuel (content/creative):**
  - [Asset 1 — e.g., "Benchmark report based on proprietary data"]
  - [Asset 2 — e.g., "5-part blog series"]
  - [Asset 3 — e.g., "Interactive calculator tool"]
- **Engine (distribution/channels):**
  - [Channel 1 — e.g., "LinkedIn organic + paid promotion"]
  - [Channel 2 — e.g., "Email nurture to existing database"]
  - [Channel 3 — e.g., "Partner co-marketing with [Partner]"]
- **Timeline:**
  - [Week 1-2]: [Prep/production]
  - [Week 3-4]: [Launch]
  - [Week 5-8]: [Sustain/optimize]
  - [Week 9-12]: [Measure/iterate]
- **DRI:** [Who owns this]
- **Stakeholders:** [Who else is involved]
- **Success metrics:**
  - Primary: [Metric + target]
  - Secondary: [Metric + target]
- **Budget:** [Estimated spend if applicable]

#### Big Bet 2: [Campaign Name]
[Same structure]

#### Big Bet 3: [Campaign Name] (if applicable)
[Same structure]

### Campaign-Strategy Alignment Check

| Campaign | Revenue Lever | ICP Target | Perception | Advantage |
|----------|-------------|-----------|-----------|-----------|
| [Bet 1] | [Lever #] | [Segment] | [P#] | [Advantage] |
| [Bet 2] | [Lever #] | [Segment] | [P#] | [Advantage] |
| [Bet 3] | [Lever #] | [Segment] | [P#] | [Advantage] |
```

## Step 4: Client Confirmation

Present the big bets:
- "Do these 1-3 campaigns feel like the right bets for this quarter?"
- "Are the goals ambitious but realistic?"
- "Do we have the resources to execute all of these?"
- "Is there anything missing — a campaign we should add or one we should cut?"

Make corrections based on feedback.

## Step 5: Save to Marketing Strategy

After client confirms, update `${ARTIFACT_DIR}/output/marketing-strategy.md`:
1. Find the `## Big Bet Campaigns` section
2. Replace everything from `*Not yet completed.*` through the `### What Goes Here` subsection with the confirmed output
3. Add `*Last updated: [today's date]*` at the top of the section

## Step 6: Enrich Context Files

Create initial campaign tasks:

1. **`${ARTIFACT_DIR}/output/campaigns/`** — Create a task file for each big bet campaign:
   ```yaml
   ---
   title: "[Campaign Name] — Big Bet Campaign"
   status: pending
   priority: 2
   assigned: agent-support
   domain: strategy
   squad: strategist
   tags: [big-bet, campaign, strategy-sprint]
   created: [today's date]
   ---
   ```
   Include the full campaign details from the big bet definition in the task body.

## Related Exercises

- **Depends on:** ALL prior exercises — this is the capstone
- **Next:** Strategy Sprint complete. Begin campaign execution with squad delegation.
- **Feeds into:** All tactical work — content creation, paid ads, outreach, tool building
