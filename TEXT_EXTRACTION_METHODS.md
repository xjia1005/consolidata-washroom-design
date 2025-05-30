# 📝 **BUILDING CODE TEXT EXTRACTION METHODS**

## 🎯 **GOAL: 100% EXACT TEXT ACCURACY**

Ensure every word, punctuation mark, and number matches the original building code exactly.

---

## 🔄 **METHOD 1: MANUAL COPY-PASTE (Most Accurate)**

### **Process**
1. **Access Official Digital Sources**
   - NBC: https://nrc.canada.ca/en/certifications-evaluations-standards/codes-canada/codes-canada-publications/national-building-code-canada-2020
   - Alberta: https://www.alberta.ca/building-code
   - IBC: https://codes.iccsafe.org/content/IBC2021P1

2. **Direct Copy from PDF/HTML**
   ```
   Step 1: Open official building code document
   Step 2: Navigate to specific section (e.g., NBC 3.7.2)
   Step 3: Select text with cursor
   Step 4: Copy (Ctrl+C)
   Step 5: Paste into database import format
   Step 6: Verify formatting preservation
   ```

### **Quality Control**
- **Character-by-character verification**
- **Punctuation validation**
- **Number accuracy check**
- **Special character preservation**

### **Sample JSON Output**
```json
{
  "identifier": "3.7.2",
  "exact_text_en": "Except as permitted by Articles 3.7.2.3. to 3.7.2.6., the minimum number of water closets required for each sex in a building shall be determined in accordance with Table 3.7.2.1.",
  "extraction_method": "manual_copy_paste",
  "source_page": 287,
  "verified_by": "Licensed Professional Engineer",
  "verification_notes": "Character-by-character verification completed"
}
```

---

## 🤖 **METHOD 2: OCR + MANUAL VERIFICATION**

### **When to Use**
- Official PDFs are scanned images
- Text selection not available
- Legacy building codes

### **Process**
```python
# OCR + Verification Workflow
import pytesseract
from PIL import Image
import difflib

def extract_with_ocr_verification(pdf_page, manual_reference):
    # Step 1: OCR extraction
    ocr_text = pytesseract.image_to_string(pdf_page)
    
    # Step 2: Manual verification
    manual_text = input("Enter manual verification text: ")
    
    # Step 3: Difference analysis
    differences = list(difflib.unified_diff(
        ocr_text.splitlines(),
        manual_text.splitlines(),
        lineterm='',
        fromfile='OCR_result',
        tofile='Manual_verification'
    ))
    
    # Step 4: Accuracy report
    if not differences:
        return {"status": "exact_match", "text": manual_text}
    else:
        return {"status": "requires_correction", "differences": differences}
```

### **Quality Standards**
- **99.9% OCR accuracy required**
- **Manual verification mandatory**
- **Double-person verification for critical sections**

---

## 🌐 **METHOD 3: API INTEGRATION (Future)**

### **Government API Integration**
```python
# Example: Canadian Government Building Code API
class BuildingCodeAPI:
    def __init__(self, jurisdiction):
        self.base_url = {
            'NBC': 'https://api.nrc-cnrc.gc.ca/codes/',
            'AB': 'https://api.alberta.ca/building-code/',
            'IBC': 'https://api.iccsafe.org/codes/'
        }[jurisdiction]
    
    def get_exact_section_text(self, section_id):
        """Get exact text from official API"""
        response = requests.get(
            f"{self.base_url}/sections/{section_id}",
            headers={'Authorization': 'Bearer {api_key}'}
        )
        
        return {
            'exact_text': response.json()['official_text'],
            'version': response.json()['code_version'],
            'last_updated': response.json()['last_modified'],
            'hash': response.json()['content_hash']
        }
```

### **API Advantages**
- **Always current**: Automatic updates when codes change
- **Authenticated**: Official government source
- **Versioned**: Track changes over time
- **Tamper-proof**: Cryptographic verification

---

## 🔍 **METHOD 4: BLOCKCHAIN VERIFICATION**

### **Concept**
Store building code text hashes on blockchain for immutable verification.

```javascript
// Building Code Text Verification Contract
contract BuildingCodeVerification {
    struct CodeSection {
        string sectionId;
        string textHash;
        string jurisdiction;
        uint256 timestamp;
        address verifier;
    }
    
    mapping(string => CodeSection) public verifiedSections;
    
    function verifySection(
        string memory sectionId,
        string memory textHash,
        string memory jurisdiction
    ) public {
        verifiedSections[sectionId] = CodeSection({
            sectionId: sectionId,
            textHash: textHash,
            jurisdiction: jurisdiction,
            timestamp: block.timestamp,
            verifier: msg.sender
        });
    }
    
    function isTextVerified(string memory sectionId, string memory text) 
        public view returns (bool) {
        string memory computedHash = sha256(abi.encodePacked(text));
        return keccak256(abi.encodePacked(verifiedSections[sectionId].textHash)) 
               == keccak256(abi.encodePacked(computedHash));
    }
}
```

---

## 📊 **TEXT VERIFICATION WORKFLOW**

### **Multi-Stage Verification Process**

```sql
-- 1. INITIAL EXTRACTION
INSERT INTO code_sections_staging (
    section_identifier,
    extracted_text,
    extraction_method,
    extracted_by,
    extraction_date
) VALUES (
    '3.7.2',
    'Except as permitted by Articles 3.7.2.3. to 3.7.2.6...',
    'manual_copy_paste',
    'John Smith, Building Code Specialist',
    CURRENT_TIMESTAMP
);

-- 2. FIRST VERIFICATION
UPDATE code_sections_staging SET
    first_verification_by = 'Jane Doe, P.Eng',
    first_verification_date = CURRENT_TIMESTAMP,
    first_verification_status = 'approved',
    first_verification_notes = 'Character-by-character verification completed'
WHERE section_identifier = '3.7.2';

-- 3. SECOND VERIFICATION (For critical sections)
UPDATE code_sections_staging SET
    second_verification_by = 'Mike Wilson, Licensed Architect',
    second_verification_date = CURRENT_TIMESTAMP,
    second_verification_status = 'approved',
    accuracy_score = 100.0
WHERE section_identifier = '3.7.2';

-- 4. FINAL APPROVAL & PROMOTION TO PRODUCTION
INSERT INTO code_sections (
    jurisdiction_id,
    section_identifier,
    original_text_en,
    text_verified_by,
    text_verified_date,
    verification_method,
    accuracy_score,
    legal_status
) SELECT 
    jurisdiction_id,
    section_identifier,
    extracted_text,
    second_verification_by,
    second_verification_date,
    'dual_manual_verification',
    accuracy_score,
    'active'
FROM code_sections_staging 
WHERE section_identifier = '3.7.2'
AND first_verification_status = 'approved'
AND second_verification_status = 'approved';
```

---

## 🛡️ **QUALITY ASSURANCE MEASURES**

### **Automated Text Validation**
```python
def validate_exact_text(extracted_text, section_metadata):
    """Automated quality checks for extracted text"""
    issues = []
    
    # Check 1: Required elements present
    if section_metadata['section_id'] == '3.7.2':
        required_phrases = [
            "minimum number of water closets",
            "Table 3.7.2.1",
            "each sex in a building"
        ]
        for phrase in required_phrases:
            if phrase not in extracted_text:
                issues.append(f"Missing required phrase: {phrase}")
    
    # Check 2: Number formatting
    numbers = re.findall(r'\d+\.?\d*', extracted_text)
    for num in numbers:
        if not validate_number_format(num):
            issues.append(f"Number formatting issue: {num}")
    
    # Check 3: Punctuation accuracy
    if extracted_text.count('.') != expected_periods[section_metadata['section_id']]:
        issues.append("Period count mismatch")
    
    # Check 4: Text length validation
    expected_length = section_metadata.get('expected_length')
    if expected_length and abs(len(extracted_text) - expected_length) > 10:
        issues.append(f"Text length variance: expected ~{expected_length}, got {len(extracted_text)}")
    
    return {
        'valid': len(issues) == 0,
        'issues': issues,
        'confidence_score': calculate_confidence(issues)
    }
```

### **Cross-Reference Validation**
```sql
-- Compare extracted text against multiple sources
CREATE OR REPLACE FUNCTION cross_reference_validation(
    p_section_id VARCHAR,
    p_extracted_text TEXT
) RETURNS TABLE (
    source VARCHAR,
    text_match BOOLEAN,
    similarity_score DECIMAL,
    differences TEXT[]
) AS $$
BEGIN
    -- Compare against official government source
    RETURN QUERY
    SELECT 
        'government_official'::VARCHAR,
        p_extracted_text = official_text,
        similarity(p_extracted_text, official_text),
        string_to_array(differences, '|')
    FROM government_code_references 
    WHERE section_identifier = p_section_id;
    
    -- Compare against professional references
    RETURN QUERY
    SELECT 
        'professional_reference'::VARCHAR,
        p_extracted_text = reference_text,
        similarity(p_extracted_text, reference_text),
        string_to_array(differences, '|')
    FROM professional_code_references 
    WHERE section_identifier = p_section_id;
END;
$$ LANGUAGE plpgsql;
```

---

## 🔄 **UPDATE MANAGEMENT**

### **Version Control for Building Code Changes**
```sql
-- Building Code Version Control
CREATE TABLE code_version_history (
    id SERIAL PRIMARY KEY,
    section_identifier VARCHAR(100),
    jurisdiction_id INTEGER,
    
    -- Version information
    old_text TEXT,
    new_text TEXT,
    change_type VARCHAR(50), -- 'addition', 'modification', 'deletion'
    change_description TEXT,
    
    -- Change tracking
    effective_date DATE,
    change_detected_date TIMESTAMP,
    change_verified_by VARCHAR(255),
    
    -- Impact analysis
    affected_projects INTEGER[],
    impact_assessment TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Automated change detection
CREATE OR REPLACE FUNCTION detect_code_changes() RETURNS VOID AS $$
DECLARE
    v_section RECORD;
    v_current_text TEXT;
    v_official_text TEXT;
BEGIN
    FOR v_section IN SELECT * FROM code_sections WHERE legal_status = 'active'
    LOOP
        -- Get current official text (API call or scheduled extraction)
        v_official_text := get_official_text(v_section.jurisdiction_id, v_section.section_identifier);
        
        -- Compare with stored text
        IF v_section.original_text_en != v_official_text THEN
            INSERT INTO code_version_history (
                section_identifier,
                jurisdiction_id,
                old_text,
                new_text,
                change_type,
                change_detected_date
            ) VALUES (
                v_section.section_identifier,
                v_section.jurisdiction_id,
                v_section.original_text_en,
                v_official_text,
                'modification',
                CURRENT_TIMESTAMP
            );
            
            -- Flag for human review
            UPDATE code_sections SET
                legal_status = 'pending_review',
                review_reason = 'Official text change detected'
            WHERE id = v_section.id;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;
```

---

## 📋 **IMPLEMENTATION CHECKLIST**

### **For NBC (National Building Code of Canada)**
- [ ] **Access official NRC digital publication**
- [ ] **Set up manual extraction process**
- [ ] **Implement dual verification workflow**
- [ ] **Create NBC-specific validation rules**
- [ ] **Establish update monitoring**

### **For Alberta Building Code**
- [ ] **Access Alberta Municipal Affairs portal**
- [ ] **Extract amendment text separately**
- [ ] **Link amendments to base NBC sections**
- [ ] **Verify amendment override logic**

### **For International Building Code (IBC)**
- [ ] **Access ICC official publications**
- [ ] **Handle different numbering system**
- [ ] **Extract table-based requirements**
- [ ] **Implement tiered calculation logic**

### **Quality Assurance**
- [ ] **Character-by-character verification**
- [ ] **Cross-reference validation**
- [ ] **Professional review process**
- [ ] **Legal disclaimer integration**
- [ ] **Audit trail maintenance**

---

## 🎯 **SUCCESS METRICS**

### **Text Accuracy KPIs**
- **100% character accuracy** for critical sections
- **99.9% automated validation pass rate**
- **Zero legal challenges** due to text inaccuracy
- **Professional acceptance** by building officials

### **Operational Metrics**
- **24-hour turnaround** for new jurisdiction addition
- **Real-time detection** of building code updates
- **99.9% system uptime** for text verification

**Result**: Your system will have legally defensible, character-perfect building code text that building officials and professionals can trust completely. 