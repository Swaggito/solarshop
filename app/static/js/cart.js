document.addEventListener('DOMContentLoaded', function() {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    // Handle quantity changes
    document.querySelectorAll('.quantity-control').forEach(control => {
        const minusBtn = control.querySelector('.minus-btn');
        const plusBtn = control.querySelector('.plus-btn');
        const input = control.querySelector('.quantity-input');
        const itemId = control.dataset.itemId;
        const pricePerUnit = parseFloat(control.dataset.price);

        minusBtn?.addEventListener('click', () => updateQuantity(input, -1, itemId, pricePerUnit));
        plusBtn?.addEventListener('click', () => updateQuantity(input, 1, itemId, pricePerUnit));
        input?.addEventListener('change', () => updateQuantity(input, 0, itemId, pricePerUnit));
    });

    // Handle remove item buttons
    document.querySelectorAll('.remove-item').forEach(button => {
        button.addEventListener('click', async function(e) {
            e.preventDefault();
            const itemId = this.dataset.itemId;
            
            try {
                const response = await fetch(`/cart/remove/${itemId}`, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': csrfToken
                    },
                    credentials: 'same-origin'
                });

                if (!response.ok) throw new Error('Network response was not ok');

                const data = await response.json();
                if (data.status === 'success') {
                    // Remove item from DOM
                    const cartItem = this.closest('.cart-item');
                    cartItem.classList.add('animate__animated', 'animate__fadeOutRight');
                    setTimeout(() => {
                        cartItem.remove();
                        updateCartTotal();
                        updateCartCount(data.cart_count);
                    }, 500);
                }
            } catch (error) {
                console.error('Error:', error);
                showNotification('Failed to remove item', 'danger');
            }
        });
    });

    // Quantity update function
    async function updateQuantity(input, change, itemId, pricePerUnit) {
        let newValue = parseInt(input.value) + change;
        newValue = Math.max(1, Math.min(newValue, 99)); // Limit between 1 and 99
        
        if (newValue === parseInt(input.value)) return;

        try {
            const response = await fetch(`/cart/update/${itemId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ quantity: newValue }),
                credentials: 'same-origin'
            });

            if (!response.ok) throw new Error('Network response was not ok');

            const data = await response.json();
            if (data.status === 'success') {
                input.value = newValue;
                updateItemTotal(input.closest('.cart-item'), newValue, pricePerUnit);
                updateCartTotal();
                showNotification('Cart updated successfully', 'success');
            }
        } catch (error) {
            console.error('Error:', error);
            showNotification('Failed to update quantity', 'danger');
            input.value = input.defaultValue;
        }
    }

    // Update item total
    function updateItemTotal(cartItem, quantity, price) {
        const totalElement = cartItem.querySelector('.item-total');
        const newTotal = (quantity * price).toFixed(2);
        totalElement.textContent = `$${newTotal}`;
    }

    // Update cart total
    function updateCartTotal() {
        const subtotal = Array.from(document.querySelectorAll('.item-total'))
            .reduce((sum, el) => sum + parseFloat(el.textContent.replace('$', '')), 0);
        
        document.getElementById('subtotal').textContent = `$${subtotal.toFixed(2)}`;
        
        const tax = subtotal * 0.1; // 10% tax
        document.getElementById('tax').textContent = `$${tax.toFixed(2)}`;
        
        const total = subtotal + tax;
        document.getElementById('total').textContent = `$${total.toFixed(2)}`;
        
        // Update checkout button state
        const checkoutBtn = document.querySelector('.checkout-btn');
        if (checkoutBtn) {
            checkoutBtn.disabled = subtotal === 0;
        }
    }

    // Show notification
    function showNotification(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0 position-fixed bottom-0 end-0 m-3`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        document.body.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        toast.addEventListener('hidden.bs.toast', () => toast.remove());
    }

    // Update cart badge count
    function updateCartCount(count) {
        const badge = document.querySelector('.nav-link .badge');
        if (badge) {
            badge.textContent = count;
            badge.classList.add('animate__animated', 'animate__tada');
            setTimeout(() => badge.classList.remove('animate__animated', 'animate__tada'), 1000);
        }
    }

    // Handle all add to cart forms
    document.querySelectorAll('form[action*="/cart/add/"]').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Adding...';

            fetch(this.action, {
                method: 'POST',
                body: new FormData(this),
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Update cart count in navbar
                    const cartBadge = document.querySelector('.cart-count');
                    if (cartBadge) {
                        cartBadge.textContent = data.cart_count;
                        cartBadge.classList.add('animate__animated', 'animate__tada');
                    }
                    
                    // Show success toast
                    showToast(data.message, 'success');
                } else {
                    showToast(data.message || 'Failed to add item to cart.', 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('Failed to add item to cart.', 'danger');
            })
            .finally(() => {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            });
        });
    });
    
    // Toast function (if not already defined in base template)
    function showToast(message, type = 'success') {
        const toastContainer = document.querySelector('.toast-container');
        const toastEl = document.createElement('div');
        toastEl.className = `toast align-items-center text-white bg-${type} border-0`;
        toastEl.setAttribute('role', 'alert');
        toastEl.setAttribute('aria-live', 'assertive');
        toastEl.setAttribute('aria-atomic', 'true');
        
        toastEl.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        toastContainer.appendChild(toastEl);
        const toast = new bootstrap.Toast(toastEl);
        toast.show();
        
        // Remove toast after it's hidden
        toastEl.addEventListener('hidden.bs.toast', () => {
            toastEl.remove();
        });
    }
});