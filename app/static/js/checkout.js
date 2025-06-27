document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('checkout-form');
    const paymentMethod = document.getElementById('payment_method');
    
    // Payment method selection
    const paymentMethodBtns = document.querySelectorAll('.payment-option');
    const paymentForms = document.querySelectorAll('.payment-form');

    paymentMethodBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Remove active class from all buttons
            paymentMethodBtns.forEach(b => b.classList.remove('active'));
            // Add active class to clicked button
            this.classList.add('active');
            
            const method = this.dataset.method;
            paymentMethod.value = method;
            
            // Show/hide appropriate payment form
            paymentForms.forEach(form => {
                form.classList.add('d-none');
            });
            document.getElementById(`${method}-form`).classList.remove('d-none');
        });
    });

    // Credit card validation
    const cardNumberInput = document.getElementById('card_number');
    const cardExpiryInput = document.getElementById('expiry_date');
    const cardCVVInput = document.getElementById('cvv');

    if (cardNumberInput) {
        cardNumberInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            value = value.replace(/(\d{4})/g, '$1 ').trim();
            e.target.value = value.substring(0, 19);
        });
    }

    if (cardExpiryInput) {
        cardExpiryInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length >= 2) {
                value = value.substring(0, 2) + '/' + value.substring(2);
            }
            e.target.value = value.substring(0, 5);
        });
    }

    // Form submission handling
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const submitBtn = this.querySelector('button[type="submit"]');
            const spinner = document.getElementById('loading-spinner');
            
            try {
                submitBtn.disabled = true;
                spinner.classList.remove('d-none');

                const formData = new FormData(this);
                const response = await fetch('/checkout', {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    const data = await response.json();
                    window.location.href = `/order/confirmation/${data.order_id}`;
                } else {
                    throw new Error('Checkout failed');
                }
            } catch (error) {
                Swal.fire({
                    icon: 'error',
                    title: 'Checkout Error',
                    text: 'There was a problem processing your payment. Please try again.'
                });
            } finally {
                submitBtn.disabled = false;
                spinner.classList.add('d-none');
            }
        });
    }
});