document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const passwordInput = document.querySelector('#password');
    const passwordStrength = document.createElement('div');
    passwordStrength.className = 'password-strength';
    passwordStrength.innerHTML = '<div class="password-strength-bar"></div>';
    passwordInput.parentNode.appendChild(passwordStrength);
    const strengthBar = passwordStrength.querySelector('.password-strength-bar');

    // Password strength indicator
    passwordInput.addEventListener('input', function() {
        const strength = calculatePasswordStrength(this.value);
        updateStrengthIndicator(strength);
    });

    // Form submission handler
    form.addEventListener('submit', function(e) {
        const submitButton = this.querySelector('button[type="submit"]');
        
        // Show loading state
        submitButton.innerHTML = `
            <span class="spinner"></span>
            Registering...
        `;
        submitButton.classList.add('btn-loading');
        submitButton.disabled = true;
    });

    // Field validation
    const fields = ['username', 'email', 'password', 'confirm'];
    fields.forEach(field => {
        const input = document.querySelector(`#${field}`);
        if (input) {
            input.addEventListener('blur', validateField);
        }
    });

    function validateField(e) {
        const field = e.target;
        const value = field.value.trim();
        const fieldName = field.id;
        const formGroup = field.closest('.mb-3');
        let isValid = true;
        let feedback = '';

        // Remove previous error classes
        field.classList.remove('is-invalid');
        let existingFeedback = formGroup.querySelector('.invalid-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }

        // Field specific validation
        switch(fieldName) {
            case 'username':
                if (value.length < 3) {
                    feedback = 'Username must be at least 3 characters';
                    isValid = false;
                }
                break;
            case 'email':
                if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
                    feedback = 'Please enter a valid email address';
                    isValid = false;
                }
                break;
            case 'password':
                if (value.length < 8) {
                    feedback = 'Password must be at least 8 characters';
                    isValid = false;
                }
                break;
            case 'confirm':
                const password = document.querySelector('#password').value;
                if (value !== password) {
                    feedback = 'Passwords do not match';
                    isValid = false;
                }
                break;
        }

        if (!isValid) {
            field.classList.add('is-invalid');
            const feedbackElement = document.createElement('div');
            feedbackElement.className = 'invalid-feedback';
            feedbackElement.textContent = feedback;
            formGroup.appendChild(feedbackElement);
        }

        return isValid;
    }

    function calculatePasswordStrength(password) {
        let strength = 0;
        
        // Length contributes up to 50%
        strength += Math.min(password.length / 12 * 50, 50);
        
        // Character variety contributes up to 50%
        const hasLower = /[a-z]/.test(password);
        const hasUpper = /[A-Z]/.test(password);
        const hasNumber = /[0-9]/.test(password);
        const hasSpecial = /[^a-zA-Z0-9]/.test(password);
        
        const varietyCount = [hasLower, hasUpper, hasNumber, hasSpecial].filter(Boolean).length;
        strength += (varietyCount / 4) * 50;
        
        return Math.min(Math.round(strength), 100);
    }

    function updateStrengthIndicator(strength) {
        let color, width;
        
        if (strength < 30) {
            color = '#fc8181'; // Red
            width = '30%';
        } else if (strength < 70) {
            color = '#f6ad55'; // Orange
            width = '60%';
        } else {
            color = '#68d391'; // Green
            width = '100%';
        }
        
        strengthBar.style.width = width;
        strengthBar.style.backgroundColor = color;
    }

    // Forgot Password Form Handler
    const forgotForm = document.getElementById('forgotPasswordForm');
    if (forgotForm) {
        forgotForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const emailInput = this.querySelector('#email');
            const submitBtn = this.querySelector('button[type="submit"]');
            const btnText = submitBtn.querySelector('.btn-text');
            const btnLoading = submitBtn.querySelector('.btn-loading');
            
            // Reset errors
            emailInput.classList.remove('is-invalid');
            
            // Basic validation
            if (!emailInput.value.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
                emailInput.classList.add('is-invalid');
                emailInput.nextElementSibling.textContent = 'Please enter a valid email address';
                return;
            }
            
            // Show loading state
            submitBtn.disabled = true;
            btnText.style.display = 'none';
            btnLoading.classList.remove('d-none');
            
            try {
                const response = await fetch('/forgot-password', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
                    },
                    body: JSON.stringify({
                        email: emailInput.value
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Show success message
                    forgotForm.innerHTML = `
                        <div class="alert alert-success">
                            <i class="fas fa-check-circle me-2"></i>
                            Password reset instructions have been sent to your email.
                            Please check your inbox.
                        </div>
                        <div class="text-center mt-4">
                            <a href="/login" class="btn btn-outline-primary">
                                <i class="fas fa-arrow-left me-2"></i>Back to Login
                            </a>
                        </div>
                    `;
                } else {
                    throw new Error(data.message || 'Failed to send reset link');
                }
                
            } catch (error) {
                emailInput.classList.add('is-invalid');
                emailInput.nextElementSibling.textContent = error.message || 'An error occurred. Please try again.';
                
                // Reset button state
                submitBtn.disabled = false;
                btnText.style.display = 'block';
                btnLoading.classList.add('d-none');
            }
        });
    }
});