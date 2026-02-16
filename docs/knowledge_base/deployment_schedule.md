# Deployment Schedule — Reading from Assignment Spreadsheet

> The bot reads team assignments directly from the
> [ICM Follow-up Prep & Survey Plan](https://docs.google.com/spreadsheets/d/1KKtZRSFAd-kIfY0pUObgu3wylt80B9tcis7medSlM7s/edit?gid=1809436197#gid=1809436197)
> Google Sheet.

## How to Read the Assignment Sheet

| Column | Field | Description |
|--------|-------|-------------|
| A | `date` | Deployment date for this barangay |
| B | `team` | Team assigned (team_a through team_f) |
| C | `brgy_prefix` | 7-character barangay prefix code (e.g., H030832) |

## Barangay Prefix to Name Mapping

The bot needs a lookup table to convert `brgy_prefix` codes to human-readable names.
This can be derived from the cases CSV or maintained separately:

| brgy_prefix | Barangay | Municipality | Province |
|-------------|----------|-------------|----------|
| H030837 | [name] | [municipality] | [province] |
| H030832 | [name] | [municipality] | [province] |
| ... | ... | ... | ... |

> This lookup is generated as part of the Stata pipeline and can be exported
> as a separate reference CSV for the bot.

## Bot Commands Using This Data

### `/assignments [date]` or `/assignments today`
1. Read the assignment sheet
2. Filter rows where `date` matches the requested date (or most recent)
3. Look up barangay names from the prefix mapping
4. Format and post:
   ```
   team_a - Libo-o, DINGLE
   team_b - Guinacas, POTOTAN
   ```

### `/where_is [team_name]`
1. Read the assignment sheet
2. Find the most recent row for the given team
3. Return: "Team A is currently assigned to [barangay], [municipality] since [date]"

### `/team_for [barangay or brgy_prefix]`
1. Search the assignment sheet for the barangay name or prefix
2. Return: "[barangay] is assigned to [team] since [date]"