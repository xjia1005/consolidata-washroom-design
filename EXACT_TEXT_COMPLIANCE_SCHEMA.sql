-- EXACT BUILDING CODE TEXT COMPLIANCE SCHEMA
-- Ensures generated checklists use exact original building code language

-- 1. ENHANCED CODE SECTIONS (Store exact original text)
DROP TABLE IF EXISTS code_sections CASCADE;
CREATE TABLE code_sections (
    id SERIAL PRIMARY KEY,
    jurisdiction_id INTEGER REFERENCES jurisdictions(id),
    
    -- Section identification
    section_identifier VARCHAR(100) NOT NULL, -- '3.7.2', 'Chapter 4.1.3', 'Part B.2'
    section_title VARCHAR(500),
    parent_section_id INTEGER REFERENCES code_sections(id),
    section_level INTEGER, -- 1=Chapter, 2=Section, 3=Subsection
    
    -- EXACT ORIGINAL TEXT (Critical for compliance)
    original_text_en TEXT NOT NULL, -- Exact English text from building code
    original_text_fr TEXT, -- Exact French text (for Canadian bilingual codes)
    original_text_other TEXT, -- Other languages as needed
    
    -- Text source verification
    source_document_title VARCHAR(500), -- "National Building Code of Canada 2020"
    source_document_page INTEGER, -- Page number in original document
    source_document_url VARCHAR(500), -- Official government URL
    source_document_hash VARCHAR(255), -- Hash of source document for integrity
    text_extraction_method VARCHAR(100), -- 'manual', 'ocr', 'api', 'copy_paste'
    text_verified_by VARCHAR(255), -- Who verified the text accuracy
    text_verified_date TIMESTAMP,
    
    -- Legal metadata
    applies_to_building_types TEXT[], -- ['office', 'school', 'assembly']
    effective_date DATE,
    superseded_date DATE,
    legal_status VARCHAR(50), -- 'active', 'superseded', 'amended'
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. EXACT TEXT FRAGMENTS (For precise referencing)
CREATE TABLE code_text_fragments (
    id SERIAL PRIMARY KEY,
    code_section_id INTEGER REFERENCES code_sections(id),
    
    -- Fragment identification
    fragment_type VARCHAR(50), -- 'requirement', 'exception', 'definition', 'table_row'
    fragment_sequence INTEGER, -- Order within the section
    
    -- EXACT TEXT
    exact_text_en TEXT NOT NULL, -- Exact fragment text
    exact_text_fr TEXT, -- French version if available
    
    -- Context and application
    applies_to_calculation BOOLEAN DEFAULT FALSE, -- Used in fixture calculations
    applies_to_design BOOLEAN DEFAULT FALSE, -- Used in spatial design
    applies_to_compliance BOOLEAN DEFAULT FALSE, -- Used in compliance checking
    
    -- Legal precision
    is_mandatory BOOLEAN DEFAULT TRUE, -- vs advisory/optional
    contains_numerical_requirement BOOLEAN DEFAULT FALSE,
    contains_exception BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. ENHANCED BUILDING CODE RULES (Link to exact text)
ALTER TABLE building_code_rules ADD COLUMN source_section_id INTEGER REFERENCES code_sections(id);
ALTER TABLE building_code_rules ADD COLUMN source_text_fragment_ids INTEGER[]; -- Array of fragment IDs
ALTER TABLE building_code_rules ADD COLUMN exact_requirement_text TEXT; -- Exact text that triggers this rule
ALTER TABLE building_code_rules ADD COLUMN exact_compliance_text TEXT; -- Exact text for compliance checking

-- 4. CHECKLIST ITEMS (Reference exact original text)
CREATE TABLE compliance_checklist_items (
    id SERIAL PRIMARY KEY,
    jurisdiction_id INTEGER REFERENCES jurisdictions(id),
    building_type VARCHAR(50),
    
    -- Checklist item identification
    item_sequence INTEGER, -- Order in checklist
    item_category VARCHAR(50), -- 'fixture_count', 'accessibility', 'clearance'
    item_title VARCHAR(255), -- Brief description
    
    -- EXACT ORIGINAL TEXT REFERENCE
    code_section_id INTEGER REFERENCES code_sections(id),
    text_fragment_id INTEGER REFERENCES code_text_fragments(id),
    exact_requirement_text TEXT NOT NULL, -- Exact text from building code
    
    -- How this applies to user's project
    calculation_rule_id INTEGER REFERENCES building_code_rules(id),
    compliance_criteria JSONB, -- How to check compliance
    
    -- User-facing information
    explanation_text TEXT, -- Our explanation (separate from original text)
    common_violations TEXT[], -- Typical issues
    recommended_action TEXT,
    
    -- Legal references
    legal_authority VARCHAR(255), -- "National Research Council Canada"
    enforcement_jurisdiction VARCHAR(255), -- "All Canadian provinces"
    penalty_for_non_compliance TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. EXACT TEXT COMPLIANCE TRACKING
CREATE TABLE text_compliance_audit (
    id SERIAL PRIMARY KEY,
    user_input_id INTEGER REFERENCES user_inputs(id),
    generated_checklist_id INTEGER,
    
    -- What exact text was used
    used_section_ids INTEGER[], -- Which code sections were referenced
    used_fragment_ids INTEGER[], -- Which text fragments were used
    exact_text_hash VARCHAR(255), -- Hash of all text used for verification
    
    -- Compliance verification
    text_accuracy_verified BOOLEAN DEFAULT FALSE,
    verified_by VARCHAR(255),
    verification_date TIMESTAMP,
    verification_notes TEXT,
    
    -- Legal protection
    disclaimer_included BOOLEAN DEFAULT TRUE,
    user_acknowledged_official_source BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. MULTI-LANGUAGE TEXT SUPPORT
CREATE TABLE code_translations (
    id SERIAL PRIMARY KEY,
    code_section_id INTEGER REFERENCES code_sections(id),
    language_code VARCHAR(10), -- 'en', 'fr', 'es', 'de', etc.
    
    -- Official translations
    translated_text TEXT NOT NULL,
    translation_source VARCHAR(255), -- Official government translation
    translation_authority VARCHAR(255), -- Who provided the translation
    is_official_translation BOOLEAN DEFAULT FALSE,
    
    -- Translation metadata
    translation_date DATE,
    translator_certification VARCHAR(255),
    translation_reviewed_by VARCHAR(255),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. INDEXES FOR PERFORMANCE
CREATE INDEX idx_code_sections_jurisdiction ON code_sections(jurisdiction_id);
CREATE INDEX idx_code_sections_identifier ON code_sections(section_identifier);
CREATE INDEX idx_code_text_fragments_section ON code_text_fragments(code_section_id);
CREATE INDEX idx_code_text_fragments_type ON code_text_fragments(fragment_type);
CREATE INDEX idx_compliance_checklist_jurisdiction ON compliance_checklist_items(jurisdiction_id);
CREATE INDEX idx_compliance_checklist_building_type ON compliance_checklist_items(building_type);
CREATE INDEX idx_text_compliance_audit_user_input ON text_compliance_audit(user_input_id);

-- Full-text search on exact text
CREATE INDEX idx_code_sections_text_search ON code_sections USING GIN (to_tsvector('english', original_text_en));
CREATE INDEX idx_code_fragments_text_search ON code_text_fragments USING GIN (to_tsvector('english', exact_text_en)); 