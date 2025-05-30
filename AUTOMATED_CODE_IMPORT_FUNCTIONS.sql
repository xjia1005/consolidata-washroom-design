-- AUTOMATED BUILDING CODE IMPORT & PROCESSING FUNCTIONS
-- Handles automatic conversion of building codes into database rules

-- 1. JURISDICTION DETECTION FUNCTION
CREATE OR REPLACE FUNCTION detect_user_jurisdiction(
    p_ip_address INET,
    p_user_agent TEXT DEFAULT NULL
) RETURNS INTEGER AS $$
DECLARE
    v_jurisdiction_id INTEGER;
    v_country_code VARCHAR(3);
    v_region VARCHAR(100);
BEGIN
    -- IP-based geolocation (simplified - integrate with real geolocation API)
    -- This would normally call an external geolocation service
    v_country_code := CASE 
        WHEN p_ip_address <<= '192.168.0.0/16'::inet THEN 'CAN' -- Local testing
        WHEN p_ip_address <<= '10.0.0.0/8'::inet THEN 'CAN'     -- Private networks default to Canada
        ELSE 'CAN' -- Default for development
    END;
    
    -- For production, replace with actual geolocation logic:
    -- SELECT country_code, region INTO v_country_code, v_region 
    -- FROM geolocate_ip(p_ip_address);
    
    -- Find matching jurisdiction
    SELECT id INTO v_jurisdiction_id
    FROM jurisdictions 
    WHERE country_code = v_country_code 
    AND region_code IS NULL -- Prefer national codes over regional
    AND auto_detect_enabled = TRUE
    ORDER BY priority_order DESC
    LIMIT 1;
    
    -- If no national code found, try regional
    IF v_jurisdiction_id IS NULL THEN
        SELECT id INTO v_jurisdiction_id
        FROM jurisdictions 
        WHERE country_code = v_country_code 
        AND auto_detect_enabled = TRUE
        ORDER BY priority_order DESC
        LIMIT 1;
    END IF;
    
    RETURN COALESCE(v_jurisdiction_id, 1); -- Default to NBC if nothing found
END;
$$ LANGUAGE plpgsql;

-- 2. FLEXIBLE RULE APPLICATION FUNCTION
CREATE OR REPLACE FUNCTION apply_building_code_rules(
    p_user_input_id INTEGER,
    p_jurisdiction_id INTEGER DEFAULT NULL
) RETURNS JSONB AS $$
DECLARE
    v_user_input user_inputs%ROWTYPE;
    v_jurisdiction_id INTEGER;
    v_results JSONB := '{}';
    v_applied_rules JSONB := '[]';
    v_rule RECORD;
    v_formula RECORD;
    v_calculated_value INTEGER;
    v_male_occupancy INTEGER;
    v_female_occupancy INTEGER;
    v_total_fixtures INTEGER := 0;
BEGIN
    -- Get user input
    SELECT * INTO v_user_input FROM user_inputs WHERE id = p_user_input_id;
    
    -- Determine jurisdiction
    v_jurisdiction_id := COALESCE(
        p_jurisdiction_id,
        v_user_input.selected_jurisdiction_id,
        v_user_input.detected_jurisdiction_id,
        1 -- Default to NBC
    );
    
    -- Calculate gender distribution
    v_male_occupancy := FLOOR(v_user_input.estimated_users * COALESCE(v_user_input.male_percentage, 0.5));
    v_female_occupancy := v_user_input.estimated_users - v_male_occupancy;
    
    -- Apply all applicable rules for this jurisdiction
    FOR v_rule IN 
        SELECT bcr.*, cf.formula_expression, cf.constants, cf.jurisdiction_variations
        FROM building_code_rules bcr
        LEFT JOIN calculation_formulas cf ON bcr.calculation_formula->>'formula_id' = cf.id::text
        WHERE bcr.jurisdiction_id = v_jurisdiction_id
        AND bcr.is_active = TRUE
        AND (
            bcr.building_types IS NULL 
            OR v_user_input.building_type = ANY(bcr.building_types)
            OR '*' = ANY(bcr.building_types)
        )
        AND (
            bcr.occupancy_range_min IS NULL 
            OR v_user_input.estimated_users >= bcr.occupancy_range_min
        )
        AND (
            bcr.occupancy_range_max IS NULL 
            OR v_user_input.estimated_users <= bcr.occupancy_range_max
        )
        ORDER BY bcr.priority DESC
    LOOP
        -- Apply the specific rule calculation
        IF v_rule.rule_type = 'fixture_count' THEN
            -- Use flexible formula evaluation
            v_calculated_value := evaluate_formula(
                v_rule.formula_expression,
                jsonb_build_object(
                    'male_occupancy', v_male_occupancy,
                    'female_occupancy', v_female_occupancy,
                    'total_occupancy', v_user_input.estimated_users,
                    'building_type', v_user_input.building_type
                ),
                v_rule.constants,
                v_rule.jurisdiction_variations->v_jurisdiction_id::text
            );
            
            -- Store result based on rule category
            v_results := v_results || jsonb_build_object(
                v_rule.rule_category, v_calculated_value
            );
            
            -- Track applied rule
            v_applied_rules := v_applied_rules || jsonb_build_object(
                'rule_uid', v_rule.rule_uid,
                'calculation', format('%s occupancy: %s = %s', 
                    v_rule.rule_category, 
                    CASE v_rule.rule_category 
                        WHEN 'male_toilet' THEN v_male_occupancy
                        WHEN 'female_toilet' THEN v_female_occupancy
                        ELSE v_user_input.estimated_users
                    END,
                    v_calculated_value),
                'code_reference', v_rule.code_section_id
            );
        END IF;
    END LOOP;
    
    -- Store results
    INSERT INTO calculated_requirements (
        user_input_id, jurisdiction_id, requirement_type, 
        calculated_values, applied_rules, confidence_score
    ) VALUES (
        p_user_input_id, v_jurisdiction_id, 'fixtures',
        v_results, v_applied_rules, 0.95
    ) ON CONFLICT (user_input_id, jurisdiction_id, requirement_type) 
    DO UPDATE SET 
        calculated_values = EXCLUDED.calculated_values,
        applied_rules = EXCLUDED.applied_rules,
        created_at = CURRENT_TIMESTAMP;
    
    RETURN v_results;
END;
$$ LANGUAGE plpgsql;

-- 3. FORMULA EVALUATION FUNCTION (Handles different calculation methods)
CREATE OR REPLACE FUNCTION evaluate_formula(
    p_formula_expression TEXT,
    p_input_values JSONB,
    p_constants JSONB,
    p_jurisdiction_overrides JSONB DEFAULT NULL
) RETURNS INTEGER AS $$
DECLARE
    v_result DECIMAL;
    v_divisor DECIMAL;
    v_building_type TEXT;
    v_occupancy INTEGER;
BEGIN
    v_building_type := p_input_values->>'building_type';
    
    -- Get jurisdiction-specific constants or fall back to defaults
    IF p_jurisdiction_overrides IS NOT NULL AND p_jurisdiction_overrides ? v_building_type THEN
        v_divisor := (p_jurisdiction_overrides->v_building_type->>'divisor')::DECIMAL;
    ELSIF p_constants ? v_building_type THEN
        v_divisor := (p_constants->v_building_type->>'divisor')::DECIMAL;
    ELSE
        v_divisor := (p_constants->>'default_divisor')::DECIMAL;
    END IF;
    
    -- Apply formula based on expression type
    IF p_formula_expression LIKE '%CEIL%' AND p_formula_expression LIKE '%/%' THEN
        -- Standard ceiling division formula: CEIL(occupancy / divisor)
        v_occupancy := CASE 
            WHEN p_input_values ? 'male_occupancy' THEN (p_input_values->>'male_occupancy')::INTEGER
            WHEN p_input_values ? 'female_occupancy' THEN (p_input_values->>'female_occupancy')::INTEGER
            ELSE (p_input_values->>'total_occupancy')::INTEGER
        END;
        
        v_result := CEIL(v_occupancy / v_divisor);
    ELSE
        -- More complex formulas can be added here
        v_result := 1; -- Default minimum
    END IF;
    
    RETURN GREATEST(1, v_result::INTEGER); -- Ensure minimum of 1
END;
$$ LANGUAGE plpgsql;

-- 4. AUTOMATED CODE IMPORT FUNCTION
CREATE OR REPLACE FUNCTION import_building_code_from_source(
    p_jurisdiction_code VARCHAR(10),
    p_import_source VARCHAR(255),
    p_source_url VARCHAR(500) DEFAULT NULL,
    p_code_data JSONB DEFAULT NULL
) RETURNS INTEGER AS $$
DECLARE
    v_jurisdiction_id INTEGER;
    v_import_job_id INTEGER;
    v_section_count INTEGER := 0;
    v_rule_count INTEGER := 0;
    v_section_data JSONB;
    v_rule_data JSONB;
BEGIN
    -- Get jurisdiction
    SELECT id INTO v_jurisdiction_id 
    FROM jurisdictions 
    WHERE jurisdiction_code = p_jurisdiction_code;
    
    IF v_jurisdiction_id IS NULL THEN
        RAISE EXCEPTION 'Jurisdiction % not found', p_jurisdiction_code;
    END IF;
    
    -- Create import job
    INSERT INTO code_import_jobs (
        jurisdiction_id, import_source, source_document_url, 
        import_status, started_at
    ) VALUES (
        v_jurisdiction_id, p_import_source, p_source_url,
        'processing', CURRENT_TIMESTAMP
    ) RETURNING id INTO v_import_job_id;
    
    -- Process code sections (if provided)
    IF p_code_data ? 'sections' THEN
        FOR v_section_data IN SELECT * FROM jsonb_array_elements(p_code_data->'sections')
        LOOP
            INSERT INTO code_sections (
                jurisdiction_id, section_identifier, section_title, 
                section_content, section_level
            ) VALUES (
                v_jurisdiction_id,
                v_section_data->>'identifier',
                v_section_data->>'title',
                v_section_data->>'content',
                COALESCE((v_section_data->>'level')::INTEGER, 1)
            );
            v_section_count := v_section_count + 1;
        END LOOP;
    END IF;
    
    -- Process building code rules (if provided)
    IF p_code_data ? 'rules' THEN
        FOR v_rule_data IN SELECT * FROM jsonb_array_elements(p_code_data->'rules')
        LOOP
            INSERT INTO building_code_rules (
                jurisdiction_id, rule_uid, rule_type, rule_category,
                building_types, condition_logic, calculation_formula,
                rule_description_en, priority
            ) VALUES (
                v_jurisdiction_id,
                format('%s_%s', p_jurisdiction_code, v_rule_data->>'rule_id'),
                v_rule_data->>'rule_type',
                v_rule_data->>'rule_category',
                CASE 
                    WHEN v_rule_data ? 'building_types' 
                    THEN ARRAY(SELECT jsonb_array_elements_text(v_rule_data->'building_types'))
                    ELSE ARRAY['*']
                END,
                v_rule_data->'condition_logic',
                v_rule_data->'calculation_formula',
                v_rule_data->>'description',
                COALESCE((v_rule_data->>'priority')::INTEGER, 50)
            );
            v_rule_count := v_rule_count + 1;
        END LOOP;
    END IF;
    
    -- Update import job
    UPDATE code_import_jobs SET
        import_status = 'completed',
        sections_imported = v_section_count,
        rules_imported = v_rule_count,
        completed_at = CURRENT_TIMESTAMP
    WHERE id = v_import_job_id;
    
    RETURN v_import_job_id;
END;
$$ LANGUAGE plpgsql;

-- 5. JURISDICTION COMPARISON FUNCTION
CREATE OR REPLACE FUNCTION compare_jurisdictions(
    p_user_input_id INTEGER,
    p_jurisdiction_codes TEXT[]
) RETURNS JSONB AS $$
DECLARE
    v_comparison JSONB := '{}';
    v_jurisdiction_code TEXT;
    v_jurisdiction_id INTEGER;
    v_results JSONB;
BEGIN
    -- Calculate requirements for each jurisdiction
    FOREACH v_jurisdiction_code IN ARRAY p_jurisdiction_codes
    LOOP
        SELECT id INTO v_jurisdiction_id 
        FROM jurisdictions 
        WHERE jurisdiction_code = v_jurisdiction_code;
        
        IF v_jurisdiction_id IS NOT NULL THEN
            v_results := apply_building_code_rules(p_user_input_id, v_jurisdiction_id);
            v_comparison := v_comparison || jsonb_build_object(v_jurisdiction_code, v_results);
        END IF;
    END LOOP;
    
    RETURN v_comparison;
END;
$$ LANGUAGE plpgsql; 