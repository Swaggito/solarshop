// About page animations and interactions
document.addEventListener('DOMContentLoaded', function() {
    // Animated counter for mission stats
    const counters = document.querySelectorAll('.stat-value');
    const speed = 200;
    
    counters.forEach(counter => {
        const animate = () => {
            const value = +counter.dataset.count;
            const data = +counter.innerText;
            const time = value / speed;
            
            if (data < value) {
                counter.innerText = Math.ceil(data + time);
                setTimeout(animate, 1);
            } else {
                counter.innerText = value.toLocaleString();
            }
        };
        
        // Start animation when element is in viewport
        const observer = new IntersectionObserver((entries) => {
            if (entries[0].isIntersecting) {
                animate();
                observer.disconnect();
            }
        });
        
        observer.observe(counter);
    });

    // Timeline animations
    const timelineItems = document.querySelectorAll('.timeline-item');
    
    timelineItems.forEach(item => {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = 1;
                    entry.target.style.transform = 'translateY(0)';
                    observer.disconnect();
                }
            });
        }, { threshold: 0.3 });
        
        // Set initial state
        item.style.opacity = 0;
        item.style.transform = 'translateY(30px)';
        item.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        
        observer.observe(item);
    });

    // Team card hover effect enhancements
    const teamCards = document.querySelectorAll('.team-card');
    teamCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            const img = card.querySelector('.team-img');
            img.style.transform = 'scale(1.05)';
            img.style.transition = 'transform 0.5s ease';
        });
        
        card.addEventListener('mouseleave', () => {
            const img = card.querySelector('.team-img');
            img.style.transform = 'scale(1)';
        });
    });
});