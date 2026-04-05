-- =====================================================
-- UHAKIX PostgreSQL Initialization Script
-- Creates all tables, indexes, audit triggers, and views
-- =====================================================

-- ── Extensions ────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ── Counties ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS counties (
    id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(3) NOT NULL,
    governor VARCHAR(200),
    population INTEGER,
    region VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── Politicians / Officials ───────────────────────────────
CREATE TABLE IF NOT EXISTS politicians (
    id VARCHAR(50) PRIMARY KEY DEFAULT 'pol_' || uuid_generate_v4(),
    full_name VARCHAR(200) NOT NULL,
    position VARCHAR(100),
    party VARCHAR(100),
    constituency VARCHAR(100),
    county_id VARCHAR(10) REFERENCES counties(id),
    phone_masked VARCHAR(50),
    email_masked VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active',
    declared_assets JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_politicians_name ON politicians USING GIN(to_tsvector('simple', full_name));
CREATE INDEX idx_politicians_county ON politicians(county_id);

-- ── Companies ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS companies (
    id VARCHAR(50) PRIMARY KEY DEFAULT 'co_' || uuid_generate_v4(),
    name VARCHAR(300) NOT NULL,
    registration_number VARCHAR(50) UNIQUE,
    registration_date DATE,
    status VARCHAR(30) DEFAULT 'active',
    business_type VARCHAR(100),
    address TEXT,
    county_id VARCHAR(10) REFERENCES counties(id),
    directors JSONB, -- [{name, id_number, address, appointment_date}]
    shareholders JSONB, -- [{name, shares, percentage}]
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_companies_name ON companies USING GIN(to_tsvector('simple', name));
CREATE INDEX idx_companies_status ON companies(status);

-- ── Tenders / Procurement ─────────────────────────────────
CREATE TABLE IF NOT EXISTS tenders (
    id VARCHAR(50) PRIMARY KEY DEFAULT 'tender_' || uuid_generate_v4(),
    reference_number VARCHAR(100),
    title TEXT NOT NULL,
    ministry VARCHAR(200),
    county_id VARCHAR(10) REFERENCES counties(id),
    estimated_cost_kes NUMERIC(18,2),
    awarded_amount_kes NUMERIC(18,2),
    contractor_id VARCHAR(50) REFERENCES companies(id),
    status VARCHAR(30) DEFAULT 'open', -- open, evaluated, awarded, cancelled, completed
    published_date DATE,
    closing_date DATE,
    award_date DATE,
    source VARCHAR(100),
    metadata JSONB, -- additional scraped data
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_tenders_ministry ON tenders(ministry);
CREATE INDEX idx_tenders_status ON tenders(status);
CREATE INDEX idx_tenders_cost ON tenders(awarded_amount_kes);
CREATE INDEX idx_tenders_date ON tenders(published_date);
CREATE INDEX idx_tenders_contractor ON tenders(contractor_id);

-- ── Transactions (IFMIS data) ─────────────────────────────
CREATE TABLE IF NOT EXISTS transactions (
    id VARCHAR(50) PRIMARY KEY DEFAULT 'txn_' || uuid_generate_v4(),
    ifmis_code VARCHAR(100),
    voucher_no VARCHAR(100),
    commitment_no VARCHAR(100),
    date DATE NOT NULL,
    ministry VARCHAR(200),
    department VARCHAR(200),
    amount_kes NUMERIC(18,2) NOT NULL CHECK (amount_kes >= 0),
    purpose TEXT,
    vendor VARCHAR(300),
    vendor_id VARCHAR(50) REFERENCES companies(id),
    county_id VARCHAR(10) REFERENCES counties(id),
    source VARCHAR(100),
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_transactions_date ON transactions(date);
CREATE INDEX idx_transactions_ministry ON transactions(ministry);
CREATE INDEX idx_transactions_amount ON transactions(amount_kes);
CREATE INDEX idx_transactions_vendor ON transactions(vendor);
CREATE INDEX idx_transactions_source ON transactions(source);

-- ── Election Votes (aggregated per station) ──────────────
CREATE TABLE IF NOT EXISTS votes (
    id VARCHAR(50) PRIMARY KEY DEFAULT 'vote_' || uuid_generate_v4(),
    station_code VARCHAR(50) NOT NULL,
    station_name VARCHAR(200),
    constituency VARCHAR(100),
    county_id VARCHAR(10) REFERENCES counties(id),
    registered_voters INTEGER,
    total_votes_cast INTEGER,
    rejected_votes INTEGER,
    presidential_results JSONB, -- {candidate: votes}
    submission_count INTEGER DEFAULT 1,
    form_34a_hashes TEXT[], -- image hashes of submitted forms
    blockchain_tx_hash VARCHAR(100),
    verification_status VARCHAR(30) DEFAULT 'pending', -- pending, verified, rejected
    submitted_at TIMESTAMPTZ DEFAULT NOW(),
    verified_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_votes_station ON votes(station_code);
CREATE INDEX idx_votes_constituency ON votes(constituency);
CREATE INDEX idx_votes_county ON votes(county_id);
CREATE INDEX idx_votes_status ON votes(verification_status);

-- ── Evidence / Anonymous Reports ──────────────────────────
CREATE TABLE IF NOT EXISTS evidence (
    id VARCHAR(50) PRIMARY KEY DEFAULT 'evd_' || uuid_generate_v4(),
    category VARCHAR(50) NOT NULL, -- corruption, irregularity, complaint, form34a
    title VARCHAR(300),
    description TEXT,
    location VARCHAR(200),
    entities_mentioned TEXT[],
    evidence_hash VARCHAR(100), -- SHA-256 of evidence package
    blockchain_tx_hash VARCHAR(100), -- Polygon transaction hash
    status VARCHAR(30) DEFAULT 'pending', -- pending, review, verified, rejected, published
    source_channel VARCHAR(30), -- web, whatsapp, ussd, telegram
    ip_logged BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    reviewed_at TIMESTAMPTZ,
    published_at TIMESTAMPTZ
);

CREATE INDEX idx_evidence_category ON evidence(category);
CREATE INDEX idx_evidence_status ON evidence(status);
CREATE INDEX idx_evidence_created ON evidence(created_at);

-- ── Citizen Reports / Submissions ─────────────────────────
CREATE TABLE IF NOT EXISTS reports (
    id VARCHAR(50) PRIMARY KEY DEFAULT 'rpt_' || uuid_generate_v4(),
    report_type VARCHAR(50) NOT NULL, -- form34a, corruption_tip, question
    title VARCHAR(300),
    description TEXT,
    location VARCHAR(200),
    email_masked VARCHAR(100), -- hashed, not stored in plaintext
    status VARCHAR(30) DEFAULT 'processing', -- processing, analyzed, verified, published
    pipeline_stage INTEGER DEFAULT 0,
    ai_processing_log JSONB,
    blockchain_recorded BOOLEAN DEFAULT FALSE,
    blockchain_hash VARCHAR(100),
    anonymous BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_reports_status ON reports(status);
CREATE INDEX idx_reports_type ON reports(report_type);
CREATE INDEX idx_reports_anonymous ON reports(anonymous);

-- ── Users (for staff/admins only — not citizens) ──────────
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(50) PRIMARY KEY DEFAULT 'usr_' || uuid_generate_v4(),
    full_name VARCHAR(200) NOT NULL,
    email VARCHAR(200) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(30) DEFAULT 'viewer', -- viewer, analyst, admin, super_admin
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);

-- ── Agent Activity Log ────────────────────────────────────
CREATE TABLE IF NOT EXISTS agent_activity (
    id VARCHAR(50) PRIMARY KEY DEFAULT 'act_' || uuid_generate_v4(),
    agent_name VARCHAR(50) NOT NULL,
    action VARCHAR(100) NOT NULL,
    input_data_hash VARCHAR(100),
    output_data_hash VARCHAR(100),
    model_used VARCHAR(100),
    processing_time_ms INTEGER,
    tokens_used INTEGER,
    status VARCHAR(20) DEFAULT 'success',
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_agent_activity_agent ON agent_activity(agent_name);
CREATE INDEX idx_agent_activity_created ON agent_activity(created_at);

-- ── Audit Trigger Function ────────────────────────────────
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO agent_activity (agent_name, action, output_data_hash, status)
        VALUES ('SYSTEM', TG_TABLE_NAME || '_insert', encode(digest(NEW::text, 'sha256'), 'hex'), 'success');
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO agent_activity (agent_name, action, output_data_hash, status)
        VALUES ('SYSTEM', TG_TABLE_NAME || '_update', encode(digest(NEW::text, 'sha256'), 'hex'), 'success');
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO agent_activity (agent_name, action, output_data_hash, status)
        VALUES ('SYSTEM', TG_TABLE_NAME || '_delete', encode(digest(OLD::text, 'sha256'), 'hex'), 'success');
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- ── Materialized Views ─────────────────────────────────────

-- Total spending by ministry
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_spending_by_ministry AS
SELECT
    ministry,
    COUNT(*) AS transaction_count,
    SUM(amount_kes) AS total_spent,
    AVG(amount_kes) AS avg_amount,
    MIN(date) AS earliest_transaction,
    MAX(date) AS latest_transaction
FROM transactions
GROUP BY ministry;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_ministry ON mv_spending_by_ministry(ministry);

-- Top contractors by total tender value
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_top_contractors AS
SELECT
    c.id AS company_id,
    c.name AS company_name,
    c.registration_number,
    COUNT(t.id) AS total_tenders,
    COALESCE(SUM(t.awarded_amount_kes), 0) AS total_value,
    COALESCE(MIN(t.awarded_amount_kes), 0) AS smallest_award,
    COALESCE(MAX(t.awarded_amount_kes), 0) AS largest_award,
    array_agg(DISTINCT t.ministry) AS ministries_served
FROM companies c
LEFT JOIN tenders t ON c.id = t.contractor_id
GROUP BY c.id, c.name, c.registration_number
ORDER BY total_value DESC;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_contractors ON mv_top_contractors(company_id);

-- County budget overview
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_county_budget_overview AS
SELECT
    c.id AS county_id,
    c.name AS county_name,
    c.code AS county_code,
    c.governor,
    (SELECT COUNT(*) FROM transactions t WHERE t.county_id = c.id) AS transaction_count,
    (SELECT COALESCE(SUM(t.amount_kes), 0) FROM transactions t WHERE t.county_id = c.id) AS total_tracked_spending,
    (SELECT COUNT(*) FROM tenders t WHERE t.county_id = c.id) AS tender_count,
    (SELECT COUNT(*) FROM votes v WHERE v.county_id = c.id AND v.verification_status = 'verified') AS verified_stations
FROM counties c;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_county_overview ON mv_county_budget_overview(county_id);

-- ── Insert 47 Kenyan Counties ─────────────────────────────
INSERT INTO counties (id, name, code, region) VALUES
('county_mombasa', 'Mombasa', '001', 'Coast'),
('county_kwale', 'Kwale', '002', 'Coast'),
('county_kilifi', 'Kilifi', '003', 'Coast'),
('county_tana_river', 'Tana River', '004', 'Coast'),
('county_lamu', 'Lamu', '005', 'Coast'),
('county_taita_taveta', 'Taita-Taveta', '006', 'Coast'),
('county_garissa', 'Garissa', '007', 'North Eastern'),
('county_wajir', 'Wajir', '008', 'North Eastern'),
('county_mandera', 'Mandera', '009', 'North Eastern'),
('county_marsabit', 'Marsabit', '010', 'Eastern'),
('county_isiolo', 'Isiolo', '011', 'Eastern'),
('county_meru', 'Meru', '012', 'Eastern'),
('county_tharaka_nithi', 'Tharaka-Nithi', '013', 'Eastern'),
('county_embu', 'Embu', '014', 'Eastern'),
('county_kitui', 'Kitui', '015', 'Eastern'),
('county_machakos', 'Machakos', '016', 'Eastern'),
('county_makueni', 'Makueni', '017', 'Eastern'),
('county_nyandarua', 'Nyandarua', '018', 'Central'),
('county_nyeri', 'Nyeri', '019', 'Central'),
('county_kirinyaga', 'Kirinyaga', '020', 'Central'),
('county_muranga', 'Murang''a', '021', 'Central'),
('county_kiambu', 'Kiambu', '022', 'Central'),
('county_turkana', 'Turkana', '023', 'Rift Valley'),
('county_west_pokot', 'West Pokot', '024', 'Rift Valley'),
('county_samburu', 'Samburu', '025', 'Rift Valley'),
('county_transnzoia', 'Trans-Nzoia', '026', 'Rift Valley'),
('county_uasin_gishu', 'Uasin Gishu', '027', 'Rift Valley'),
('county_elgeyo_marakwet', 'Elgeyo-Marakwet', '028', 'Rift Valley'),
('county_nandi', 'Nandi', '029', 'Rift Valley'),
('county_baringo', 'Baringo', '030', 'Rift Valley'),
('county_laikipia', 'Laikipia', '031', 'Rift Valley'),
('county_nakuru', 'Nakuru', '032', 'Rift Valley'),
('county_narok', 'Narok', '033', 'Rift Valley'),
('county_kajiado', 'Kajiado', '034', 'Rift Valley'),
('county_kericho', 'Kericho', '035', 'Rift Valley'),
('county_bomet', 'Bomet', '036', 'Rift Valley'),
('county_kakamega', 'Kakamega', '037', 'Western'),
('county_vihiga', 'Vihiga', '038', 'Western'),
('county_bungoma', 'Bungoma', '039', 'Western'),
('county_busia', 'Busia', '040', 'Western'),
('county_siaya', 'Siaya', '041', 'Nyanza'),
('county_kisumu', 'Kisumu', '042', 'Nyanza'),
('county_homa_bay', 'Homa Bay', '043', 'Nyanza'),
('county_migori', 'Migori', '044', 'Nyanza'),
('county_kisii', 'Kisii', '045', 'Nyanza'),
('county_nyamira', 'Nyamira', '046', 'Nyanza'),
('county_nairobi', 'Nairobi', '047', 'Nairobi')
ON CONFLICT (id) DO NOTHING;

-- ── Refresh materialized views ─────────────────────────────
REFRESH MATERIALIZED VIEW IF EXISTS mv_spending_by_ministry;
REFRESH MATERIALIZED VIEW IF EXISTS mv_top_contractors;
REFRESH MATERIALIZED VIEW IF EXISTS mv_county_budget_overview;
