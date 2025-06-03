-- 🎯 Enhanced Database Schema for High-Accuracy Building Code Compliance
-- Ensures complete clause coverage with full traceability

-- =====================================================
-- Table 1: component (Individual Washroom Fixtures)
-- =====================================================
CREATE TABLE IF NOT EXISTS component (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    component_code TEXT UNIQUE NOT NULL,     -- 'TOILET_STANDARD', 'SINK_CHILD_LOW'
    name TEXT NOT NULL,                      -- 'Standard Toilet', 'Child-Height Sink'
    category TEXT NOT NULL,                  -- 'toilet', 'sink', 'urinal', 'grab_bar', 'partition'
    description TEXT,
    
    -- Physical Properties
    dimensions TEXT,                         -- JSON: {"width": 0.8, "depth": 1.2, "height": 0.4}
    clearance_requirements TEXT,             -- JSON: {"front": 0.6, "sides": 0.15, "door_swing": 0.9}
    
    -- Code Compliance
    applicable_jurisdictions TEXT,           -- JSON: ["NBC", "Alberta", "Ontario"]
    accessibility_level TEXT,               -- 'standard', 'accessible', 'child_specific'
    
    -- Metadata
    manufacturer_specs TEXT,                -- JSON: manufacturer data
    cost_range TEXT,                        -- 'low', 'medium', 'high'
    maintenance_level TEXT,                 -- 'minimal', 'standard', 'high'
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- Table 2: component_assembly (Functional Units)
-- =====================================================
CREATE TABLE IF NOT EXISTS component_assembly (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assembly_code TEXT UNIQUE NOT NULL,     -- 'ACCESSIBLE_STALL', 'STANDARD_MALE_STALL'
    name TEXT NOT NULL,                     -- 'Accessible Toilet Stall', 'Standard Male Stall'
    description TEXT,
    
    -- Assembly Composition
    component_ids TEXT NOT NULL,            -- JSON: ["TOILET_ACCESSIBLE", "GRAB_BAR_REAR", "GRAB_BAR_SIDE"]
    relationship_rules TEXT,                -- JSON: spatial relationships between components
    
    -- Space Requirements
    total_footprint TEXT,                   -- JSON: {"width": 2.0, "depth": 2.2}
    circulation_space TEXT,                 -- JSON: {"turning_radius": 1.5, "approach_space": 1.2}
    
    -- Code Compliance
    applicable_building_types TEXT,         -- JSON: ["office", "school", "retail"]
    occupancy_requirements TEXT,            -- JSON: {"min_occupancy": 1, "max_occupancy": 100}
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- Table 3: context_logic_rule (Input-Triggered Rules)
-- =====================================================
CREATE TABLE IF NOT EXISTS context_logic_rule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_code TEXT UNIQUE NOT NULL,         -- 'DAYCARE_CHILD_SINK_RULE', 'ACCESSIBILITY_REQUIRED_RULE'
    rule_name TEXT NOT NULL,
    rule_category TEXT,                     -- 'occupancy_based', 'accessibility', 'building_type', 'fixture_count'
    
    -- Trigger Conditions (JSON Logic)
    trigger_condition TEXT NOT NULL,        -- JSON: Complex conditions when rule applies
    priority INTEGER DEFAULT 50,           -- Higher = more important
    
    -- Required Outputs
    required_component_ids TEXT,            -- JSON: ["SINK_CHILD_LOW", "TOILET_CHILD_HEIGHT"]
    required_assembly_ids TEXT,             -- JSON: ["ACCESSIBLE_STALL", "FAMILY_FACILITY"]
    required_clause_ids TEXT,               -- JSON: ["NBC_3.7.2.1_4", "NBC_3.8.3.3_1"]
    
    -- Metadata
    jurisdiction TEXT NOT NULL,             -- 'NBC', 'Alberta', 'Ontario', 'BC'
    effective_date DATE,
    superseded_by INTEGER,                  -- References newer rule
    
    -- Explanation
    rule_explanation TEXT,                  -- Why this rule applies
    code_reference TEXT,                    -- Source building code section
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- Table 4: building_code_clause (Complete Clause Database)
-- =====================================================
CREATE TABLE IF NOT EXISTS building_code_clause (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    clause_code TEXT UNIQUE NOT NULL,       -- 'NBC_3.7.2.1_4', 'ABC_3.8.3.3_1'
    clause_number TEXT NOT NULL,            -- '3.7.2.1.(4)', '3.8.3.3.(1)'
    
    -- Jurisdiction & Version
    jurisdiction TEXT NOT NULL,             -- 'NBC', 'Alberta', 'Ontario', 'BC'
    code_version TEXT NOT NULL,             -- '2020', '2015', '2012'
    document_title TEXT,                    -- 'National Building Code of Canada'
    
    -- Clause Content
    clause_title TEXT,                      -- 'Water Closets for Children'
    clause_text_en TEXT NOT NULL,          -- Full English text
    clause_text_fr TEXT,                    -- Full French text (for bilingual compliance)
    
    -- Source Information
    page_number INTEGER,
    section_reference TEXT,                 -- 'Part 3, Section 3.7, Subsection 3.7.2'
    table_reference TEXT,                  -- 'Table 3.7.2.1'
    figure_reference TEXT,                 -- 'Figure 3.8.3.3.A'
    
    -- Applicability
    applies_to_building_types TEXT,        -- JSON: ["office", "school", "daycare"]
    applies_to_occupancy_types TEXT,       -- JSON: ["A1", "A2", "B", "E"]
    applies_to_components TEXT,            -- JSON: ["TOILET_STANDARD", "SINK_CHILD_LOW"]
    
    -- Relationships
    related_clause_ids TEXT,               -- JSON: other clauses that interact
    supersedes_clause_ids TEXT,            -- JSON: clauses this overrides
    exception_clause_ids TEXT,             -- JSON: exceptions to this clause
    
    -- Metadata
    is_mandatory BOOLEAN DEFAULT TRUE,     -- vs advisory/recommended
    enforcement_level TEXT,                -- 'critical', 'important', 'recommended'
    last_updated DATE,
    verified_by TEXT,                      -- Who verified the text accuracy
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- Indexes for Performance
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_component_code ON component(component_code);
CREATE INDEX IF NOT EXISTS idx_component_category ON component(category);
CREATE INDEX IF NOT EXISTS idx_component_jurisdiction ON component(applicable_jurisdictions);

CREATE INDEX IF NOT EXISTS idx_assembly_code ON component_assembly(assembly_code);
CREATE INDEX IF NOT EXISTS idx_assembly_building_types ON component_assembly(applicable_building_types);

CREATE INDEX IF NOT EXISTS idx_rule_code ON context_logic_rule(rule_code);
CREATE INDEX IF NOT EXISTS idx_rule_jurisdiction ON context_logic_rule(jurisdiction);
CREATE INDEX IF NOT EXISTS idx_rule_category ON context_logic_rule(rule_category);
CREATE INDEX IF NOT EXISTS idx_rule_priority ON context_logic_rule(priority);

CREATE INDEX IF NOT EXISTS idx_clause_code ON building_code_clause(clause_code);
CREATE INDEX IF NOT EXISTS idx_clause_jurisdiction ON building_code_clause(jurisdiction);
CREATE INDEX IF NOT EXISTS idx_clause_building_types ON building_code_clause(applies_to_building_types);
CREATE INDEX IF NOT EXISTS idx_clause_enforcement ON building_code_clause(enforcement_level);

-- =====================================================
-- Views for Common Queries
-- =====================================================

-- View: Active Rules by Jurisdiction
CREATE VIEW IF NOT EXISTS active_rules_by_jurisdiction AS
SELECT 
    rule_code,
    rule_name,
    rule_category,
    jurisdiction,
    trigger_condition,
    required_component_ids,
    required_assembly_ids,
    required_clause_ids,
    priority
FROM context_logic_rule
WHERE superseded_by IS NULL
ORDER BY jurisdiction, priority DESC;

-- View: Critical Building Code Clauses
CREATE VIEW IF NOT EXISTS critical_clauses AS
SELECT 
    clause_code,
    clause_number,
    clause_title,
    jurisdiction,
    code_version,
    enforcement_level,
    applies_to_building_types,
    applies_to_components
FROM building_code_clause
WHERE enforcement_level = 'critical'
ORDER BY jurisdiction, clause_number;

-- View: Component Assembly Details
CREATE VIEW IF NOT EXISTS assembly_component_details AS
SELECT 
    ca.assembly_code,
    ca.name as assembly_name,
    ca.component_ids,
    ca.total_footprint,
    ca.applicable_building_types,
    GROUP_CONCAT(c.name) as component_names
FROM component_assembly ca
LEFT JOIN component c ON JSON_EXTRACT(ca.component_ids, '$') LIKE '%' || c.component_code || '%'
GROUP BY ca.assembly_code;

-- =====================================================
-- Triggers for Data Integrity
-- =====================================================

-- Trigger: Update timestamp on rule changes
CREATE TRIGGER IF NOT EXISTS update_rule_timestamp
AFTER UPDATE ON context_logic_rule
BEGIN
    UPDATE context_logic_rule 
    SET created_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.id;
END;

-- Trigger: Validate JSON fields
CREATE TRIGGER IF NOT EXISTS validate_component_json
BEFORE INSERT ON component
BEGIN
    SELECT CASE
        WHEN NEW.dimensions IS NOT NULL AND json_valid(NEW.dimensions) = 0 THEN
            RAISE(ABORT, 'Invalid JSON in dimensions field')
        WHEN NEW.clearance_requirements IS NOT NULL AND json_valid(NEW.clearance_requirements) = 0 THEN
            RAISE(ABORT, 'Invalid JSON in clearance_requirements field')
        WHEN NEW.applicable_jurisdictions IS NOT NULL AND json_valid(NEW.applicable_jurisdictions) = 0 THEN
            RAISE(ABORT, 'Invalid JSON in applicable_jurisdictions field')
    END;
END; 