---
name: tool-inventory
description: "Strategy Sprint prerequisite to Exercise 7: Tool Inventory. Establishes which marketing tools the client actually operates, as opposed to which ones they pay for, so that channel scoring and any generated GTM plan are rooted in real capability. Writes output/tool-inventory.yaml."
metadata:
  version: 1.0.0
---

# Tool Inventory

You are establishing what the client can actually execute with today.

This runs **before** `/channel-strategy` (Exercise 7). Channel scoring has a Team Capability dimension worth 20% of every channel's score, and any downstream GTM plan is only as real as the stack it assumes. Both are guesses until someone has asked what is actually in place.

## The distinction this exercise exists to make

**Paying for a tool is not using it.** A client with a CRM seat nobody has logged into since onboarding does not have a CRM. A client with marketing automation that sends one newsletter a quarter has an email tool, not marketing automation.

Every question below is really the same question: *what would happen tomorrow if you had to run a campaign on this?* Record the answer to that, not the answer to "do you have one."

This is the whole point of the exercise. A tool inventory that lists licenses produces a channel score that flatters the client and a GTM plan that assumes capability nobody has. Getting this wrong is worse than skipping the exercise, because it launders a guess into a recorded fact.

## Prerequisites

Read `${ARTIFACT_DIR}/output/marketing-strategy.md` for the Company Overview section, which carries team size and budget. A two-person team claiming eight actively-used platforms is worth a follow-up question.

## Categories to cover

Ask about each. A category the client does not use at all is a finding, not a gap in your notes.

| Category | Examples of what to ask about |
|----------|-------------------------------|
| **CRM** | Where contacts and deals live, who updates them, whether pipeline stages reflect reality |
| **Marketing automation** | Email sending, sequences, lifecycle triggers, list segmentation |
| **Scheduling** | Meeting booking, calendar routing, how a lead gets to a call |
| **Content and CMS** | Where the site and blog are published from, who can publish without a developer |
| **Analytics** | Web analytics, attribution, dashboards, what anyone actually looks at |
| **Data and enrichment** | Contact data sources, enrichment, list building, verification |
| **Ad platforms** | Which ad accounts exist, which have spent money in the last 90 days |

## How to ask

For each tool the client names, establish four things. The first is the only one people volunteer.

1. **What is it.** Product name and, where it matters, the tier. "HubSpot" and "HubSpot Enterprise" are different capabilities.
2. **Is it live.** When was it last used in anger? A date, or "not in months," or "we bought it and never set it up." Do not accept "yes."
3. **Who operates it.** A named person or role. A tool with no owner is a tool nobody will run a campaign on.
4. **What it is blocked on.** Missing integration, missing data, nobody trained, contract expiring. This is where the useful answers are.

Then ask two questions that are not about any specific tool:

- "What do you wish you had?" Names the gap the client already feels.
- "What are you paying for that you would cancel tomorrow?" Names the shelfware faster than asking about each tool in turn.

## Recording what you do not know

If the client cannot answer whether a tool is live, record it as `unknown`. Do not infer, and do not average it into "probably used."

`unknown` is a real and useful state here: it tells the channel-strategy scorer to treat that capability as absent for scoring while flagging it as worth a follow-up, which is different from a confirmed absence. An invented "yes" produces a Team Capability score with nothing behind it, and that score then gets a weight, a rank and a budget allocation, and by then nobody remembers it was a guess.

## Output

Present for confirmation, then save.

```markdown
# Tool Inventory: {Client Name}
Date: {YYYY-MM-DD}

## In active use
| Category | Tool | Tier | Owner | Last used | Notes |
|---|---|---|---|---|---|

## Owned but not operating
| Category | Tool | Why not | Cost | Recoverable? |
|---|---|---|---|---|

## Not in the stack
{Categories with nothing in them. State them explicitly.}

## Unknown
{Tools where live status could not be established, and what would settle it.}

## Constraints for channel scoring
{The two or three facts channel-strategy most needs: what the team can run
without hiring, what is blocked and on what, what would have to be bought.}
```

## Saving output

After the client confirms, write **`${ARTIFACT_DIR}/output/tool-inventory.yaml`** conforming to `schema/strategy_sprint_input.schema.json`.

The sidecar carries the required envelope header (`schemaVersion`, `exerciseId: tool-inventory`, `generatedAt`, `confirmedByClient`) plus the payload. Set `confirmedByClient: false` if you are saving a draft the client has not yet ratified. Do not set it true to move things along: a downstream consumer halts on unconfirmed content deliberately, and defeating that check by mislabelling is worse than the delay it avoids.

Then update the manifest at `${ARTIFACT_DIR}/output/sprint-manifest.yaml`: set this step's `status` and `completedAt`, or `status: failed` with a `failureReason` if you could not complete it. **A step that ran and failed must say so rather than being left as `unrun`**, because those two states have different remedies and the manifest is the only place the difference survives.

This exercise writes no section to `marketing-strategy.md`. It is an input to the sprint rather than a chapter of the strategy, and the human-readable inventory lives in its own file.

## Feeding /channel-strategy

Exercise 7 scores Team Capability at 20% of each channel's weighted score. Hand it:

- **In active use**, which is what "the team has skills and tools for this channel" actually means
- **Owned but not operating**, which is a cheaper path to capability than buying, and should raise a channel's score less than active use but more than nothing
- **Not in the stack**, which is what a low Team Capability score should be grounded in
- **Unknown**, which should score as absent AND appear in the scoring detail as unknown, so nobody later reads a low score as a confirmed finding

A channel scored 5 on Team Capability with no corresponding entry in the active-use list is a scoring error, and channel-strategy should catch it rather than pass it through.

## Provenance

Written 2026-08-05 for this repo. Not extracted from the source framework: it exists because a GTM plan generated from sprint output has to be rooted in tools the client actually operates, and nothing in the sprint established that. It is a prerequisite rather than a numbered exercise, because it gathers input rather than producing strategy.
