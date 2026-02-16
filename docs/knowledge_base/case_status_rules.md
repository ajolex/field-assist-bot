# Case Status Rules & Lifecycle

## Case ID Format

- Format: `H[Province_Code][Municipality_Code][Barangay_Code][HH_Number]`
- Example: `H019412021`
  - `H` = Household prefix
  - `019` = Province-Municipality prefix (first 3 digits after H)
  - `412` = Barangay code (next 3 digits)
  - `021` = Household number within the barangay
- **Barangay prefix** (`brgy_prefix`): First 7 characters of caseid (e.g., `H019412`). All households in the same barangay share the same prefix.
- **Case label** format on SurveyCTO: `[caseid]-[hh_resp_name]` (e.g., `H019412021-Juan Dela Cruz`)

## How Cases Are Created

Cases are generated from the intersection of two datasets:
1. **PSPS Wave 1 Household Survey** — baseline respondents who consented AND agreed to share PII
2. **ICM Phase A Selected Households** — households selected for the ICM livelihoods study
3. **Wave 1 Livelihoods Participants** — matched to determine treatment arm assignment

Only households that appear in **all three** datasets (and are not pilot households) become follow-up cases.

## Case Assignment to Teams

- The **Field Manager (Eunice)** updates the [ICM Follow-up Prep & Survey Plan](https://docs.google.com/spreadsheets/d/1KKtZRSFAd-kIfY0pUObgu3wylt80B9tcis7medSlM7s/edit?gid=1809436197#gid=1809436197) spreadsheet with team-to-barangay assignments
- Each row contains: `date`, `team`, `brgy_prefix`, and a pre-generated `stata command`
- The **SRA (Aubrey)** then runs Stata code that:
  1. Reads the barangay prefix assignments
  2. Assigns the `users` field (team name) for each case
  3. Exports a CSV file for upload to SurveyCTO server

### Team Assignment via Stata

Cases are assigned by barangay prefix. Example:
```stata
replace users = "team_a" if brgy_prefix == "H030837"
replace users = "team_b" if brgy_prefix == "H030832"
```

Only cases where `users != ""` (i.e., assigned to a team) are exported. Unassigned cases are dropped from the export.

### Assignment Spreadsheet Structure

| Column | Content | Example |
|--------|---------|---------|
| A: `date` | Date of assignment/deployment | September 25, 2025 |
| B: `team` | Team name | team_b |
| C: `brgy_prefix` | Barangay prefix code | H030832 |
| E-H: `stata command` | Pre-built Stata replace command | `replace users = "team_b" if brgy_prefix== "H030832"` |

## What Gets Uploaded to SurveyCTO

The exported CSV contains these columns:

| Column | Description | Example |
|--------|-------------|---------|
| `id` | Case ID (same as `caseid`) | H030832015 |
| `label` | Display label: `caseid-hh_resp_name` | H030832015-Maria Santos |
| `barangay` | Barangay name | Guinacas |
| `zone` | Zone within barangay | Zone 1 |
| `users` | Team assignment (who can see the case) | team_b |
| `formids` | Which forms the case requires | See below |
| `hh_head` | Head of household name | Juan Santos |
| `hh_resp_name` | Baseline respondent name | Maria Santos |
| `caseid` | Case identifier | H030832015 |
| `municipality` | Municipality name | Pototan |
| `province` | Province name | Iloilo |
| `w1_liveli_treat` | Treatment arm (0=control, 1/2/3=treatment) | 2 |

### Form Assignment Logic

| Treatment Status | Forms Assigned (`formids`) |
|-----------------|---------------------------|
| **Treatment** (w1_liveli_treat = 1, 2, or 3) | `ICM_follow_up_launch_integrated,ICM_Business_linked_launch` (both HH + ICM Business) |
| **Control** (w1_liveli_treat = 0 or missing) | `ICM_follow_up_launch_integrated` (HH survey only — no ICM Business module) |

> ⚠️ **Key implication**: Control households do NOT get the ICM Business Module form. If an FO asks why a control household doesn't have the ICM business form, the answer is: "This household is only assigned the household survey. This is by design."

## Case Statuses on SurveyCTO

Case visibility to FOs is controlled by the `users` column in the SurveyCTO cases dataset.

### How Case Closure Works (SurveyCTO Server Logic)

The SurveyCTO form uses the following publishing formula to update the `users` field:

```
if(${consent_agree} = 1 and ${now_complete} = 1 and ${pull_icm_form_status} = 1,
   'Closed',
   if(${consent_agree} = 0,
      'Refused',
      ${users}))
```

This means:

| Condition | `users` value becomes | Effect |
|-----------|----------------------|--------|
| Consent given + HH complete + ICM complete | `Closed` | Case disappears from FO's tablet |
| Consent refused | `Refused` | Case disappears from FO's tablet |
| Interview started but not finished | `[original team name]` (unchanged) | Case remains visible to the team |

### Status Summary

| Status | How It's Set | Visible to FO? | Description |
|--------|-------------|----------------|-------------|
| **`team_[x]`** (e.g., `team_a`) | Initial upload | ✅ Yes — visible to that team | Case is open and assigned |
| **`Closed`** | Auto — form publishes when consent=1 + HH complete + ICM complete | ❌ No | Both surveys successfully completed |
| **`Refused`** | Auto — form publishes when consent=0 | ❌ No | Respondent refused consent |
| **Still shows team name** | Form not finalized or only partially complete | ✅ Yes | Interview in progress or not yet started |

### Important Notes

- There is **no automatic "Non-Response" status**. If a household is never interviewed (respondent permanently unavailable), the case remains assigned to the team (`team_[x]`) unless manually changed.
- To mark a case as non-response, the **SRA must manually update** the cases dataset on SurveyCTO server (changing `users` to something like `non_response` or removing the team assignment).
- **Reopening a closed case**: The SRA must manually edit the cases dataset on SurveyCTO server, changing `users` back to the team name. The FO then needs to "Get Blank Form" to see it again.

## When Can a Case Be Reopened?

A case can be reopened when:
1. It was marked `Refused` or manually closed, but the respondent is now available (mop-up phase)
2. There was a data quality issue flagged in HFC checks that requires re-interview
3. The case was incorrectly submitted/closed
4. SurveyCTO sync error caused the case to disappear from the FO's tablet

**Who can reopen**: Only the Senior Research Associate (SRA) via SurveyCTO server — by editing the cases dataset and changing the `users` value back to the team name.

**Process**:
1. FO/FC reports the case ID and reason to SRA (via Discord)
2. SRA verifies the case status on the server
3. SRA edits the cases dataset: changes `users` from `Closed`/`Refused` back to `team_[x]`
4. FO must "Get Blank Form" to see the reopened case

## Case Not Appearing on Tablet

Common reasons and fixes:

| Reason | Fix |
|--------|-----|
| Case is assigned to a **different team** | Check assignment sheet — was this brgy assigned to this team? |
| FO hasn't done **"Get Blank Form"** | Refresh forms on tablet |
| Case was already **Closed** (completed) | Check server — if it needs reopening, SRA handles it |
| Case was **Refused** | Check server — `users` = `Refused` means it's hidden |
| Case was **never uploaded** | New batch hasn't been uploaded yet — SRA needs to upload the CSV |
| **Sync issue** | Ensure internet connection, try "Get Blank Form" again |
| Case was in a **different batch** | Cases are uploaded in batches — check which batch this brgy was in |

## Mop-Up Cases

- Mop-up = revisiting cases that remain open (never completed) or were Refused during main deployment
- Mop-up cases may be **re-uploaded** in a new batch with updated team assignments
- The SRA generates a new CSV from the same Stata pipeline, filtering for incomplete cases
- FOs must check their mop-up case list separately
- Same protocol rules apply for respondent availability (max 3 visits, 2+ different days)