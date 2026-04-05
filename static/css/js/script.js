document.addEventListener('DOMContentLoaded', function() {
    // Handle flash message dismissal
    const closeButtons = document.querySelectorAll('.close-flash');
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const flash = this.parentElement;
            flash.style.opacity = '0';
            setTimeout(() => {
                flash.style.display = 'none';
            }, 300); // Match CSS transition duration
        });
    });

    // Auto-dismiss flash messages after 5 seconds
    setTimeout(function() {
        const flashes = document.querySelectorAll('.flash');
        flashes.forEach(flash => {
            flash.style.opacity = '0';
            setTimeout(() => {
                flash.style.display = 'none';
            }, 300);
        });
    }, 5000);
});