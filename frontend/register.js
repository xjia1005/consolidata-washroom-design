// Registration Form JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializeRegistrationForm();
    handlePlanSelection();
});

function initializeRegistrationForm() {
    const form = document.getElementById('registration-form');
    const submitBtn = document.getElementById('register-btn');
    
    // Form validation
    setupFormValidation();
    
    // Form submission
    form.addEventListener('submit', handleFormSubmission);
    
    // Real-time validation
    setupRealTimeValidation();
}

function handlePlanSelection() {
    // Check if plan is specified in URL
    const urlParams = new URLSearchParams(window.location.search);
    const selectedPlan = urlParams.get('plan');
    
    if (selectedPlan && selectedPlan !== 'free') {
        showPlanSelection(selectedPlan);
        document.getElementById('selected_plan').value = selectedPlan;
    }
}

function showPlanSelection(planType) {
    const planSelection = document.getElementById('plan-selection');
    const planInfo = document.getElementById('selected-plan-info');
    
    const plans = {
        'professional': {
            name: 'Professional',
            price: '$29/month',
            description: 'Unlimited projects with enhanced analysis'
        },
        'project': {
            name: 'Pay Per Project',
            price: '$15/project',
            description: 'Single project with all professional features'
        },
        'team': {
            name: 'Team',
            price: '$99/month',
            description: 'Up to 5 users with collaboration features'
        },
        'enterprise': {
            name: 'Enterprise',
            price: '$299/month',
            description: 'Unlimited users with custom features'
        }
    };
    
    const plan = plans[planType];
    if (plan) {
        planInfo.innerHTML = `
            <div class="plan-name">${plan.name}</div>
            <div class="plan-price">${plan.price}</div>
            <div class="plan-description">${plan.description}</div>
        `;
        planSelection.style.display = 'block';
    }
}

function setupFormValidation() {
    const form = document.getElementById('registration-form');
    const inputs = form.querySelectorAll('input[required]');
    
    inputs.forEach(input => {
        input.addEventListener('blur', validateField);
        input.addEventListener('input', clearFieldError);
    });
    
    // Password confirmation validation
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirm_password');
    
    confirmPassword.addEventListener('input', function() {
        if (this.value && this.value !== password.value) {
            setFieldError(this, 'Passwords do not match');
        } else {
            clearFieldError.call(this);
        }
    });
    
    // Email validation
    const email = document.getElementById('email');
    email.addEventListener('input', function() {
        if (this.value && !isValidEmail(this.value)) {
            setFieldError(this, 'Please enter a valid email address');
        } else {
            clearFieldError.call(this);
        }
    });
    
    // Phone validation
    const phone = document.getElementById('phone');
    phone.addEventListener('input', function() {
        if (this.value && !isValidPhone(this.value)) {
            setFieldError(this, 'Please enter a valid phone number');
        } else {
            clearFieldError.call(this);
        }
    });
}

function setupRealTimeValidation() {
    const email = document.getElementById('email');
    const password = document.getElementById('password');
    
    // Email availability check (debounced)
    let emailTimeout;
    email.addEventListener('input', function() {
        clearTimeout(emailTimeout);
        emailTimeout = setTimeout(() => {
            if (this.value && isValidEmail(this.value)) {
                checkEmailAvailability(this.value);
            }
        }, 500);
    });
    
    // Password strength indicator
    password.addEventListener('input', function() {
        updatePasswordStrength(this.value);
    });
}

function validateField(event) {
    const field = event.target;
    const value = field.value.trim();
    
    // Required field validation
    if (field.hasAttribute('required') && !value) {
        setFieldError(field, 'This field is required');
        return false;
    }
    
    // Specific field validations
    switch (field.type) {
        case 'email':
            if (value && !isValidEmail(value)) {
                setFieldError(field, 'Please enter a valid email address');
                return false;
            }
            break;
        case 'tel':
            if (value && !isValidPhone(value)) {
                setFieldError(field, 'Please enter a valid phone number');
                return false;
            }
            break;
        case 'password':
            if (value && value.length < 8) {
                setFieldError(field, 'Password must be at least 8 characters');
                return false;
            }
            break;
    }
    
    setFieldValid(field);
    return true;
}

function clearFieldError() {
    const field = this;
    const formGroup = field.closest('.form-group');
    formGroup.classList.remove('invalid');
    
    // Remove error message
    const errorMsg = formGroup.querySelector('.error-message');
    if (errorMsg) {
        errorMsg.remove();
    }
}

function setFieldError(field, message) {
    const formGroup = field.closest('.form-group');
    formGroup.classList.add('invalid');
    formGroup.classList.remove('valid');
    
    // Remove existing error message
    const existingError = formGroup.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }
    
    // Add new error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.style.color = '#f44336';
    errorDiv.style.fontSize = '0.85rem';
    errorDiv.style.marginTop = '0.25rem';
    errorDiv.textContent = message;
    
    const helpText = formGroup.querySelector('.form-help');
    if (helpText) {
        formGroup.insertBefore(errorDiv, helpText);
    } else {
        formGroup.appendChild(errorDiv);
    }
}

function setFieldValid(field) {
    const formGroup = field.closest('.form-group');
    formGroup.classList.add('valid');
    formGroup.classList.remove('invalid');
    
    // Remove error message
    const errorMsg = formGroup.querySelector('.error-message');
    if (errorMsg) {
        errorMsg.remove();
    }
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function isValidPhone(phone) {
    if (!phone) return true; // Phone is optional
    const phoneRegex = /^\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$/;
    return phoneRegex.test(phone);
}

function checkEmailAvailability(email) {
    // This would typically make an API call to check if email is available
    // For now, we'll just show a loading state
    const emailField = document.getElementById('email');
    const formGroup = emailField.closest('.form-group');
    
    formGroup.classList.add('loading');
    
    // Simulate API call
    setTimeout(() => {
        formGroup.classList.remove('loading');
        // In a real implementation, you'd check the API response
        setFieldValid(emailField);
    }, 1000);
}

function updatePasswordStrength(password) {
    const strengthIndicator = document.getElementById('password-strength');
    if (!strengthIndicator) {
        // Create strength indicator if it doesn't exist
        const passwordGroup = document.getElementById('password').closest('.form-group');
        const indicator = document.createElement('div');
        indicator.id = 'password-strength';
        indicator.className = 'password-strength';
        indicator.style.marginTop = '0.5rem';
        passwordGroup.appendChild(indicator);
    }
    
    const strength = calculatePasswordStrength(password);
    const indicator = document.getElementById('password-strength');
    
    indicator.innerHTML = `
        <div class="strength-bar">
            <div class="strength-fill strength-${strength.level}" style="width: ${strength.percentage}%"></div>
        </div>
        <div class="strength-text">${strength.text}</div>
    `;
}

function calculatePasswordStrength(password) {
    let score = 0;
    let feedback = [];
    
    if (password.length >= 8) score += 25;
    else feedback.push('at least 8 characters');
    
    if (/[a-z]/.test(password)) score += 25;
    else feedback.push('lowercase letters');
    
    if (/[A-Z]/.test(password)) score += 25;
    else feedback.push('uppercase letters');
    
    if (/[0-9]/.test(password)) score += 25;
    else feedback.push('numbers');
    
    if (/[^A-Za-z0-9]/.test(password)) score += 10;
    
    let level, text;
    if (score < 30) {
        level = 'weak';
        text = 'Weak - Add ' + feedback.slice(0, 2).join(' and ');
    } else if (score < 60) {
        level = 'fair';
        text = 'Fair - Add ' + feedback.slice(0, 1).join('');
    } else if (score < 90) {
        level = 'good';
        text = 'Good';
    } else {
        level = 'strong';
        text = 'Strong';
    }
    
    return { level, text, percentage: Math.min(score, 100) };
}

async function handleFormSubmission(event) {
    event.preventDefault();
    
    const form = event.target;
    const submitBtn = document.getElementById('register-btn');
    const formData = new FormData(form);
    
    // Validate all fields
    const isValid = validateForm(form);
    if (!isValid) {
        showMessage('Please correct the errors above', 'error');
        return;
    }
    
    // Show loading state
    submitBtn.classList.add('loading');
    submitBtn.disabled = true;
    
    try {
        // Prepare data
        const data = {
            email: formData.get('email'),
            password: formData.get('password'),
            first_name: formData.get('first_name'),
            last_name: formData.get('last_name'),
            phone: formData.get('phone'),
            company: formData.get('company'),
            profession: formData.get('profession'),
            selected_plan: formData.get('selected_plan'),
            terms_accepted: formData.get('terms_accepted') === 'on',
            marketing_emails: formData.get('marketing_emails') === 'on'
        };
        
        // Validate terms acceptance
        if (!data.terms_accepted) {
            showMessage('You must accept the Terms of Service and Privacy Policy', 'error');
            return;
        }
        
        // Submit registration
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showMessage(result.message, 'success');
            
            // If checkout URL provided, redirect to payment
            if (result.checkout_url) {
                setTimeout(() => {
                    window.location.href = result.checkout_url;
                }, 2000);
            } else {
                // Redirect to dashboard or verification page
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 2000);
            }
        } else {
            showMessage(result.error, 'error');
        }
        
    } catch (error) {
        console.error('Registration error:', error);
        showMessage('Registration failed. Please try again.', 'error');
    } finally {
        // Reset loading state
        submitBtn.classList.remove('loading');
        submitBtn.disabled = false;
    }
}

function validateForm(form) {
    const inputs = form.querySelectorAll('input[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!validateField({ target: input })) {
            isValid = false;
        }
    });
    
    // Additional validations
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm_password').value;
    
    if (password !== confirmPassword) {
        setFieldError(document.getElementById('confirm_password'), 'Passwords do not match');
        isValid = false;
    }
    
    return isValid;
}

function showMessage(message, type) {
    const messagesContainer = document.getElementById('form-messages');
    
    // Clear existing messages
    messagesContainer.innerHTML = '';
    
    // Create new message
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = message;
    
    messagesContainer.appendChild(messageDiv);
    
    // Auto-hide success messages
    if (type === 'success') {
        setTimeout(() => {
            messageDiv.remove();
        }, 5000);
    }
}

// Social authentication functions (placeholder)
function signInWithGoogle() {
    showMessage('Google sign-in coming soon!', 'warning');
}

function signInWithMicrosoft() {
    showMessage('Microsoft sign-in coming soon!', 'warning');
}

// Add CSS for password strength indicator
const style = document.createElement('style');
style.textContent = `
    .password-strength {
        margin-top: 0.5rem;
    }
    
    .strength-bar {
        height: 4px;
        background: #e1e5e9;
        border-radius: 2px;
        overflow: hidden;
        margin-bottom: 0.25rem;
    }
    
    .strength-fill {
        height: 100%;
        transition: width 0.3s ease, background-color 0.3s ease;
    }
    
    .strength-weak { background: #f44336; }
    .strength-fair { background: #ff9800; }
    .strength-good { background: #2196f3; }
    .strength-strong { background: #4caf50; }
    
    .strength-text {
        font-size: 0.85rem;
        color: #666;
    }
    
    .error-message {
        color: #f44336;
        font-size: 0.85rem;
        margin-top: 0.25rem;
    }
`;
document.head.appendChild(style); 