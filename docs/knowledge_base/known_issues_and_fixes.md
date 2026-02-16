# Known Issues & Fixes Log

> This document tracks known SurveyCTO form issues, bugs, and their resolutions.
> Updated by SRA whenever a new issue is identified and resolved.

## Current Form Versions

| Form | Version | Version ID | Last Updated | Change Summary |
|------|---------|-----------|--------------|----------------|
| ICM Household Survey | [version] | 2509011334 | Sep 1, 2025 | [summary of changes] |
| ICM Business Module (linked) | [version] | 2509010136 | Sep 1, 2025 | [summary of changes] |

## Active Known Issues

### Issue #001: [Example — Age soft constraint triggers incorrectly]
- **Date reported**: [date]
- **Reported by**: [FO name]
- **Form**: HH Survey
- **Module**: Household Roster
- **Question**: `r_age_soft`
- **Description**: Soft constraint on age triggers when head of household is 17 years old
  and iber is 1. The message asks "Given their relationship to one another, are their ages
  correct?" This is a valid soft constraint — FO should confirm with respondent and select
  "Yes" if ages are correct.
- **Status**: Working as intended (soft constraint, not a bug)
- **FO Action**: Confirm ages with respondent. If correct, select "Yes" to proceed.

### Issue #002: [Example — Cases not appearing after upload]
- **Date reported**: [date]
- **Description**: After new cases are uploaded for mop-up, FOs cannot see them
- **Cause**: FOs need to "Get Blank Form" AND refresh their case list
- **Fix**: Go to main menu → Get Blank Form → then check case list
- **Status**: Resolved (user action required)

### Issue #003: [Template for new issues]
- **Date reported**:
- **Reported by**:
- **Form**:
- **Module**:
- **Question field name**:
- **Description**:
- **Screenshot**: [link or description]
- **Status**: [Investigating / Fix deployed / Working as intended / Won't fix]
- **FO Action**:
- **Fix version**:

## Resolved Issues Archive

| # | Date | Form | Issue | Resolution | Fix Version |
|---|------|------|-------|------------|-------------|
| — | — | — | — | — | — |

## Form Change Log

| Date | Form | Version | Changes |
|------|------|---------|---------|
| Sep 1, 2025 | HH Survey | 2509011334 | [list changes] |
| Sep 1, 2025 | ICM Business | 2509010136 | [list changes] |
| Aug 28, 2025 | Both | [prev version] | Important updates to both forms — all FOs must Get Blank Form |

## How to Report a New Issue

1. FO encounters issue → change language to **English**
2. Take a **screenshot** of the error/question
3. Send to **SFO/FC** with: Case ID, question name (if visible), description
4. SFO/FC forwards to **SRA** on Discord `#scto` channel
5. SRA investigates and updates this document