document.addEventListener('DOMContentLoaded', function() {
    const quickViewModal = new bootstrap.Modal(document.getElementById('quickViewModal'));
    const productCards = document.querySelectorAll('.product-card');

    // Quick view functionality
    productCards.forEach(card => {
        const quickViewBtn = card.querySelector('.quick-view-btn');
        quickViewBtn.addEventListener('click', async () => {
            const productId = card.dataset.id;
            try {
                const response = await fetch(`/api/products/${productId}`);
                const product = await response.json();
                
                document.getElementById('productModalLabel').textContent = product.name;
                document.querySelector('.modal-product-image').src = product.image;
                document.querySelector('.modal-price').textContent = `$${product.price}`;
                document.querySelector('.modal-brand').textContent = `Brand: ${product.brand}`;
                document.querySelector('.modal-description').textContent = product.description;
                
                quickViewModal.show();
            } catch (error) {
                console.error('Error fetching product details:', error);
            }
        });
    });

    // Lazy loading images
    const lazyImages = document.querySelectorAll('img[loading="lazy"]');
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    observer.unobserve(img);
                }
            });
        });

        lazyImages.forEach(img => imageObserver.observe(img));
    }

    // Add to cart functionality
    const addToCartBtns = document.querySelectorAll('.add-to-cart-btn');
    addToCartBtns.forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const productId = btn.closest('.product-card').dataset.id;
            
            try {
                const response = await fetch('/cart/add/' + productId, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                
                if (response.ok) {
                    const toast = new bootstrap.Toast(document.getElementById('addedToCartToast'));
                    toast.show();
                    updateCartBadge();
                }
            } catch (error) {
                console.error('Error adding to cart:', error);
            }
        });
    });

    // Initialize product image lazy loading
    const productImages = document.querySelectorAll('.product-image[loading="lazy"]');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.add('loaded');
                    observer.unobserve(img);
                }
            });
        });

        productImages.forEach(img => imageObserver.observe(img));
    }

    // Add to cart functionality
    const addToCartButtons = document.querySelectorAll('.add-to-cart-btn, .add-to-cart-modal');
    
    addToCartButtons.forEach(button => {
        button.addEventListener('click', async function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const productId = this.closest('.product-card').dataset.id;
            const originalHTML = this.innerHTML;
            
            try {
                // Show loading state
                this.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                this.disabled = true;

                // Send request to add item to cart
                const response = await fetch(`/cart/add/${productId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });

                if (!response.ok) throw new Error('Failed to add item to cart');

                const data = await response.json();
                
                // Update cart count in navbar
                const cartBadge = document.querySelector('.nav-link .badge');
                if (cartBadge) {
                    cartBadge.textContent = data.cart_count;
                    cartBadge.classList.add('animate__animated', 'animate__tada');
                }

                // Show success message
                showToast('Product added to cart successfully!', 'success');
                
            } catch (error) {
                console.error('Error:', error);
                showToast('Failed to add item to cart', 'danger');
            } finally {
                // Reset button state
                this.innerHTML = originalHTML;
                this.disabled = false;
            }
        });
    });

    // Quick view functionality
    const quickViewButtons = document.querySelectorAll('.quick-view-btn');
    quickViewButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const card = this.closest('.product-card');
            const productId = card.dataset.id;
            const productName = card.querySelector('.product-title').textContent;
            const productPrice = card.querySelector('.price').textContent;
            const productImage = card.querySelector('.product-image').src;

            // Update quick view modal content
            const modal = document.getElementById('quickViewModal');
            modal.querySelector('.modal-title').textContent = productName;
            modal.querySelector('.modal-product-image').src = productImage;
            modal.querySelector('.modal-price').textContent = productPrice;

            // Show modal
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();
        });
    });

    // Toast notification function
    function showToast(message, type = 'success') {
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
});