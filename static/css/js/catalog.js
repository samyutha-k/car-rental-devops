document.addEventListener('DOMContentLoaded', function() {
    const vehicleCards = document.querySelectorAll('.vehicle-card');

    vehicleCards.forEach(card => {
        const carousel = card.querySelector('.vehicle-image-carousel');
        const imageElement = card.querySelector('.vehicle-image');
        const prevBtn = card.querySelector('.carousel-btn.prev');
        const nextBtn = card.querySelector('.carousel-btn.next');

        // Skip if no carousel or missing elements
        if (!carousel || !imageElement || !prevBtn || !nextBtn) {
            console.warn('Skipping carousel initialization: missing elements', card);
            return;
        }

        // Get images from data-images attribute
        let images = card.dataset.images ? card.dataset.images.split(',') : [];
        if (!images.length || images[0] === 'placeholder') {
            images = ['/static/uploads/vehicle-placeholder.jpg'];
        } else {
            images = images.map(img => `/static/uploads/${img.trim()}`);
        }

        let currentIndex = 0;
        let touchStartX = 0;
        let touchEndX = 0;

        // Create carousel dots container
        const dotsContainer = document.createElement('div');
        dotsContainer.className = 'carousel-dots';
        if (images.length > 1) {
            images.forEach((_, index) => {
                const dot = document.createElement('span');
                dot.className = 'carousel-dot';
                if (index === 0) dot.classList.add('active');
                dot.addEventListener('click', () => {
                    updateImage(index);
                });
                dotsContainer.appendChild(dot);
            });
            carousel.appendChild(dotsContainer);
        }

        // Function to update the image and dots
        function updateImage(index) {
            if (index < 0 || index >= images.length) return;
            imageElement.style.backgroundImage = `url('${images[index]}')`;
            currentIndex = index;

            // Update active dot
            const dots = dotsContainer.querySelectorAll('.carousel-dot');
            dots.forEach((dot, i) => {
                dot.classList.toggle('active', i === index);
            });
        }

        // Next button click
        nextBtn.addEventListener('click', () => {
            currentIndex = (currentIndex + 1) % images.length;
            updateImage(currentIndex);
        });

        // Previous button click
        prevBtn.addEventListener('click', () => {
            currentIndex = (currentIndex - 1 + images.length) % images.length;
            updateImage(currentIndex);
        });

        // Touch/swipe support
        carousel.addEventListener('touchstart', e => {
            touchStartX = e.changedTouches[0].screenX;
        });

        carousel.addEventListener('touchend', e => {
            touchEndX = e.changedTouches[0].screenX;
            const swipeDistance = touchEndX - touchStartX;
            if (swipeDistance > 50) {
                // Swipe right (previous)
                currentIndex = (currentIndex - 1 + images.length) % images.length;
                updateImage(currentIndex);
            } else if (swipeDistance < -50) {
                // Swipe left (next)
                currentIndex = (currentIndex + 1) % images.length;
                updateImage(currentIndex);
            }
        });

        // Auto-advance carousel every 5 seconds (optional)
        let autoAdvance = setInterval(() => {
            currentIndex = (currentIndex + 1) % images.length;
            updateImage(currentIndex);
        }, 5000);

        // Pause auto-advance on hover
        carousel.addEventListener('mouseenter', () => clearInterval(autoAdvance));
        carousel.addEventListener('mouseleave', () => {
            autoAdvance = setInterval(() => {
                currentIndex = (currentIndex + 1) % images.length;
                updateImage(currentIndex);
            }, 5000);
        });
    });
});