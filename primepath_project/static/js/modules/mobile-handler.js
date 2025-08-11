/**
 * Mobile Event Handler Module
 * Adds touch support without breaking desktop functionality
 * All events are added alongside existing click events, not replacing them
 */

(function() {
    'use strict';
    
    const MobileHandler = {
        // Configuration
        config: {
            isMobile: false,
            isTablet: false,
            hasTouch: false,
            viewportWidth: window.innerWidth,
            viewportHeight: window.innerHeight,
            debugMode: true  // Enable console logging
        },
        
        // Initialize mobile detection and handlers
        init: function() {
            this.detectDevice();
            this.setupEventListeners();
            this.enhanceTouchTargets();
            this.setupOrientationHandler();
            this.logDebug('initialization', 'MobileHandler initialized', this.config);
            
            // Re-check on resize
            window.addEventListener('resize', this.debounce(() => {
                this.config.viewportWidth = window.innerWidth;
                this.config.viewportHeight = window.innerHeight;
                this.detectDevice();
            }, 250));
        },
        
        // Detect device type
        detectDevice: function() {
            const width = window.innerWidth;
            
            // Check for touch capability
            this.config.hasTouch = ('ontouchstart' in window) || 
                                   (navigator.maxTouchPoints > 0) || 
                                   (navigator.msMaxTouchPoints > 0);
            
            // Determine device type based on viewport
            this.config.isMobile = width <= 767;
            this.config.isTablet = width > 767 && width <= 1024;
            
            // Add body classes for CSS targeting
            document.body.classList.toggle('touch-device', this.config.hasTouch);
            document.body.classList.toggle('mobile-device', this.config.isMobile);
            document.body.classList.toggle('tablet-device', this.config.isTablet);
            
            this.logDebug('device_detection', 'Device detected', {
                isMobile: this.config.isMobile,
                isTablet: this.config.isTablet,
                hasTouch: this.config.hasTouch,
                viewport: `${width}x${this.config.viewportHeight}`
            });
        },
        
        // Setup touch event listeners alongside click events
        setupEventListeners: function() {
            if (!this.config.hasTouch) {
                this.logDebug('touch_events', 'Touch events not needed - no touch capability detected');
                return;
            }
            
            // Add touch events to all clickable elements
            const clickableSelectors = [
                'button',
                '.btn',
                'a[href]',
                '.question-nav-btn',
                '.answer-option',
                '.mcq-option',
                'input[type="submit"]',
                'input[type="button"]'
            ];
            
            clickableSelectors.forEach(selector => {
                const elements = document.querySelectorAll(selector);
                elements.forEach(element => {
                    this.addTouchSupport(element);
                });
            });
            
            this.logDebug('touch_events', `Added touch support to ${clickableSelectors.length} element types`);
        },
        
        // Add touch support to an element
        addTouchSupport: function(element) {
            if (!element || element.dataset.touchEnabled === 'true') {
                return; // Already processed
            }
            
            // Mark as processed
            element.dataset.touchEnabled = 'true';
            
            // Track touch state
            let touchStartTime = 0;
            let touchStartX = 0;
            let touchStartY = 0;
            
            // Touch start handler
            element.addEventListener('touchstart', (e) => {
                touchStartTime = Date.now();
                touchStartX = e.touches[0].clientX;
                touchStartY = e.touches[0].clientY;
                
                // Add visual feedback
                element.classList.add('touch-active');
                
                this.logDebug('touch_start', 'Touch started', {
                    element: element.tagName,
                    id: element.id || 'no-id',
                    class: element.className
                });
            }, { passive: true });
            
            // Touch end handler
            element.addEventListener('touchend', (e) => {
                const touchDuration = Date.now() - touchStartTime;
                const touchEndX = e.changedTouches[0].clientX;
                const touchEndY = e.changedTouches[0].clientY;
                
                // Calculate movement
                const deltaX = Math.abs(touchEndX - touchStartX);
                const deltaY = Math.abs(touchEndY - touchStartY);
                
                // Remove visual feedback
                element.classList.remove('touch-active');
                
                // If it's a tap (not a swipe), trigger click
                if (touchDuration < 500 && deltaX < 10 && deltaY < 10) {
                    // Check if element has existing click handler
                    if (!element.onclick && !element.hasAttribute('onclick')) {
                        // For links without onclick, let default behavior handle it
                        if (element.tagName !== 'A') {
                            // Trigger synthetic click for non-links
                            setTimeout(() => {
                                element.click();
                            }, 0);
                        }
                    }
                    
                    this.logDebug('touch_tap', 'Tap detected', {
                        element: element.tagName,
                        duration: touchDuration,
                        movement: `${deltaX},${deltaY}`
                    });
                }
            }, { passive: true });
            
            // Prevent ghost clicks on touch devices
            element.addEventListener('touchend', (e) => {
                if (this.config.hasTouch) {
                    e.preventDefault();
                }
            }, { passive: false });
        },
        
        // Enhance touch targets for better usability
        enhanceTouchTargets: function() {
            if (!this.config.isMobile && !this.config.isTablet) {
                return;
            }
            
            // Find small touch targets and enhance them
            const minSize = 44; // Apple's recommended minimum
            const targets = document.querySelectorAll('button, a, input[type="checkbox"], input[type="radio"]');
            
            let enhanced = 0;
            targets.forEach(target => {
                const rect = target.getBoundingClientRect();
                if (rect.width < minSize || rect.height < minSize) {
                    target.style.minWidth = `${minSize}px`;
                    target.style.minHeight = `${minSize}px`;
                    target.classList.add('touch-enhanced');
                    enhanced++;
                }
            });
            
            if (enhanced > 0) {
                this.logDebug('touch_targets', `Enhanced ${enhanced} small touch targets`);
            }
        },
        
        // Handle orientation changes
        setupOrientationHandler: function() {
            if (!this.config.isMobile && !this.config.isTablet) {
                return;
            }
            
            window.addEventListener('orientationchange', () => {
                const orientation = window.orientation || screen.orientation.angle;
                const isLandscape = Math.abs(orientation) === 90;
                
                document.body.classList.toggle('landscape-orientation', isLandscape);
                document.body.classList.toggle('portrait-orientation', !isLandscape);
                
                this.logDebug('orientation', 'Orientation changed', {
                    angle: orientation,
                    isLandscape: isLandscape
                });
                
                // Recalculate after orientation change
                setTimeout(() => {
                    this.detectDevice();
                    this.enhanceTouchTargets();
                }, 100);
            });
        },
        
        // Handle swipe gestures for navigation
        setupSwipeGestures: function(element, callbacks) {
            if (!this.config.hasTouch) {
                return;
            }
            
            let touchStartX = 0;
            let touchStartY = 0;
            let touchStartTime = 0;
            
            element.addEventListener('touchstart', (e) => {
                touchStartX = e.touches[0].clientX;
                touchStartY = e.touches[0].clientY;
                touchStartTime = Date.now();
            }, { passive: true });
            
            element.addEventListener('touchend', (e) => {
                const touchEndX = e.changedTouches[0].clientX;
                const touchEndY = e.changedTouches[0].clientY;
                const touchDuration = Date.now() - touchStartTime;
                
                // Calculate swipe distance and direction
                const deltaX = touchEndX - touchStartX;
                const deltaY = touchEndY - touchStartY;
                const absDeltaX = Math.abs(deltaX);
                const absDeltaY = Math.abs(deltaY);
                
                // Minimum swipe distance (in pixels)
                const minSwipeDistance = 50;
                
                // Maximum time for swipe (in ms)
                const maxSwipeTime = 300;
                
                if (touchDuration < maxSwipeTime) {
                    if (absDeltaX > minSwipeDistance && absDeltaX > absDeltaY) {
                        // Horizontal swipe
                        if (deltaX > 0) {
                            if (callbacks.onSwipeRight) {
                                callbacks.onSwipeRight();
                                this.logDebug('swipe', 'Swipe right detected');
                            }
                        } else {
                            if (callbacks.onSwipeLeft) {
                                callbacks.onSwipeLeft();
                                this.logDebug('swipe', 'Swipe left detected');
                            }
                        }
                    } else if (absDeltaY > minSwipeDistance) {
                        // Vertical swipe
                        if (deltaY > 0) {
                            if (callbacks.onSwipeDown) {
                                callbacks.onSwipeDown();
                                this.logDebug('swipe', 'Swipe down detected');
                            }
                        } else {
                            if (callbacks.onSwipeUp) {
                                callbacks.onSwipeUp();
                                this.logDebug('swipe', 'Swipe up detected');
                            }
                        }
                    }
                }
            }, { passive: true });
        },
        
        // Utility: Debounce function
        debounce: function(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },
        
        // Debug logging
        logDebug: function(action, message, data = null) {
            if (!this.config.debugMode) {
                return;
            }
            
            const logEntry = {
                module: 'MobileHandler',
                action: action,
                message: message,
                timestamp: new Date().toISOString()
            };
            
            if (data) {
                logEntry.data = data;
            }
            
            console.log(`[MOBILE_HANDLER] ${JSON.stringify(logEntry)}`);
        }
    };
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => MobileHandler.init());
    } else {
        MobileHandler.init();
    }
    
    // Export for use in other modules
    window.MobileHandler = MobileHandler;
})();