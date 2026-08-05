---
name: channel-strategy
description: "Strategy Sprint Exercise 7: Channel Strategy. Prioritizes marketing channels by audience fit, cost efficiency, team capability, and competitive advantage, producing a tiered channel list with budget allocation. Output is automatically saved to the /marketing-strategy skill."
metadata:
  version: 1.0.0
---

# Channel Strategy Exercise

You are running the Channel Strategy exercise. It decides which channels deserve investment and which to deprioritize, so that the campaigns designed in `/big-bets` are built on channels that were chosen deliberately rather than named from habit.

This exercise runs seventh, after the strategy is settled and before campaigns are designed. It consumes the ICP, positioning, and advantages work; `/big-bets` consumes its output as campaign fuel.

## Prerequisites

Read `${ARTIFACT_DIR}/output/marketing-strategy.md`. These sections should be complete before scoring:

- **Company Overview** for budget and team size
- **ICP Prioritization** for where the audience actually is
- **Marketing Advantages** for assets that make a channel winnable
- **Positioning** for the intent match a channel has to carry

If those sections still read `*Not yet completed.*`, stop and run the earlier exercises first. Scoring channels without an ICP produces a ranked list of guesses.

## When to Use

- As Exercise 7 of a full Strategy Sprint
- Standalone at quarterly reviews to re-evaluate channel allocation
- When launching a product or service that may shift channel priorities
- When a channel is underperforming and the decision is fix or abandon

---

## Channels to Evaluate

Score each channel that is relevant to the client. Do not score all twelve out of completeness; a channel nobody would ever fund does not need a number.

| Channel | Description |
|---------|-------------|
| **Paid Social** | Meta Ads, LinkedIn Ads, TikTok Ads: paid distribution on social platforms |
| **Organic Social** | LinkedIn posts, Twitter/X, Instagram, TikTok: unpaid social presence |
| **SEO** | Search engine optimization: blog content, technical SEO, link building |
| **Email** | Newsletter, nurture sequences, cold outreach, lifecycle emails |
| **Cold Outreach** | Direct outbound: cold email, cold calling, LinkedIn DMs |
| **Content Marketing** | Blog posts, guides, whitepapers, podcasts, video: owned media |
| **Events** | Webinars, conferences, meetups, workshops: live or virtual |
| **Partnerships** | Co-marketing, affiliate programs, referral programs, integrations |
| **Paid Search** | Google Ads, Bing Ads: search intent capture |
| **Display/Programmatic** | Banner ads, retargeting, programmatic buys |
| **PR/Media** | Press releases, media outreach, earned media |
| **Community** | Forums, Slack/Discord groups, user communities |

---

## Scoring Framework

Rate each channel 1-5 on four dimensions:

### 1. Audience Fit (weight: 35%)
- Where does the target audience actually spend time?
- What is the intent match? (active searching vs passive browsing)
- How reachable is the ICP on this channel?

**Score guide:**
- 5 = ICP is highly concentrated here, strong intent match
- 3 = ICP is present but mixed with non-targets
- 1 = ICP rarely uses this channel

### 2. Cost Efficiency (weight: 25%)
- What is the expected CAC relative to other channels?
- How does cost scale? (linear, logarithmic, exponential)
- What is the minimum viable spend to test?

**Score guide:**
- 5 = Low CAC, scales efficiently, cheap to test
- 3 = Moderate CAC, reasonable scaling
- 1 = High CAC, expensive to test, poor unit economics

### 3. Team Capability (weight: 20%)
- Does the team have the skills and tools for this channel?
- How much ramp-up time is needed?
- How much of it can be automated or outsourced?

**Score guide:**
- 5 = Deep expertise, tools already in place
- 3 = Some experience, would need moderate upskilling
- 1 = No experience, would need to hire or outsource

### 4. Competitive Advantage (weight: 20%)
- Is this channel underexploited by competitors?
- Does the client have unique assets for it? (brand, content library, network)
- Can they win here with a differentiated approach?

**Score guide:**
- 5 = Competitors are absent or weak, client has a unique advantage
- 3 = Competitors are active, level playing field
- 1 = Competitors dominate, this would be fighting uphill

---

## Scoring Process

### Step 1: Gather Inputs

Before scoring, collect:
- The ICP profile from `${ARTIFACT_DIR}/output/marketing-strategy.md`
- Current channel performance data, if any exists
- Competitor channel presence, from `${ARTIFACT_DIR}/output/competitors.md` or the client brief
- Team capabilities and budget constraints, from the Company Overview section
- Brand voice and existing content assets

Where a number is not available, say so in the scoring detail rather than estimating one. A score carrying an invented CAC is worse than a score marked unknown.

### Step 2: Score Each Channel

For each relevant channel, compute:

```
Weighted Score = (Audience Fit x 0.35) + (Cost Efficiency x 0.25) + (Team Capability x 0.20) + (Competitive Advantage x 0.20)
```

### Step 3: Rank and Tier

Sort channels by weighted score and assign tiers:

| Tier | Score Range | Recommendation |
|------|-------------|----------------|
| **Primary** | 4.0 - 5.0 | Full investment: dedicate budget and team time |
| **Secondary** | 3.0 - 3.9 | Test with limited budget, validate before scaling |
| **Experimental** | 2.0 - 2.9 | Small experiments only, time-boxed with clear success criteria |
| **Deprioritized** | 1.0 - 1.9 | Skip for now, revisit at the next quarterly review |

Two channels separated by less than 0.3 are not meaningfully ranked against each other. Present them as a tie and let the client break it on something the framework does not measure.

### Step 4: Budget Allocation

Distribute budget across tiers:
- **Primary channels:** 60-70% of total marketing budget
- **Secondary channels:** 20-30% of total marketing budget
- **Experimental channels:** 5-10% of total marketing budget
- **Deprioritized:** 0%

Within each tier, allocate proportionally by weighted score.

---

## Output Format

Present this to the client for confirmation before saving:

```markdown
# Channel Strategy: {Client Name}
Date: {YYYY-MM-DD}
Review cycle: Quarterly

## Prioritized Channel List

### Primary Channels
1. **{Channel}**: Score {X.X}
   - Why: {1-2 sentence rationale}
   - Budget allocation: {X}%
   - Key metrics: {what to track}
   - Owner: {who runs this}

### Secondary Channels
...

### Experimental Channels
...

### Deprioritized Channels
...

## Budget Summary
| Channel | Tier | Monthly Budget | % of Total |
|---------|------|---------------|------------|
| ... | ... | ... | ... |

## Scoring Detail
| Channel | Audience | Cost Eff. | Team Cap. | Comp. Adv. | Weighted |
|---------|----------|-----------|-----------|------------|----------|
| ... | ... | ... | ... | ... | ... |

## Next Review
{date of next quarterly review}
```

---

## Saving Output

After the client confirms, update `${ARTIFACT_DIR}/output/marketing-strategy.md`:

1. Find the `## Channel Strategy` section
2. Replace everything from `*Not yet completed.*` through the `### What Goes Here` subsection with the confirmed output
3. Leave every other section untouched

Also write the full scoring detail to **`${ARTIFACT_DIR}/output/channels.md`**, so the per-channel reasoning survives even though only the tiered list and budget summary go into the master document.

---

## Feeding /big-bets

`/big-bets` runs next and needs the Engine of each campaign to be a real channel decision. Hand it:

- The Primary and Secondary tiers, which are the only channels a campaign should be built on
- The budget allocation, which bounds what a campaign can actually spend
- The Deprioritized list, so a campaign does not quietly reintroduce a channel this exercise ruled out

A campaign whose Engine names a Deprioritized channel is a contradiction between two exercises, and the sprint should surface it rather than ship both.

---

## Re-evaluation Triggers

Re-run this exercise when:
- A primary channel's CAC increases more than 30% quarter over quarter
- A new competitor enters or exits a channel
- The client launches a new product or service
- Budget changes by more than 20%
- Team composition changes
- An experimental channel shows promising early results

---

## Provenance

Extracted 2026-08-05 from the same source directory the other seven exercises came from on 2026-07-27 (see the lineage note in the README), where it had been left behind because it was never wired into the sprint sequence: it carried no exercise number and no output contract, and only its description claimed sprint membership.

Adapted for this repo: given the Exercise 7 position and the `${ARTIFACT_DIR}` output contract used by every other exercise, prerequisites and the `/big-bets` handoff made explicit, and references to a specific agent fleet generalized to roles.

**Edit this file here, not in the source repo.** This repo is canonical for the sprint.
