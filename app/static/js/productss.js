document.addEventListener('DOMContentLoaded', function() {
    // Thumbnail selection
    const thumbnails = document.querySelectorAll('.thumbnail');
    thumbnails.forEach(thumb => {
        thumb.addEventListener('click', function() {
            // Remove active class from all thumbnails
            thumbnails.forEach(t => t.classList.remove('active'));
            // Add active class to clicked thumbnail
            this.classList.add('active');
            
            // Get the clicked image's source
            const imgSrc = this.src;
            
            // Update carousel image
            const carouselItems = document.querySelectorAll('.carousel-item');
            carouselItems.forEach((item, index) => {
                if (index === 0) {
                    const carouselImg = item.querySelector('img');
                    carouselImg.src = imgSrc;
                }
            });
            
            // Update the carousel to show the first slide
            const carousel = new bootstrap.Carousel(document.getElementById('product-carousel'), {
                interval: false
            });
            carousel.to(0);
        });
    });

    // Add to cart functionality
    const addToCartForm = document.getElementById('add-to-cart-form');
    if (addToCartForm) {
        addToCartForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const quantity = this.querySelector('input[name="quantity"]').value;
            const productId = this.getAttribute('action').split('product_id=')[1];
            
            // Show loading state
            this.querySelector('button[type="submit"]').innerHTML = `
                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                Adding...
            `;
            
            // Simulate API call
            setTimeout(() => {
                // Reset button
                this.querySelector('button[type="submit"]').innerHTML = `
                    <i class="bi bi-cart-plus"></i> Add to Cart
                `;
                
                // Create a notification
                const notification = document.createElement('div');
                notification.className = 'toast-container position-fixed bottom-0 end-0 p-3';
                
                const toast = document.createElement('div');
                toast.className = 'toast align-items-center text-white bg-success border-0';
                toast.setAttribute('role', 'alert');
                toast.setAttribute('aria-live', 'assertive');
                toast.setAttribute('aria-atomic', 'true');
                
                const toastHeader = document.createElement('div');
                toastHeader.className = 'd-flex';
                
                const toastBody = document.createElement('div');
                toastBody.className = 'toast-body';
                toastBody.textContent = `${quantity} ${quantity > 1 ? 'items' : 'item'} added to cart`;
                
                toast.append(toastHeader, toastBody);
                notification.appendChild(toast);
                document.body.appendChild(notification);
                
                // Show toast
                const bsToast = new bootstrap.Toast(toast);
                bsToast.show();
                
                // Remove toast after delay
                setTimeout(() => {
                    notification.remove();
                }, 3000);
            }, 1000);
        });
    }
});