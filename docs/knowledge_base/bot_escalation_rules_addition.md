## Case Pipeline Actions — Bot vs. Human

| Action | Bot Can Do? | How |
|--------|------------|-----|
| Look up case status | ✅ Yes | Query SurveyCTO API for `users` field value |
| Look up team assignment | ✅ Yes | Read assignment Google Sheet |
| Tell FO which forms they should see | ✅ Yes | Check `formids` based on treatment status |
| Explain why a case has no ICM Business form | ✅ Yes | "This is a control household — only the HH survey is assigned" |
| Announce new case uploads | ✅ Yes | Read assignment sheet → format announcement |
| Reopen a closed/refused case | ❌ No — SRA only | Bot logs request: "🔔 @Aubrey, [FO] requests reopening case [ID]. Reason: [reason]" |
| Upload new cases to SurveyCTO | ❌ No — SRA only | Requires Stata processing + server access |
| Change team assignment | ❌ No — SRA only | Requires editing cases dataset on server |
| Explain partial closure | ✅ Yes | "Case [ID] is still open because the ICM Business module hasn't been completed yet. The HH survey is done but the case won't close until both forms are submitted." |
| Explain why case shows as Refused | ✅ Yes | "Case [ID] was marked as Refused because consent was not given. If this was an error or the respondent has changed their mind, contact @Aubrey to reopen." |