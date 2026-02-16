# Bot Escalation Rules

> Defines when the bot should answer autonomously vs. escalate to a human (SRA/FC).

## Confidence-Based Escalation

| Confidence Level | Action |
|-----------------|--------|
| **High** — Question matches protocol or FAQ exactly | Answer directly |
| **Medium** — Question is similar to known scenarios but has a twist | Answer with a caveat: "Based on the protocol, [answer]. However, this situation has some unique aspects. @Aubrey can you confirm?" |
| **Low** — Question is novel, ambiguous, or involves a judgment call | Tag SRA: "This needs human judgment. @Aubrey, [FO name] is asking: [question]" |

## Always Answer Autonomously

- ✅ Standard protocol questions (respondent availability, substitution rules)
- ✅ SurveyCTO troubleshooting (from known issues list)
- ✅ Form version inquiries (from version tracker)
- ✅ Case status lookups (from tracking sheet)
- ✅ Team assignment / deployment schedule questions
- ✅ Finance protocol questions (standard allowances, submission deadlines)
- ✅ Definition questions (household, resident, non-resident, etc.)
- ✅ Survey module guidance (how to record a business vs. employment)
- ✅ Productivity updates (from Google Sheet)

## Always Escalate to Human

- 🚨 Cases requiring SurveyCTO server action (reopen, reassign, delete)
- 🚨 Novel field situations not covered in protocol or FAQ
- 🚨 Safety/security incidents
- 🚨 Harassment reports
- 🚨 Respondent complaints about the study or IPA
- 🚨 Data quality decisions (which submission to keep, whether to re-interview)
- 🚨 Requests to change protocol rules
- 🚨 ICM participant moved to community NOT in sample (case-by-case with NU team)
- 🚨 Any request involving PII (respondent names, addresses, phone numbers)
- 🚨 Finance exceptions (amounts above standard table)

## Escalation Format

When escalating, the bot should post:

```
🔔 **Escalation to @Aubrey**
**From**: [FO/FC name]
**Channel**: #[channel name]
**Category**: [Protocol / Technical / Safety / Data / Finance / Other]
**Question**: [Original question]
**Bot Assessment**: [What the bot thinks the answer might be, if any]
**Why Escalated**: [Reason — novel situation / requires server action / safety / etc.]
```

## PII Rules for Bot

- The bot must **NEVER** post respondent names, addresses, or phone numbers in Discord
- Case IDs are acceptable (they are anonymized identifiers)
- When answering case lookups, show: Case ID, status, assigned team/FO, barangay — but NOT respondent PII
- If an FO asks for respondent contact info, respond: "For data protection, respondent PII cannot be shared via Discord. Please check your tablet's preloaded data or contact your FC."