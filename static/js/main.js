// Main JavaScript for Strava Workout Description Generator

// Global variables
let authWindow = null;
let authCheckInterval = null;

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is returning from auth
    checkAuthCallback();
    
    // Add smooth scrolling to internal links
    addSmoothScrolling();
    
    // Add intersection observer for animations
    setupScrollAnimations();
    
    // Listen for popup messages
    window.addEventListener('message', handlePopupMessage);
    
    // Add keyboard support for CTA buttons
    document.querySelectorAll('.cta-button').forEach(button => {
        button.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
    });
    
    // Add touch feedback for mobile
    if ('ontouchstart' in window) {
        document.querySelectorAll('.cta-button, .capability-card, .step').forEach(el => {
            el.addEventListener('touchstart', function() {
                this.style.transform = 'scale(0.98)';
            });
            el.addEventListener('touchend', function() {
                this.style.transform = '';
            });
        });
    }
    
    // Handle window resize for responsive popup sizing
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            // Update any responsive elements if needed
        }, 150);
    });
});

// Main function to connect to Strava
function connectStrava() {
    // Add loading state to button
    const buttons = document.querySelectorAll('.cta-button');
    buttons.forEach(btn => {
        btn.style.pointerEvents = 'none';
        btn.style.opacity = '0.7';
    });
    
    showLoadingModal();
    
    // Open Strava auth in popup with mobile-friendly dimensions
    const authUrl = '/auth/login';
    const isMobile = window.innerWidth <= 768;
    const popupFeatures = isMobile ? 
        'width=' + Math.min(400, window.innerWidth) + ',height=' + Math.min(600, window.innerHeight) + ',scrollbars=yes' :
        'width=600,height=700,scrollbars=yes,resizable=yes';
    
    authWindow = window.open(authUrl, 'stravaAuth', popupFeatures);
    
    // Monitor the popup for completion
    authCheckInterval = setInterval(checkAuthComplete, 1000);
    
    // Handle popup blocked
    if (!authWindow) {
        hideLoadingModal();
        showError('Popup blocked! Please allow popups and try again.');
        return;
    }
    
    // Handle manual popup close
    authWindow.addEventListener('beforeunload', function() {
        setTimeout(() => {
            if (authWindow.closed) {
                clearInterval(authCheckInterval);
                hideLoadingModal();
            }
        }, 1000);
    });
}

// Check if auth is complete
function checkAuthComplete() {
    if (!authWindow || authWindow.closed) {
        clearInterval(authCheckInterval);
        hideLoadingModal();
        return;
    }
    
    try {
        // Try to access the popup's URL
        const popupUrl = authWindow.location.href;
        
        // Check if we're on the success page
        if (popupUrl.includes('/auth/success') || popupUrl.includes('access_token=')) {
            clearInterval(authCheckInterval);
            authWindow.close();
            handleAuthSuccess();
        }
    } catch (e) {
        // Cross-origin error is expected while on Strava's domain
        // Just continue checking
    }
}

// Handle popup message from auth success page
function handlePopupMessage(event) {
    if (event.data && event.data.type === 'strava_auth_success') {
        clearInterval(authCheckInterval);
        if (authWindow) {
            authWindow.close();
        }
        
        // Store token for later use
        localStorage.setItem('strava_token', event.data.access_token);
        localStorage.setItem('athlete_id', event.data.athlete_id);
        localStorage.setItem('expires_at', event.data.expires_at);
        
        handleAuthSuccess();
    }
}

// Handle successful authentication
function handleAuthSuccess() {
    hideLoadingModal();
    
    // Reset button states
    const buttons = document.querySelectorAll('.cta-button');
    buttons.forEach(btn => {
        btn.style.pointerEvents = 'auto';
        btn.style.opacity = '1';
    });
    
    // Show success message
    showSuccessPage();
}

// Check for auth callback on page load
function checkAuthCallback() {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('access_token');
    const error = urlParams.get('error');
    
    if (error) {
        showError('Authentication failed: ' + error);
        return;
    }
    
    if (token) {
        // We have a token, show success
        handleAuthSuccess();
    }
}

// Show success page
function showSuccessPage() {
    // Create success content
    const successHtml = `
        <div class="success-page">
            <div class="success-content">
                <div class="success-icon">✅</div>
                <h1>Successfully Connected!</h1>
                <p>Your Strava account is now connected to our workout description generator.</p>
                
                <div class="success-details">
                    <h3>What happens next?</h3>
                    <ul>
                        <li>We've set up automatic monitoring of your new activities</li>
                        <li>Every workout will be analysed within seconds of completion</li>
                        <li>Professional descriptions will be automatically added to your activities</li>
                        <li>You can close this page and forget about it!</li>
                    </ul>
                </div>
                
                <div class="success-actions">
                    <button class="cta-button secondary" onclick="goToStrava()">
                        View Your Strava Profile
                    </button>
                </div>
                
                <div class="webhook-status">
                    <div class="status-indicator active"></div>
                    <span>Automatic processing: Active</span>
                </div>
            </div>
        </div>
    `;
    
    // Replace page content
    document.body.innerHTML = successHtml;
    
    // No additional styles needed - CSS is already included
}


// Go to Strava
function goToStrava() {
    window.open('https://www.strava.com/dashboard', '_blank');
}

// Show loading modal
function showLoadingModal(message = 'Connecting to Strava...') {
    const modal = document.getElementById('loadingModal');
    const messageElement = modal.querySelector('h3');
    if (messageElement) {
        messageElement.textContent = message;
    }
    modal.classList.remove('hidden');
}

// Hide loading modal
function hideLoadingModal() {
    const modal = document.getElementById('loadingModal');
    modal.classList.add('hidden');
}

// Show error message
function showError(message) {
    // Reset button states
    const buttons = document.querySelectorAll('.cta-button');
    buttons.forEach(btn => {
        btn.style.pointerEvents = 'auto';
        btn.style.opacity = '1';
    });
    
    const errorModal = document.createElement('div');
    errorModal.className = 'modal';
    errorModal.innerHTML = `
        <div class="modal-content error-modal">
            <div class="error-icon">❌</div>
            <h3>Connection Failed</h3>
            <p>${message}</p>
            <button class="cta-button" onclick="this.parentElement.parentElement.remove(); location.reload();" aria-label="Close error and try again">
                Try Again
            </button>
        </div>
    `;
    document.body.appendChild(errorModal);
    
    // Auto-close after 10 seconds
    setTimeout(() => {
        if (errorModal.parentNode) {
            errorModal.remove();
        }
    }, 10000);
}

// Add smooth scrolling
function addSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Setup scroll animations with reduced motion support
function setupScrollAnimations() {
    // Check for reduced motion preference
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    
    if (prefersReducedMotion) {
        return; // Skip animations if user prefers reduced motion
    }
    
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    document.querySelectorAll('.step, .capability-card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
}

// Add success page styles
function addSuccessPageStyles() {
    const styles = `
        <style>
        .success-page {
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
            padding: 40px 20px;
        }
        
        .success-content {
            max-width: 600px;
            text-align: center;
            background: white;
            padding: 60px 40px;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        
        .success-icon {
            font-size: 4rem;
            margin-bottom: 20px;
        }
        
        .success-content h1 {
            font-size: 2.5rem;
            margin-bottom: 20px;
            color: var(--text-primary);
        }
        
        .success-content > p {
            font-size: 1.2rem;
            color: var(--text-secondary);
            margin-bottom: 40px;
        }
        
        .success-details {
            background: #f8f9fa;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 40px;
            text-align: left;
        }
        
        .success-details h3 {
            margin-bottom: 16px;
            color: var(--text-primary);
        }
        
        .success-details ul {
            list-style: none;
            padding: 0;
        }
        
        .success-details li {
            padding: 8px 0;
            padding-left: 24px;
            position: relative;
            color: var(--text-secondary);
        }
        
        .success-details li::before {
            content: '✓';
            position: absolute;
            left: 0;
            color: var(--primary-color);
            font-weight: bold;
        }
        
        .success-actions {
            display: flex;
            gap: 16px;
            justify-content: center;
            margin-bottom: 40px;
            flex-wrap: wrap;
        }
        
        .webhook-status {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            color: var(--text-secondary);
            font-size: 0.9rem;
        }
        
        .status-indicator {
            width: 8px;
            height: 8px;
            background: #22c55e;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .analysis-result {
            max-width: 500px;
        }
        
        .result-details {
            text-align: left;
            margin: 20px 0;
        }
        
        .description-result {
            background: #f8f9fa;
            padding: 16px;
            border-radius: 8px;
            margin-top: 16px;
        }
        
        .generated-desc {
            font-weight: 500;
            color: var(--primary-color);
            margin-top: 8px;
        }
        
        .error-modal {
            text-align: center;
        }
        
        .error-icon {
            font-size: 3rem;
            margin-bottom: 16px;
        }
        
        @media (max-width: 768px) {
            .success-content {
                padding: 40px 24px;
                margin: 20px;
            }
            
            .success-actions {
                flex-direction: column;
                align-items: center;
            }
            
            .success-actions .cta-button {
                width: 100%;
                max-width: 280px;
            }
        }
        </style>
    `;
    
    document.head.insertAdjacentHTML('beforeend', styles);
}