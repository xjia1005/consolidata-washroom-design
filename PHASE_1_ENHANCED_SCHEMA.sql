-- ENHANCED PHASE 1: MULTI-JURISDICTIONAL BUILDING CODE SCHEMA
-- Supports automatic code integration and global scalability

-- 1. JURISDICTION MANAGEMENT
CREATE TABLE jurisdictions (
    id SERIAL PRIMARY KEY,
    jurisdiction_code VARCHAR(10) UNIQUE NOT NULL, -- 'NBC', 'AB', 'ON', 'BC', 'IBC', 'UK'
    jurisdiction_name VARCHAR(255) NOT NULL, -- 'National Building Code of Canada'
    country_code VARCHAR(3), -- 'CAN', 'USA', 'GBR'
    region_code VARCHAR(10), -- 'Alberta', 'Ontario', 'California'
    code_version VARCHAR(50), -- '2020', '2015 with Alberta amendments'
    effective_date DATE,
    superseded_date DATE,
    authority_website VARCHAR(500),
    auto_detect_enabled BOOLEAN DEFAULT TRUE,
    priority_order INTEGER DEFAULT 50, -- For conflict resolution
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. CODE SECTION MAPPING (Handles different numbering systems)
CREATE TABLE code_sections (
    id SERIAL PRIMARY KEY,
    jurisdiction_id INTEGER REFERENCES jurisdictions(id),
    section_identifier VARCHAR(100) NOT NULL, -- '3.7.2', 'Chapter 4.1.3', 'Part B.2'
    section_title VARCHAR(500),
    section_content TEXT,
    parent_section_id INTEGER REFERENCES code_sections(id),
    section_level INTEGER, -- 1=Chapter, 2=Section, 3=Subsection
    applies_to_building_types TEXT[], -- ['office', 'school', 'assembly']
    effective_date DATE,
    superseded_date DATE,
    original_document_reference VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. FLEXIBLE BUILDING CODE RULES ENGINE
CREATE TABLE building_code_rules (
    id SERIAL PRIMARY KEY,
    jurisdiction_id INTEGER REFERENCES jurisdictions(id),
    rule_uid VARCHAR(255) UNIQUE NOT NULL, -- 'NBC_3.7.2_TOILET_COUNT_OFFICE'
    rule_type VARCHAR(50) NOT NULL, -- 'fixture_count', 'clearance', 'accessibility'
    rule_category VARCHAR(50), -- 'toilet', 'sink', 'urinal', 'accessibility'
    
    -- Flexible targeting
    building_types TEXT[], -- ['office', 'school'] or ['*'] for all
    occupancy_classes TEXT[], -- ['A1', 'B', 'E'] or NULL for all
    occupancy_range_min INTEGER, -- Applies to buildings with ≥ X people
    occupancy_range_max INTEGER, -- Applies to buildings with ≤ X people
    
    -- Rule Logic (JSON for maximum flexibility)
    condition_logic JSONB, -- When this rule applies
    calculation_formula JSONB, -- How to calculate requirements
    output_mapping JSONB, -- What the result represents
    
    -- Multi-language support
    rule_description_en TEXT,
    rule_description_fr TEXT, -- For Canadian bilingual requirements
    
    -- Metadata
    code_section_id INTEGER REFERENCES code_sections(id),
    priority INTEGER DEFAULT 50,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. CALCULATION FORMULAS (Reusable across jurisdictions)
CREATE TABLE calculation_formulas (
    id SERIAL PRIMARY KEY,
    formula_name VARCHAR(255) NOT NULL,
    formula_category VARCHAR(50), -- 'fixture_count', 'area_requirement'
    
    -- Formula definition
    input_parameters JSONB, -- {"male_occupancy": "integer", "building_type": "string"}
    formula_expression TEXT, -- "CEIL(male_occupancy / divisor)"
    constants JSONB, -- {"divisor": {"office": 75, "school": 100}}
    
    -- Multi-jurisdiction compatibility
    jurisdiction_variations JSONB, -- Override constants per jurisdiction
    unit_system VARCHAR(10) DEFAULT 'metric', -- 'metric', 'imperial'
    
    -- Usage examples for testing
    example_inputs JSONB,
    example_outputs JSONB,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. USER LOCATION & CODE DETECTION
CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE,
    user_ip_address INET,
    detected_country VARCHAR(3), -- From IP geolocation
    detected_region VARCHAR(100),
    detected_jurisdiction_id INTEGER REFERENCES jurisdictions(id),
    
    -- User preferences (override detection)
    selected_jurisdiction_id INTEGER REFERENCES jurisdictions(id),
    user_selected_override BOOLEAN DEFAULT FALSE,
    
    -- Session metadata
    user_agent TEXT,
    language_preference VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. AUTOMATED CODE IMPORT TRACKING
CREATE TABLE code_import_jobs (
    id SERIAL PRIMARY KEY,
    jurisdiction_id INTEGER REFERENCES jurisdictions(id),
    import_source VARCHAR(255), -- 'manual', 'pdf_parser', 'api_sync', 'web_scraper'
    source_document_url VARCHAR(500),
    source_document_hash VARCHAR(255), -- To detect changes
    
    -- Import results
    import_status VARCHAR(50), -- 'pending', 'processing', 'completed', 'failed'
    sections_imported INTEGER DEFAULT 0,
    rules_imported INTEGER DEFAULT 0,
    formulas_imported INTEGER DEFAULT 0,
    error_log TEXT,
    
    -- Processing metadata
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    next_check_date TIMESTAMP, -- For automatic updates
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. ENHANCED USER INPUTS (Multi-jurisdiction support)
ALTER TABLE user_inputs ADD COLUMN IF NOT EXISTS session_id VARCHAR(255);
ALTER TABLE user_inputs ADD COLUMN IF NOT EXISTS selected_jurisdiction_id INTEGER REFERENCES jurisdictions(id);
ALTER TABLE user_inputs ADD COLUMN IF NOT EXISTS detected_jurisdiction_id INTEGER REFERENCES jurisdictions(id);
ALTER TABLE user_inputs ADD COLUMN IF NOT EXISTS jurisdiction_override_reason TEXT;
ALTER TABLE user_inputs ADD COLUMN IF NOT EXISTS language_preference VARCHAR(10) DEFAULT 'en';

-- 8. ENHANCED CALCULATED REQUIREMENTS (Multi-jurisdiction results)
CREATE TABLE calculated_requirements (
    id SERIAL PRIMARY KEY,
    user_input_id INTEGER REFERENCES user_inputs(id),
    session_id VARCHAR(255),
    jurisdiction_id INTEGER REFERENCES jurisdictions(id),
    
    requirement_type VARCHAR(50), -- 'fixtures', 'space', 'accessibility'
    calculated_values JSONB, -- The calculated fixture counts/requirements
    applied_rules JSONB, -- Which rules were used with their UIDs
    applied_formulas JSONB, -- Which formulas were used
    
    -- Multi-jurisdiction comparison
    alternative_jurisdictions JSONB, -- Results if different codes were applied
    jurisdiction_differences JSONB, -- Key differences between codes
    
    -- Validation & confidence
    confidence_score DECIMAL(3,2), -- 0.00-1.00 confidence in calculation
    validation_notes TEXT,
    requires_human_review BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 9. JURISDICTION-SPECIFIC OVERRIDES
CREATE TABLE jurisdiction_overrides (
    id SERIAL PRIMARY KEY,
    base_jurisdiction_id INTEGER REFERENCES jurisdictions(id),
    override_jurisdiction_id INTEGER REFERENCES jurisdictions(id),
    
    -- What's being overridden
    override_type VARCHAR(50), -- 'formula_constant', 'rule_addition', 'rule_modification'
    target_rule_uid VARCHAR(255),
    override_data JSONB,
    
    -- Why this override exists
    override_reason TEXT,
    legal_reference VARCHAR(500),
    
    effective_date DATE,
    superseded_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 10. INDEXES FOR PERFORMANCE
CREATE INDEX idx_jurisdictions_code ON jurisdictions(jurisdiction_code);
CREATE INDEX idx_jurisdictions_country_region ON jurisdictions(country_code, region_code);
CREATE INDEX idx_code_sections_jurisdiction ON code_sections(jurisdiction_id);
CREATE INDEX idx_code_sections_identifier ON code_sections(section_identifier);
CREATE INDEX idx_building_code_rules_jurisdiction ON building_code_rules(jurisdiction_id);
CREATE INDEX idx_building_code_rules_type ON building_code_rules(rule_type);
CREATE INDEX idx_building_code_rules_building_types ON building_code_rules USING GIN (building_types);
CREATE INDEX idx_user_sessions_ip ON user_sessions(user_ip_address);
CREATE INDEX idx_user_sessions_jurisdiction ON user_sessions(detected_jurisdiction_id);
CREATE INDEX idx_calculated_requirements_jurisdiction ON calculated_requirements(jurisdiction_id);

-- Sample data for testing multi-jurisdiction support
INSERT INTO jurisdictions (jurisdiction_code, jurisdiction_name, country_code, region_code, code_version, effective_date) VALUES 
('NBC', 'National Building Code of Canada', 'CAN', NULL, '2020', '2020-12-01'),
('AB', 'Alberta Building Code', 'CAN', 'Alberta', '2019 (based on NBC 2015)', '2019-05-01'),
('ON', 'Ontario Building Code', 'CAN', 'Ontario', 'O. Reg. 332/12', '2012-12-31'),
('BC', 'British Columbia Building Code', 'CAN', 'British Columbia', '2018', '2018-12-20'),
('IBC', 'International Building Code', 'USA', NULL, '2021', '2021-01-01'),
('ADA', 'Americans with Disabilities Act', 'USA', NULL, '2010 Standards', '2012-03-15'); 