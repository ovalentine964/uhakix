# 🇰🇪 HAKIKI — Verify Everything
## Multi-Agent AI for Government Transparency & Electoral Integrity

> *"Kila shilingi ihesabiwe"* — Every single shilling must be counted.

HAKIKI ("Verify" in Swahili) is Kenya's first AI-powered, multi-agent government transparency and electoral accountability platform. Built by CoHusdex multi-agent team.

We illuminate every corrupt deal, verify every vote, track every shilling — so citizens can hold power accountable without shedding blood.

### What HAKIKI Does:

1. **🔍 Corruption Detection** — AI cross-references IFMIS, Treasury, PPRA, PPDA, Company Registry, Parliament Hansard to find suspicious connections
2. **📊 Real-Time Oversight** — Citizens track government spending in real-time via web, USSD, WhatsApp
3. **🗳️ Election Integrity** — Vote counting verification via citizen photo uploads → AI verification → blockchain immutability → live public dashboard
4. **📢 Automated Reporting** — AI generates reports for media, civil society, and parliament automatically
5. **🔗 Blockchain Evidence** — All findings immutably stored on Polygon blockchain

### Tech Stack:

- **AI Engine:** NVIDIA NIM API (multi-agent system)
- **Graph DB:** Neo4j (entity relationship mapping)
- **Blockchain:** Polygon (evidence storage, vote verification)
- **Frontend:** React + TypeScript (web), React Native (mobile)
- **Backend:** FastAPI (Python)
- **Accessibility:** Web + USSD (*XXX#) + WhatsApp bot
- **Data Lake:** PostgreSQL + Parquet

### Multi-Agent Architecture:

| Agent | Role |
|-------|------|
| **JASIRI** | Chief orchestrator and decision engine |
| **RIFT** | Government data ingestion and scraping |
| **SCOUT** | News and social monitoring for red flags |
| **SPHINX** | Cross-reference analysis, risk scoring |
| **KAZI** | Data pipeline and ETL maintenance |
| **HERALD** | Public reports, media alerts |
| **SHIELD** | Legal compliance and privacy redaction |
| **VIGIL** | System uptime monitoring |
| **ATLAS** | Cross-border data correlation |
| **LEDGER** | Financial tracking, budget vs actual |
| **POLL WITNESS** | Form 34A photo extraction |
| **VERIFY** | Election result validation |
| **COUNT** | Real-time vote counting aggregation |
| **ALERT** | Anomaly detection during elections |

### Election Verification — How It Works:

```
Citizen at polling station
   ↓
Takes photo of Form 34A (posted on wall outside)
   ↓
Uploads via USSD, WhatsApp, or Web
   ↓
VERIFY AGENT + AI checks authenticity
 - Watermarks detected
 - Official signatures matched
 - Polling station code valid
   ↓
If VERIFIED → COUNT AGENT adds to national tally
If NOT VERIFIED → Flagged for manual review
   ↓
Blockchain stores verified result hash
   ↓
Public dashboard shows real-time verified count
```

### Economic Foundation:

Built on 44 units of Economics & Statistics from Masinde Muliro University — every analysis is econometrically validated, every risk score is statistically grounded.

### Current Status:

🔄 **Architecture Phase** — Full technical design in progress

### License:

AGPL-3.0 (open source — everyone can audit our code)

---

*"No more bloodshed over elections. No more stolen shillings. Just verify. Just Hakiki."*

🇰🇪 Built for Kenya. Built for Africa. Built for the world.
