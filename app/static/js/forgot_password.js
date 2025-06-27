document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('forgotPasswordForm');
    const emailInput = document.getElementById('email');
    const submitBtn = form.querySelector('button[type="submit"]');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoading = submitBtn.querySelector('.btn-loading');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Reset previous errors
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
            const response = await fetch(form.action, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                },
                body: JSON.stringify({
                    email: emailInput.value
                })
            });

            const data = await response.json();

            if (data.success) {
                // Show success message
                form.innerHTML = `
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
            // Show error
            emailInput.classList.add('is-invalid');
            emailInput.nextElementSibling.textContent = error.message || 'An error occurred. Please try again.';
            
            // Reset button state
            submitBtn.disabled = false;
            btnText.style.display = 'block';
            btnLoading.classList.add('d-none');
        }
    });
});
