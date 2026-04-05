"""
UHAKIX Neo4j Schema Definition
Production graph schema for government entities, transactions, and connections.
"""

# ── Node Labels ──────────────────────────────────────────────
NODE_LABELS = {
    # People
    "Person": {
        "properties": ["name", "id_number_hash", "phone_hash", "title", "status", "created_at"],
        "constraints": ["name", "id_number_hash"],
        "indexes": ["name", "status"],
    },
    # Organizations
    "Company": {
        "properties": ["name", "registration_number_hash", "type", "status", "incorporated_date", "country", "created_at"],
        "constraints": ["registration_number_hash"],
        "indexes": ["name", "status", "type"],
    },
    # Government Bodies
    "Ministry": {
        "properties": ["name", "code", "parent_ministry", "established_date", "status", "created_at"],
        "constraints": ["code"],
        "indexes": ["name"],
    },
    "County": {
        "properties": ["name", "code", "governor", "budget_allocation", "population", "created_at"],
        "constraints": ["code"],
        "indexes": ["name", "code"],
    },
    "Department": {
        "properties": ["name", "code", "ministry_code", "created_at"],
        "indexes": ["name", "ministry_code"],
    },
    # Financial
    "Transaction": {
        "properties": [
            "id", "amount_kes", "date", "purpose", "ifmis_code",
            "ministry_code", "department_code", "vendor_name",
            "county_code", "source_url", "data_provenance",
            "blockchain_hash", "created_at",
        ],
        "indexes": ["amount_kes", "date", "ministry_code", "vendor_name", "county_code", "blockchain_hash"],
    },
    "Tender": {
        "properties": [
            "id", "reference_number", "title", "description",
            "estimated_cost_kes", "awarded_amount_kes", "status",
            "ministry_code", "county_code", "publication_date",
            "closing_date", "award_date", "source_url",
            "data_provenance", "created_at",
        ],
        "indexes": ["reference_number", "status", "ministry_code", "county_code", "awarded_amount_kes"],
    },
    "Contract": {
        "properties": [
            "id", "tender_reference", "contractor_name",
            "contract_value_kes", "start_date", "end_date",
            "status", "completion_pct", "created_at",
        ],
        "indexes": ["contractor_name", "status", "contract_value_kes"],
    },
    "Budget": {
        "properties": [
            "entity_code", "fiscal_year", "allocated_kes",
            "spent_kes", "variance_pct", "created_at",
        ],
        "indexes": ["entity_code", "fiscal_year"],
    },
    # Election
    "PollingStation": {
        "properties": [
            "code", "name", "constituency", "county",
            "registered_voters", "latitude", "longitude", "created_at",
        ],
        "constraints": ["code"],
        "indexes": ["name", "constituency", "county"],
    },
    "Form34A": {
        "properties": [
            "submission_id", "station_code", "station_name",
            "constituency", "county", "photo_hash",
            "presidential_votes_json", "total_votes_cast",
            "rejected_votes", "presiding_officer",
            "verification_status", "submitted_at",
            "submitter_name_hash", "blockchain_hash",
        ],
        "indexes": ["submission_id", "station_code", "verification_status", "county"],
    },
    "ElectionAlert": {
        "properties": [
            "id", "alert_type", "severity", "description",
            "location", "evidence_sources", "created_at",
            "resolved", "resolution_notes",
        ],
        "indexes": ["alert_type", "severity", "location"],
    },
    # Governance
    "GazetteNotice": {
        "properties": [
            "id", "notice_number", "title", "date",
            "description", "entities_involved", "source_url",
            "created_at",
        ],
        "indexes": ["notice_number", "date"],
    },
    # Meta
    "DataSource": {
        "properties": ["name", "url", "type", "last_sync", "status", "created_at"],
        "constraints": ["name"],
    },
}

# ── Relationship Types ───────────────────────────────────────
RELATIONSHIPS = {
    # Corporate relationships
    "DIRECTOR_OF": ["Person", "Company"],
    "SHAREHOLDER_OF": ["Person", "Company"],
    "OWNED_BY": ["Company", "Person"],

    # Government structure
    "PART_OF": ["Department", "Ministry"],
    "GOVERNS": ["County", "Ministry"],  # County govt manages county ministry

    # People ↔ Government
    "WORKS_FOR": ["Person", "Ministry"],
    "WORKS_FOR": ["Person", "Company"],
    "APPOINTED_BY": ["Person", "Ministry"],  # Gazette appointment
    "ELECTED_TO": ["Person", "Constituency"],

    # Procurement
    "AWARDED_TO": ["Tender", "Company"],
    "BID_BY": ["Tender", "Company"],
    "CONTRACTED_FOR": ["Contract", "Ministry"],
    "CONTRACTED_FOR": ["Contract", "County"],
    "CONTRACTED_TO": ["Contract", "Company"],

    # Financial flows
    "PAID_TO": ["Transaction", "Company"],
    "PAID_BY": ["Transaction", "Ministry"],
    "PAID_BY": ["Transaction", "County"],

    # Budget
    "ALLOCATED_TO": ["Budget", "County"],
    "ALLOCATED_TO": ["Budget", "Ministry"],

    # Elections
    "LOCATED_IN": ["PollingStation", "Constituency"],
    "LOCATED_IN": ["Constituency", "County"],
    "SUBMITTED_FOR": ["Form34A", "PollingStation"],
    "TRIGGERED_ALERT": ["Form34A", "ElectionAlert"],

    # Anomalies
    "FLAGGED_ON_TRANSACTION": ["ElectionAlert", "Transaction"],
    "FLAGGED_ON_TENDER": ["ElectionAlert", "Tender"],

    # Connections (SCOUT discovered)
    "SHARED_ADDRESS": ["Company", "Company"],
    "SHARED_PHONE": ["Company", "Company"],
    "SHARED_PHONE": ["Person", "Company"],
    "RELATED_ENTITY": ["Person", "Person"],
    "RELATED_ENTITY": ["Company", "Company"],
    "COMMON_DIRECTOR": ["Company", "Company"],
}


# ── Schema Creation Queries ─────────────────────────────────
def generate_create_constraints() -> list[str]:
    """Generate Neo4j Cypher queries to create constraints."""
    queries = []
    for label, info in NODE_LABELS.items():
        for prop in info.get("constraints", []):
            name = f"unique_{label.lower()}_{prop}"
            queries.append(
                f"CREATE CONSTRAINT {name} IF NOT EXISTS "
                f"FOR (n:{label}) REQUIRE n.{prop} IS UNIQUE;"
            )
    return queries


def generate_create_indexes() -> list[str]:
    """Generate Neo4j Cypher queries to create indexes."""
    queries = []
    for label, info in NODE_LABELS.items():
        for prop in info.get("indexes", []):
            name = f"idx_{label.lower()}_{prop}"
            queries.append(
                f"CREATE INDEX {name} IF NOT EXISTS "
                f"FOR (n:{label}) ON (n.{prop});"
            )
    return queries


# ── Common Queries ───────────────────────────────────────────
COMMON_QUERIES = {
    # Find all transactions for a company
    "company_transactions": """
        MATCH (c:Company {name: $company_name})
        <-[:PAID_TO]-(t:Transaction)
        RETURN t ORDER BY t.date DESC LIMIT $limit
    """,

    # Find companies connected to a person
    "person_companies": """
        MATCH (p:Person {name: $person_name})
        -[r:DIRECTOR_OF|SHAREHOLDER_OF|WORKS_FOR]->(c:Company)
        RETURN p AS person, type(r) AS relationship, c AS company
    """,

    # Find tender award patterns (same company winning many tenders)
    "tender_concentration": """
        MATCH (c:Company)<-[:AWARDED_TO]-(t:Tender)
        WITH c, count(t) AS tender_count, sum(t.awarded_amount_kes) AS total_value
        WHERE tender_count >= $min_tenders
        RETURN c.name, tender_count, total_value
        ORDER BY total_value DESC LIMIT 20
    """,

    # Budget variance by county
    "county_budget_variance": """
        MATCH (b:Budget)-[:ALLOCATED_TO]->(co:County {code: $county_code})
        WHERE b.fiscal_year = $fiscal_year
        RETURN co.name AS county, b.allocated_kes, b.spent_kes, b.variance_pct
    """,

    # Cross-reference: same directors in companies that win tenders
    "conflict_interest_pattern": """
        MATCH (p:Person)-[:DIRECTOR_OF]->(c1:Company)<-[:AWARDED_TO]-(t:Tender)
        -[:CONTRACTED_FOR]->(m:Ministry)
        MATCH (p)-[:WORKS_FOR|DIRECTOR_OF]->(c2:Company)
        WHERE c1 <> c2
        AND c2 IN [(c2)<-[:PAID_BY]-(trx) | trx]
        RETURN DISTINCT
            p.name AS person,
            c1.name AS winning_company,
            c2.name AS connected_company,
            m.name AS ministry,
            t.title AS tender_title,
            t.awarded_amount_kes AS amount
    """,

    # Election: multiple Form 34A for same station
    "form_34a_cross_verify": """
        MATCH (f:Form34A)-[:SUBMITTED_FOR]->(ps:PollingStation {code: $station_code})
        WHERE f.verification_status = 'verified'
        RETURN f.submission_id, f.presidential_votes_json,
               f.submitter_name_hash, f.submitted_at,
               f.blockchain_hash
        ORDER BY f.submitted_at
    """,

    # Election anomaly detection: turnout outliers
    "election_turnout_anomalies": """
        MATCH (f:Form34A)-[:SUBMITTED_FOR]->(ps:PollingStation)
        WHERE ps.constituency = $constituency
        WITH ps, f,
             toFloat(f.total_votes_cast) / ps.registered_voters AS turnout_rate
        WITH constituency,
             avg(turnout_rate) AS avg_turnout,
             stdev(turnout_rate) AS std_turnout
        MATCH (f:Form34A)-[:SUBMITTED_FOR]->(ps:PollingStation)
        WHERE abs(
            (toFloat(f.total_votes_cast) / ps.registered_voters) - avg_turnout
        ) > $threshold_stddev * std_turnout
        RETURN ps.name, ps.code,
               toFloat(f.total_votes_cast) / ps.registered_voters AS turnout_rate,
               avg_turnout, std_turnout
    """,
}
