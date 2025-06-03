// Pricing Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializePricingToggles();
    initializeAnalytics();
});

function initializePricingToggles() {
    const annualToggle = document.getElementById('annual-toggle');
    
    if (annualToggle) {
        annualToggle.addEventListener('change', function() {
            togglePricingDisplay(this.checked);
        });
    }
}

function togglePricingDisplay(isAnnual) {
    // Toggle price displays
    const monthlyPrices = document.querySelectorAll('.monthly-price');
    const annualPrices = document.querySelectorAll('.annual-price');
    const monthlyPeriods = document.querySelectorAll('.monthly-period');
    const annualPeriods = document.querySelectorAll('.annual-period');
    const monthlyBilling = document.querySelectorAll('.monthly-billing');
    const annualBilling = document.querySelectorAll('.annual-billing');
    
    if (isAnnual) {
        // Show annual pricing
        monthlyPrices.forEach(el => el.style.display = 'none');
        annualPrices.forEach(el => el.style.display = 'inline');
        monthlyPeriods.forEach(el => el.style.display = 'none');
        annualPeriods.forEach(el => el.style.display = 'inline');
        monthlyBilling.forEach(el => el.style.display = 'none');
        annualBilling.forEach(el => el.style.display = 'block');
        
        // Update registration links to include annual parameter
        updateRegistrationLinks('annual');
    } else {
        // Show monthly pricing
        monthlyPrices.forEach(el => el.style.display = 'inline');
        annualPrices.forEach(el => el.style.display = 'none');
        monthlyPeriods.forEach(el => el.style.display = 'inline');
        annualPeriods.forEach(el => el.style.display = 'none');
        monthlyBilling.forEach(el => el.style.display = 'block');
        annualBilling.forEach(el => el.style.display = 'none');
        
        // Update registration links to monthly
        updateRegistrationLinks('monthly');
    }
    
    // Track pricing toggle event
    trackEvent('pricing_toggle', {
        billing_type: isAnnual ? 'annual' : 'monthly'
    });
}

function updateRegistrationLinks(billingType) {
    const registrationLinks = document.querySelectorAll('a[href*="/register?plan="]');
    
    registrationLinks.forEach(link => {
        const url = new URL(link.href);
        const plan = url.searchParams.get('plan');
        
        if (plan && plan !== 'project') { // Project plan doesn't have annual billing
            url.searchParams.set('billing', billingType);
            link.href = url.toString();
        }
    });
}

function initializeAnalytics() {
    // Track pricing page view
    trackEvent('pricing_page_view', {
        timestamp: new Date().toISOString(),
        user_agent: navigator.userAgent,
        referrer: document.referrer
    });
    
    // Track plan clicks
    const planButtons = document.querySelectorAll('.pricing-card .btn');
    planButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const card = this.closest('.pricing-card');
            const planName = card.querySelector('h3').textContent;
            const planPrice = card.querySelector('.amount:not([style*="display: none"])').textContent;
            
            trackEvent('plan_click', {
                plan_name: planName,
                plan_price: planPrice,
                button_text: this.textContent,
                card_position: Array.from(card.parentNode.children).indexOf(card)
            });
        });
    });
    
    // Track FAQ interactions
    const faqItems = document.querySelectorAll('.faq-item');
    faqItems.forEach(item => {
        item.addEventListener('click', function() {
            const question = this.querySelector('h4').textContent;
            trackEvent('faq_click', {
                question: question
            });
        });
    });
    
    // Track add-on interest
    const addonCards = document.querySelectorAll('.addon-card');
    addonCards.forEach(card => {
        card.addEventListener('click', function() {
            const addonName = this.querySelector('h4').textContent;
            const addonPrice = this.querySelector('.addon-price').textContent;
            
            trackEvent('addon_interest', {
                addon_name: addonName,
                addon_price: addonPrice
            });
        });
    });
}

function trackEvent(eventName, properties = {}) {
    // Basic analytics tracking
    console.log('Analytics Event:', eventName, properties);
    
    // You can integrate with analytics services here:
    // Google Analytics, Mixpanel, Amplitude, etc.
    
    // Example Google Analytics 4 integration:
    if (typeof gtag !== 'undefined') {
        gtag('event', eventName, properties);
    }
    
    // Example Mixpanel integration:
    if (typeof mixpanel !== 'undefined') {
        mixpanel.track(eventName, properties);
    }
    
    // Store in localStorage for later analysis
    try {
        const events = JSON.parse(localStorage.getItem('bcode_analytics') || '[]');
        events.push({
            event: eventName,
            properties: properties,
            timestamp: new Date().toISOString()
        });
        
        // Keep only last 100 events
        if (events.length > 100) {
            events.splice(0, events.length - 100);
        }
        
        localStorage.setItem('bcode_analytics', JSON.stringify(events));
    } catch (e) {
        console.warn('Could not store analytics event:', e);
    }
}

// Pricing calculator functionality
function calculateAnnualSavings(monthlyPrice) {
    const annualPrice = monthlyPrice * 10; // 2 months free
    const monthlySavings = monthlyPrice * 2;
    const percentageSavings = Math.round((monthlySavings / (monthlyPrice * 12)) * 100);
    
    return {
        annualPrice: annualPrice,
        monthlySavings: monthlySavings,
        percentageSavings: percentageSavings
    };
}

// Plan comparison functionality
function showPlanComparison() {
    const comparisonModal = document.createElement('div');
    comparisonModal.className = 'plan-comparison-modal';
    comparisonModal.innerHTML = `
        <div class="comparison-content">
            <div class="comparison-header">
                <h3>Plan Comparison</h3>
                <button class="close-btn" onclick="this.closest('.plan-comparison-modal').remove()">×</button>
            </div>
            <div class="comparison-table">
                <!-- Comparison table content would go here -->
                <p>Detailed plan comparison coming soon!</p>
            </div>
        </div>
    `;
    
    document.body.appendChild(comparisonModal);
    
    // Track comparison view
    trackEvent('plan_comparison_view');
}

// ROI Calculator
function calculateROI(planPrice, projectsPerMonth, timePerProject, hourlyRate) {
    const monthlyCost = planPrice;
    const timeSavedPerProject = 2; // hours saved per project
    const totalTimeSaved = projectsPerMonth * timeSavedPerProject;
    const monthlySavings = totalTimeSaved * hourlyRate;
    const netSavings = monthlySavings - monthlyCost;
    const roi = ((netSavings / monthlyCost) * 100).toFixed(1);
    
    return {
        monthlyCost: monthlyCost,
        monthlySavings: monthlySavings,
        netSavings: netSavings,
        roi: roi,
        timeSaved: totalTimeSaved
    };
}

// Add ROI calculator to page
function addROICalculator() {
    const roiSection = document.createElement('section');
    roiSection.className = 'roi-calculator';
    roiSection.innerHTML = `
        <div class="roi-content">
            <h3>💰 Calculate Your ROI</h3>
            <p>See how much time and money BCode Pro can save your firm</p>
            <div class="roi-inputs">
                <div class="input-group">
                    <label>Projects per month:</label>
                    <input type="number" id="projects-per-month" value="5" min="1" max="100">
                </div>
                <div class="input-group">
                    <label>Your hourly rate ($):</label>
                    <input type="number" id="hourly-rate" value="75" min="25" max="500">
                </div>
                <button onclick="updateROICalculation()" class="btn btn-primary">Calculate Savings</button>
            </div>
            <div id="roi-results" class="roi-results"></div>
        </div>
    `;
    
    // Insert before FAQ section
    const faqSection = document.querySelector('.faq-section');
    if (faqSection) {
        faqSection.parentNode.insertBefore(roiSection, faqSection);
    }
}

function updateROICalculation() {
    const projectsPerMonth = parseInt(document.getElementById('projects-per-month').value) || 5;
    const hourlyRate = parseInt(document.getElementById('hourly-rate').value) || 75;
    const professionalPlanPrice = 29;
    
    const roi = calculateROI(professionalPlanPrice, projectsPerMonth, 2, hourlyRate);
    
    const resultsDiv = document.getElementById('roi-results');
    resultsDiv.innerHTML = `
        <div class="roi-summary">
            <div class="roi-metric">
                <span class="metric-value">$${roi.monthlySavings}</span>
                <span class="metric-label">Monthly Savings</span>
            </div>
            <div class="roi-metric">
                <span class="metric-value">${roi.timeSaved}h</span>
                <span class="metric-label">Time Saved</span>
            </div>
            <div class="roi-metric">
                <span class="metric-value">${roi.roi}%</span>
                <span class="metric-label">ROI</span>
            </div>
        </div>
        <p class="roi-explanation">
            With ${projectsPerMonth} projects per month, BCode Pro saves you ${roi.timeSaved} hours worth $${roi.monthlySavings}, 
            giving you a ${roi.roi}% return on investment!
        </p>
    `;
    
    // Track ROI calculation
    trackEvent('roi_calculation', {
        projects_per_month: projectsPerMonth,
        hourly_rate: hourlyRate,
        calculated_roi: roi.roi,
        monthly_savings: roi.monthlySavings
    });
}

// Initialize ROI calculator on page load
document.addEventListener('DOMContentLoaded', function() {
    // Add ROI calculator after a short delay
    setTimeout(addROICalculator, 1000);
});

// Export functions for global access
window.showPlanComparison = showPlanComparison;
window.updateROICalculation = updateROICalculation; 