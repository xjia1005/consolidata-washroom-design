# 🎯 High-Accuracy Public Washroom System Workflow Implementation

## 🔄 **Complete Logic Workflow for Maximum Accuracy**

Based on your comprehensive workflow specification, here's the implementation plan that ensures:
- ✅ **High accuracy**
- ✅ **No missing clauses** 
- ✅ **Traceable logic**
- ✅ **Future scalability**

---

## 📊 **Enhanced 4-Table Architecture**

### **Table 1: `component` (Individual Washroom Fixtures)**
```sql
CREATE TABLE component (
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
```

### **Table 2: `component_assembly` (Functional Units)**
```sql
CREATE TABLE component_assembly (
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
```

### **Table 3: `context_logic_rule` (Input-Triggered Rules)**
```sql
CREATE TABLE context_logic_rule (
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
```

### **Table 4: `building_code_clause` (Complete Clause Database)**
```sql
CREATE TABLE building_code_clause (
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
```

---

## 🔄 **Step-by-Step Implementation Workflow**

### **STEP 1: Enhanced User Input Processing**

```python
def process_user_inputs(user_data):
    """
    Enhanced input processing with validation and normalization
    """
    # Normalize and validate inputs
    normalized_inputs = {
        "occupancy_type": user_data.get("building_type", "office").lower(),
        "room_dimensions": {
            "length": float(user_data.get("room_length", 10.0)),
            "width": float(user_data.get("room_width", 8.0)),
            "height": float(user_data.get("room_height", 3.0))
        },
        "total_occupants": int(user_data.get("occupancy_load", 50)),
        "accessibility_required": user_data.get("accessibility_level", "basic") != "basic",
        "jurisdiction": user_data.get("jurisdiction", "NBC"),
        "special_requirements": user_data.get("special_requirements", []),
        "fixture_preferences": user_data.get("fixture_preferences", {})
    }
    
    # Calculate derived values
    normalized_inputs["room_area"] = (
        normalized_inputs["room_dimensions"]["length"] * 
        normalized_inputs["room_dimensions"]["width"]
    )
    normalized_inputs["occupancy_density"] = (
        normalized_inputs["total_occupants"] / normalized_inputs["room_area"]
    )
    
    return normalized_inputs
```

### **STEP 2: Context Logic Rule Matching Engine**

```python
def match_context_logic_rules(normalized_inputs):
    """
    Match user inputs to applicable context logic rules
    Ensures no rules are missed and all conditions are properly evaluated
    """
    applicable_rules = []
    
    # Query all rules for the jurisdiction
    cursor.execute("""
        SELECT * FROM context_logic_rule 
        WHERE jurisdiction = ? OR jurisdiction = 'ALL'
        ORDER BY priority DESC
    """, (normalized_inputs["jurisdiction"],))
    
    all_rules = cursor.fetchall()
    
    for rule in all_rules:
        # Parse trigger condition JSON
        trigger_condition = json.loads(rule["trigger_condition"])
        
        # Evaluate condition against inputs
        if evaluate_trigger_condition(trigger_condition, normalized_inputs):
            applicable_rules.append({
                "rule": rule,
                "match_reason": generate_match_explanation(trigger_condition, normalized_inputs),
                "required_components": json.loads(rule["required_component_ids"] or "[]"),
                "required_assemblies": json.loads(rule["required_assembly_ids"] or "[]"),
                "required_clauses": json.loads(rule["required_clause_ids"] or "[]")
            })
    
    return applicable_rules

def evaluate_trigger_condition(condition, inputs):
    """
    Safely evaluate complex trigger conditions
    """
    # Example conditions:
    # {"occupancy_type": "daycare", "total_occupants": ">25"}
    # {"accessibility_required": true, "room_area": "<20"}
    # {"AND": [{"building_type": "school"}, {"occupancy_density": ">2.0"}]}
    
    if isinstance(condition, dict):
        if "AND" in condition:
            return all(evaluate_trigger_condition(sub_cond, inputs) for sub_cond in condition["AND"])
        elif "OR" in condition:
            return any(evaluate_trigger_condition(sub_cond, inputs) for sub_cond in condition["OR"])
        else:
            # Simple key-value conditions
            for key, expected_value in condition.items():
                actual_value = inputs.get(key)
                if not evaluate_single_condition(actual_value, expected_value):
                    return False
            return True
    
    return False

def evaluate_single_condition(actual, expected):
    """
    Evaluate single condition with operators
    """
    if isinstance(expected, str) and expected.startswith(">"):
        return float(actual) > float(expected[1:])
    elif isinstance(expected, str) and expected.startswith("<"):
        return float(actual) < float(expected[1:])
    elif isinstance(expected, str) and expected.startswith(">="):
        return float(actual) >= float(expected[2:])
    elif isinstance(expected, str) and expected.startswith("<="):
        return float(actual) <= float(expected[2:])
    else:
        return actual == expected
```

### **STEP 3: Component Assembly Expansion**

```python
def expand_component_assemblies(applicable_rules):
    """
    Expand all required assemblies into individual components
    Ensures complete component coverage
    """
    all_required_components = set()
    all_required_assemblies = []
    assembly_expansion_log = []
    
    # Collect all required assemblies
    for rule_match in applicable_rules:
        for assembly_id in rule_match["required_assemblies"]:
            # Get assembly details
            cursor.execute("""
                SELECT * FROM component_assembly WHERE assembly_code = ?
            """, (assembly_id,))
            assembly = cursor.fetchone()
            
            if assembly:
                all_required_assemblies.append(assembly)
                
                # Expand to individual components
                component_ids = json.loads(assembly["component_ids"])
                for component_id in component_ids:
                    all_required_components.add(component_id)
                
                assembly_expansion_log.append({
                    "assembly": assembly["name"],
                    "components": component_ids,
                    "reason": f"Required by rule: {rule_match['rule']['rule_name']}"
                })
    
    # Add directly required components
    for rule_match in applicable_rules:
        for component_id in rule_match["required_components"]:
            all_required_components.add(component_id)
    
    return {
        "required_components": list(all_required_components),
        "required_assemblies": all_required_assemblies,
        "expansion_log": assembly_expansion_log
    }
```

### **STEP 4: Building Code Clause Collection**

```python
def collect_building_code_clauses(component_expansion, applicable_rules, jurisdiction):
    """
    Collect all building code clauses related to components and rules
    Ensures complete clause coverage with traceability
    """
    all_clause_ids = set()
    clause_collection_log = []
    
    # 1. Clauses directly required by rules
    for rule_match in applicable_rules:
        for clause_id in rule_match["required_clauses"]:
            all_clause_ids.add(clause_id)
            clause_collection_log.append({
                "clause_id": clause_id,
                "source": "direct_rule_requirement",
                "rule": rule_match["rule"]["rule_name"],
                "reason": rule_match["match_reason"]
            })
    
    # 2. Clauses linked to required components
    for component_id in component_expansion["required_components"]:
        cursor.execute("""
            SELECT bcc.* FROM building_code_clause bcc
            WHERE JSON_EXTRACT(bcc.applies_to_components, '$') LIKE ?
            AND bcc.jurisdiction = ?
        """, (f'%{component_id}%', jurisdiction))
        
        component_clauses = cursor.fetchall()
        for clause in component_clauses:
            all_clause_ids.add(clause["clause_code"])
            clause_collection_log.append({
                "clause_id": clause["clause_code"],
                "source": "component_linkage",
                "component": component_id,
                "clause_title": clause["clause_title"]
            })
    
    # 3. Get full clause details
    clause_details = []
    for clause_id in all_clause_ids:
        cursor.execute("""
            SELECT * FROM building_code_clause WHERE clause_code = ?
        """, (clause_id,))
        clause = cursor.fetchone()
        if clause:
            clause_details.append(clause)
    
    return {
        "clauses": clause_details,
        "collection_log": clause_collection_log,
        "total_clauses": len(clause_details)
    }
```

### **STEP 5: Logic Validation Pass (Accuracy Layer)**

```python
def validate_logic_completeness(component_expansion, clause_collection, applicable_rules):
    """
    Comprehensive validation to ensure no missing clauses or components
    """
    validation_results = {
        "is_complete": True,
        "warnings": [],
        "errors": [],
        "coverage_map": {},
        "recommendations": []
    }
    
    # 1. Component Coverage Check
    required_components = set(component_expansion["required_components"])
    components_with_clauses = set()
    
    for clause in clause_collection["clauses"]:
        if clause["applies_to_components"]:
            component_list = json.loads(clause["applies_to_components"])
            components_with_clauses.update(component_list)
    
    uncovered_components = required_components - components_with_clauses
    if uncovered_components:
        validation_results["warnings"].append({
            "type": "uncovered_components",
            "message": f"Components without linked clauses: {list(uncovered_components)}",
            "severity": "medium"
        })
    
    # 2. Jurisdiction Consistency Check
    jurisdictions_found = set(clause["jurisdiction"] for clause in clause_collection["clauses"])
    if len(jurisdictions_found) > 1:
        validation_results["warnings"].append({
            "type": "mixed_jurisdictions",
            "message": f"Multiple jurisdictions found: {list(jurisdictions_found)}",
            "severity": "high"
        })
    
    # 3. Rule Application Completeness
    for rule_match in applicable_rules:
        rule_clauses = set(rule_match["required_clauses"])
        found_clauses = set(clause["clause_code"] for clause in clause_collection["clauses"])
        missing_clauses = rule_clauses - found_clauses
        
        if missing_clauses:
            validation_results["errors"].append({
                "type": "missing_rule_clauses",
                "rule": rule_match["rule"]["rule_name"],
                "missing_clauses": list(missing_clauses),
                "severity": "critical"
            })
            validation_results["is_complete"] = False
    
    # 4. Generate Coverage Map
    validation_results["coverage_map"] = {
        "total_components_required": len(required_components),
        "components_with_clauses": len(components_with_clauses),
        "coverage_percentage": (len(components_with_clauses) / len(required_components)) * 100 if required_components else 100,
        "total_clauses_found": len(clause_collection["clauses"]),
        "rules_applied": len(applicable_rules)
    }
    
    return validation_results
```

### **STEP 6: Generate Final Compliance Checklist**

```python
def generate_compliance_checklist(clause_collection, component_expansion, validation_results):
    """
    Generate comprehensive compliance checklist with full traceability
    """
    checklist_sections = []
    
    # Group clauses by category
    clause_categories = {}
    for clause in clause_collection["clauses"]:
        category = determine_clause_category(clause)
        if category not in clause_categories:
            clause_categories[category] = []
        clause_categories[category].append(clause)
    
    # Generate sections
    for category, clauses in clause_categories.items():
        section_items = []
        
        for clause in clauses:
            # Find why this clause is required
            requirement_reason = find_clause_requirement_reason(
                clause["clause_code"], 
                clause_collection["collection_log"]
            )
            
            # Determine affected components
            affected_components = []
            if clause["applies_to_components"]:
                component_codes = json.loads(clause["applies_to_components"])
                for comp_code in component_codes:
                    if comp_code in component_expansion["required_components"]:
                        affected_components.append(comp_code)
            
            section_items.append({
                "clause_id": clause["clause_code"],
                "clause_number": clause["clause_number"],
                "title": clause["clause_title"],
                "requirement": clause["clause_text_en"],
                "code_reference": f"{clause['jurisdiction']} {clause['clause_number']}",
                "page_reference": clause["page_number"],
                "why_required": requirement_reason,
                "affected_components": affected_components,
                "priority": clause["enforcement_level"],
                "status": "pending",
                "verification_method": determine_verification_method(clause),
                "compliance_notes": ""
            })
        
        checklist_sections.append({
            "category": category,
            "title": format_category_title(category),
            "icon": get_category_icon(category),
            "items": section_items,
            "total_items": len(section_items)
        })
    
    # Add validation summary
    checklist_summary = {
        "project_info": {
            "total_sections": len(checklist_sections),
            "total_items": sum(section["total_items"] for section in checklist_sections),
            "critical_items": sum(1 for section in checklist_sections 
                                for item in section["items"] 
                                if item["priority"] == "critical"),
            "coverage_score": validation_results["coverage_map"]["coverage_percentage"]
        },
        "validation_status": validation_results,
        "sections": checklist_sections
    }
    
    return checklist_summary
```

### **STEP 7: Enhanced 2D Layout Generation**

```python
def generate_2d_layout_with_compliance(component_expansion, room_dimensions, clause_collection):
    """
    Generate 2D layout with real-time compliance checking
    """
    layout_engine = ComplianceAwareLayoutEngine(
        room_dimensions=room_dimensions,
        clauses=clause_collection["clauses"]
    )
    
    # 1. Position required assemblies
    positioned_assemblies = []
    for assembly in component_expansion["required_assemblies"]:
        position = layout_engine.find_optimal_position(assembly)
        positioned_assemblies.append({
            "assembly": assembly,
            "position": position,
            "compliance_status": layout_engine.check_assembly_compliance(assembly, position)
        })
    
    # 2. Validate spatial requirements
    spatial_validation = layout_engine.validate_spatial_compliance()
    
    # 3. Generate layout visualization
    layout_data = {
        "room_dimensions": room_dimensions,
        "positioned_assemblies": positioned_assemblies,
        "spatial_validation": spatial_validation,
        "compliance_score": calculate_layout_compliance_score(positioned_assemblies),
        "layout_efficiency": calculate_space_efficiency(positioned_assemblies, room_dimensions),
        "accessibility_paths": layout_engine.generate_accessibility_paths(),
        "clearance_zones": layout_engine.calculate_clearance_zones()
    }
    
    return layout_data
```

---

## 🎯 **Integration with Existing Consolidata System**

### **Phase 1: Database Enhancement** (Week 1-2)
1. **Extend existing SQLite database** with the 4 enhanced tables
2. **Populate with comprehensive NBC/Alberta/Ontario clause data**
3. **Create sample context logic rules** for common scenarios
4. **Add component and assembly definitions**

### **Phase 2: Logic Engine Implementation** (Week 3-4)
1. **Implement the 7-step workflow** in Python
2. **Add validation and accuracy checking**
3. **Create traceability logging system**
4. **Integrate with existing `/api/complete-analysis` endpoint**

### **Phase 3: Frontend Integration** (Week 5-6)
1. **Enhance existing Consolidata frontend** with detailed checklist display
2. **Add 2D layout visualization**
3. **Implement export functionality** (PDF/TXT/DXF)
4. **Add real-time validation feedback**

---

## 🚀 **Next Steps**

1. **Which component should we implement first?**
   - Enhanced database schema with the 4 tables?
   - Context logic rule matching engine?
   - Compliance checklist generation?

2. **Sample data creation:**
   - Should we start with NBC office building scenarios?
   - Focus on accessibility compliance rules?
   - Include daycare/school specific requirements?

3. **Testing approach:**
   - Create test cases for each step of the workflow?
   - Validate against known building code scenarios?
   - Set up automated accuracy checking?

This high-accuracy workflow ensures **complete building code coverage** with **full traceability** while integrating seamlessly with your existing Consolidata system! 🏗️✨ 