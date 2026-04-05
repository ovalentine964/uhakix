-- ── PostgreSQL Init Script ─────────────────────────────────
-- Creates required tables and indexes for UJUZIO

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Entities
CREATE TABLE IF NOT EXISTS entities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    entity_type VARCHAR(50) NOT NULL CHECK (entity_type IN ('person', 'company', 'ministry', 'county', 'department', 'parliament')),
    registration_number VARCHAR(100),
    description TEXT,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_entities_name_trgm ON entities USING gin (name gin_trgm_ops);
CREATE INDEX idx_entities_type ON entities (entity_type);
CREATE INDEX idx_entities_status ON entities (status);

-- Transactions
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source VARCHAR(50) NOT NULL,
    ifmis_code VARCHAR(100),
    ministry_id UUID REFERENCES entities(id),
    department_id UUID REFERENCES entities(id),
    county_id UUID REFERENCES entities(id),
    vendor_id UUID REFERENCES entities(id),
    amount_kes DECIMAL(18, 2) NOT NULL,
    purpose TEXT,
    transaction_date DATE NOT NULL,
    fiscal_year VARCHAR(9),
    data_provenance JSONB,
    blockhain_hash VARCHAR(66),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_transactions_date ON transactions (transaction_date);
CREATE INDEX idx_transactions_amount ON transactions (amount_kes);
CREATE INDEX idx_transactions_vendor ON transactions (vendor_id);
CREATE INDEX idx_transactions_ministry ON transactions (ministry_id);

-- Tenders
CREATE TABLE IF NOT EXISTS tenders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    reference_number VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    ministry_id UUID REFERENCES entities(id),
    county_id UUID REFERENCES entities(id),
    estimated_cost_kes DECIMAL(18, 2),
    awarded_amount_kes DECIMAL(18, 2),
    winner_id UUID REFERENCES entities(id),
    status VARCHAR(20) CHECK (status IN ('open', 'awarded', 'cancelled', 'completed')),
    publication_date DATE,
    closing_date DATE,
    award_date DATE,
    source_url VARCHAR(500),
    data_provenance JSONB,
    blockhain_hash VARCHAR(66),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_tenders_status ON tenders (status);
CREATE INDEX idx_tenders_ministry ON tenders (ministry_id);
CREATE INDEX idx_tenders_awarded ON tenders (awarded_amount_kes);

-- Budgets
CREATE TABLE IF NOT EXISTS budgets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_id UUID REFERENCES entities(id),
    fiscal_year VARCHAR(9) NOT NULL,
    allocated_kes DECIMAL(18, 2) NOT NULL,
    spent_kes DECIMAL(18, 2) DEFAULT 0,
    variance_pct DECIMAL(5, 2),
    source VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_budgets_entity ON budgets (entity_id);
CREATE INDEX idx_budgets_year ON budgets (fiscal_year);

-- Election Data
CREATE TABLE IF NOT EXISTS polling_stations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    constituency VARCHAR(100) NOT NULL,
    county VARCHAR(100) NOT NULL,
    registered_voters INTEGER,
    latitude DECIMAL(10, 6),
    longitude DECIMAL(10, 6),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_stations_constituency ON polling_stations (constituency);
CREATE INDEX idx_stations_county ON polling_stations (county);

CREATE TABLE IF NOT EXISTS form_34a_submissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    submission_id VARCHAR(100) UNIQUE NOT NULL,
    station_id UUID REFERENCES polling_stations(id),
    image_hash VARCHAR(64) NOT NULL,
    image_url VARCHAR(500),
    extracted_data JSONB,
    verification_result JSONB,
    verification_status VARCHAR(20) DEFAULT 'pending'
        CHECK (verification_status IN ('pending', 'verified', 'rejected', 'needs_review')),
    blockchain_hash VARCHAR(66),
    submitted_at TIMESTAMP DEFAULT NOW(),
    submitter_name_hash VARCHAR(64),
    verified_at TIMESTAMP
);

CREATE INDEX idx_submissions_station ON form_34a_submissions (station_id);
CREATE INDEX idx_submissions_status ON form_34a_submissions (verification_status);
CREATE INDEX idx_submissions_submitted ON form_34a_submissions (submitted_at);

-- Anomaly Reports
CREATE TABLE IF NOT EXISTS anomaly_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    anomaly_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    category VARCHAR(30) CHECK (category IN ('procurement', 'budget', 'election', 'general')),
    description TEXT NOT NULL,
    location VARCHAR(255),
    evidence_sources JSONB,
    entities_involved UUID[],
    status VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open', 'investigating', 'resolved', 'dismissed')),
    created_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP,
    resolution_notes TEXT
);

CREATE INDEX idx_anomalies_severity ON anomaly_reports (severity);
CREATE INDEX idx_anomalies_category ON anomaly_reports (category);
CREATE INDEX idx_anomalies_status ON anomaly_reports (status);

-- Audit Trail (VIGIL)
CREATE TABLE IF NOT EXISTS audit_trail (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(255) NOT NULL,
    action VARCHAR(50) NOT NULL,
    old_value JSONB,
    new_value JSONB,
    hash VARCHAR(64) NOT NULL,
    performed_by VARCHAR(50) DEFAULT 'system',
    performed_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_entity ON audit_trail (entity_type, entity_id);
CREATE INDEX idx_audit_performed_at ON audit_trail (performed_at);

-- Audit function for automatic logging
CREATE OR REPLACE FUNCTION audit_trigger_func()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_trail(entity_type, entity_id, action, old_value, new_value, hash)
    VALUES (
        TG_TABLE_NAME,
        COALESCE(NEW.id::TEXT, OLD.id::TEXT),
        TG_OP,
        row_to_json(OLD),
        row_to_json(NEW),
        encode(sha256(COALESCE(NEW.id::TEXT, OLD.id::TEXT)::bytea), 'hex')
    );
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;
