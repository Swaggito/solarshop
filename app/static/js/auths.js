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
});