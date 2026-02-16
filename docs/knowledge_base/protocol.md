# ICM Follow-Up Survey — Field Protocol & Knowledge Base

> **Study**: ICM Follow-Up Survey
> **Organization**: Innovations for Poverty Action (IPA) Philippines
> **Partner**: International Care Ministries (ICM)
> **Baseline**: Philippines Socioeconomic Panel Survey (PSPS) — [Details](https://poverty-action.org/philippines-socioeconomic-panel-survey)
> **Study Page**: [Combining Cash Grants with Ultra-Poor Livelihoods Training Program](https://poverty-action.org/combining-cash-grants-with-ultra-poor-livelihoods-training-program-philippines)
> **Survey Platform**: SurveyCTO
> **Data Management**: Stata
> **Field Communication**: Discord
> **Productivity Tracking**: [Google Sheets Tracker](https://docs.google.com/spreadsheets/d/17T2bDbSg2Dh_2BYNkD79Nxqftfsh3OFRlUlX8_Vq7Jo/edit?gid=1057006547#gid=1057006547)

---

## 1. Study Background

### 1.1 What is this study?

This is a **follow-up survey** for a Randomized Controlled Trial (RCT) evaluating the impact of a livelihood program on ultra-poor households in Western Visayas, Philippines.

- **Baseline**: Conducted as part of the Philippines Socioeconomic Panel Survey (PSPS), 2023–2025.
- **Follow-up purpose**: Measure changes in social and economic outcomes (income, assets, food security) for households participating in the ICM Livelihood RCT.
- **Partnership**: IPA Philippines partnered with International Care Ministries (ICM), which runs a 15-lesson program called **Transform** for members of ultra-poor households.

### 1.2 What is the ICM Transform Program?

ICM provides training sessions on **livelihoods, health, and values**. In the Livelihood RCT, IPA supplemented the livelihood training component with cash grants that participants can invest in a business — either as a group or individually.

The Transform program focuses on three key areas:

- **Values**: Guidance on relationships and personal character
- **Health**: Guidance on physical needs
- **Livelihood**: Training for income-generating activities

### 1.3 Treatment Arms (RCT Design)

| Arm | Description |
|-----|-------------|
| **T1** | Small grant to enforced groups |
| **T2** | Large grant to individuals |
| **T3** | Large grant to individuals, encouraged to form groups (optional) |
| **Control** | No intervention (no ICM Transform program, no grants) |

> ⚠️ **CRITICAL**: Field officers must **NEVER** reveal a household's treatment status or compare grant sizes across households. Treat every respondent identically.

### 1.4 Coverage

- **400 barangays** across Iloilo, Aklan, Antique, Capiz, and Negros
- Non-random sample of households from the PSPS, selected for the ICM Transform program

---

## 2. Questionnaire Structure

The follow-up survey has **two main parts**:

### Part 1: Household Survey Questionnaire (from PSPS baseline)

| Module | Key Content |
|--------|-------------|
| **Household Roster** | Confirm/update members, demographics, education |
| **Consumption** | Food (last 7 days), non-food (last 30 days), durable goods (last 12 months), PPI items (last 6 months) |
| **Income & Labor** | Employment, income sources, hours worked, unearned income |
| **Agriculture** | Plots, crops, livestock, poultry, fishing, forestry (recall period: since July 2024) |
| **Non-Agricultural Businesses** | Business operations, profits, ownership |
| **Assets** | Housing, land, vehicles, equipment, furniture, appliances |
| **Health & Household Vulnerability** | Health expenditure, food security, water insecurity, shocks |
| **Housing Characteristics** | Dwelling materials, utilities, toilet facilities |
| **Financial Inclusion** | Savings, borrowing, banking habits |

### Part 2: ICM Business Module (new for follow-up)

- Only administered to **ICM program participants**
- Identifies which business from the household module is the "ICM business"
- Reverifies information if the ICM participant ≠ household survey respondent
- Captures business operations, sales, profits, and group dynamics

---

## 3. Respondent Protocol

> ⚠️ **THIS IS THE MOST CRITICAL SECTION. These rules must be followed strictly.**

### 3.1 Key Fact: Respondent Overlap

The respondent for the **Household Survey** and the **ICM Business Module** are **not always the same person**. The overlap is roughly **75%**. The ICM program participant is not necessarily the baseline household survey respondent.

### 3.2 Respondent Overlap Scenarios

| Scenario | HH Survey Respondent | ICM Business Respondent | Notes |
|----------|---------------------|------------------------|-------|
| **A** | Original PSPS respondent | Same person (also ICM participant) | Most common (~75%). Single respondent for entire survey. |
| **B** | Original PSPS respondent | Different person (ICM participant) | Complete HH survey with original respondent, then locate ICM participant for ICM Business Module. |
| **C** | New most knowledgeable member | Same person (also ICM participant) | Original respondent unavailable. New respondent handles both. |
| **D** | New most knowledgeable member | Different person (ICM participant) | Original respondent unavailable. New member does HH survey; locate ICM participant for ICM Business Module. |

### 3.3 Survey Programming Logic for Respondent Identification

1. **Pull data**: Retrieve PSPS household respondent name
2. **Pull data**: Retrieve ICM participant name from ICM data
3. **Calculate**: Are the household respondent and ICM participant the same person?
4. **If NOT the same**: After `hh_resp_note`, add the question:

   > *"I would also like to speak with [ICM_participant_name] for 15 minutes after I finish speaking to [bl_hh_resp_name]. Is he/she available?"*

   - **If no** → Ask: *"Will the ICM participant return to this household and resume being a resident?"*
     - (i.e., (1) return to living under this roof for at least 30 days AND (2) share food from a common source and/or share in a common resource pool)
     - **If yes** → Date and time field: *"When will they return and be available to interview?"*
     - **If no** →
       - *"When did the ICM participant move away?"* [date field]
       - *"Is there a phone number we can contact them on?"*
       - *"Where have they moved to?"* [text entry field]

### 3.4 ICM Business Module — Reverification Logic

- **SKIP** reverification questions if the respondent is the same as in the HH module AND this is the business they already identified
- **ASK** reverification questions if the ICM participant is different from the HH survey respondent, OR if the HH respondent is the ICM participant but did not mention the ICM business earlier

---

## 4. Household Respondent Availability Protocol

### 4.1 If Original Household Respondent is Temporarily Unavailable

*(Irrespective of whether the ICM participant is available)*

```
Step 1: Ask about respondent's availability over the coming days
        while the team is still in this community.
        → If available in coming days: REVISIT on the scheduled day.

Step 2: If NOT available in coming days OR still unavailable on scheduled day:
        → Find the NEXT MOST KNOWLEDGEABLE RESPONDENT in the household.

Step 3: If BOTH original respondent AND next knowledgeable member are unavailable:
        → Reschedule for a MAXIMUM of 3 visits on at least 2 DIFFERENT days.

Step 4: If unavailable after ALL attempts (3 visits, 2+ different days):
        → Mark the household as PERMANENTLY UNAVAILABLE.
```

### 4.2 If ICM Participant is Unavailable

First determine: Is the ICM participant **temporarily** or **permanently** unavailable?

**Key question**: Will the ICM participant return and resume being a resident?
- Definition of "resident": Living under this roof for at least 30 days AND sharing food from a common source and/or sharing in a common resource pool.

#### 4.2a ICM Participant is TEMPORARILY Unavailable (HH survey is complete)

```
Step 1: Reschedule for a day/time when ICM participant is expected to be available.

Step 2: Reschedule for a MAXIMUM of 3 visits on at least 2 DIFFERENT days.

Step 3: If ICM participant is STILL unavailable after all attempts:
        → Leave ICM participant survey as NON-RESPONSE.
        → Mark the HOUSEHOLD as COMPLETE (HH survey portion is done).
```

#### 4.2b ICM Participant is PERMANENTLY Unavailable

Complete the household survey for the original household, then:

| ICM Participant's New Location | Action |
|-------------------------------|--------|
| Moved **within the same community** | Conduct HH survey AND ICM participant survey at their **new household** |
| Moved to **another community within the study sample** | Conduct HH survey AND ICM participant survey at their **new household** |
| Moved to a **community NOT in our sample** | **Discuss with the NU team** on a case-by-case basis |

### 4.3 Decision Flowchart Summary

```
Original HH respondent available?
├── YES → Conduct HH survey
│         ICM participant same person?
│         ├── YES → Continue to ICM Business Module
│         └── NO → Is ICM participant available?
│                   ├── YES → Conduct ICM Business Module with them
│                   └── NO → [See 4.2a or 4.2b above]
│
└── NO (temporarily unavailable)
    ├── Available in coming days? → REVISIT
    ├── Not available → Find next most knowledgeable member
    ├── Both unavailable → Reschedule (max 3 visits, 2+ days)
    └── Still unavailable → Mark PERMANENTLY UNAVAILABLE
```

---

## 5. Household Definitions

### 5.1 What is a Household?

> All people, including children and non-relatives, who **live together** and have a **common arrangement in the preparation and consumption of food**.

### 5.2 Household Head

- Must be someone **currently residing** in the household
- Cannot be a person who lives elsewhere
- If the recognized head is away ≥3 months → listed as non-resident → designate a substitute **"acting" head of household**

### 5.3 Resident vs. Non-Resident Members

| Category | Definition |
|----------|-----------|
| **Resident** | Lives in household OR away for **<3 months**; includes students <18 who live at school |
| **Non-Resident** | Away for **≥3 months** for work/school (age 18+) |

### 5.4 Special Rules

**Student rule**:
- Primary/secondary student living at school → **Resident member** (boarder)
- Primary/secondary student living with relatives for school, returns home on holidays/weekends → **Resident member**
- University/post-secondary student who has moved elsewhere as primary residence → **Non-resident member**

**Time rule**:
- Majority of time in household → **Resident**
- Majority of time outside household → **Non-resident**
- **Exception**: Minors (<18) living away for school → always **Resident**

**Returning non-residents**: Members recorded as non-residents in PSPS who have returned → add as **new resident members** and remove from non-resident list.

---

## 6. Field Situation Decision Rules

### 6.1 Respondent Has Moved / Temporarily Relocated

**Scenario**: Respondent is temporarily staying at another house (e.g., house under repair, staying with partner).

**Rule**:
- If the respondent **does not know when they will return** to the original location → **Interview them at the current/new location**.
- If the respondent **will return within the team's deployment period** → Schedule a revisit at the original location.
- If the respondent has **permanently moved within the same community** → Interview at the new household.
- If permanently moved to **another community in the sample** → Interview at the new household.
- If permanently moved to **a community NOT in the sample** → Escalate to NU team.

### 6.2 Interviewing the 2nd Knowledgeable Respondent

**Scenario**: Field officer asks if they can interview the 2nd most knowledgeable respondent.

**Rules**:
- Only permitted if the **original respondent is unavailable** during the team's remaining days in the barangay.
- On the **1st visit**, always attempt to schedule a revisit first.
- If it is the **last day** in the barangay AND the original respondent is unavailable → **Yes, proceed with 2nd knowledgeable respondent**.
- If the **other main respondent IS available** → Interview the available main respondent first.

### 6.3 Cases Not Appearing on Tablet / Reopening Cases

**Scenario**: Field officer reports that assigned cases are not appearing in their SurveyCTO case list.

**Steps**:
1. Confirm the **case IDs** (e.g., H019412021, H019412025)
2. Check the **tracking/assignment sheet** for the cases
3. Verify in SurveyCTO server whether the cases are assigned to the correct field officer
4. If cases need to be reopened or reassigned → Senior Research Associate handles via SurveyCTO server

### 6.4 Form Version Issues

**Scenario**: Field officer is using an outdated form version or experiencing form errors.

**Steps**:
1. Field officer should go to **"Get Blank Form"** in SurveyCTO Collect
2. Download the latest version of all forms (HH and ICM)
3. Verify version numbers match the current versions announced on Discord
4. If errors persist → Take a screenshot, change language to English, share with SFO/FC → escalate to SRA/RA

---

## 7. SurveyCTO Protocols

### 7.1 Daily Routine

1. **Start of day**: Get Blank Forms (or as instructed) — always check the version number
2. **Before each interview**: Ensure you have the correct and latest form version
3. **During interview**: Save frequently to update recovery points
4. **After interview**: Mark as finalized, verify all responses, submit when internet is available
5. **End of day**: Submit all finalized forms; charge tablet

### 7.2 Form Functions

| Function | Description |
|----------|-------------|
| **Save** | Saves responses as you go; updates recovery point for crashed forms |
| **Language** | Toggle between English, Hiligaynon, Kinaray-a |
| **Validate** | Redirects to fields that are invalid/required; form must be valid to submit |
| **Comments** | Use to record responses that need further checking (within SurveyCTO Collect) |

### 7.3 Data Entry Types

| Type | Description |
|------|-------------|
| **Text** | Free text entry |
| **Select one** | Round option buttons — pick only one |
| **Select multiple** | Square checkboxes — pick one or more |
| **Integer** | Whole numbers only |
| **Date** | Date picker |
| **Buttons** | Special codes: Don't Know (-999), Refuse to Answer (-888) |

### 7.4 Constraints

- **Hard constraint**: Cannot proceed to the next question until corrected
- **Soft constraint**: Warning/double-check, can proceed after confirmation
- **Report immediately** if constraint errors seem incorrect

### 7.5 Troubleshooting

| Issue | Solution |
|-------|---------|
| **Form crashed, not saved** | Main page → 3 dots → "Resumed Crashed Form" → select matching CaseID row → check saved responses and resume |
| **Programming issue / error popup** | Screenshot the error → share with SFO/FC → SFO/FC shares with SRA/RA |
| **Tablet slow** | Be patient; occasional lag is normal. If persistent, flag to SFO/FC |
| **Question skipped without response** | Change to English → screenshot → share with SFO/FC → escalate to SRA/RA |
| **Skip pattern error** | Change to English → screenshot → share with SFO/FC → escalate to SRA/RA |
| **Tablet won't turn on** | May need ~25 minutes of charging if fully drained |
| **Touchscreen misaligned** | Restart tablet |

---

## 8. Survey Module Quick Reference

### 8.1 Household Roster

- Begin with head of household (household decides who this is)
- Preload baseline roster → confirm current members → note departures → add new members
- Record: name, gender, age, relationship, education
- Non-residents: away ≥3 months (18+)
- Verify gender; no N/A for middle names

### 8.2 Consumption

- **Food & beverages**: Last 7 days (rice, meat, vegetables, alcohol, tobacco)
- **PPI items**: Last 6 months (potatoes, tocino, tapa, etc.)
- **Non-durable goods**: Last 30 days (soap, fuel, transport)
- **Durable goods**: Last 12 months (furniture, appliances)
- Encourage estimates; clarify units (kilos vs. sacks vs. gantang)
- Double-check large amounts; offer breaks if respondent fatigues

### 8.3 Income & Labor

- **Paid work screening**: Last 30 days, any paid work? (residents 13+)
- Classify as **agricultural** or **non-agricultural** employment
- Record: job names (be specific — "farm laborer" not just "laborer"), hours, days, pay schedule, amount
- **Unearned income**: Residents 6+ — remittances, government support (4Ps), pensions, gifts (last 12 months)
- **Key distinction**: Employment = paid by someone else; Business = work for themselves

### 8.4 Agriculture (Recall: Since July 2024)

- **Crops/Plots**: Number of plots, size, crops grown, production, revenue, costs
- **Livestock**: Types owned/raised, quantity, sales, expenses, feed costs
- **Poultry**: Types owned/raised, quantity, sales, expenses, feed costs
- **Fishing**: Catch, sales, costs, revenue
- **Forestry**: Tree planting, products, hunting, revenue
- Co-ownership: Clarify amounts for household's share only
- For current count questions (lv_total_own, pltry_total_own): Enter **0** if all sold/died — record what happened

### 8.5 Non-Agricultural Business

- Any income-generating activity NOT classified as agriculture
- Examples: sari-sari store, carpentry, tricycle business, etc.
- One person can own a business AND be employed elsewhere
- Record: operations, profits, ownership, time spent

### 8.6 Assets

- Categories: housing, land, vehicles, equipment, furniture, appliances
- For items on **installment**: report amount paid so far (not full loan value) for "how much did you pay"; report full current value for "selling value"
- **Pawned items**: No longer owned → do not report as asset
- **Land**: Does NOT include cultivated land (covered in agriculture)
- **Cell phones** ≠ wireless telephones (SIM card distinction)
- Housing construction, roof, floor: **Observe, do not ask**

### 8.7 Health & Household Vulnerability

- **Health expenses**: Medical products, outpatient, inpatient (last 12 months) — household aggregate, exclude insurance-covered amounts
- **Food security**: 8 questions on difficulty obtaining food due to lack of resources (last 12 months)
- **Water insecurity**: 12 questions; response scale: Never (0), Rarely (1–2), Sometimes (3–10), Often (11–20), Always (20+) times per year
- **Shocks**: Natural disasters, deaths, theft; select all experienced; coping strategies (up to 3 in order of importance); if shock happened multiple times, ask about most recent

### 8.8 Housing Characteristics

- Observe and record: wall material, roof material, floor material
- Ask about: ownership, lighting, water source, toilet facilities
- If multiple materials → select **main/most used**
- If multiple utilities → select **most commonly used by most members**
- Housing unit = one lived in for >3 months or intended >3 months

### 8.9 Financial Inclusion — Savings

- Does household have savings? Where kept?
- For each method: owner, amount, deposits, withdrawals, interest rate
- Enter **0** if no deposits/withdrawals/interest in last 12 months
- "Owner" = person with decision-making power over savings

### 8.10 ICM Business Module

- **Only for ICM program participants**
- Confirm participation, grant receipt, grant usage
- Identify ICM business from all household IGAs listed in HH modules
- Classify: business sector + ICM business type
- Identify if business is: new (started after grant), existing (expanded with grant), or discontinued (restarted with grant)
- Reverification questions: asked if respondent differs from HH module respondent
- **Group dynamics** questions: only for participants who reported running a group business

---

## 9. RCT Integrity Rules (for all field staff)

### 9.1 Neutrality

- **NEVER** reveal treatment/control status
- **NEVER** compare grant sizes between households or communities
- **NEVER** express surprise, approval, or disapproval about answers
- Interview as if you don't know the household's assignment

### 9.2 Handling Tough Questions from Respondents

| Question | Suggested Response |
|----------|-------------------|
| *"Why didn't I receive a cash grant/training?"* | "Different barangays were selected randomly to help us learn what works. We value your time and answers equally, regardless of whether you received the grant or not." |
| *"Will I get the grant/training later?"* | "We can't promise future programs. Today we are only doing the survey." |
| *"What should I do to qualify next time?"* | "There is no application process for this research. No one knows if you will receive the grant or not; the process is random." |
| *"You already interviewed me, why again?"* | "This is a follow-up survey. We are collecting updated information to understand how things have changed over time, which helps improve future programs." |
| *"ICM pastors collected names but never returned. Why should we trust you?"* | "We understand your frustration. IPA is a research organization conducting a survey to understand livelihoods. Your participation is voluntary and greatly appreciated." |

### 9.3 Consistency

- Ask questions **exactly as written** in the form
- Same wording, probes, and order for all respondents
- Use approved translations (Hiligaynon, Kinaray-a)

### 9.4 No Spillovers

- Do not share program information across households or communities
- Do not discuss one household's answers with another

---

## 10. Informed Consent Key Points

| Element | Details |
|---------|---------|
| **Organization** | IPA is a non-profit research organization (not program delivery or charity) |
| **Purpose** | Follow-up survey to understand livelihoods and program impact |
| **Study versions** | Households randomly assigned with 25% chance per version; neither respondent nor researcher chose |
| **Duration** | ~1 hour 15 minutes |
| **Content** | Household information, consumption, agriculture, non-agricultural businesses |
| **Compensation** | 100 PHP worth of soap after completion |
| **Voluntary** | Participation is completely voluntary; can skip questions or stop anytime; no penalty |
| **Confidentiality** | Answers accessible only to research team and IPA oversight; data anonymized when no longer needed; no identifying information in publications |
| **Permissions** | Consent to: interview, audio recording (QC), GPS coordinates, PII sharing for future studies |
| **Risks** | Some questions may cause discomfort; free to decline |

---

## 11. Interview Best Practices

### 11.1 Probing Techniques

- **Anchoring**: "Since the last market day (Saturday), on which days did you sell?"
- **Decomposition**: "Let's go day by day — about how much did you spend on rice each day?"
- **Bounding**: "Just to check, was that in July or earlier?"
- **Estimation**: "If the exact amount is hard, is it closer to ₱100, ₱300, or ₱500?"
- **Verification**: "I'll repeat what I heard and you can correct me…"

### 11.2 Probing Dos and Don'ts

| ✅ Do | ❌ Don't |
|------|---------|
| Use "Anything else?" | Lead: "Did you spend around ₱500?" |
| "Walk me through last week day by day" | Add examples that narrow meaning |
| Convert to consistent units and note which unit respondent used | Combine concepts in one probe (no double-barrel questions) |
| Allow quiet thinking time | Rush the respondent |

### 11.3 Encoding Rules

- Every question requires an answer
- **Don't Know (-999)**: Respondent genuinely doesn't know, even after consulting other members
- **Refuse to Answer (-888)**: Respondent explicitly refused
- **Other, specify**: Type answers in ENGLISH; try to match existing choices first
- Choice lists get updated → always download latest form version
- Blue text = enumerator instructions, NOT read aloud
- Use "Comments" in SurveyCTO for responses needing further checking

### 11.4 Handling "Don't Know" and "Refuse"

- Try to understand root cause: doesn't understand the question? concerned about "correct" answer? worried about confidentiality?
- Probe before accepting DK/Refuse — we don't learn anything from these responses
- Never pressure; accept gracefully after probing

### 11.5 Handling Objections

| Concern | Response |
|---------|---------|
| "I'm not feeling well" | "I understand. I will come back later." |
| "My house is too messy" | "No problem. We can do the survey right here, or I can come back later." |
| "How did you get my address?" | "We collected your data when you agreed to participate last year. We also coordinated with the barangay." |
| "My opinions don't matter" | "Your opinion represents many others like you and contributes to improving programs." |
| "I'm too busy" | "The interview takes about 1–1.5 hours. We can adjust to your schedule." |
| "Surveys are a waste of time" | "This survey helps understand livelihoods so programs can be improved. It's a chance to contribute." |

---

## 12. Personally Identifiable Information (PII) Protection

### 12.1 What is PII?

Any piece of information that can potentially distinguish, identify, or trace an individual — or can be combined with other data to identify someone.

### 12.2 Sensitive vs. Non-Sensitive PII

- **Sensitive**: Could result in substantial harm if disclosed (requires strict protection)
- **Non-sensitive**: Lower risk individually, but can pose risks when combined with other data

### 12.3 Safeguarding Rules

- **DO**: Use SurveyCTO encryption; keep tablets secure; store equipment safely overnight
- **DON'T**: Share respondent information outside IPA; write household roster on paper; let non-IPA personnel see collected data; carry large sums of cash
- SurveyCTO encrypts data so that even if hacked, individuals cannot be identified

---

## 13. Safety & Security Protocols

### 13.1 General Safety

- FOs should **never be in a barangay alone** (buddy system)
- Refrain from surveying respondents who are drunk
- Initial coordination with barangays / local guide / BHW or kagawad
- Advance coordination with PNP for awareness of field staff presence
- Always carry: ID, uniform, required documents (coordination letters, endorsements)

### 13.2 Risk Management

| Risk | Protocol |
|------|----------|
| **Traffic accident** | Helmets mandatory; no travel on unsafe roads during rain; immediate reporting |
| **Theft** | Be discreet with tablets/equipment; carry small cash; return equipment after fieldwork |
| **Extreme heat** | No fieldwork during hottest hours; fans available; assign closer respondents to at-risk staff |
| **Heavy rain** | No fieldwork |
| **Physical injury / dog bites** | Use first-aid kit; access barangay health center; follow reporting mechanisms |
| **Health issues** | Do not go to field if sick; masks available; evacuate barangay during endemic outbreaks (e.g., dengue) |
| **Reputational risks** | Always have ID, uniform, documents; treat people with respect; FC/FM resolve in person if needed |
| **Safeguarding** | Report suspected abuse/harassment to HR: hr-philippines@poverty-action.org |

### 13.3 Crisis Management

1. Validate information from reliable source → report to immediate supervisor via SMS/call/email
2. Refrain from going to affected areas → stay in station until clearance from local authorities
3. FC prepares re-deployment plan and issues order to proceed
4. **Never ride or use military vehicles**

---

## 14. Communication & Conduct

- Keep device charged and on at all times
- Respond to calls/messages from supervisors promptly
- Be polite, respectful, and professional
- Be open to directions, advice, and criticism
- Be honest — immediately raise issues and ask questions
- **No smoking or alcohol** during work hours
- Remain neutral
- Wear uniforms, IDs; avoid slippers (unless trekking), shorts, sleeveless tops, tattered jeans

### 14.1 Escalation Protocol

| Issue Type | Step 1 | Step 2 | Step 3 |
|------------|--------|--------|--------|
| **Field or finance** | Report to supervisor | If no resolution in 2 days → report to supervisor's supervisor | No retaliation for issues raised |
| **Harassment** | Directly report to RA or fill out anonymous form | — | — |
| **Survey programming error** | Screenshot (English) → share with SFO/FC | SFO/FC shares with SRA/RA | — |

---

## 15. Productivity

- **Target**: 3.5 surveys per day per FO (21 surveys per week)
- Tracked via [Google Sheets Productivity Tracker](https://docs.google.com/spreadsheets/d/17T2bDbSg2Dh_2BYNkD79Nxqftfsh3OFRlUlX8_Vq7Jo/edit?gid=1057006547#gid=1057006547)

---

## 16. Field Teams & Deployment

### 16.1 Team Structure

| FC | Area | Teams | FOs |
|----|------|-------|-----|
| **FC 1 — Elsan** | Iloilo (41 brgys) | Team A, Team B | 7 FOs |
| **FC 2 — Mariecris** | Antique + Iloilo (41 brgys total) | Team C, Team D | 7 FOs |
| **FC 3 — Kiera** | Aklan + Capiz (38 brgys) | Team E, Team F | 6 FOs |

### 16.2 Team Rosters

**Team A** (FC Elsan): Mark Lorens Mendoza Gilongo, Jenny Lou Toles Estacio, Mariel Del Rio, Rolando Bandiola Jr.

**Team B** (FC Elsan): Elenita Gicos De La Peña, Wellyn Grace Alaban Parcia, Annalou Empanado Encontro

**Team C** (FC Mariecris): Trixie Marie Jardeleza Saber, Marielle Kaye Ignacio Alonzo, Franz Reoben Posadas Geneblaza, Rosevil Tayo Desamparado

**Team D** (FC Mariecris): Jemma Marie Tillo, Adrian Montecastro Ferrer, Mark Daniel Balagao Benson

**Team E** (FC Kiera): Ramie Dela Cruz De Pedro Jr., Marvin Mondia, Janet Villanueva Serafica

**Team F** (FC Kiera): Mary May Aspela Fuentes, Mary Jean Villaflor, Aila Gregorio Eli

### 16.3 Distribution

| Province | Barangays (Phase A) |
|----------|-------------------|
| Aklan | 16 |
| Antique | 25 |
| Capiz | 22 |
| Iloilo | 57 |
| **Total** | **120** |

---

## 17. Finance Protocols

- **Lump Sum Allowances**: Upload request + signed attendance sheet to Box folder (Project Lump-sum Allowances)
- Attendance sheet must reflect correct duration dates
- Submit on **first day** of allowance request duration
- Finance processing: **Every Monday and Thursday**
- Amounts not on the standard table require prior approval from Budget Holder

### 17.1 Standard Allowances

| Staff | Comm Allowance | Per Diem | Transport | Accommodation |
|-------|---------------|----------|-----------|---------------|
| **FC** | ₱100/day | ₱600/day | ₱350/day | ₱600/day |
| **FO** | ₱100/day | ₱600/day | ₱250/day | ₱600/day |

---

## 18. Key Definitions Quick Reference

| Term | Definition |
|------|-----------|
| **Household** | All people who live together and share food preparation/consumption |
| **Resident member** | Lives in HH or away <3 months |
| **Non-resident member** | Away ≥3 months for work/school (18+) |
| **Head of household** | Designated by household; must currently reside there |
| **Most knowledgeable respondent** | Next best person to answer HH survey if original respondent unavailable |
| **ICM participant** | Household member who participated in the ICM Transform program |
| **Mop-up** | Follow-up visits to complete remaining/incomplete cases |
| **Agricultural employment** | Paid work for someone else in agriculture/forestry/fishing |
| **Non-agricultural employment** | Paid work for someone else outside agriculture |
| **Agricultural business** | Self-owned farming, livestock, poultry, fishing, forestry |
| **Non-agricultural business** | Self-owned income-generating activity outside agriculture |
| **PPI** | Progress out of Poverty Index (standard poverty measurement) |
| **Hard constraint** | SurveyCTO validation that blocks proceeding |
| **Soft constraint** | SurveyCTO warning that allows proceeding after confirmation |
| **Pull data** | SurveyCTO feature that retrieves preloaded data (e.g., names from baseline) |