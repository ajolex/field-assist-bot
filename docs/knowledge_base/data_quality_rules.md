# Data Quality Checks & Common Errors

> These checks are run by the SRA (in Stata) on submitted data.
> When issues are flagged, FOs may be asked to clarify or correct.
> The bot should be able to explain what a flag means and what the FO needs to do.

## High Frequency Checks (HFCs) — Run Daily

### 1. Duplicate Submissions
- **What**: Same case ID submitted more than once
- **Cause**: FO accidentally submitted twice, or form was re-opened and re-submitted
- **FO Action**: Confirm which submission is correct; SRA will delete the duplicate

### 2. Survey Duration Outliers
- **What**: Survey completed in < 30 minutes or > 3 hours
- **Flag**: Too fast may indicate skipping; too slow may indicate issues
- **FO Action**: Explain reason (e.g., respondent was very cooperative/had many businesses)

### 3. Consent Refused but Survey Completed
- **What**: Consent = No, but survey data exists
- **FO Action**: Clarify — was consent actually given? If not, data must be deleted

### 4. Roster Inconsistencies
- **What**: Number of resident members doesn't match baseline ± expected changes
- **FO Action**: Verify — did members leave/join? Provide explanation

### 5. Income/Consumption Outliers
- **What**: Values that are extremely high or low relative to the sample
- **Examples**: Monthly income > ₱100,000; food expenditure = ₱0
- **FO Action**: Confirm with respondent or provide context

### 6. GPS Coordinates
- **What**: GPS location is far from assigned barangay
- **FO Action**: Explain — was interview conducted at a different location? (e.g., respondent relocated)

### 7. Don't Know / Refuse Rates
- **What**: FO has abnormally high DK (-999) or Refuse (-888) rates
- **FO Action**: Review probing techniques; FC to observe during next interview

### 8. Enumerator-Specific Patterns
- **What**: One FO's data consistently differs from others (e.g., always lower consumption)
- **FO Action**: FC accompaniment for quality check

## Back Checks — Run Weekly

- Random sample of completed interviews are called back
- Verify: Was the interview conducted? Were key questions asked correctly?
- FOs are not told which cases will be back-checked

## How Quality Flags Are Communicated

1. SRA runs checks in Stata
2. Flags are compiled in a spreadsheet
3. FC receives the flags and discusses with relevant FOs
4. FO provides clarification or correction
5. SRA updates the dataset

## Common Data Entry Errors

| Error | Example | How to Avoid |
|-------|---------|--------------|
| Wrong unit | Entered 5 sacks but meant 5 kilos | Always confirm units before recording |
| Missing zero | Entered 100 instead of 1000 | Double-check amounts |
| Wrong household member | Recorded income for wrong person | Confirm name before each member section |
| Skipped probe | Accepted DK without probing | Always probe before accepting DK |
| Wrong recall period | Reported annual amount for monthly question | Re-read the time period to respondent |