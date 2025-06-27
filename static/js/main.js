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
});

// Main function to connect to Strava
function connectStrava() {
    showLoadingModal();
    
    // Open Strava auth in popup
    const authUrl = '/auth/login';
    authWindow = window.open(
        authUrl, 
        'stravaAuth', 
        'width=600,height=700,scrollbars=yes,resizable=yes'
    );
    
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
                        <li>Every workout will be analyzed within seconds of completion</li>
                        <li>Professional descriptions will be automatically added to your activities</li>
                        <li>You can close this page and forget about it!</li>
                    </ul>
                </div>
                
                <div class="success-actions">
                    <button class="cta-button" onclick="testWithRecentActivity()">
                        Test with Recent Activity
                    </button>
                    <button class="cta-button secondary" onclick="goToStrava()">
                        View on Strava
                    </button>
                </div>
                
                <div class="webhook-status">
                    <div class="status-indicator"></div>
                    <span>Webhook monitoring: Active</span>
                </div>
            </div>
        </div>
    `;
    
    // Replace page content
    document.body.innerHTML = successHtml;
    
    // Add success page styles
    addSuccessPageStyles();
}

// Test with recent activity
function testWithRecentActivity() {
    showLoadingModal('Testing with your most recent activity...');
    
    // Get access token from URL or storage
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('access_token') || localStorage.getItem('strava_token');
    
    if (!token) {
        hideLoadingModal();
        showError('No access token found. Please reconnect.');
        return;
    }
    
    // Call API to test analysis
    fetch('/activities/recent?access_token=' + token + '&days=7')
        .then(response => response.json())
        .then(data => {
            if (data.activities && data.activities.length > 0) {
                const latestActivity = data.activities[0];
                return analyzeActivity(latestActivity.id, token);
            } else {
                throw new Error('No recent activities found');
            }
        })
        .then(result => {
            hideLoadingModal();
            showAnalysisResult(result);
        })
        .catch(error => {
            hideLoadingModal();
            showError('Test failed: ' + error.message);
        });
}

// Analyze activity
function analyzeActivity(activityId, token) {
    return fetch(`/activities/${activityId}/analyze?access_token=${token}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            activity_id: activityId,
            include_streams: true,
            analysis_type: 'auto',
            generate_description: true,
            update_activity: false
        })
    }).then(response => response.json());
}

// Show analysis result
function showAnalysisResult(result) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content analysis-result">
            <h3>Analysis Complete!</h3>
            <div class="result-details">
                <p><strong>Activity:</strong> ${result.analysis?.activity_name || 'Unknown'}</p>
                <p><strong>Analysis Method:</strong> ${result.analysis?.analysis_method || 'basic'}</p>
                <p><strong>Confidence:</strong> ${Math.round((result.analysis?.confidence || 0) * 100)}%</p>
                <div class="description-result">
                    <h4>Generated Description:</h4>
                    <p class="generated-desc">${result.analysis?.short_description || 'No pattern detected'}</p>
                </div>
            </div>
            <button class="cta-button" onclick="this.parentElement.parentElement.remove()">
                Close
            </button>
        </div>
    `;
    document.body.appendChild(modal);
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
    const errorModal = document.createElement('div');
    errorModal.className = 'modal';
    errorModal.innerHTML = `
        <div class="modal-content error-modal">
            <div class="error-icon">❌</div>
            <h3>Connection Failed</h3>
            <p>${message}</p>
            <button class="cta-button" onclick="this.parentElement.parentElement.remove()">
                Try Again
            </button>
        </div>
    `;
    document.body.appendChild(errorModal);
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

// Setup scroll animations
function setupScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    document.querySelectorAll('.feature-card, .step, .capability-card').forEach(el => {
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