# UHAKIX — OpenClaw Agent Skills
## Skills for the UHAKIX Multi-Agent System

These skills enable the AgentIQ agent team to power UHAKIX with AI-powered government transparency, election verification, civic education, and citizen voice interaction.

---

## Skill 1: UHAKIX Transparency Engine
**Purpose:** Monitor government spending, procurement, and tenders

### What It Does
- Scrapes IFMIS, tenders.go.ke, Controller of Budget, National Treasury
- Cross-references politicians with companies and contracts
- Detects suspicious patterns (over-invoicing, sole-source awards)
- Generates transparency reports for citizens

### Trigger Questions
- "How much did county X spend on Y?"
- "Who won this tender?"
- "Show me all contracts awarded to company X"
- "Is this project being delivered?"

### Data Sources
- `ifmis.go.ke` — Government financial transactions
- `tenders.go.ke` — Procurement portal
- `controllerofbudget.go.ke` — Budget execution reports
- National Treasury — Budget allocations
- Company Registry — CR12 directors/shareholders
- IEBC — Election results and candidate data

### Output Format
```
Project/Contract: [name]
Amount: KES [actual amount]
Contractor: [company name]
Director: [politician connection if found]
Status: [delivered / in progress / not started / suspicious]
Evidence: [links to IFMIS, tender documents]
Risk: [Low / Medium / High]
```

---

## Skill 2: UHAKIX Election Verification
**Purpose:** Real-time election result verification via citizen photo uploads

### What It Does
- Receives Form 34A/B photos from citizens
- NVIDIA Vision AI extracts numbers (candidate names, vote counts)
- VERIFY agent checks watermarks, serial numbers, station code
- COUNT agent aggregates verified votes
- BLOCKCHAIN stores hash of verified results
- ALERT agent detects anomalies (discrepancies, missing stations)

### Trigger Questions
- "Verify the results from this station"
- "Show me the vote count for my constituency"
- "Are these results legitimate?"
- "Where are the results for station X?"

### Verification Flow
```
Citizen photo → NVIDIA Vision AI extracts data
→ VERIFY checks: watermarks, signatures, station codes
→ Consensus: 3+ reports from same station = VERIFIED
→ COUNT: Aggregates to national tally
→ BLOCKCHAIN: Stores hash permanently
→ ALERT: Flags anomalies for manual review
```

---

## Skill 3: UHAKIX Civic Education
**Purpose:** Educate citizens on their Constitutional rights and political manipulation tactics

### What It Does
- Answers questions about Constitutional rights (Arts 35, 43, 47, 73-77, 201, 226)
- Detects political manipulation (48 Laws adapted for Kenyan politics)
- Provides budget literacy education
- Explains how government works
- Warns about voter manipulation tactics

### Trigger Questions
- "What are my rights as a citizen?"
- "How do I know if a politician is lying?"
- "Nipelece 48 Laws ya Power kama politician anatumia"
- "How is county budget money supposed to be spent?"
- "What should I look for in a candidate?"

### Output Format
```
🇰🇪 Civic Education Response:

Article/Topic: [specific article or law]
Summary: [plain-language explanation]
Your Rights: [bullet points]
Red Flags: [what to watch out for]
What To Do: [actionable next steps]
```

---

## Skill 4: UHAKIX Voice Interaction
**Purpose:** Enable voice-based interaction for citizens who prefer speaking over typing

### What It Does
- Speech-to-Text (Whisper large-v3): Transcribes voice notes to text
- Language Detection: Auto-detects Swahili, English, or code-switching
- Sheng Normalization: Converts common Sheng terms to standard Swahili/English
- Text-to-Speech (MMS-TTS): Converts UHAKIX responses to audio
- Works on WhatsApp, Telegram, web, and USSD

### Trigger Inputs
- Citizen voice note (WhatsApp/Telegram)
- Microphone button on web app
- Phone call (future)

### Supported Languages
| Language | STT | TTS | Notes |
|----------|-----|-----|-------|
| Kiswahili | ✅ Whisper large-v3 | ✅ MMS-TTS (swh) | Best accuracy |
| English | ✅ Whisper large-v3 | ✅ MMS-TTS (eng) | Best accuracy |
| Sheng | ⚠️ Code-switching | ❌ Not directly | Normalized via glossary |

---

## Skill 5: UHAKIX Anonymous Reporting
**Purpose:** Enable citizens to report corruption, fake projects, and governance issues securely

### What It Does
- Receives anonymous reports (text, photo, voice)
- No registration required
- No personal data stored
- Blockchain-hashes evidence permanently
- AI verifies against government data
- Generates public report (anonymized)

### Report Types
1. Fake project (money spent, no delivery)
2. Over-invoiced contract
3. Ghost worker on government payroll
4. Bribery/corruption incident
5. Service denial by government
6. Political manipulation tactic

### Verification Flow
```
Citizen report → AI analysis
→ Cross-reference with government data (IFMIS, tenders, auditor reports)
→ Verify: Does the data support the claim?
→ If verified → Publish (anonymized) + alert to media + report to EACC
→ If inconclusive → Flag for further investigation
→ If disproven → Log but do not publish
```

---

## Core Framework Rules (Never Violated)

1. **No Data Fabrication** — All information from verified sources
2. **Citizen Anonymity** — No personal data, ever
3. **Political Neutrality** — No endorsements, only facts
4. **3-Source Rule** — Corruption flag requires 3+ independent sources
5. **Legal Compliance** — Compliant with Kenya Data Protection Act 2019
6. **Open Source** — AGPL-3.0, all code auditable
7. **Anti-Manipulation** — Detects and warns about political manipulation
