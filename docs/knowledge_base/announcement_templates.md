# Announcement Templates

> Standard message templates the bot can use for routine announcements.
> Variables in [brackets] are filled dynamically from data sources.

---

## Daily: Case Upload Notification

```
📋 **Case Assignments Uploaded**

The following cases have been uploaded:

[team_name] – [barangay], [MUNICIPALITY]
[team_name] – [barangay], [MUNICIPALITY]
...

Please check your case list and "Get Blank Form" before starting interviews today.
```

## Form Version Update

```
🔄 **Form Update — Action Required**

@everyone Important updates have been made to the following forms:

| Form | New Version | Version ID |
|------|------------|-----------|
| [form_name] | [version] | [version_id] |

**All FOs must "Get Blank Form" (HH and ICM) before your next respondent.**

Make sure you're using the versions listed above.
```

## Daily Productivity Summary

```
📊 **Daily Productivity Report — [Date]**

| Team | FO | Completed Today | Weekly Total | Weekly Target | % of Target |
|------|----|----|----|----|-----|
| [team] | [FO name] | [n] | [n] | 21 | [%] |
...

**Overall**: [total] surveys completed | [remaining] remaining
**On track**: [Yes/No — based on weekly target of 21 per FO]
```

## Weekly Progress Summary

```
📈 **Weekly Progress Report — Week [N] ([dates])**

| Province | Target | Completed | Remaining | % Complete |
|----------|--------|-----------|-----------|------------|
| Iloilo | [n] | [n] | [n] | [%] |
| Aklan | [n] | [n] | [n] | [%] |
| Antique | [n] | [n] | [n] | [%] |
| Capiz | [n] | [n] | [n] | [%] |
| **Total** | **[n]** | **[n]** | **[n]** | **[%]** |

Top performers: [FO names]
Cases needing attention: [list of non-response or delayed cases]
```

## Mop-Up Assignment

```
🔁 **Mop-Up Assignments — [Date/Round]**

The following mop-up cases have been uploaded:

| Team | Barangay | Municipality | # Cases |
|------|----------|-------------|---------|
| [team] | [brgy] | [muni] | [n] |

Please "Get Blank Form" and check your case list.
Remember: Same protocol rules apply. Maximum 3 visits on 2+ different days.
```

## Morning Reminder

```
🌅 **Good morning, teams!**

📍 Today's deployment:
[team_a] → [barangay], [municipality]
[team_b] → [barangay], [municipality]
...

📋 Reminders:
- Get Blank Form before first interview
- Current form versions: HH [version] | ICM [version]
- Target: 3.5 surveys per FO today
- Report any issues to your FC immediately

Stay safe and good luck! 🙏
```

## Safety Alert

```
⚠️ **Safety Alert — [Date]**

@everyone [Description of safety concern — e.g., weather warning, security issue]

**Action required**: [specific instructions — e.g., no fieldwork today, evacuate area, check in with FC]

**Affected teams**: [team list or "All teams"]

Please confirm you have received this message by reacting with ✅.
```