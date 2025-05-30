# 🎯 MVP PHASE 2: Spatial Layout Generation

## 📋 **PHASE 2 GOAL**
Transform calculated requirements from Phase 1 into actual spatial layouts using your existing design_modules system with intelligent placement and clearance checking.

---

## 🔧 **IMPLEMENTATION TASKS**

### **Task 2.1: Enhance Design Modules System** *(3 days)*

Extend your existing design_modules to work with calculated requirements:

```sql
-- Add spatial layout rules
CREATE TABLE layout_placement_rules (
    id SERIAL PRIMARY KEY,
    rule_name VARCHAR(255) NOT NULL,
    rule_category VARCHAR(50), -- 'clearance', 'accessibility', 'circulation', 'privacy'
    priority INTEGER DEFAULT 50,
    applies_to_module_type VARCHAR(100), -- 'toilet_unit', 'sink_unit', 'urinal_unit'
    spatial_constraints JSONB, -- Clearance requirements in JSON
    placement_logic JSONB, -- How to place relative to other modules
    code_reference VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Enhanced module placements with clearances
ALTER TABLE module_components ADD COLUMN clearance_front DECIMAL;
ALTER TABLE module_components ADD COLUMN clearance_sides DECIMAL;
ALTER TABLE module_components ADD COLUMN clearance_back DECIMAL;
ALTER TABLE module_components ADD COLUMN accessibility_features JSONB;

-- Layout generation tracking
CREATE TABLE layout_generation_log (
    id SERIAL PRIMARY KEY,
    user_input_id INTEGER REFERENCES user_inputs(id),
    generation_attempt INTEGER,
    selected_modules JSONB,
    placement_algorithm VARCHAR(50),
    layout_result JSONB,
    performance_metrics JSONB,
    success BOOLEAN,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Task 2.2: Smart Module Selection Function** *(3 days)*

```sql
-- Function to select appropriate design modules based on requirements
CREATE OR REPLACE FUNCTION select_design_modules(
    p_user_input_id INTEGER
) RETURNS TABLE (
    module_id INTEGER,
    module_name VARCHAR,
    module_type VARCHAR,
    quantity INTEGER,
    selection_reason TEXT
) AS $$
DECLARE
    v_requirements JSONB;
    v_user_input user_inputs%ROWTYPE;
    v_male_toilets INTEGER;
    v_female_toilets INTEGER;
    v_accessible_toilets INTEGER;
    v_sinks INTEGER;
BEGIN
    -- Get calculated requirements from Phase 1
    SELECT calculated_values INTO v_requirements 
    FROM calculated_requirements 
    WHERE user_input_id = p_user_input_id AND requirement_type = 'fixtures';
    
    SELECT * INTO v_user_input FROM user_inputs WHERE id = p_user_input_id;
    
    -- Extract fixture counts
    v_male_toilets := (v_requirements->>'male_toilets')::INTEGER;
    v_female_toilets := (v_requirements->>'female_toilets')::INTEGER;
    v_accessible_toilets := (v_requirements->>'accessible_toilets')::INTEGER;
    v_sinks := (v_requirements->>'sinks')::INTEGER;
    
    -- Select standard toilet modules
    IF v_male_toilets > 0 THEN
        RETURN QUERY SELECT 
            dm.id,
            dm.name::VARCHAR,
            dm.type::VARCHAR,
            v_male_toilets,
            'Required by NBC 3.7.2 for male occupancy'::TEXT
        FROM design_modules dm 
        WHERE dm.type = 'toilet_unit' 
        AND dm.name ILIKE '%standard%'
        LIMIT 1;
    END IF;
    
    IF v_female_toilets > 0 THEN
        RETURN QUERY SELECT 
            dm.id,
            dm.name::VARCHAR,
            dm.type::VARCHAR,
            v_female_toilets,
            'Required by NBC 3.7.2 for female occupancy'::TEXT
        FROM design_modules dm 
        WHERE dm.type = 'toilet_unit' 
        AND dm.name ILIKE '%standard%'
        LIMIT 1;
    END IF;
    
    -- Select accessible toilet modules
    IF v_accessible_toilets > 0 THEN
        RETURN QUERY SELECT 
            dm.id,
            dm.name::VARCHAR,
            dm.type::VARCHAR,
            v_accessible_toilets,
            'Required by NBC 3.8.3.12 for accessibility'::TEXT
        FROM design_modules dm 
        WHERE dm.type = 'toilet_unit' 
        AND dm.name ILIKE '%accessible%'
        LIMIT 1;
    END IF;
    
    -- Select sink modules (prefer double sinks for efficiency)
    RETURN QUERY SELECT 
        dm.id,
        dm.name::VARCHAR,
        dm.type::VARCHAR,
        CEIL(v_sinks / 2.0)::INTEGER, -- Use double sinks where possible
        'Required for hand washing - 1 per 2 toilets minimum'::TEXT
    FROM design_modules dm 
    WHERE dm.type = 'sink_unit' 
    AND dm.name ILIKE '%double%'
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;
```

### **Task 2.3: Spatial Layout Algorithm** *(4 days)*

```sql
-- Advanced layout generation function
CREATE OR REPLACE FUNCTION generate_spatial_layout(
    p_user_input_id INTEGER
) RETURNS JSONB AS $$
DECLARE
    v_user_input user_inputs%ROWTYPE;
    v_selected_modules RECORD;
    v_layout JSONB := '[]';
    v_current_x DECIMAL := 0.5; -- Start 0.5m from wall
    v_current_y DECIMAL := 0.5;
    v_row_height DECIMAL := 0;
    v_module_placement JSONB;
    v_clearance_rules JSONB;
    v_module_info RECORD;
BEGIN
    -- Get user input
    SELECT * INTO v_user_input FROM user_inputs WHERE id = p_user_input_id;
    
    -- Process each selected module type
    FOR v_selected_modules IN 
        SELECT * FROM select_design_modules(p_user_input_id)
    LOOP
        -- Get module dimensions and clearance requirements
        SELECT dm.*, dm.dimensions 
        INTO v_module_info
        FROM design_modules dm 
        WHERE dm.id = v_selected_modules.module_id;
        
        -- Get clearance rules for this module type
        SELECT spatial_constraints INTO v_clearance_rules
        FROM layout_placement_rules
        WHERE applies_to_module_type = v_selected_modules.module_type
        AND rule_category = 'clearance'
        ORDER BY priority DESC
        LIMIT 1;
        
        -- Place multiple instances of this module
        FOR i IN 1..v_selected_modules.quantity LOOP
            -- Calculate module dimensions
            DECLARE
                v_module_length DECIMAL := COALESCE((v_module_info.dimensions->>'length')::DECIMAL, 1.5);
                v_module_width DECIMAL := COALESCE((v_module_info.dimensions->>'width')::DECIMAL, 0.9);
                v_front_clearance DECIMAL := COALESCE((v_clearance_rules->>'front_clearance')::DECIMAL, 0.6);
                v_side_clearance DECIMAL := COALESCE((v_clearance_rules->>'side_clearance')::DECIMAL, 0.15);
            BEGIN
                -- Check if module fits in current row
                IF v_current_x + v_module_length + v_side_clearance > v_user_input.length - 0.5 THEN
                    -- Move to next row
                    v_current_x := 0.5;
                    v_current_y := v_current_y + v_row_height + 1.2; -- 1.2m circulation
                    v_row_height := 0;
                END IF;
                
                -- Create module placement record
                v_module_placement := jsonb_build_object(
                    'module_id', v_selected_modules.module_id,
                    'module_name', v_selected_modules.module_name,
                    'module_type', v_selected_modules.module_type,
                    'instance', i,
                    'x_position', v_current_x,
                    'y_position', v_current_y,
                    'width', v_module_width,
                    'length', v_module_length,
                    'rotation', 0,
                    'clearances', jsonb_build_object(
                        'front', v_front_clearance,
                        'sides', v_side_clearance,
                        'back', 0.15
                    ),
                    'accessibility_features', CASE 
                        WHEN v_selected_modules.module_name ILIKE '%accessible%' 
                        THEN '["grab_bars", "wider_door", "transfer_space"]'::JSONB
                        ELSE '[]'::JSONB
                    END
                );
                
                -- Add to layout
                v_layout := v_layout || v_module_placement;
                
                -- Update position for next module
                v_current_x := v_current_x + v_module_length + v_side_clearance + 0.6; -- 0.6m spacing
                v_row_height := GREATEST(v_row_height, v_module_width + v_front_clearance);
            END;
        END LOOP;
    END LOOP;
    
    -- Store layout in generated_designs
    UPDATE generated_designs 
    SET layout = v_layout,
        module_placements = v_layout
    WHERE user_input_id = p_user_input_id;
    
    -- If no existing design, create one
    IF NOT FOUND THEN
        INSERT INTO generated_designs (user_input_id, name, description, layout, module_placements)
        VALUES (p_user_input_id, 'Auto-Generated Layout', 'Generated using spatial algorithm', v_layout, v_layout);
    END IF;
    
    -- Log generation attempt
    INSERT INTO layout_generation_log (user_input_id, generation_attempt, selected_modules, layout_result, success)
    VALUES (p_user_input_id, 1, 
           (SELECT jsonb_agg(row_to_json(sm)) FROM select_design_modules(p_user_input_id) sm),
           v_layout, TRUE);
    
    RETURN v_layout;
END;
$$ LANGUAGE plpgsql;
```

### **Task 2.4: Clearance Validation Function** *(2 days)*

```sql
-- Function to validate layout clearances and accessibility
CREATE OR REPLACE FUNCTION validate_layout_clearances(
    p_user_input_id INTEGER
) RETURNS TABLE (
    validation_type VARCHAR,
    status VARCHAR,
    message TEXT,
    details JSONB
) AS $$
DECLARE
    v_layout JSONB;
    v_user_input user_inputs%ROWTYPE;
    v_module JSONB;
    v_clearance_issues INTEGER := 0;
    v_accessibility_issues INTEGER := 0;
BEGIN
    -- Get layout and user input
    SELECT layout INTO v_layout FROM generated_designs WHERE user_input_id = p_user_input_id ORDER BY created_at DESC LIMIT 1;
    SELECT * INTO v_user_input FROM user_inputs WHERE id = p_user_input_id;
    
    -- Check each module's clearances
    FOR i IN 0..jsonb_array_length(v_layout) - 1 LOOP
        v_module := v_layout->i;
        
        -- Check if module fits within room boundaries
        IF (v_module->>'x_position')::DECIMAL + (v_module->>'length')::DECIMAL > v_user_input.length THEN
            v_clearance_issues := v_clearance_issues + 1;
        END IF;
        
        IF (v_module->>'y_position')::DECIMAL + (v_module->>'width')::DECIMAL > v_user_input.width THEN
            v_clearance_issues := v_clearance_issues + 1;
        END IF;
        
        -- Check accessibility compliance for accessible modules
        IF v_module->>'module_name' ILIKE '%accessible%' THEN
            -- Verify 1500mm x 1500mm clear space in front
            IF (v_module->>'clearances'->>'front')::DECIMAL < 1.5 THEN
                v_accessibility_issues := v_accessibility_issues + 1;
            END IF;
        END IF;
    END LOOP;
    
    -- Return clearance validation results
    RETURN QUERY SELECT 
        'clearance'::VARCHAR,
        CASE WHEN v_clearance_issues = 0 THEN 'pass' ELSE 'fail' END,
        CASE 
            WHEN v_clearance_issues = 0 THEN 'All modules fit within room boundaries'
            ELSE v_clearance_issues::TEXT || ' modules exceed room boundaries'
        END,
        jsonb_build_object('issues_count', v_clearance_issues);
    
    -- Return accessibility validation results
    RETURN QUERY SELECT 
        'accessibility'::VARCHAR,
        CASE WHEN v_accessibility_issues = 0 THEN 'pass' ELSE 'fail' END,
        CASE 
            WHEN v_accessibility_issues = 0 THEN 'All accessibility clearances met'
            ELSE v_accessibility_issues::TEXT || ' accessibility clearance violations'
        END,
        jsonb_build_object('issues_count', v_accessibility_issues);
END;
$$ LANGUAGE plpgsql;
```

### **Task 2.5: Populate Layout Rules** *(1 day)*

```sql
-- Insert spatial layout rules
INSERT INTO layout_placement_rules (rule_name, rule_category, applies_to_module_type, spatial_constraints, code_reference) VALUES

-- Toilet clearance requirements
('Standard Toilet Clearance', 'clearance', 'toilet_unit',
 '{"front_clearance": 0.6, "side_clearance": 0.15, "door_swing": 0.76}',
 'NBC 3.7.2'),

('Accessible Toilet Clearance', 'clearance', 'accessible_toilet_unit', 
 '{"front_clearance": 1.5, "side_clearance": 0.9, "transfer_space": 0.9}',
 'NBC 3.8.3'),

-- Sink clearance requirements
('Sink Clearance', 'clearance', 'sink_unit',
 '{"front_clearance": 0.6, "side_clearance": 0.3, "knee_clearance": 0.7}',
 'NBC 3.7.4'),

-- Circulation requirements
('Corridor Width', 'circulation', 'all',
 '{"min_corridor_width": 1.2, "accessible_corridor_width": 1.5}',
 'NBC 3.8.2'),

-- Privacy requirements
('Visual Privacy', 'privacy', 'toilet_unit',
 '{"sight_line_blocking": true, "privacy_distance": 1.8}',
 'General Standards');
```

---

## 🧪 **TESTING PHASE 2**

### **Test 1: Module Selection**
```sql
-- Test module selection for 200-person office
SELECT * FROM select_design_modules(1); -- Assuming user_input_id = 1

-- Expected: Standard toilets (2 male, 3 female), Accessible toilet (1), Double sink (2)
```

### **Test 2: Layout Generation**
```sql
-- Generate spatial layout
SELECT generate_spatial_layout(1);

-- Should return JSONB array with module placements including coordinates
```

### **Test 3: Clearance Validation**
```sql
-- Validate generated layout
SELECT * FROM validate_layout_clearances(1);

-- Should return pass/fail for clearances and accessibility
```

### **Test 4: Insert Test Project**
```sql
-- Insert test project
INSERT INTO user_inputs (
    project_name, building_type, length, width, height, 
    estimated_users, jurisdiction, male_percentage
) VALUES (
    'Test Office Building', 'office', 12.0, 8.0, 3.0, 
    200, 'NBC', 0.5
);

-- Test calculation
SELECT calculate_fixture_requirements(currval('user_inputs_id_seq'));

-- Expected result:
-- {
--   "male_toilets": 2,        -- 100 males / 75 = 1.33 → 2
--   "female_toilets": 3,      -- 100 females / 40 = 2.5 → 3  
--   "accessible_toilets": 1,  -- max(1, 5 total * 0.05) = 1
--   "total_toilets": 6,
--   "sinks": 4,               -- max(2, 5 * 0.8) = 4
--   "accessible_sinks": 1
-- }
```

### **Test 5: School Calculation**
```sql
-- Test school
INSERT INTO user_inputs (project_name, building_type, estimated_users, jurisdiction) 
VALUES ('Test School', 'school', 300, 'NBC');

SELECT calculate_fixture_requirements(currval('user_inputs_id_seq'));

-- Expected: 2 male (150/100), 4 female (150/45), 1 accessible
```

### **Test 6: Compliance Checklist**
```sql
-- Generate checklist
SELECT * FROM generate_compliance_checklist(1);

-- Should return multiple checklist items with NBC code references
```

### **Test 7: Enhanced Compliance**
```sql
-- Test enhanced compliance
SELECT * FROM check_washroom_compliance_v2(1);

-- Should return detailed compliance analysis with calculated requirements
```

### **Test 8: Compare Requirements Across Codes**
```sql
-- Compare requirements across codes
SELECT compare_jurisdictions(project_id, ['NBC', 'AB', 'ON', 'IBC']);
-- Returns: differences for user to understand
```

### **Test 9: Exact Text Compliance**
```sql
-- System automatically selects exact text based on jurisdiction
SELECT original_text_en FROM code_sections 
WHERE jurisdiction_id = user_jurisdiction 
AND applies_to_building_type = user_building_type;
```

### **Test 10: Exact Text Compliance Checklist**
```sql
-- Generate checklist using exact original building code language
SELECT generate_exact_text_compliance_checklist(project_id, jurisdiction_id);
```

---

## 📈 **PHASE 2 SUCCESS CRITERIA**

✅ **Smart module selection working**
- Selects appropriate modules based on calculated requirements
- Handles different building types and occupancy loads
- Provides clear reasoning for selections

✅ **Spatial layout algorithm functional**
- Places modules with proper clearances
- Handles room size constraints
- Generates valid coordinates for all modules

✅ **Clearance validation working**
- Detects clearance violations
- Validates accessibility compliance
- Provides detailed validation results

✅ **Integration with existing system**
- Works with existing design_modules table
- Updates generated_designs with spatial layouts
- Maintains database relationships

---

## 🔄 **NEXT PHASE PREP**

Phase 2 deliverables feed into Phase 3:
- Validated spatial layouts → Compliance verification input
- Module placements with clearances → Detailed compliance checking
- Layout validation results → Compliance scoring

**Phase 3 will verify these generated layouts against all building code requirements and produce comprehensive compliance reports.** 

-- 1. BUILDING CODE RULES TABLE
-- This is the heart of the system - programmable building code rules
CREATE TABLE building_code_rules (
    id SERIAL PRIMARY KEY,
    rule_id VARCHAR(100) UNIQUE NOT NULL, -- 'NBC_3.7.2_TOILET_COUNT'
    rule_type VARCHAR(50) NOT NULL, -- 'fixture_count', 'clearance', 'accessibility'
    jurisdiction VARCHAR(50) NOT NULL, -- 'NBC', 'Ontario', 'Alberta'
    code_section VARCHAR(100) NOT NULL, -- 'NBC 3.7.2'
    building_type VARCHAR(50), -- 'office', 'school', 'retail', NULL for all
    occupancy_type VARCHAR(10), -- 'A1', 'B', 'E' (optional)
    
    -- The magic happens here - JSON logic for rules
    condition_logic JSONB, -- When this rule applies
    requirement_logic JSONB, -- What the rule calculates
    
    -- Metadata
    measurement_units VARCHAR(20), -- 'count', 'mm', 'percentage'
    priority INTEGER DEFAULT 50, -- Higher = more important
    code_text TEXT, -- Original code text for reference
    effective_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. CALCULATION FORMULAS TABLE
-- Store reusable mathematical formulas
CREATE TABLE calculation_formulas (
    id SERIAL PRIMARY KEY,
    formula_name VARCHAR(255) NOT NULL,
    formula_type VARCHAR(50), -- 'fixture_count', 'area_calculation'
    building_type VARCHAR(50),
    jurisdiction VARCHAR(50),
    input_parameters JSONB, -- ["male_occupancy", "female_occupancy"]
    formula_expression TEXT, -- The actual formula
    output_description TEXT,
    code_reference VARCHAR(100),
    examples JSONB, -- Example calculations
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. ENHANCE YOUR EXISTING USER_INPUTS TABLE
-- Add the missing columns we need
ALTER TABLE user_inputs ADD COLUMN IF NOT EXISTS jurisdiction VARCHAR(50);
ALTER TABLE user_inputs ADD COLUMN IF NOT EXISTS occupancy_type VARCHAR(10);
ALTER TABLE user_inputs ADD COLUMN IF NOT EXISTS male_percentage DECIMAL DEFAULT 0.5;
ALTER TABLE user_inputs ADD COLUMN IF NOT EXISTS accessibility_level VARCHAR(20) DEFAULT 'standard';

-- 4. CALCULATED REQUIREMENTS STORAGE
-- Store the results of our calculations
CREATE TABLE calculated_requirements (
    id SERIAL PRIMARY KEY,
    user_input_id INTEGER REFERENCES user_inputs(id),
    requirement_type VARCHAR(50), -- 'fixtures', 'space', 'accessibility'
    calculated_values JSONB, -- The calculated fixture counts
    applied_rules JSONB, -- Which rules were used
    calculation_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_building_code_rules_jurisdiction ON building_code_rules(jurisdiction);
CREATE INDEX idx_building_code_rules_building_type ON building_code_rules(building_type);
CREATE INDEX idx_building_code_rules_rule_type ON building_code_rules(rule_type);
CREATE INDEX idx_calculated_requirements_user_input ON calculated_requirements(user_input_id); 
```

-- MASTER FUNCTION: Calculate Fixture Requirements
CREATE OR REPLACE FUNCTION calculate_fixture_requirements(
    p_user_input_id INTEGER
) RETURNS JSONB AS $$
DECLARE
    v_user_input user_inputs%ROWTYPE;
    v_male_occupancy INTEGER;
    v_female_occupancy INTEGER;
    v_requirements JSONB := '{}';
    v_applied_rules JSONB := '[]';
    v_rule RECORD;
    v_male_toilets INTEGER := 0;
    v_female_toilets INTEGER := 0;
    v_accessible_toilets INTEGER := 0;
    v_sinks INTEGER := 0;
    v_urinals INTEGER := 0;
BEGIN
    -- Get user input data
    SELECT * INTO v_user_input FROM user_inputs WHERE id = p_user_input_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'User input not found for id: %', p_user_input_id;
    END IF;
    
    -- Calculate gender-based occupancy
    v_male_occupancy := FLOOR(v_user_input.estimated_users * COALESCE(v_user_input.male_percentage, 0.5));
    v_female_occupancy := v_user_input.estimated_users - v_male_occupancy;
    
    -- Apply building code rules in priority order
    FOR v_rule IN 
        SELECT * FROM building_code_rules 
        WHERE (building_type = v_user_input.building_type OR building_type IS NULL)
        AND (jurisdiction = v_user_input.jurisdiction OR jurisdiction = 'NBC')
        AND rule_type = 'fixture_count'
        ORDER BY priority DESC, id ASC
    LOOP
        -- NBC Office Toilet Requirements (Example)
        IF v_rule.rule_id = 'NBC_3.7.2_TOILET_COUNT_OFFICE' THEN
            v_male_toilets := GREATEST(v_male_toilets, CEIL(v_male_occupancy / 75.0));
            v_female_toilets := GREATEST(v_female_toilets, CEIL(v_female_occupancy / 40.0));
            
            -- Track which rule was applied
            v_applied_rules := v_applied_rules || jsonb_build_object(
                'rule_id', v_rule.rule_id,
                'calculation', format('Male: %s/75 = %s, Female: %s/40 = %s', 
                    v_male_occupancy, v_male_toilets, v_female_occupancy, v_female_toilets)
            );
        END IF;
        
        -- NBC School Toilet Requirements
        IF v_rule.rule_id = 'NBC_3.7.2_TOILET_COUNT_SCHOOL' THEN
            v_male_toilets := GREATEST(v_male_toilets, CEIL(v_male_occupancy / 100.0));
            v_female_toilets := GREATEST(v_female_toilets, CEIL(v_female_occupancy / 45.0));
            
            v_applied_rules := v_applied_rules || jsonb_build_object(
                'rule_id', v_rule.rule_id,
                'calculation', format('Male: %s/100 = %s, Female: %s/45 = %s', 
                    v_male_occupancy, v_male_toilets, v_female_occupancy, v_female_toilets)
            );
        END IF;
        
        -- NBC Accessibility Requirements
        IF v_rule.rule_id = 'NBC_3.8.3_ACCESSIBLE_COUNT' THEN
            v_accessible_toilets := GREATEST(1, CEIL((v_male_toilets + v_female_toilets) * 0.05));
            
            v_applied_rules := v_applied_rules || jsonb_build_object(
                'rule_id', v_rule.rule_id,
                'calculation', format('5%% of %s total toilets = %s (min 1)', 
                    v_male_toilets + v_female_toilets, v_accessible_toilets)
            );
        END IF;
    END LOOP;
    
    -- Calculate sinks (general rule: 1 per 2 toilets, minimum 2)
    v_sinks := GREATEST(2, CEIL((v_male_toilets + v_female_toilets) * 0.8));
    
    -- Build final requirements JSON
    v_requirements := jsonb_build_object(
        'male_toilets', v_male_toilets,
        'female_toilets', v_female_toilets,
        'accessible_toilets', v_accessible_toilets,
        'total_toilets', v_male_toilets + v_female_toilets + v_accessible_toilets,
        'sinks', v_sinks,
        'accessible_sinks', GREATEST(1, CEIL(v_sinks * 0.1)),
        'urinals', CASE 
            WHEN v_user_input.building_type IN ('office', 'school') THEN CEIL(v_male_toilets * 0.5)
            ELSE 0 
        END,
        'calculation_basis', jsonb_build_object(
            'total_occupancy', v_user_input.estimated_users,
            'male_occupancy', v_male_occupancy,
            'female_occupancy', v_female_occupancy,
            'building_type', v_user_input.building_type,
            'jurisdiction', v_user_input.jurisdiction
        )
    );
    
    -- Store the calculated requirements
    INSERT INTO calculated_requirements (user_input_id, requirement_type, calculated_values, applied_rules)
    VALUES (p_user_input_id, 'fixtures', v_requirements, v_applied_rules)
    ON CONFLICT (user_input_id, requirement_type) 
    DO UPDATE SET 
        calculated_values = EXCLUDED.calculated_values,
        applied_rules = EXCLUDED.applied_rules,
        created_at = CURRENT_TIMESTAMP;
    
    RETURN v_requirements;
END;
$$ LANGUAGE plpgsql; 
```

-- ENHANCED COMPLIANCE FUNCTION
CREATE OR REPLACE FUNCTION check_washroom_compliance_v2(
    p_user_input_id INTEGER
) RETURNS TABLE (
    check_type VARCHAR,
    status VARCHAR,
    message TEXT,
    details JSONB
) AS $$
DECLARE
    v_requirements JSONB;
    v_user_input user_inputs%ROWTYPE;
    v_design_layout JSONB;
    v_fixture_compliance BOOLEAN := TRUE;
    v_accessibility_compliance BOOLEAN := TRUE;
BEGIN
    -- Get user input
    SELECT * INTO v_user_input FROM user_inputs WHERE id = p_user_input_id;
    
    -- Calculate requirements using new rules engine
    SELECT calculate_fixture_requirements(p_user_input_id) INTO v_requirements;
    
    -- Get current design layout (if exists)
    SELECT layout INTO v_design_layout 
    FROM generated_designs 
    WHERE user_input_id = p_user_input_id 
    ORDER BY created_at DESC LIMIT 1;
    
    -- FIXTURE COUNT COMPLIANCE CHECK
    RETURN QUERY SELECT 
        'fixture_count'::VARCHAR,
        CASE 
            WHEN v_design_layout IS NULL THEN 'pending'
            ELSE 'calculated'
        END,
        format('Required fixtures calculated: %s male toilets, %s female toilets, %s accessible toilets, %s sinks',
            v_requirements->>'male_toilets',
            v_requirements->>'female_toilets', 
            v_requirements->>'accessible_toilets',
            v_requirements->>'sinks')::TEXT,
        v_requirements;
    
    -- ACCESSIBILITY COMPLIANCE CHECK
    RETURN QUERY SELECT 
        'accessibility'::VARCHAR,
        CASE 
            WHEN (v_requirements->>'accessible_toilets')::INTEGER >= 1 THEN 'pass'
            ELSE 'fail'
        END,
        format('Accessibility requirement: %s accessible toilet(s) required by NBC 3.8.3.12',
            v_requirements->>'accessible_toilets')::TEXT,
        jsonb_build_object(
            'required_accessible', v_requirements->>'accessible_toilets',
            'code_reference', 'NBC 3.8.3.12'
        );
    
    -- BUILDING CODE COMPLIANCE SUMMARY
    RETURN QUERY SELECT 
        'building_code'::VARCHAR,
        'calculated'::VARCHAR,
        format('Building code analysis complete for %s building with %s occupants under %s jurisdiction',
            v_user_input.building_type,
            v_user_input.estimated_users,
            COALESCE(v_user_input.jurisdiction, 'NBC'))::TEXT,
        jsonb_build_object(
            'jurisdiction', COALESCE(v_user_input.jurisdiction, 'NBC'),
            'building_type', v_user_input.building_type,
            'occupancy', v_user_input.estimated_users,
            'requirements', v_requirements
        );
END;
$$ LANGUAGE plpgsql; 
```

-- Add New Zealand Building Code
INSERT INTO jurisdictions VALUES 
('NZBC', 'New Zealand Building Code', 'NZL', NULL, '2022');

-- Import their rules via JSON
SELECT import_building_code_from_source('NZBC', 'manual', NULL, nz_rules_json);

-- Immediately available to users in New Zealand 

-- System monitors for building code changes
-- Notifies when NBC 2025 is released
-- Analyzes impact on existing projects 

-- Every building code section stores EXACT original text
CREATE TABLE code_sections (
    original_text_en TEXT NOT NULL, -- Word-for-word from building code
    original_text_fr TEXT,          -- Official bilingual versions
    source_document_title VARCHAR(500),
    source_document_page INTEGER,
    text_verified_by VARCHAR(255)
); 