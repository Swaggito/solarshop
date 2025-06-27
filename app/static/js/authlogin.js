// Login Form Enhancement
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.querySelector('.login-container form');
    
    if (loginForm) {
        // Form submission handler
        loginForm.addEventListener('submit', function(e) {
            const submitButton = this.querySelector('button[type="submit"]');
            
            // Show loading state
            submitButton.innerHTML = `
                <span class="spinner"></span>
                Logging in...
            `;
            submitButton.classList.add('btn-loading');
            submitButton.disabled = true;
        });

        // Add floating label effect
        const floatLabels = () => {
            const inputs = document.querySelectorAll('.login-container .form-control');
            inputs.forEach(input => {
                const label = input.previousElementSibling;
                
                if (input.value) {
                    label.classList.add('active');
                }
                
                input.addEventListener('focus', () => {
                    label.classList.add('active');
                });
                
                input.addEventListener('blur', () => {
                    if (!input.value) {
                        label.classList.remove('active');
                    }
                });
            });
        };
        
        floatLabels();

        // Password visibility toggle
        const passwordInput = document.querySelector('#password');
        if (passwordInput) {
            const passwordToggle = document.createElement('span');
            passwordToggle.className = 'password-toggle';
            passwordToggle.innerHTML = '<i class="far fa-eye"></i>';
            passwordInput.parentNode.appendChild(passwordToggle);
            
            passwordToggle.addEventListener('click', function() {
                const icon = this.querySelector('i');
                if (passwordInput.type === 'password') {
                    passwordInput.type = 'text';
                    icon.classList.replace('fa-eye', 'fa-eye-slash');
                } else {
                    passwordInput.type = 'password';
                    icon.classList.replace('fa-eye-slash', 'fa-eye');
                }
            });
        }
    }
});