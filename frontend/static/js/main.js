// Simple JavaScript for DBS Event Management System

// Auto-hide flash messages after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.opacity = '0';
            setTimeout(function() {
                alert.remove();
            }, 300);
        }, 5000);
    });
});

// Confirm delete actions
function confirmDelete(message) {
    return confirm(message || 'Are you sure you want to delete this item?');
}

// Form validation helper
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;
    
    const inputs = form.querySelectorAll('[required]');
    let isValid = true;
    
    inputs.forEach(function(input) {
        if (!input.value.trim()) {
            input.classList.add('border-red-500');
            isValid = false;
        } else {
            input.classList.remove('border-red-500');
        }
    });
    
    return isValid;
}

// Date validation - ensure event date is in the future
document.addEventListener('DOMContentLoaded', function() {
    const dateInputs = document.querySelectorAll('input[type="datetime-local"]');
    
    dateInputs.forEach(function(input) {
        input.addEventListener('change', function() {
            const selectedDate = new Date(this.value);
            const now = new Date();
            
            if (selectedDate < now) {
                alert('Please select a future date and time');
                this.value = '';
            }
        });
    });
});

// Event filtering functionality
document.addEventListener('DOMContentLoaded', function() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const eventCards = document.querySelectorAll('.event-card');
    const visibleCountElement = document.getElementById('visible-events-count');
    
    if (filterButtons.length === 0 || eventCards.length === 0) return;
    
    filterButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const filterType = this.getAttribute('data-filter');
            
            // Update button styles
            filterButtons.forEach(function(btn) {
                btn.classList.remove('bg-blue-600', 'text-white');
                btn.classList.add('bg-gray-200', 'text-gray-700');
            });
            
            this.classList.remove('bg-gray-200', 'text-gray-700');
            this.classList.add('bg-blue-600', 'text-white');
            
            // Filter events
            let visibleCount = 0;
            eventCards.forEach(function(card) {
                const priceType = card.getAttribute('data-price-type');
                
                if (filterType === 'all' || priceType === filterType) {
                    card.style.display = 'block';
                    visibleCount++;
                } else {
                    card.style.display = 'none';
                }
            });
            
            // Update visible count
            if (visibleCountElement) {
                visibleCountElement.textContent = visibleCount;
            }
        });
    });
});
