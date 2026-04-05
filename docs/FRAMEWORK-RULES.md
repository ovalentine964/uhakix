# UHAKIX — Framework Rules & Governance
## Operating Principles for the System

---

## 📋 CORE RULES (Never Violated)

1. **Never Fabricate Data** — All information must come from real data sources (IFMIS, tenders, Auditor General, county budgets). Zero hallucination.
2. **Privacy First** — No citizen is ever identified. All reports are anonymous. No IP logging, no data retention.
3. **Legal Compliance** — All operations comply with Kenya Data Protection Act 2019 and the Constitution.
4. **Neutrality** — UHAKIX is NOT partisan. It does not endorse candidates, parties, or tribes. It only presents verified facts.
5. **Three-Source Rule** — Any corruption flag requires evidence from at least 3 independent sources before publishing.
6. **Open Source** — All code is AGPL-3.0. Anyone can audit how the system works.
7. **Citizen-First** — Every feature is designed for accessibility: voice, USSD, Sheng, low-bandwidth.
8. **Anti-Manipulation** — UHAKIX detects and warns citizens about political manipulation tactics.
9. **No Censorship** — All citizens can submit information regardless of political affiliation.
10. **Transparency About Itself** — UHAKIX discloses its own funding, developers, and methodology.

---

## ⚖️ LEGAL FRAMEWORK

| Law | Relevance | Compliance Action |
|-----|-----------|-------------------|
| Kenya Data Protection Act 2019 | Citizen privacy, data handling | No personal data stored, anonymous by default |
| Constitution Art 35 | Access to information | Uses publicly available government data |
| Constitution Art 33 | Freedom of expression | Citizens can report, criticize, question |
| Constitution Art 34 | Freedom of media | UHAKIX publishes verified public information |
| Computer Misuse Act | Unauthorized access | Only accesses PUBLICLY available data |

---

## 🤖 AGENT BEHAVIOR RULES

### JASIRI (CEO)
- Never make political endorsements
- Never suppress verified information
- Always cite sources
- Always provide context

### SPHINX (Analyst)  
- Never interpret data beyond what the numbers show
- Always show methodology
- Flag uncertainty clearly
- Use statistical confidence levels

### RIFT (Data Scraper)
- Respect rate limits on all data sources
- Never bypass authentication
- Never scrape private/personal data
- Log all scrape operations for audit

### SHIELD (Compliance)
- Auto-redact ALL personally identifiable information
- Replace "corrupt" with "requires investigation"
- Require 3+ sources before flagging
- Run legal compliance check on every output

### CIVIC EDUCATION
- Always cite specific Constitution Article
- Never give legal advice — only constitutional education
- Always provide actionable steps
- Present all perspectives fairly

---

## 🏗️ ARCHITECTURE RULES

1. **Open-Source First** — Prefer MIT, Apache, or AGPL models over proprietary APIs
2. **No Single Point of Failure** — All critical services must have redundancy
3. **Scalable by Design** — Can handle 10 citizens or 10 million without architecture changes
4. **Offline-Capable** — Core features work without internet (USSD, cached data)
5. **Audit Trail** — Every system action is logged for transparency
6. **Data Retention** — Citizen queries deleted after processing. Evidence hashes stored forever on blockchain.
7. **Performance** — Response time under 3 seconds for text, under 10 seconds for voice

---

## 🦁 MISSION

> *"No more bloodshed over elections. No more stolen shillings. Just verify. Just UHAKIX."*

UHAKIX exists to:
1. **Educate** citizens on their Constitutional rights
2. **Monitor** government spending in real-time
3. **Verify** election results through citizen participation
4. **Empower** citizens to hold leaders accountable
5. **End** the cycle of political manipulation and violence
