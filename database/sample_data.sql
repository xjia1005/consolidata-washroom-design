-- 🎯 Sample Data for High-Accuracy Building Code Compliance System
-- Real NBC/Alberta building code scenarios for testing

-- =====================================================
-- Sample Components (Individual Washroom Fixtures)
-- =====================================================

INSERT OR REPLACE INTO component (component_code, name, category, description, dimensions, clearance_requirements, applicable_jurisdictions, accessibility_level, cost_range, maintenance_level) VALUES

-- Standard Toilets
('TOILET_STANDARD', 'Standard Water Closet', 'toilet', 'Standard height toilet for general use', 
 '{"width": 0.8, "depth": 1.2, "height": 0.4}', 
 '{"front": 0.6, "sides": 0.15, "door_swing": 0.9}',
 '["NBC", "Alberta", "Ontario", "BC"]', 'standard', 'medium', 'standard'),

('TOILET_ACCESSIBLE', 'Accessible Water Closet', 'toilet', 'Accessible height toilet with grab bar mounting', 
 '{"width": 0.8, "depth": 1.2, "height": 0.43}', 
 '{"front": 1.5, "sides": 0.9, "transfer_space": 0.9}',
 '["NBC", "Alberta", "Ontario", "BC"]', 'accessible', 'high', 'standard'),

('TOILET_CHILD_HEIGHT', 'Child-Height Water Closet', 'toilet', 'Lower height toilet for children under 12', 
 '{"width": 0.7, "depth": 1.0, "height": 0.28}', 
 '{"front": 0.6, "sides": 0.15, "door_swing": 0.8}',
 '["NBC", "Alberta", "Ontario"]', 'child_specific', 'medium', 'standard'),

-- Sinks/Lavatories
('SINK_STANDARD', 'Standard Lavatory', 'sink', 'Standard height sink for general use', 
 '{"width": 0.6, "depth": 0.5, "height": 0.85}', 
 '{"front": 0.6, "sides": 0.1, "knee_space": 0.68}',
 '["NBC", "Alberta", "Ontario", "BC"]', 'standard', 'medium', 'minimal'),

('SINK_ACCESSIBLE', 'Accessible Lavatory', 'sink', 'Accessible sink with knee clearance', 
 '{"width": 0.6, "depth": 0.5, "height": 0.85}', 
 '{"front": 0.75, "knee_clearance": 0.68, "approach_space": 1.2}',
 '["NBC", "Alberta", "Ontario", "BC"]', 'accessible', 'high', 'minimal'),

('SINK_CHILD_LOW', 'Child-Height Lavatory', 'sink', 'Lower height sink for children', 
 '{"width": 0.5, "depth": 0.4, "height": 0.65}', 
 '{"front": 0.6, "sides": 0.1, "knee_space": 0.55}',
 '["NBC", "Alberta", "Ontario"]', 'child_specific', 'medium', 'minimal'),

-- Urinals
('URINAL_STANDARD', 'Standard Urinal', 'urinal', 'Wall-mounted urinal for general use', 
 '{"width": 0.4, "depth": 0.35, "height": 0.6}', 
 '{"front": 0.6, "sides": 0.15, "privacy_screen": 0.3}',
 '["NBC", "Alberta", "Ontario", "BC"]', 'standard', 'medium', 'minimal'),

('URINAL_ACCESSIBLE', 'Accessible Urinal', 'urinal', 'Lower height urinal with grab bars', 
 '{"width": 0.4, "depth": 0.35, "height": 0.43}', 
 '{"front": 0.75, "sides": 0.3, "grab_bar_clearance": 0.15}',
 '["NBC", "Alberta", "Ontario", "BC"]', 'accessible', 'high', 'minimal'),

-- Grab Bars
('GRAB_BAR_REAR', 'Rear Grab Bar', 'grab_bar', 'Horizontal grab bar behind toilet', 
 '{"length": 0.9, "diameter": 0.035, "height": 0.84}', 
 '{"wall_clearance": 0.035, "mounting_height": 0.84}',
 '["NBC", "Alberta", "Ontario", "BC"]', 'accessible', 'low', 'minimal'),

('GRAB_BAR_SIDE', 'Side Grab Bar', 'grab_bar', 'Side-mounted grab bar for transfer', 
 '{"length": 0.6, "diameter": 0.035, "height": 0.84}', 
 '{"wall_clearance": 0.035, "swing_clearance": 0.6}',
 '["NBC", "Alberta", "Ontario", "BC"]', 'accessible', 'low', 'minimal'),

-- Partitions and Doors
('PARTITION_STANDARD', 'Standard Toilet Partition', 'partition', 'Standard privacy partition', 
 '{"width": 1.2, "height": 1.8, "thickness": 0.05}', 
 '{"door_swing": 0.9, "gap_bottom": 0.15, "gap_top": 0.3}',
 '["NBC", "Alberta", "Ontario", "BC"]', 'standard', 'medium', 'minimal'),

('PARTITION_ACCESSIBLE', 'Accessible Toilet Partition', 'partition', 'Accessible stall partition with wider door', 
 '{"width": 2.0, "height": 1.8, "thickness": 0.05}', 
 '{"door_swing": 0.9, "door_width": 0.85, "latch_height": 0.9}',
 '["NBC", "Alberta", "Ontario", "BC"]', 'accessible', 'high', 'minimal');

-- =====================================================
-- Sample Component Assemblies (Functional Units)
-- =====================================================

INSERT OR REPLACE INTO component_assembly (assembly_code, name, description, component_ids, relationship_rules, total_footprint, circulation_space, applicable_building_types, occupancy_requirements) VALUES

-- Standard Stalls
('STANDARD_MALE_STALL', 'Standard Male Toilet Stall', 'Basic male toilet stall with standard fixtures',
 '["TOILET_STANDARD", "PARTITION_STANDARD"]',
 '{"toilet_position": "center_rear", "partition_clearance": 0.15, "door_swing": "outward"}',
 '{"width": 1.2, "depth": 1.8, "area": 2.16}',
 '{"approach_space": 0.6, "door_clearance": 0.9}',
 '["office", "retail", "industrial", "assembly"]',
 '{"min_occupancy": 1, "max_occupancy": 1000}'),

('STANDARD_FEMALE_STALL', 'Standard Female Toilet Stall', 'Basic female toilet stall with standard fixtures',
 '["TOILET_STANDARD", "PARTITION_STANDARD"]',
 '{"toilet_position": "center_rear", "partition_clearance": 0.15, "door_swing": "outward"}',
 '{"width": 1.2, "depth": 1.8, "area": 2.16}',
 '{"approach_space": 0.6, "door_clearance": 0.9}',
 '["office", "retail", "industrial", "assembly"]',
 '{"min_occupancy": 1, "max_occupancy": 1000}'),

-- Accessible Stalls
('ACCESSIBLE_STALL', 'Accessible Toilet Stall', 'Fully accessible toilet stall with grab bars',
 '["TOILET_ACCESSIBLE", "GRAB_BAR_REAR", "GRAB_BAR_SIDE", "PARTITION_ACCESSIBLE"]',
 '{"toilet_position": "side_mounted", "grab_bar_spacing": 0.9, "transfer_space": "right_side"}',
 '{"width": 2.0, "depth": 2.2, "area": 4.4}',
 '{"turning_radius": 1.5, "approach_space": 1.2, "transfer_space": 0.9}',
 '["office", "retail", "industrial", "assembly", "school", "daycare"]',
 '{"min_occupancy": 1, "max_occupancy": 10000}'),

-- Child-Specific Assemblies
('CHILD_TOILET_STALL', 'Child-Height Toilet Stall', 'Toilet stall designed for children under 12',
 '["TOILET_CHILD_HEIGHT", "PARTITION_STANDARD"]',
 '{"toilet_position": "center_rear", "partition_height": 1.5, "door_height": 1.4}',
 '{"width": 1.0, "depth": 1.6, "area": 1.6}',
 '{"approach_space": 0.6, "door_clearance": 0.8}',
 '["school", "daycare", "recreation"]',
 '{"min_occupancy": 10, "max_occupancy": 500}'),

-- Sink Assemblies
('STANDARD_SINK_UNIT', 'Standard Sink Unit', 'Standard lavatory with mirror and accessories',
 '["SINK_STANDARD"]',
 '{"mirror_height": 1.8, "soap_dispenser": "wall_mounted", "towel_dispenser": "wall_mounted"}',
 '{"width": 0.8, "depth": 0.6, "area": 0.48}',
 '{"approach_space": 0.6, "side_clearance": 0.1}',
 '["office", "retail", "industrial", "assembly"]',
 '{"min_occupancy": 1, "max_occupancy": 1000}'),

('ACCESSIBLE_SINK_UNIT', 'Accessible Sink Unit', 'Accessible lavatory with proper clearances',
 '["SINK_ACCESSIBLE"]',
 '{"mirror_height": 1.0, "knee_clearance": 0.68, "approach_angle": "front_only"}',
 '{"width": 0.8, "depth": 0.75, "area": 0.6}',
 '{"approach_space": 1.2, "knee_clearance": 0.68}',
 '["office", "retail", "industrial", "assembly", "school", "daycare"]',
 '{"min_occupancy": 1, "max_occupancy": 10000}'),

-- Family Facilities
('FAMILY_FACILITY', 'Family/Universal Washroom', 'Large accessible room for families and caregivers',
 '["TOILET_ACCESSIBLE", "SINK_ACCESSIBLE", "GRAB_BAR_REAR", "GRAB_BAR_SIDE"]',
 '{"layout": "open_plan", "baby_change_table": "fold_down", "adult_change_table": "optional"}',
 '{"width": 3.0, "depth": 3.0, "area": 9.0}',
 '{"turning_radius": 1.5, "door_clearance": 1.2, "maneuvering_space": 2.0}',
 '["office", "retail", "assembly", "school", "daycare", "healthcare"]',
 '{"min_occupancy": 50, "max_occupancy": 10000}');

-- =====================================================
-- Sample Context Logic Rules (Input-Triggered Rules)
-- =====================================================

INSERT OR REPLACE INTO context_logic_rule (rule_code, rule_name, rule_category, trigger_condition, priority, required_component_ids, required_assembly_ids, required_clause_ids, jurisdiction, effective_date, rule_explanation, code_reference) VALUES

-- Occupancy-Based Rules
('NBC_OFFICE_BASIC_FIXTURES', 'NBC Office Basic Fixture Requirements', 'fixture_count',
 '{"building_type": "office", "total_occupants": ">1"}', 90,
 '["TOILET_STANDARD", "SINK_STANDARD"]',
 '["STANDARD_MALE_STALL", "STANDARD_FEMALE_STALL", "STANDARD_SINK_UNIT"]',
 '["NBC_3.7.2.1", "NBC_3.7.3.1"]',
 'NBC', '2020-01-01',
 'Basic toilet and sink requirements for office buildings based on occupancy',
 'NBC 2020 Section 3.7.2'),

('NBC_ACCESSIBILITY_REQUIRED', 'NBC Accessibility Requirements', 'accessibility',
 '{"accessibility_required": true}', 95,
 '["TOILET_ACCESSIBLE", "SINK_ACCESSIBLE", "GRAB_BAR_REAR", "GRAB_BAR_SIDE"]',
 '["ACCESSIBLE_STALL", "ACCESSIBLE_SINK_UNIT"]',
 '["NBC_3.8.3.3", "NBC_3.8.3.12", "NBC_3.8.3.7"]',
 'NBC', '2020-01-01',
 'Accessible fixtures required when accessibility level is enhanced or universal',
 'NBC 2020 Section 3.8.3'),

-- Building Type Specific Rules
('NBC_DAYCARE_CHILD_FIXTURES', 'NBC Daycare Child-Specific Fixtures', 'building_type',
 '{"building_type": "daycare", "total_occupants": ">10"}', 85,
 '["TOILET_CHILD_HEIGHT", "SINK_CHILD_LOW"]',
 '["CHILD_TOILET_STALL"]',
 '["NBC_3.7.2.1_4", "NBC_3.7.3.2"]',
 'NBC', '2020-01-01',
 'Child-height fixtures required in daycare facilities serving more than 10 children',
 'NBC 2020 Section 3.7.2.1.(4)'),

('NBC_SCHOOL_MIXED_FIXTURES', 'NBC School Mixed Age Fixtures', 'building_type',
 '{"building_type": "school"}', 80,
 '["TOILET_STANDARD", "TOILET_CHILD_HEIGHT", "SINK_STANDARD", "SINK_CHILD_LOW"]',
 '["STANDARD_MALE_STALL", "STANDARD_FEMALE_STALL", "CHILD_TOILET_STALL"]',
 '["NBC_3.7.2.1", "NBC_3.7.2.1_4"]',
 'NBC', '2020-01-01',
 'Schools require both adult and child-height fixtures',
 'NBC 2020 Section 3.7.2'),

-- Occupancy Density Rules
('NBC_HIGH_OCCUPANCY_URINALS', 'NBC High Occupancy Urinal Requirements', 'occupancy_based',
 '{"building_type": "office", "total_occupants": ">50", "occupancy_density": ">2.0"}', 75,
 '["URINAL_STANDARD"]',
 '[]',
 '["NBC_3.7.2.2"]',
 'NBC', '2020-01-01',
 'Urinals required in high-occupancy male washrooms to reduce wait times',
 'NBC 2020 Section 3.7.2.2'),

-- Family Facility Rules
('NBC_FAMILY_FACILITY_LARGE', 'NBC Family Facility for Large Buildings', 'accessibility',
 '{"total_occupants": ">100", "accessibility_level": "enhanced"}', 70,
 '[]',
 '["FAMILY_FACILITY"]',
 '["NBC_3.8.3.15"]',
 'NBC', '2020-01-01',
 'Family/universal washrooms required in large buildings with enhanced accessibility',
 'NBC 2020 Section 3.8.3.15'),

-- Alberta-Specific Rules
('ABC_ENHANCED_ACCESSIBILITY', 'Alberta Enhanced Accessibility Requirements', 'accessibility',
 '{"jurisdiction": "Alberta", "accessibility_level": "enhanced"}', 88,
 '["TOILET_ACCESSIBLE", "URINAL_ACCESSIBLE"]',
 '["ACCESSIBLE_STALL"]',
 '["ABC_3.8.3.3_ENHANCED"]',
 'Alberta', '2019-01-01',
 'Alberta requires enhanced accessibility features beyond NBC minimums',
 'Alberta Building Code 2019 Section 3.8.3.3'),

-- Complex Conditional Rules
('NBC_RETAIL_CUSTOMER_ACCESS', 'NBC Retail Customer Washroom Access', 'building_type',
 '{"AND": [{"building_type": "retail"}, {"total_occupants": ">20"}, {"public_access": true}]}', 82,
 '["TOILET_STANDARD", "TOILET_ACCESSIBLE", "SINK_STANDARD", "SINK_ACCESSIBLE"]',
 '["STANDARD_MALE_STALL", "STANDARD_FEMALE_STALL", "ACCESSIBLE_STALL", "STANDARD_SINK_UNIT"]',
 '["NBC_3.7.1.1", "NBC_3.8.3.3"]',
 'NBC', '2020-01-01',
 'Retail buildings with public access require both standard and accessible facilities',
 'NBC 2020 Section 3.7.1');

-- =====================================================
-- Sample Building Code Clauses (Complete Clause Database)
-- =====================================================

INSERT OR REPLACE INTO building_code_clause (clause_code, clause_number, jurisdiction, code_version, document_title, clause_title, clause_text_en, page_number, section_reference, applies_to_building_types, applies_to_occupancy_types, applies_to_components, is_mandatory, enforcement_level, last_updated, verified_by) VALUES

-- NBC Fixture Count Clauses
('NBC_3.7.2.1', '3.7.2.1', 'NBC', '2020', 'National Building Code of Canada 2020',
 'Water Closets Required',
 'Except as permitted by Articles 3.7.2.2. to 3.7.2.4., water closets shall be provided in washrooms at the rate of not less than the number determined in accordance with Table 3.7.2.1.',
 156, 'Part 3, Section 3.7, Subsection 3.7.2',
 '["office", "retail", "industrial", "assembly", "school"]',
 '["A1", "A2", "A3", "B", "D", "E", "F"]',
 '["TOILET_STANDARD", "TOILET_ACCESSIBLE"]',
 TRUE, 'critical', '2024-01-01', 'NBC_Verification_Team'),

('NBC_3.7.2.1_4', '3.7.2.1.(4)', 'NBC', '2020', 'National Building Code of Canada 2020',
 'Water Closets for Children',
 'Where a building is intended to be used primarily by children, at least half the water closets shall be designed for use by children.',
 156, 'Part 3, Section 3.7, Subsection 3.7.2',
 '["school", "daycare", "recreation"]',
 '["A2", "E"]',
 '["TOILET_CHILD_HEIGHT"]',
 TRUE, 'critical', '2024-01-01', 'NBC_Verification_Team'),

('NBC_3.7.2.2', '3.7.2.2', 'NBC', '2020', 'National Building Code of Canada 2020',
 'Urinals',
 'In washrooms for males, urinals are permitted to replace not more than 67% of the required water closets.',
 157, 'Part 3, Section 3.7, Subsection 3.7.2',
 '["office", "retail", "industrial", "assembly"]',
 '["A1", "A2", "A3", "B", "D", "F"]',
 '["URINAL_STANDARD", "URINAL_ACCESSIBLE"]',
 FALSE, 'important', '2024-01-01', 'NBC_Verification_Team'),

('NBC_3.7.3.1', '3.7.3.1', 'NBC', '2020', 'National Building Code of Canada 2020',
 'Lavatories Required',
 'Lavatories shall be provided in washrooms at the rate of not less than the number determined in accordance with Table 3.7.3.1.',
 158, 'Part 3, Section 3.7, Subsection 3.7.3',
 '["office", "retail", "industrial", "assembly", "school", "daycare"]',
 '["A1", "A2", "A3", "B", "D", "E", "F"]',
 '["SINK_STANDARD", "SINK_ACCESSIBLE", "SINK_CHILD_LOW"]',
 TRUE, 'critical', '2024-01-01', 'NBC_Verification_Team'),

-- NBC Accessibility Clauses
('NBC_3.8.3.3', '3.8.3.3', 'NBC', '2020', 'National Building Code of Canada 2020',
 'Accessible Water Closet Stalls',
 'At least one water closet stall in each washroom shall conform to the requirements for accessible water closet stalls described in Article 3.8.3.12.',
 201, 'Part 3, Section 3.8, Subsection 3.8.3',
 '["office", "retail", "industrial", "assembly", "school", "daycare"]',
 '["A1", "A2", "A3", "B", "D", "E", "F"]',
 '["TOILET_ACCESSIBLE", "GRAB_BAR_REAR", "GRAB_BAR_SIDE", "PARTITION_ACCESSIBLE"]',
 TRUE, 'critical', '2024-01-01', 'NBC_Verification_Team'),

('NBC_3.8.3.12', '3.8.3.12', 'NBC', '2020', 'National Building Code of Canada 2020',
 'Accessible Water Closet Stall Requirements',
 'An accessible water closet stall shall: (a) have minimum inside dimensions of 1 500 mm by 1 500 mm, (b) be equipped with grab bars conforming to Article 3.8.3.13.',
 205, 'Part 3, Section 3.8, Subsection 3.8.3',
 '["office", "retail", "industrial", "assembly", "school", "daycare"]',
 '["A1", "A2", "A3", "B", "D", "E", "F"]',
 '["TOILET_ACCESSIBLE", "GRAB_BAR_REAR", "GRAB_BAR_SIDE"]',
 TRUE, 'critical', '2024-01-01', 'NBC_Verification_Team'),

('NBC_3.8.3.7', '3.8.3.7', 'NBC', '2020', 'National Building Code of Canada 2020',
 'Door Maneuvering Clearance',
 'Doors shall be provided with maneuvering clearance on the latch side that conforms to the requirements in Table 3.8.3.7.',
 203, 'Part 3, Section 3.8, Subsection 3.8.3',
 '["office", "retail", "industrial", "assembly", "school", "daycare"]',
 '["A1", "A2", "A3", "B", "D", "E", "F"]',
 '["PARTITION_ACCESSIBLE"]',
 TRUE, 'critical', '2024-01-01', 'NBC_Verification_Team'),

('NBC_3.8.3.15', '3.8.3.15', 'NBC', '2020', 'National Building Code of Canada 2020',
 'Universal Washrooms',
 'Where required by Article 3.8.3.3., universal washrooms shall be provided and shall conform to the requirements described in this Article.',
 208, 'Part 3, Section 3.8, Subsection 3.8.3',
 '["office", "retail", "assembly", "school", "healthcare"]',
 '["A1", "A2", "A3", "B", "E"]',
 '["TOILET_ACCESSIBLE", "SINK_ACCESSIBLE"]',
 TRUE, 'important', '2024-01-01', 'NBC_Verification_Team'),

-- Alberta-Specific Clauses
('ABC_3.8.3.3_ENHANCED', '3.8.3.3', 'Alberta', '2019', 'Alberta Building Code 2019',
 'Enhanced Accessible Requirements',
 'In addition to NBC requirements, Alberta requires enhanced accessibility features including: (a) accessible urinals where urinals are provided, (b) additional grab bar configurations.',
 198, 'Part 3, Section 3.8, Subsection 3.8.3',
 '["office", "retail", "industrial", "assembly"]',
 '["A1", "A2", "A3", "B", "D", "F"]',
 '["URINAL_ACCESSIBLE", "GRAB_BAR_REAR", "GRAB_BAR_SIDE"]',
 TRUE, 'critical', '2024-01-01', 'Alberta_Code_Team'),

-- General Building Clauses
('NBC_3.7.1.1', '3.7.1.1', 'NBC', '2020', 'National Building Code of Canada 2020',
 'Washroom Requirements',
 'Washrooms shall be provided in buildings in accordance with this Section.',
 154, 'Part 3, Section 3.7, Subsection 3.7.1',
 '["office", "retail", "industrial", "assembly", "school", "daycare"]',
 '["A1", "A2", "A3", "B", "D", "E", "F"]',
 '["TOILET_STANDARD", "SINK_STANDARD"]',
 TRUE, 'critical', '2024-01-01', 'NBC_Verification_Team'); 