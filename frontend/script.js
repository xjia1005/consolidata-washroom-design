// Consolidata Washroom Design - Main JavaScript
// Auto-detect API URL based on environment
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:5000/api' 
    : `${window.location.protocol}//${window.location.host}/api`;

let apiConnected = false;

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Consolidata system initializing...');
    console.log('🔧 API Base URL:', API_BASE_URL);
    checkApiConnection();
    setupEventListeners();
});

// Check API connection
async function checkApiConnection() {
    const statusCard = document.getElementById('api-status');
    const indicator = statusCard.querySelector('.status-indicator');
    const statusText = statusCard.querySelector('.status-text');
    
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        
        if (data.status === 'healthy') {
            apiConnected = true;
            indicator.className = 'status-indicator connected';
            statusText.textContent = '✅ System Ready - Building Code Compliance API Connected';
            statusCard.style.background = '#f0fdf4';
            statusCard.style.borderLeft = '4px solid #10b981';
        } else {
            throw new Error('API not healthy');
        }
    } catch (error) {
        apiConnected = false;
        indicator.className = 'status-indicator error';
        statusText.textContent = '❌ API Offline - Backend server not running';
        statusCard.style.background = '#fef2f2';
        statusCard.style.borderLeft = '4px solid #ef4444';
    }
}

// Setup event listeners
function setupEventListeners() {
    // Form validation on input change
    const inputs = document.querySelectorAll('.form-control');
    inputs.forEach(input => {
        input.addEventListener('change', validateFormField);
        input.addEventListener('input', validateFormField);
    });
}

// Validate individual form field
function validateFormField(event) {
    const field = event.target;
    const value = field.value;
    
    // Remove existing validation classes
    field.classList.remove('error', 'success');
    
    // Validate based on field type
    let isValid = true;
    
    if (field.type === 'number') {
        isValid = value && parseFloat(value) > 0;
    } else if (field.tagName === 'SELECT') {
        isValid = value && value.trim() !== '';
    } else {
        isValid = value && value.trim() !== '';
    }
    
    // Apply validation styling
    if (isValid) {
        field.style.borderColor = '#10b981';
        field.style.boxShadow = '0 0 0 3px rgba(16, 185, 129, 0.1)';
    } else {
        field.style.borderColor = '#ef4444';
        field.style.boxShadow = '0 0 0 3px rgba(239, 68, 68, 0.1)';
    }
}

// Scroll to design section
function scrollToDesign() {
    document.getElementById('design').scrollIntoView({ 
        behavior: 'smooth',
        block: 'start'
    });
}

// Test system functionality
function testSystem() {
    showNotification('🧪 Running system tests...', 'info');
    
    // Test form validation
    setTimeout(() => {
        validateForm();
        
        // Test API if connected
        if (apiConnected) {
            setTimeout(() => {
                testAPI();
            }, 1000);
        }
    }, 500);
}

// Validate form
function validateForm() {
    const occupancy = document.getElementById('occupancy').value;
    const length = document.getElementById('room-length').value;
    const width = document.getElementById('room-width').value;
    const buildingType = document.getElementById('building-type').value;
    const jurisdiction = document.getElementById('jurisdiction').value;
    const accessibility = document.getElementById('accessibility').value;
    
    let isValid = true;
    let errors = [];
    
    // Validate occupancy
    if (!occupancy || parseInt(occupancy) <= 0) {
        errors.push('Occupancy load must be greater than 0');
        isValid = false;
    }
    
    // Validate dimensions
    if (!length || parseFloat(length) <= 0) {
        errors.push('Room length must be greater than 0');
        isValid = false;
    }
    
    if (!width || parseFloat(width) <= 0) {
        errors.push('Room width must be greater than 0');
        isValid = false;
    }
    
    // Validate selections
    if (!buildingType) {
        errors.push('Building type must be selected');
        isValid = false;
    }
    
    if (!jurisdiction) {
        errors.push('Jurisdiction must be selected');
        isValid = false;
    }
    
    if (!accessibility) {
        errors.push('Accessibility level must be selected');
        isValid = false;
    }
    
    // Show validation results
    if (isValid) {
        showNotification('✅ Form Validation: All parameters are valid!', 'success');
        return true;
    } else {
        showNotification(`❌ Form Validation Failed: ${errors.join(', ')}`, 'error');
        return false;
    }
}

// Test API connection
async function testAPI() {
    if (!apiConnected) {
        showNotification('❌ Cannot test API - Backend server not running', 'error');
        return;
    }
    
    showNotification('🔧 Testing API with sample data...', 'info');
    
    const testData = {
        occupancy_load: 100,
        building_type: 'office',
        jurisdiction: 'NBC',
        code_version: '2020',
        accessibility_level: 'basic',
        room_dimensions: {
            length: 10.0,
            width: 8.0,
            height: 3.0
        }
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/complete-analysis`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(testData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('✅ API Test: Backend is working correctly!', 'success');
        } else {
            showNotification(`❌ API Test Failed: ${result.error}`, 'error');
        }
    } catch (error) {
        showNotification(`❌ API Test Failed: ${error.message}`, 'error');
    }
}

// Generate design
async function generateDesign() {
    // Validate form first
    if (!validateForm()) {
        showNotification('❌ Please fix form errors before generating design', 'error');
        return;
    }
    
    if (!apiConnected) {
        showNotification('❌ Cannot generate design - Backend server not running', 'error');
        return;
    }
    
    // Show loading state
    showLoading(true);
    
    // Collect form data
    const formData = {
        occupancy_load: parseInt(document.getElementById('occupancy').value),
        building_type: document.getElementById('building-type').value,
        jurisdiction: document.getElementById('jurisdiction').value,
        code_version: '2020',
        accessibility_level: document.getElementById('accessibility').value,
        room_dimensions: {
            length: parseFloat(document.getElementById('room-length').value),
            width: parseFloat(document.getElementById('room-width').value),
            height: 3.0
        }
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/complete-analysis`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayResults(result.report);
            showNotification('🎉 Design generated successfully!', 'success');
        } else {
            showNotification(`❌ Design generation failed: ${result.error}`, 'error');
        }
    } catch (error) {
        showNotification(`❌ Error: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

// Show/hide loading state
function showLoading(show) {
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    
    if (show) {
        loading.style.display = 'block';
        results.innerHTML = '';
        loading.scrollIntoView({ behavior: 'smooth' });
    } else {
        loading.style.display = 'none';
    }
}

// Display results
function displayResults(report) {
    const resultsDiv = document.getElementById('results');
    const fixtures = report.fixture_requirements;
    const score = report.compliance_score || 0;
    
    // Create results HTML
    const resultsHTML = `
        <h3 class="text-center mb-2">🎉 Washroom Design Results</h3>
        
        <div class="compliance-score">
            <div class="score-number">${score.toFixed(1)}%</div>
            <h4>Compliance Score</h4>
            <p>${getComplianceMessage(score)}</p>
        </div>
        
        <h4>📊 Fixture Requirements</h4>
        <div class="results-grid">
            <div class="result-card">
                <div class="result-number">${fixtures.water_closets_male}</div>
                <div class="result-label">Male Water Closets</div>
            </div>
            <div class="result-card">
                <div class="result-number">${fixtures.water_closets_female}</div>
                <div class="result-label">Female Water Closets</div>
            </div>
            <div class="result-card">
                <div class="result-number">${fixtures.urinals}</div>
                <div class="result-label">Urinals</div>
            </div>
            <div class="result-card">
                <div class="result-number">${fixtures.lavatories}</div>
                <div class="result-label">Lavatories</div>
            </div>
            <div class="result-card">
                <div class="result-number">${fixtures.accessible_stalls}</div>
                <div class="result-label">Accessible Stalls</div>
            </div>
            <div class="result-card">
                <div class="result-number">${fixtures.total_fixtures}</div>
                <div class="result-label">Total Fixtures</div>
            </div>
        </div>
        
        <div class="success">
            <h4>📋 Design Summary</h4>
            <p><strong>Calculation Basis:</strong> ${fixtures.calculation_basis}</p>
            <p><strong>Code References:</strong> ${fixtures.code_references.join(', ')}</p>
            <p><strong>Layout Elements:</strong> ${report.layout_elements.length} positioned elements</p>
            <p><strong>Compliance Items:</strong> ${report.compliance_checklist.length} requirements checked</p>
        </div>
        
        ${report.recommendations && report.recommendations.length > 0 ? `
            <div class="recommendations">
                <h4>💡 Recommendations</h4>
                <ul>
                    ${report.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                </ul>
            </div>
        ` : ''}
        
        <div class="form-actions mt-2">
            <button class="btn btn-primary" onclick="exportToCAD()">📐 Export to AutoCAD</button>
            <button class="btn btn-secondary" onclick="generateNewDesign()">🔄 Generate New Design</button>
            <button class="btn btn-outline" onclick="printResults()">🖨️ Print Results</button>
        </div>
    `;
    
    resultsDiv.innerHTML = resultsHTML;
    resultsDiv.scrollIntoView({ behavior: 'smooth' });
}

// Get compliance message based on score
function getComplianceMessage(score) {
    if (score >= 95) return '🌟 Excellent! Full compliance achieved.';
    if (score >= 85) return '✅ Very Good! Minor optimizations possible.';
    if (score >= 70) return '⚠️ Good! Some improvements recommended.';
    if (score >= 50) return '🔧 Fair! Several issues need attention.';
    return '❌ Poor! Major compliance issues detected.';
}

// Export to CAD (placeholder)
function exportToCAD() {
    showNotification('📐 AutoCAD export feature coming soon!', 'info');
}

// Generate new design
function generateNewDesign() {
    document.getElementById('results').innerHTML = '';
    scrollToDesign();
    showNotification('🔄 Ready for new design parameters', 'info');
}

// Print results
function printResults() {
    window.print();
}

// Show notification
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(n => n.remove());
    
    // Create notification
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" style="background: none; border: none; font-size: 1.2rem; cursor: pointer;">×</button>
        </div>
    `;
    
    // Style notification
    notification.style.cssText = `
        position: fixed;
        top: 90px;
        right: 20px;
        max-width: 400px;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 1001;
        animation: slideIn 0.3s ease-out;
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

// Add slide-in animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);

// Utility functions
function formatNumber(num) {
    return new Intl.NumberFormat().format(num);
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-CA', {
        style: 'currency',
        currency: 'CAD'
    }).format(amount);
}

// Error handling
window.addEventListener('error', function(event) {
    console.error('JavaScript Error:', event.error);
    showNotification('❌ An unexpected error occurred. Please refresh the page.', 'error');
});

// Console welcome message
console.log(`
🏗️ Consolidata Washroom Design System
✅ Frontend loaded successfully
🔧 API Base URL: ${API_BASE_URL}
📚 Building Code Compliance Ready
`); 