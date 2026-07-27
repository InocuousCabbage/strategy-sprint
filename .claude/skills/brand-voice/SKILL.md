---
name: brand-voice
description: "Per-client brand voice / communication style guide. Reads client override from artifacts/<client>/input/brand-voice.md when present; falls back to the built-in defaults below. Ensures all agent-drafted content matches the client's voice, not a generic AI voice. Use when drafting external communications or reviewing drafts."
---

# Brand Voice Skill

> Per-client communication style guide. Reads override from `${ARTIFACT_DIR}/input/brand-voice.md` if present; otherwise applies the built-in defaults below.

## Per-client override (2026-07-27, strategy-sprint extraction)

If `${ARTIFACT_DIR}/input/brand-voice.md` exists, it OVERRIDES the built-in defaults section-by-section. The override file uses the same YAML-block shape as the defaults below (tone, greeting, signoff, formality, phrases to use, phrases to avoid, examples).

Standalone invocation: set `ARTIFACT_DIR` first, then run this skill. It will:

1. Copy the built-in defaults to `${ARTIFACT_DIR}/output/brand-voice.md` as the baseline.
2. Read `${ARTIFACT_DIR}/input/brand-voice.md` if present, overlay its sections onto the output.
3. Announce which sections came from override vs default, so the operator can spot gaps.

If no override exists AND no client-specific voice has been discussed, PROMPT the operator for at least the top-3 style traits and voice examples before writing the output. Do not silently ship generic Ben-personal defaults for a client where they don't fit.

## Trigger

- Drafting any external communication (email, message, post) FOR THE CLIENT
- Before sending any response on the client's behalf
- Manual: "check <client>'s voice" or "review this draft"

---

## Communication Styles

### Personal Communications

**Style:** Casual and brief

Use for: Friends, family, casual texts, personal social media

```yaml
tone: casual and brief
greeting: "Hi [name]"
signoff: "Best, Ben"
formality: casual
```

### Professional Communications

**Style:** Direct and concise

Use for: Work emails, business contacts, professional networking

```yaml
tone: direct and concise
greeting: "Hi [name],"
signoff: "Best, Ben"
formality: professional
```

---

## Formality Levels

| Level | When to Use | Characteristics |
|-------|-------------|-----------------|
| **Casual** | Friends, family, close colleagues | Short, informal, "Hi [name]" |
| **Conversational** | Colleagues, acquaintances | Friendly but clear, brief |
| **Professional** | New contacts, clients | Clear, concise, professional |
| **Formal** | Legal, investors, VIPs | Full sentences, proper structure |

---

## Personality Markers

```yaml
greeting_style: "Hi [name]"
signoff_style: "Best, Ben"
signature: "Ben"

# Context-adjusted:
casual_greeting: "Hi [name]"
professional_greeting: "Hi [Name],"
formal_greeting: "Hello [Name],"

casual_signoff: "Best, Ben"
professional_signoff: "Best, Ben"
formal_signoff: "Best regards, Ben"
```

---

## Do's and Don'ts

### Always Do

- Get to the point quickly
- Keep it short
- Match the energy of who you're responding to
- Be direct about asks
- Use simple, plain English
- Separate facts from assumptions
- Use positive phrasing when possible

### Never Do

- Use robotic language or corporate jargon
- Use excessive exclamation marks
- Use corporate buzzwords (synergy, leverage, etc.)
- Use too many emojis
- Use the phrase "aren't just"
- Use vague business jargon
- Elaborate unnecessarily
- Use negative phrasing when positive would work
- Over-polish or make wording feel unnatural
- Use language that's too technical for the audience

### Word Choices

```yaml
never_use:
  - "synergy"
  - "leverage"
  - "circle back"
  - "per my last email"
  - "I'd be happy to"
  - "Great question!"
  - "aren't just"
  - "hope this finds you well"
```

---

## Templates by Context

### Personal Message

```
Hi [name]

[Direct point]

Best, Ben
```

### Professional Email

```
Hi [Name],

[One sentence context if needed]

[Main point]

[Clear ask or next step]

Best,
Ben
```

### Quick Message (iMessage, text)

- Keep it short
- Skip greetings for ongoing conversations
- Respond in kind to their style

---

## Validation Checklist

Before sending ANY communication, verify:

- [ ] Does this sound like Ben? (Not robotic)
- [ ] Is the formality level right for this person?
- [ ] Is it short enough? (Can anything be cut?)
- [ ] No banned words/phrases?
- [ ] Would Ben be comfortable if this were public?

---

## Configuration Summary

```yaml
user_name: "Ben"

voice_profile:
  personal_style: "casual and brief"
  professional_style: "direct and concise"
  greeting: "Hi [name]"
  signoff: "Best, Ben"

channel_defaults:
  email:
    formality: professional
    max_length: 150 words
  message:
    formality: casual
    max_length: 500 chars
```

---

*Your voice is your brand. Every message either builds or erodes trust. This skill ensures consistency.*
