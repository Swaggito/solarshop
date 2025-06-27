document.addEventListener('DOMContentLoaded', function() {
    // Initialize elements
    const productCards = document.querySelectorAll('.product-card');
    const quickViewButtons = document.querySelectorAll('.quick-view-btn');
    const modal = new bootstrap.Modal(document.getElementById('quickViewModal'));
    const modalTitle = document.getElementById('productModalLabel');
    const modalImage = document.querySelector('.modal-product-image');
    const modalPrice = document.querySelector('.modal-price');
    const modalBrand = document.querySelector('.modal-brand');
    const modalDescription = document.querySelector('.modal-description');
    const viewDetailsLink = document.querySelector('.view-details-link');
    const cartToast = new bootstrap.Toast(document.getElementById('addedToCartToast'));
    
    // Add skeleton loading to images
    const lazyImages = document.querySelectorAll('.product-image');
    lazyImages.forEach(img => {
        // Create skeleton element
        const skeleton = document.createElement('div');
        skeleton.className = 'skeleton';
        skeleton.style.width = '100%';
        skeleton.style.height = '100%';
        skeleton.style.position = 'absolute';
        skeleton.style.top = '0';
        skeleton.style.left = '0';
        
        // Insert skeleton before image
        img.parentElement.appendChild(skeleton);
        
        // Load image
        img.onload = function() {
            skeleton.style.opacity = '0';
            setTimeout(() => {
                skeleton.remove();
                img.style.opacity = '1';
            }, 300);
        };
        
        // Set initial opacity
        img.style.opacity = '0';
        img.style.transition = 'opacity 0.5s ease';
    });
    
    // Quick view functionality
    quickViewButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            const card = this.closest('.product-card');
            const id = card.dataset.id;
            const name = card.querySelector('.card-title').textContent;
            const price = card.querySelector('.price').textContent;
            const brand = card.querySelector('.brand').textContent;
            
            // Set modal content
            modalTitle.textContent = name;
            modalPrice.textContent = price;
            modalBrand.textContent = brand;
            
            // Set image with fade effect
            modalImage.style.opacity = '0';
            setTimeout(() => {
                modalImage.src = card.querySelector('.product-image').src;
                modalImage.onload = () => {
                    modalImage.style.opacity = '1';
                };
            }, 300);
            
            // Set description and link
            modalDescription.textContent = "Detailed product description would appear here. This includes specifications, features, and other important information about the product.";
            viewDetailsLink.href = `/product/${id}`;
            
            // Show modal with animation
            modal.show();
        });
    });
    
    // Add to cart functionality
    const addToCart = async (id, name, element) => {
        // Visual feedback
        const originalHTML = element.innerHTML;
        element.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Adding...';
        element.disabled = true;
        
        try {
            // Simulate API request
            await new Promise(resolve => setTimeout(resolve, 800));
            
            // In real app: fetch('/cart/add', { method: 'POST', body: JSON.stringify({ productId: id }) })
            console.log(`Added product ${id} to cart: ${name}`);
            
            // Show success toast
            cartToast.show();
            
            // Update cart count (assuming you have an element with id "cart-count")
            const cartCount = document.getElementById('cart-count');
            if (cartCount) {
                const currentCount = parseInt(cartCount.textContent) || 0;
                cartCount.textContent = currentCount + 1;
                
                // Animation effect
                cartCount.classList.add('animate-bounce');
                setTimeout(() => {
                    cartCount.classList.remove('animate-bounce');
                }, 1000);
            }
        } catch (error) {
            console.error('Error adding to cart:', error);
            // Show error toast
            const errorToast = new bootstrap.Toast(document.getElementById('errorToast'));
            if (errorToast) errorToast.show();
        } finally {
            // Reset button state
            element.innerHTML = originalHTML;
            element.disabled = false;
        }
    };
    
    // Attach event listeners to all add-to-cart buttons
    document.querySelectorAll('.add-to-cart-btn, .add-to-cart-modal').forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            const card = this.closest('.product-card');
            const id = card.dataset.id;
            const name = card.querySelector('.card-title').textContent;
            
            addToCart(id, name, this);
        });
    });
    
    // Product card click handler
    productCards.forEach(card => {
        card.addEventListener('click', function(e) {
            // Ignore clicks on buttons and links
            if (e.target.closest('button') || e.target.closest('a')) return;
            
            const id = this.dataset.id;
            window.location.href = `/product/${id}`;
        });
        
        // Add keyboard accessibility
        card.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                const id = card.dataset.id;
                window.location.href = `/product/${id}`;
            }
        });
        
        // Add focus styles for accessibility
        card.setAttribute('tabindex', '0');
    });
    
    // Infinite scroll implementation (optional)
    let isLoading = false;
    const loadMoreProducts = async () => {
        if (isLoading) return;
        isLoading = true;
        
        // Show loading spinner
        const loader = document.createElement('div');
        loader.className = 'text-center py-5';
        loader.innerHTML = '<div class="spinner-border text-primary"></div>';
        document.querySelector('.row').appendChild(loader);
        
        try {
            // Simulate API request
            await new Promise(resolve => setTimeout(resolve, 1500));
            
            // In real app: fetch next page of products
            console.log('Loading more products...');
            
            // Add new products to the grid
            // This would be implemented with actual product data
        } catch (error) {
            console.error('Error loading more products:', error);
        } finally {
            loader.remove();
            isLoading = false;
        }
    };
    
    // Infinite scroll trigger
    window.addEventListener('scroll', () => {
        const { scrollTop, scrollHeight, clientHeight } = document.documentElement;
        if (scrollTop + clientHeight >= scrollHeight - 500 && !isLoading) {
            loadMoreProducts();
        }
    });
    
    // Add to cart animation effect
    document.addEventListener('click', function(e) {
        if (e.target.closest('.add-to-cart-btn') || e.target.closest('.add-to-cart-modal')) {
            const button = e.target.closest('button');
            button.classList.add('animate-pulse');
            setTimeout(() => {
                button.classList.remove('animate-pulse');
            }, 500);
        }
    });
    
    // Product image gallery
    const mainImage = document.querySelector('#main-product-image');
    const thumbnails = document.querySelectorAll('.product-thumbnail');

    thumbnails.forEach(thumb => {
        thumb.addEventListener('click', function() {
            mainImage.src = this.getAttribute('data-full-image');
            thumbnails.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
        });
    });

    // Quantity controls
    const quantityInput = document.querySelector('.quantity-input');
    if (quantityInput) {
        document.querySelector('.quantity-decrease').addEventListener('click', () => {
            if (quantityInput.value > 1) quantityInput.value--;
        });
        document.querySelector('.quantity-increase').addEventListener('click', () => {
            quantityInput.value = parseInt(quantityInput.value) + 1;
        });
    }

    // Add to cart with animation
    const addToCartBtn = document.querySelector('.add-to-cart-btn');
    if (addToCartBtn) {
        addToCartBtn.addEventListener('click', async function(e) {
            e.preventDefault();
            const productId = this.dataset.productId;
            const quantity = document.querySelector('.quantity-input').value;

            try {
                const response = await fetch('/cart/add/' + productId, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ quantity: quantity })
                });

                if (response.ok) {
                    showSuccessMessage();
                    updateCartBadge();
                }
            } catch (error) {
                console.error('Error:', error);
            }
        });
    }

    // Handle lazy loading
    document.addEventListener('DOMContentLoaded', function() {
        const lazyImages = document.querySelectorAll('.lazy-image');
        
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.add('loaded');
                        imageObserver.unobserve(img);
                    }
                });
            });

            lazyImages.forEach(img => imageObserver.observe(img));
        }
    });

    // Update main product image
    function updateMainImage(src) {
        const mainImage = document.getElementById('main-product-image');
        mainImage.style.opacity = '0';
        
        setTimeout(() => {
            mainImage.src = src;
            mainImage.style.opacity = '1';
        }, 300);
    }
});

function showSuccessMessage() {
    const toast = new bootstrap.Toast(document.getElementById('addToCartToast'));
    toast.show();
}

function updateCartBadge(count) {
    const badge = document.querySelector('.cart-badge');
    if (badge) {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'inline' : 'none';
    }
}