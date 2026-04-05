document.addEventListener('DOMContentLoaded', function() {
    const toggleButtons = document.querySelectorAll('.toggle-btn');

    toggleButtons.forEach(button => {
        const vehicleId = button.dataset.vehicleId;
        const reservationList = document.getElementById(`reservations-${vehicleId}`);

        // Skip if reservation list is missing
        if (!reservationList) {
            console.warn(`Reservation list not found for vehicle ID: ${vehicleId}`);
            return;
        }

        // Initialize ARIA attributes
        button.setAttribute('aria-expanded', 'false');
        button.setAttribute('aria-controls', `reservations-${vehicleId}`);
        reservationList.setAttribute('aria-hidden', 'true');

        button.addEventListener('click', function() {
            const isExpanded = this.getAttribute('aria-expanded') === 'true';
            
            // Toggle visibility with slide animation
            if (isExpanded) {
                reservationList.style.maxHeight = reservationList.scrollHeight + 'px';
                setTimeout(() => {
                    reservationList.style.maxHeight = '0';
                    reservationList.classList.add('hidden');
                }, 10);
            } else {
                reservationList.classList.remove('hidden');
                reservationList.style.maxHeight = reservationList.scrollHeight + 'px';
                setTimeout(() => {
                    reservationList.style.maxHeight = 'none';
                }, 300); // Match CSS transition duration
            }

            // Update ARIA attributes
            this.setAttribute('aria-expanded', !isExpanded);
            reservationList.setAttribute('aria-hidden', isExpanded);

            // Toggle active class for icon rotation
            this.classList.toggle('active');
        });
    });
});