-- EXACT TEXT COMPLIANCE FUNCTIONS
-- Generate checklists using exact original building code language

-- 1. ENHANCED CHECKLIST GENERATION (Uses exact original text)
CREATE OR REPLACE FUNCTION generate_exact_text_compliance_checklist(
    p_user_input_id INTEGER,
    p_jurisdiction_id INTEGER DEFAULT NULL,
    p_language_code VARCHAR(10) DEFAULT 'en'
) RETURNS TABLE (
    item_sequence INTEGER,
    item_category VARCHAR,
    code_reference VARCHAR,
    exact_original_text TEXT,
    calculated_requirement TEXT,
    compliance_status VARCHAR,
    explanation TEXT,
    legal_authority VARCHAR
) AS $$
DECLARE
    v_user_input user_inputs%ROWTYPE;
    v_jurisdiction_id INTEGER;
    v_requirements JSONB;
    v_checklist_item RECORD;
    v_exact_text TEXT;
    v_calculated_value TEXT;
    v_compliance_status VARCHAR;
BEGIN
    -- Get user input and determine jurisdiction
    SELECT * INTO v_user_input FROM user_inputs WHERE id = p_user_input_id;
    v_jurisdiction_id := COALESCE(p_jurisdiction_id, v_user_input.selected_jurisdiction_id, 1);
    
    -- Get calculated requirements
    v_requirements := apply_building_code_rules(p_user_input_id, v_jurisdiction_id);
    
    -- Generate checklist items using exact original text
    FOR v_checklist_item IN
        SELECT 
            ci.item_sequence,
            ci.item_category,
            cs.section_identifier,
            CASE 
                WHEN p_language_code = 'fr' AND cs.original_text_fr IS NOT NULL 
                THEN cs.original_text_fr
                ELSE cs.original_text_en
            END as exact_text,
            ci.explanation_text,
            ci.legal_authority,
            ci.compliance_criteria,
            bcr.rule_uid,
            bcr.rule_category
        FROM compliance_checklist_items ci
        JOIN code_sections cs ON ci.code_section_id = cs.id
        LEFT JOIN building_code_rules bcr ON ci.calculation_rule_id = bcr.id
        WHERE ci.jurisdiction_id = v_jurisdiction_id
        AND (ci.building_type = v_user_input.building_type OR ci.building_type = '*')
        ORDER BY ci.item_sequence
    LOOP
        -- Get calculated value for this requirement
        v_calculated_value := CASE 
            WHEN v_checklist_item.rule_category IS NOT NULL AND v_requirements ? v_checklist_item.rule_category
            THEN format('Required: %s', v_requirements->>v_checklist_item.rule_category)
            ELSE 'See building code requirements'
        END;
        
        -- Determine compliance status
        v_compliance_status := CASE 
            WHEN v_checklist_item.rule_category IS NOT NULL AND v_requirements ? v_checklist_item.rule_category
            THEN 'calculated'
            ELSE 'requires_review'
        END;
        
        -- Return the checklist item with exact original text
        RETURN QUERY SELECT 
            v_checklist_item.item_sequence,
            v_checklist_item.item_category::VARCHAR,
            v_checklist_item.section_identifier::VARCHAR,
            v_checklist_item.exact_text,
            v_calculated_value::TEXT,
            v_compliance_status::VARCHAR,
            v_checklist_item.explanation_text,
            v_checklist_item.legal_authority::VARCHAR;
    END LOOP;
    
    -- Audit trail - record what exact text was used
    INSERT INTO text_compliance_audit (
        user_input_id, 
        used_section_ids, 
        exact_text_hash,
        disclaimer_included
    ) VALUES (
        p_user_input_id,
        ARRAY(SELECT DISTINCT code_section_id FROM compliance_checklist_items 
              WHERE jurisdiction_id = v_jurisdiction_id),
        md5(string_agg(exact_text, '' ORDER BY item_sequence)),
        TRUE
    );
END;
$$ LANGUAGE plpgsql;

-- 2. EXACT TEXT IMPORT FUNCTION
CREATE OR REPLACE FUNCTION import_exact_building_code_text(
    p_jurisdiction_code VARCHAR(10),
    p_section_data JSONB
) RETURNS INTEGER AS $$
DECLARE
    v_jurisdiction_id INTEGER;
    v_section_id INTEGER;
    v_section JSONB;
    v_fragment JSONB;
    v_import_count INTEGER := 0;
BEGIN
    -- Get jurisdiction
    SELECT id INTO v_jurisdiction_id 
    FROM jurisdictions 
    WHERE jurisdiction_code = p_jurisdiction_code;
    
    IF v_jurisdiction_id IS NULL THEN
        RAISE EXCEPTION 'Jurisdiction % not found', p_jurisdiction_code;
    END IF;
    
    -- Process each section
    FOR v_section IN SELECT * FROM jsonb_array_elements(p_section_data->'sections')
    LOOP
        -- Insert code section with exact original text
        INSERT INTO code_sections (
            jurisdiction_id,
            section_identifier,
            section_title,
            original_text_en,
            original_text_fr,
            source_document_title,
            source_document_page,
            source_document_url,
            text_extraction_method,
            applies_to_building_types,
            legal_status
        ) VALUES (
            v_jurisdiction_id,
            v_section->>'identifier',
            v_section->>'title',
            v_section->>'exact_text_en', -- EXACT original English text
            v_section->>'exact_text_fr', -- EXACT original French text  
            v_section->>'source_document',
            (v_section->>'page_number')::INTEGER,
            v_section->>'official_url',
            COALESCE(v_section->>'extraction_method', 'manual'),
            ARRAY(SELECT jsonb_array_elements_text(v_section->'building_types')),
            COALESCE(v_section->>'legal_status', 'active')
        ) RETURNING id INTO v_section_id;
        
        -- Process text fragments if provided
        IF v_section ? 'text_fragments' THEN
            FOR v_fragment IN SELECT * FROM jsonb_array_elements(v_section->'text_fragments')
            LOOP
                INSERT INTO code_text_fragments (
                    code_section_id,
                    fragment_type,
                    fragment_sequence,
                    exact_text_en,
                    exact_text_fr,
                    applies_to_calculation,
                    applies_to_compliance,
                    is_mandatory,
                    contains_numerical_requirement
                ) VALUES (
                    v_section_id,
                    v_fragment->>'type',
                    (v_fragment->>'sequence')::INTEGER,
                    v_fragment->>'exact_text_en',
                    v_fragment->>'exact_text_fr',
                    COALESCE((v_fragment->>'for_calculation')::BOOLEAN, FALSE),
                    COALESCE((v_fragment->>'for_compliance')::BOOLEAN, TRUE),
                    COALESCE((v_fragment->>'mandatory')::BOOLEAN, TRUE),
                    COALESCE((v_fragment->>'has_numbers')::BOOLEAN, FALSE)
                );
            END LOOP;
        END IF;
        
        v_import_count := v_import_count + 1;
    END LOOP;
    
    RETURN v_import_count;
END;
$$ LANGUAGE plpgsql;

-- 3. TEXT VERIFICATION FUNCTION
CREATE OR REPLACE FUNCTION verify_exact_text_accuracy(
    p_section_id INTEGER,
    p_verified_by VARCHAR(255)
) RETURNS BOOLEAN AS $$
DECLARE
    v_section_exists BOOLEAN;
BEGIN
    -- Check if section exists and has original text
    SELECT EXISTS(
        SELECT 1 FROM code_sections 
        WHERE id = p_section_id 
        AND original_text_en IS NOT NULL 
        AND length(original_text_en) > 0
    ) INTO v_section_exists;
    
    IF NOT v_section_exists THEN
        RETURN FALSE;
    END IF;
    
    -- Mark as verified
    UPDATE code_sections SET
        text_verified_by = p_verified_by,
        text_verified_date = CURRENT_TIMESTAMP,
        legal_status = 'active'
    WHERE id = p_section_id;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- 4. GENERATE COMPLIANCE REPORT WITH EXACT TEXT
CREATE OR REPLACE FUNCTION generate_compliance_report_with_exact_text(
    p_user_input_id INTEGER,
    p_jurisdiction_id INTEGER DEFAULT NULL,
    p_include_legal_disclaimers BOOLEAN DEFAULT TRUE
) RETURNS TEXT AS $$
DECLARE
    v_report TEXT := '';
    v_checklist_item RECORD;
    v_jurisdiction_name VARCHAR(255);
    v_user_input user_inputs%ROWTYPE;
    v_disclaimer TEXT;
BEGIN
    -- Get jurisdiction and user input info
    SELECT * INTO v_user_input FROM user_inputs WHERE id = p_user_input_id;
    SELECT jurisdiction_name INTO v_jurisdiction_name 
    FROM jurisdictions WHERE id = COALESCE(p_jurisdiction_id, 1);
    
    -- Generate report header
    v_report := format(E'BUILDING CODE COMPLIANCE CHECKLIST\n');
    v_report := v_report || format(E'Generated for: %s\n', v_user_input.project_name);
    v_report := v_report || format(E'Building Type: %s\n', v_user_input.building_type);
    v_report := v_report || format(E'Occupancy: %s persons\n', v_user_input.estimated_users);
    v_report := v_report || format(E'Applicable Code: %s\n', v_jurisdiction_name);
    v_report := v_report || format(E'Generated: %s\n\n', CURRENT_TIMESTAMP);
    
    -- Add legal disclaimer if requested
    IF p_include_legal_disclaimers THEN
        v_disclaimer := E'LEGAL DISCLAIMER: This checklist references exact text from the applicable building code. ';
        v_disclaimer := v_disclaimer || E'Users must verify current code requirements with local authorities. ';
        v_disclaimer := v_disclaimer || E'This system provides guidance only and does not replace professional consultation.\n\n';
        v_report := v_report || v_disclaimer;
    END IF;
    
    -- Generate checklist items with exact original text
    FOR v_checklist_item IN 
        SELECT * FROM generate_exact_text_compliance_checklist(p_user_input_id, p_jurisdiction_id)
        ORDER BY item_sequence
    LOOP
        v_report := v_report || format(E'%s. %s\n', 
            v_checklist_item.item_sequence, 
            upper(v_checklist_item.item_category));
        
        v_report := v_report || format(E'   Code Reference: %s\n', 
            v_checklist_item.code_reference);
        
        v_report := v_report || format(E'   Requirement: "%s"\n', 
            v_checklist_item.exact_original_text);
        
        v_report := v_report || format(E'   Calculated: %s\n', 
            v_checklist_item.calculated_requirement);
        
        v_report := v_report || format(E'   Status: %s\n', 
            v_checklist_item.compliance_status);
        
        IF v_checklist_item.explanation IS NOT NULL THEN
            v_report := v_report || format(E'   Explanation: %s\n', 
                v_checklist_item.explanation);
        END IF;
        
        v_report := v_report || format(E'   Authority: %s\n\n', 
            v_checklist_item.legal_authority);
    END LOOP;
    
    -- Add footer with verification info
    v_report := v_report || E'---\n';
    v_report := v_report || E'This checklist uses exact text from the applicable building code.\n';
    v_report := v_report || format(E'Always consult the official %s for complete requirements.\n', v_jurisdiction_name);
    
    RETURN v_report;
END;
$$ LANGUAGE plpgsql; 