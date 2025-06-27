document.addEventListener('DOMContentLoaded', function() {
    // Handle category filter changes
    const categoryInputs = document.querySelectorAll('input[name="category"]');
    categoryInputs.forEach(input => {
        input.addEventListener('change', function() {
            const params = new URLSearchParams(window.location.search);
            
            if (this.checked) {
                params.set('category_id', this.value);
            } else {
                params.delete('category_id');
            }
            
            // Reload page with new filters
            window.location.search = params.toString();
        });
    });
    
    // Handle brand filter changes
    const brandInputs = document.querySelectorAll('input[name="brand"]');
    brandInputs.forEach(input => {
        input.addEventListener('change', function() {
            const params = new URLSearchParams(window.location.search);
            
            if (this.checked) {
                params.set('brand_id', this.value);
            } else {
                params.delete('brand_id');
            }
            
            // Reload page with new filters
            window.location.search = params.toString();
        });
    });
    
    // Apply Filters button handler
    document.querySelector('.btn-apply-filters')?.addEventListener('click', function() {
        const selectedCategories = Array.from(document.querySelectorAll('input[name="category"]:checked'))
            .map(input => input.value);
            
        const params = new URLSearchParams();
        if (selectedCategories.length) {
            params.set('category_id', selectedCategories[0]); // For now, just use first selected
        }
        
        window.location.search = params.toString();
    });
});
