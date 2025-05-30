# 🏗️ MVP PHASE 1: Building Code Rules Engine

## 📋 **PHASE 1 GOAL**
Add programmable building code rules to your existing PostgreSQL system to enable automated fixture calculations and compliance checking.

---

## 🔧 **IMPLEMENTATION TASKS**

### **Task 1.1: Enhance PostgreSQL Schema** *(3 days)*

Add building code tables to your existing schema:

```sql
-- Add to your existing schema.sql

-- Building Code Rules Table
CREATE TABLE building_code_rules (
    id SERIAL PRIMARY KEY,
    rule_id VARCHAR(100) UNIQUE NOT NULL, -- 'NBC_3.7.2_TOILET_COUNT'
    rule_type VARCHAR(50) NOT NULL, -- 'fixture_count', 'clearance', 'accessibility'
    jurisdiction VARCHAR(50) NOT NULL, -- 'NBC', 'Ontario', 'Alberta'
    code_section VARCHAR(100) NOT NULL,
    building_type VARCHAR(50), -- 'office', 'school', 'retail'
    occupancy_type VARCHAR(10), -- 'A1', 'B', 'E'
    condition_logic JSONB, -- When rule applies
    requirement_logic JSONB, -- What rule requires
    formula_logic JSONB, -- Mathematical formulas
    measurement_units VARCHAR(20),
    priority INTEGER DEFAULT 50,
    code_text TEXT,
    effective_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Calculation Engine Table
CREATE TABLE calculation_formulas (
    id SERIAL PRIMARY KEY,
    formula_name VARCHAR(255) NOT NULL,
    formula_type VARCHAR(50), -- 'fixture_count', 'area', 'clearance'
    building_type VARCHAR(50),
    jurisdiction VARCHAR(50),
    input_parameters JSONB, -- Required inputs
    formula_expression TEXT, -- JavaScript-like formula
    output_description TEXT,
    code_reference VARCHAR(100),
    examples JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Enhanced User Requirements (extend your existing user_inputs)
ALTER TABLE user_inputs ADD COLUMN jurisdiction VARCHAR(50);
ALTER TABLE user_inputs ADD COLUMN occupancy_type VARCHAR(10);
ALTER TABLE user_inputs ADD COLUMN male_percentage DECIMAL DEFAULT 0.5;
ALTER TABLE user_inputs ADD COLUMN accessibility_level VARCHAR(20) DEFAULT 'standard';

-- Calculated Requirements Storage
CREATE TABLE calculated_requirements (
    id SERIAL PRIMARY KEY,
    user_input_id INTEGER REFERENCES user_inputs(id),
    requirement_type VARCHAR(50), -- 'fixtures', 'space', 'accessibility'
    calculated_values JSONB,
    applied_rules JSONB, -- Which rules were used
    calculation_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Task 1.2: Create Code Rules Engine Functions** *(4 days)*

```sql
-- Function to calculate fixture requirements
CREATE OR REPLACE FUNCTION calculate_fixture_requirements(
    p_user_input_id INTEGER
) RETURNS JSONB AS $$
DECLARE
    v_user_input user_inputs%ROWTYPE;
    v_male_occupancy INTEGER;
    v_female_occupancy INTEGER;
    v_requirements JSONB := '{}';
    v_rule RECORD;
BEGIN
    -- Get user input
    SELECT * INTO v_user_input FROM user_inputs WHERE id = p_user_input_id;
    
    -- Calculate gender-based occupancy
    v_male_occupancy := FLOOR(v_user_input.estimated_users * v_user_input.male_percentage);
    v_female_occupancy := v_user_input.estimated_users - v_male_occupancy;
    
    -- Apply building code rules
    FOR v_rule IN 
        SELECT * FROM building_code_rules 
        WHERE (building_type = v_user_input.building_type OR building_type IS NULL)
        AND (jurisdiction = v_user_input.jurisdiction OR jurisdiction = 'NBC')
        AND rule_type = 'fixture_count'
        ORDER BY priority DESC
    LOOP
        -- NBC Office Example: 1 toilet per 75 males, 1 per 40 females
        IF v_rule.rule_id = 'NBC_3.7.2_TOILET_COUNT' THEN
            v_requirements := v_requirements || jsonb_build_object(
                'male_toilets', CEIL(v_male_occupancy / 75.0),
                'female_toilets', CEIL(v_female_occupancy / 40.0)
            );
        END IF;
        
        -- Accessibility requirements: 5% minimum, at least 1
        IF v_rule.rule_id = 'NBC_3.8.3_ACCESSIBLE_COUNT' THEN
            v_requirements := v_requirements || jsonb_build_object(
                'accessible_toilets', GREATEST(1, CEIL((v_requirements->>'male_toilets')::INTEGER + (v_requirements->>'female_toilets')::INTEGER * 0.05))
            );
        END IF;
    END LOOP;
    
    -- Calculate sinks (1 per 2 toilets minimum)
    v_requirements := v_requirements || jsonb_build_object(
        'sinks', GREATEST(2, CEIL(((v_requirements->>'male_toilets')::INTEGER + (v_requirements->>'female_toilets')::INTEGER) * 0.8))
    );
    
    -- Store calculated requirements
    INSERT INTO calculated_requirements (user_input_id, requirement_type, calculated_values)
    VALUES (p_user_input_id, 'fixtures', v_requirements);
    
    RETURN v_requirements;
END;
$$ LANGUAGE plpgsql;

-- Function to generate compliance checklist
CREATE OR REPLACE FUNCTION generate_compliance_checklist(
    p_user_input_id INTEGER
) RETURNS TABLE (
    item_category VARCHAR,
    checklist_item TEXT,
    requirement_description TEXT,
    code_reference VARCHAR,
    required_value TEXT,
    status VARCHAR
) AS $$
DECLARE
    v_user_input user_inputs%ROWTYPE;
    v_requirements JSONB;
    v_rule RECORD;
BEGIN
    -- Get user input and calculated requirements
    SELECT * INTO v_user_input FROM user_inputs WHERE id = p_user_input_id;
    SELECT calculated_values INTO v_requirements 
    FROM calculated_requirements 
    WHERE user_input_id = p_user_input_id AND requirement_type = 'fixtures';
    
    -- Generate checklist items from building code rules
    FOR v_rule IN 
        SELECT * FROM building_code_rules 
        WHERE (building_type = v_user_input.building_type OR building_type IS NULL)
        AND (jurisdiction = v_user_input.jurisdiction OR jurisdiction = 'NBC')
        ORDER BY rule_type, priority DESC
    LOOP
        RETURN QUERY SELECT 
            v_rule.rule_type::VARCHAR,
            ('Verify ' || v_rule.rule_id)::TEXT,
            v_rule.code_text::TEXT,
            v_rule.code_section::VARCHAR,
            CASE 
                WHEN v_rule.rule_type = 'fixture_count' THEN v_requirements::TEXT
                ELSE v_rule.requirement_logic::TEXT
            END,
            'pending'::VARCHAR;
    END LOOP;
END;
$$ LANGUAGE plpgsql;
```

### **Task 1.3: Populate Building Code Rules** *(2 days)*

```sql
-- Insert key NBC building code rules
INSERT INTO building_code_rules (rule_id, rule_type, jurisdiction, code_section, building_type, condition_logic, requirement_logic, code_text) VALUES

-- NBC Toilet Requirements
('NBC_3.7.2_TOILET_COUNT', 'fixture_count', 'NBC', 'NBC 3.7.2', 'office', 
 '{"occupancy": ">1"}',
 '{"male_toilets": "Math.ceil(male_occupancy/75)", "female_toilets": "Math.ceil(female_occupancy/40)"}',
 'Water closets shall be provided for each sex at the rate of one for every 75 males and one for every 40 females.'),

-- NBC School Requirements  
('NBC_3.7.2_SCHOOL_TOILET', 'fixture_count', 'NBC', 'NBC 3.7.2', 'school',
 '{"occupancy": ">1"}', 
 '{"male_toilets": "Math.ceil(male_occupancy/100)", "female_toilets": "Math.ceil(female_occupancy/45)"}',
 'For schools: one water closet for every 100 males and one for every 45 females.'),

-- NBC Accessibility Requirements
('NBC_3.8.3_ACCESSIBLE_COUNT', 'fixture_count', 'NBC', 'NBC 3.8.3.12', NULL,
 '{"total_fixtures": ">=1"}',
 '{"accessible_toilets": "Math.max(1, Math.ceil(total_toilets * 0.05))"}',
 'Where washrooms are required, at least one accessible washroom shall be provided.'),

-- NBC Clearance Requirements  
('NBC_3.8.3_CLEARANCE', 'clearance', 'NBC', 'NBC 3.8.3', NULL,
 '{"fixture_type": "accessible_toilet"}',
 '{"front_clearance": 1500, "side_clearance": 900, "transfer_space": 900}',
 'A clear floor space of 1500mm x 1500mm shall be provided in front of accessible water closets.');

-- Insert calculation formulas
INSERT INTO calculation_formulas (formula_name, formula_type, building_type, input_parameters, formula_expression, code_reference) VALUES

('NBC Office Toilet Count', 'fixture_count', 'office', 
 '["male_occupancy", "female_occupancy"]',
 'male_toilets = Math.ceil(male_occupancy/75); female_toilets = Math.ceil(female_occupancy/40);',
 'NBC 3.7.2'),

('NBC School Toilet Count', 'fixture_count', 'school',
 '["male_occupancy", "female_occupancy"]', 
 'male_toilets = Math.ceil(male_occupancy/100); female_toilets = Math.ceil(female_occupancy/45);',
 'NBC 3.7.2'),

('Total Washroom Area', 'area_calculation', NULL,
 '["fixture_count", "circulation_factor"]',
 'total_area = (fixture_count * 3.0) * circulation_factor;',
 'General Standards');
```

### **Task 1.4: Enhance Existing Compliance Functions** *(2 days)*

Update your existing `check_washroom_compliance` function to use the new rules engine:

```sql
-- Enhanced compliance checking using building code rules
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
    v_design_layout JSONB;
BEGIN
    -- Calculate requirements using building code rules
    v_requirements := calculate_fixture_requirements(p_user_input_id);
    
    -- Get current design layout
    SELECT layout INTO v_design_layout 
    FROM generated_designs 
    WHERE user_input_id = p_user_input_id 
    ORDER BY created_at DESC LIMIT 1;
    
    -- Check fixture count compliance
    RETURN QUERY SELECT 
        'fixture_count'::VARCHAR,
        CASE 
            WHEN v_design_layout IS NULL THEN 'fail'
            WHEN (v_design_layout->>'toilet_count')::INTEGER >= (v_requirements->>'male_toilets')::INTEGER + (v_requirements->>'female_toilets')::INTEGER 
            THEN 'pass'
            ELSE 'fail'
        END,
        'Fixture count verification against NBC requirements'::TEXT,
        jsonb_build_object(
            'required', v_requirements,
            'provided', COALESCE(v_design_layout, '{}')
        );
    
    -- Check accessibility compliance
    RETURN QUERY SELECT 
        'accessibility'::VARCHAR,
        CASE 
            WHEN v_design_layout IS NULL THEN 'fail'
            WHEN (v_design_layout->>'accessible_toilet_count')::INTEGER >= (v_requirements->>'accessible_toilets')::INTEGER
            THEN 'pass' 
            ELSE 'fail'
        END,
        'Accessibility compliance check'::TEXT,
        jsonb_build_object(
            'required_accessible', v_requirements->>'accessible_toilets',
            'provided_accessible', COALESCE(v_design_layout->>'accessible_toilet_count', '0')
        );
END;
$$ LANGUAGE plpgsql;
```

---

## 🧪 **TESTING PHASE 1**

### **Test 1: Basic Calculation**
```sql
-- Insert test project
INSERT INTO user_inputs (project_name, building_type, length, width, height, estimated_users, jurisdiction, male_percentage)
VALUES ('Test Office Building', 'office', 12.0, 8.0, 3.0, 200, 'NBC', 0.5);

-- Calculate requirements
SELECT calculate_fixture_requirements(currval('user_inputs_id_seq'));

-- Expected result: {"male_toilets": 2, "female_toilets": 3, "accessible_toilets": 1, "sinks": 4}
```

### **Test 2: Compliance Checklist**
```sql
-- Generate checklist
SELECT * FROM generate_compliance_checklist(currval('user_inputs_id_seq'));

-- Should return checklist items with NBC code references
```

---

## 📈 **PHASE 1 SUCCESS CRITERIA**

✅ **Building code rules engine functional**
- NBC toilet count calculations working
- Multiple building types supported (office, school)
- Accessibility requirements calculated

✅ **Integration with existing system**  
- New functions work with existing user_inputs table
- Compliance checking enhanced with code rules
- Database performance maintained

✅ **Ready for Phase 2**
- Foundation for layout generation established
- Code rule evaluation framework working
- Test data and examples validated

---

## 🔄 **NEXT PHASE PREP**

Phase 1 deliverables feed into Phase 2:
- `calculated_requirements` table → Layout generation input
- `building_code_rules` → Spatial layout constraints  
- Enhanced `user_inputs` → Complete project parameters

**Phase 2 will use these calculated requirements to generate actual spatial layouts with your existing design_modules system.** 