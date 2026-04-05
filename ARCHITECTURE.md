# ARCHITECTURE.md — UHAKIX Data Flow & System Design

## Data Flow Diagrams

### 1. Government Data Ingestion Pipeline
```
┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
│  IFMIS           │   │  tenders.go.ke   │   │  Treasury        │
│  (transactions)  │   │  (procurement)   │   │  (allocations)   │
└────────┬─────────┘   └────────┬─────────┘   └────────┬─────────┘
         │                      │                      │
         ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SCRAPER SERVICES (Python)                     │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐       │
│  │ IFMIS  │ │Tenders │ │  COB   │ │Treasury │ │Gazette │  ...  │
│  └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘       │
└──────┼──────────┼───────────┼───────────┼──────────┼────────────┘
       │          │           │           │          │
       ▼          ▼           ▼           ▼          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATA NORMALIZATION LAYER                      │
│  • Standardize currency (KES)                                    │
│  • Standardize entity names (ministry, county, company)          │
│  • Extract structured fields from HTML/PDF                       │
│  • Deduplicate records                                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              MULTI-AGENT ANALYSIS PIPELINE                       │
│                                                                  │
│  ┌────────┐     ┌────────┐     ┌────────┐     ┌────────┐      │
│  │ JASIRI │────▶│ SPHINX │────▶│ SCOUT  │────▶│ SHIELD │      │
│  │Budget  │     │Anomaly │     │Network │     │Legal   │      │
│  │Intel   │     │Detect  │     │Mapping │     │Filter  │      │
│  └────────┘     └────────┘     └───┬────┘     └───┬────┘      │
│                                    │               │           │
│  ┌────────┐                        │               │           │
│  │  RIFT  │────────────────────────┘               │           │
│  │Procure │                                        │           │
│  │Analysis│────────────────────────────────────────┘           │
│  └────────┘                                                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
       ┌──────────────┐            ┌──────────────┐
       │   Neo4j      │            │ PostgreSQL   │
       │  (Graph DB)  │            │ (Structured  │
       │  Connections │            │  Storage)    │
       └──────┬───────┘            └──────┬───────┘
              │                           │
              └───────────┬───────────────┘
                          ▼
                   ┌──────────────┐
                   │   Redis      │
                   │  (Cache)     │
                   └──────┬───────┘
                          ▼
                   ┌──────────────┐
                   │    API       │
                   │  Endpoints   │
                   └──────────────┘
```

### 2. Election Verification Pipeline
```
Citizen                        AI Pipeline                        Blockchain
   │                                │                                 │
   │  📷 Upload Form 34A           │                                 │
   ├─────────────────────────────▶│                                 │
   │                               │                                 │
   │                               │  1. POLL WITNESS Agent          │
   │                               │     ┌─────────────────────┐     │
   │                               │     │ Vision Model (NVIDIA) │     │
   │                               │     │ OCR + Data Extract    │     │
   │                               │     │ Station code, votes,  │     │
   │                               │     │ totals, serial #      │     │
   │                               │     └──────────┬──────────┘     │
   │                               │                │                │
   │                               │  2. VERIFY Agent               │
   │                               │     ┌─────────────────────┐     │
   │                               │     │ Check: watermarks    │     │
   │                               │     │ signatures, math     │     │
   │                               │     │ consistency          │     │
   │                               │     └──────────┬──────────┘     │
   │                               │                │                │
   │                               │  3. COUNT Agent                 │
   │                               │     ┌─────────────────────┐     │
   │                               │     │ Cross-verify with    │     │
   │                               │     │ other submissions    │     │
   │                               │     │ for same station     │     │
   │                               │     │ Aggregate → median   │     │
   │                               │     └──────────┬──────────┘     │
   │                               │                │                │
   │                               │  4. ALERT Agent                 │
   │                               │     ┌─────────────────────┐     │
   │                               │     │ Check: turnout >95%  │     │
   │                               │     │ duplicate submissions│     │
   │                               │     │ timing anomalies     │     │
   │                               │     └──────────┬──────────┘     │
   │                               │                │                │
   │                               │  5. LEDGER Agent               │
   │                               │     ┌─────────────────────┐     │
   │                               │     │ SHA-256 hash of     │     │
   │                               │     │ station results     │     │
   │                               │     └──────────┬──────────┘     │
   │                               │                │                │
   │                               │                ├───────────────▶│
   │                               │                │  Store hash on │
   │                               │                │  Polygon chain │
   │                               │                │                │
   │  ✅ "Station 001 verified     │                │  Citizens can  │
   │     & recorded on-chain"      │◀───────────────┤  verify later  │
   │◀──────────────────────────────│                │                │
```

### 3. Citizen Query Flow (WhatsApp/USSD/Web)
```
Citizen                    UHAKIX Platform                 Data Sources
   │                              │                              │
   │ "How much did Health Ministry│                              │
   │  spend on road construction?"│                              │
   ├─────────────────────────────▶│                              │
   │                              │  1. KAZI routes to JASIRI    │
   │                              │                              │
   │                              │  2. JASIRI queries Neo4j +   │
   │                              │     analyzes spending data   │
   │                              │                              │
   │                              │  3. HERALD translates to     │
   │                              │     Swahili/English reply    │
   │                              │                              │
   │                              │  4. SHIELD legal review:     │
   │                              │     ✓ No accusations         │
   │                              │     ✓ 3+ sources ✓ Redacted  │
   │                              │                              │
   │ "The Ministry of Health spent│                              │
   │  KES 2.3B on road-related   │                              │
   │  projects in FY 2023/24.    │                              │
   │  Sources: IFMIS, Treasury,  │                              │
   │  Controller of Budget."     │                              │
   │◀─────────────────────────────│                              │
```

### 4. Multi-Agent Coordination
```
                    KAZI (Orchestrator)
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
         JASIRI       RIFT       SCOUT
       (Budget)   (Procurement) (Network)
              │          │          │
              └──────────┼──────────┘
                         ▼
                      SPHINX
                  (Anomaly Detection)
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
          ATLAS       SHIELD     LEDGER
         (Geographic)  (Legal)   (Blockchain)
              │          │          │
              └──────────┼──────────┘
                         ▼
                      HERALD
                  (Citizen Output)
                         │
                     VIGIL
                 (Audit Log — always)
```

## Scaling Strategy

### Phase 1: Free Tier (0-10K users)
- Heroku Free / Render Free for backend
- Neon Free for PostgreSQL
- Neo4j Aura Free (1M nodes)
- Redis Upstash Free
- AWS S3 Free Tier
- Polygon Amoy Testnet (free)
- NVIDIA NIM Free Tier

### Phase 2: Low-Cost Production (10K-100K users)
- AWS ECS Fargate (backend)
- RDS PostgreSQL (db.t3.medium)
- Neo4j Aura Professional
- AWS ElastiCache Redis
- CloudFront CDN for frontend
- Polygon Mainnet (cheap gas)

### Phase 3: Scale (100K+ users)
- Kubernetes cluster (EKS/GKE)
- Read replicas for PostgreSQL
- Neo4j Causal Cluster
- Redis Cluster
- Multi-region deployment
- Polygon mainnet + L2
