// Cart functionality
document.addEventListener('DOMContentLoaded', function() {
  // Cart quantity adjustments
  document.querySelectorAll('.quantity-btn').forEach(button => {
    button.addEventListener('click', function() {
      const input = this.parentNode.querySelector('.quantity-input');
      let value = parseInt(input.value);
      
      if (this.classList.contains('plus')) {
        value++;
      } else if (this.classList.contains('minus') && value > 1) {
        value--;
      }
      
      input.value = value;
      updateCartTotal(this);
    });
  });

  // Remove cart items
  document.querySelectorAll('.remove-item').forEach(button => {
    button.addEventListener('click', function() {
      this.closest('.cart-item').remove();
      updateCartTotal();
    });
  });

  // Search functionality
  const searchInput = document.getElementById('search-input');
  if (searchInput) {
    searchInput.addEventListener('keyup', function() {
      const term = this.value.toLowerCase();
      document.querySelectorAll('.product-card').forEach(card => {
        const name = card.querySelector('.product-name').textContent.toLowerCase();
        card.style.display = name.includes(term) ? '' : 'none';
      });
    });
  }

  // Image gallery for product details
  const thumbnails = document.querySelectorAll('.thumbnail');
  if (thumbnails.length > 0) {
    const mainImage = document.getElementById('main-product-image');
    
    thumbnails.forEach(thumb => {
      thumb.addEventListener('click', function() {
        mainImage.src = this.src;
        thumbnails.forEach(t => t.classList.remove('active'));
        this.classList.add('active');
      });
    });
  }
});

function updateCartTotal(trigger = null) {
  let total = 0;
  let itemCount = 0;
  
  document.querySelectorAll('.cart-item').forEach(item => {
    const price = parseFloat(item.querySelector('.item-price').textContent.replace('$', ''));
    const quantity = parseInt(item.querySelector('.quantity-input').value);
    const subtotal = price * quantity;
    
    item.querySelector('.item-subtotal').textContent = '$' + subtotal.toFixed(2);
    total += subtotal;
    itemCount += quantity;
  });
  
  document.getElementById('cart-total').textContent = '$' + total.toFixed(2);
  
  // Update cart badge if changed from product page
  if (trigger && trigger.closest('.product-actions')) {
    const cartBadge = document.querySelector('.cart-badge');
    if (cartBadge) {
      cartBadge.textContent = itemCount;
    }
  }
}

// Initialize Bootstrap tooltips
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl)
})