/**
 * RoutineTest Mode Toggle Fix
 * Fixes the duplicate toggle issue and ensures only header toggle is visible
 * Created: August 18, 2025
 */

console.group('%c[MODE_TOGGLE_FIX] Initializing comprehensive fix', 'background: #FF5722; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;');

(function() {
    'use strict';
    
    // Configuration
    const FIX_CONFIG = {
        headerToggleId: 'modeToggleContainer',
        statsBoxSelectors: [
            '.class-stats',
            '.class-stat',
            '.stats-box',
            '.stat-box',
            '.stats-cards',
            '.stat-card',
            '.statistics-container',
            '.dashboard-stats'
        ],
        debugMode: true
    };
    
    /**
     * Main fix function - removes duplicate toggles from stats areas
     */
    function removeDuplicateToggles() {
        console.log('[MODE_TOGGLE_FIX] Scanning for duplicate toggles in stats areas...');
        
        let duplicatesFound = 0;
        let duplicatesRemoved = 0;
        
        // Check each stats box selector
        FIX_CONFIG.statsBoxSelectors.forEach(selector => {
            const statsElements = document.querySelectorAll(selector);
            
            statsElements.forEach(element => {
                // Look for any toggle-related elements within stats boxes
                const toggleElements = element.querySelectorAll([
                    '.mode-toggle-container',
                    '.mode-toggle-wrapper',
                    '.mode-toggle-btn',
                    '[id*="toggle"]',
                    '[class*="toggle"]',
                    'button:contains("Mode")'
                ].join(', '));
                
                // Also check for text content that might contain "function:"
                const textNodes = Array.from(element.childNodes).filter(node => 
                    node.nodeType === Node.TEXT_NODE || node.nodeType === Node.ELEMENT_NODE
                );
                
                textNodes.forEach(node => {
                    const text = node.textContent || node.innerText || '';
                    if (text.includes('function:') || text.includes('function :')) {
                        console.warn('[MODE_TOGGLE_FIX] Found "function:" text in stats box:', {
                            selector: selector,
                            text: text.substring(0, 100),
                            element: element
                        });
                        
                        // Try to fix the text
                        if (node.nodeType === Node.TEXT_NODE) {
                            node.textContent = text.replace(/function\s*:\s*/gi, '');
                        } else if (node.innerText) {
                            node.innerText = text.replace(/function\s*:\s*/gi, '');
                        }
                        duplicatesFound++;
                    }
                });
                
                // Remove any toggle elements found in stats boxes
                toggleElements.forEach(toggle => {
                    console.warn('[MODE_TOGGLE_FIX] Found toggle element in stats box, removing:', {
                        selector: selector,
                        toggleClass: toggle.className,
                        toggleId: toggle.id,
                        toggleText: toggle.textContent?.substring(0, 50)
                    });
                    
                    // Log before removal for debugging
                    if (FIX_CONFIG.debugMode) {
                        console.log('[DEBUG] Toggle element details:', {
                            outerHTML: toggle.outerHTML?.substring(0, 200),
                            parentElement: toggle.parentElement?.className,
                            innerHTML: toggle.innerHTML?.substring(0, 100)
                        });
                    }
                    
                    toggle.remove();
                    duplicatesRemoved++;
                });
            });
        });
        
        // Also search for any elements containing "function: Teacher Mode" or "function: Admin Mode"
        const allElements = document.querySelectorAll('*');
        allElements.forEach(element => {
            if (element.textContent && 
                (element.textContent.includes('function: Teacher Mode') || 
                 element.textContent.includes('function: Admin Mode') ||
                 element.textContent.includes('function : Teacher Mode') ||
                 element.textContent.includes('function : Admin Mode'))) {
                
                // Skip if it's the main header toggle
                if (element.closest('#' + FIX_CONFIG.headerToggleId)) {
                    return;
                }
                
                console.warn('[MODE_TOGGLE_FIX] Found element with "function:" text:', {
                    tagName: element.tagName,
                    className: element.className,
                    id: element.id,
                    text: element.textContent.substring(0, 100),
                    parent: element.parentElement?.className
                });
                
                // Fix the text content
                if (element.childNodes.length === 1 && element.firstChild.nodeType === Node.TEXT_NODE) {
                    element.firstChild.textContent = element.firstChild.textContent.replace(/function\s*:\s*/gi, '');
                    duplicatesFound++;
                    console.log('[MODE_TOGGLE_FIX] Fixed text content');
                }
            }
        });
        
        console.log(`[MODE_TOGGLE_FIX] Scan complete. Found: ${duplicatesFound}, Removed: ${duplicatesRemoved}`);
        return { found: duplicatesFound, removed: duplicatesRemoved };
    }
    
    /**
     * Verify header toggle is working correctly
     */
    function verifyHeaderToggle() {
        console.log('[MODE_TOGGLE_FIX] Verifying header toggle...');
        
        const headerToggle = document.getElementById(FIX_CONFIG.headerToggleId);
        
        if (headerToggle) {
            console.log('✅ Header toggle found and verified');
            
            // Ensure it's properly positioned
            const styles = window.getComputedStyle(headerToggle);
            console.log('[MODE_TOGGLE_FIX] Header toggle positioning:', {
                position: styles.position,
                top: styles.top,
                right: styles.right,
                display: styles.display,
                visibility: styles.visibility
            });
            
            // Check button text doesn't have "function:"
            const toggleBtn = headerToggle.querySelector('.mode-toggle-btn');
            if (toggleBtn) {
                const btnText = toggleBtn.textContent || toggleBtn.innerText || '';
                if (btnText.includes('function:')) {
                    console.warn('[MODE_TOGGLE_FIX] Header toggle has "function:" prefix, fixing...');
                    toggleBtn.textContent = btnText.replace(/function\s*:\s*/gi, '');
                }
            }
            
            return true;
        } else {
            console.error('❌ Header toggle not found!');
            return false;
        }
    }
    
    /**
     * Add monitoring to detect any dynamically added toggles
     */
    function addToggleMonitoring() {
        console.log('[MODE_TOGGLE_FIX] Setting up dynamic toggle monitoring...');
        
        // Create MutationObserver to watch for DOM changes
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        // Check if added node is or contains a toggle
                        const isToggle = node.classList && (
                            node.classList.contains('mode-toggle-container') ||
                            node.classList.contains('mode-toggle-wrapper') ||
                            node.classList.contains('mode-toggle-btn')
                        );
                        
                        const containsToggle = node.querySelector && node.querySelector('.mode-toggle-container, .mode-toggle-wrapper, .mode-toggle-btn');
                        
                        if (isToggle || containsToggle) {
                            // Check if it's not the header toggle
                            const isHeaderToggle = node.id === FIX_CONFIG.headerToggleId || 
                                                 node.closest('#' + FIX_CONFIG.headerToggleId);
                            
                            if (!isHeaderToggle) {
                                console.warn('[MODE_TOGGLE_FIX] Dynamically added toggle detected, removing:', {
                                    element: node,
                                    parent: node.parentElement
                                });
                                
                                // Check if it's in a stats area
                                const inStatsArea = FIX_CONFIG.statsBoxSelectors.some(selector => 
                                    node.closest(selector)
                                );
                                
                                if (inStatsArea) {
                                    console.log('[MODE_TOGGLE_FIX] Toggle is in stats area, removing...');
                                    node.remove();
                                }
                            }
                        }
                        
                        // Check for "function:" text
                        const text = node.textContent || node.innerText || '';
                        if (text.includes('function:')) {
                            console.warn('[MODE_TOGGLE_FIX] Element with "function:" added to DOM:', node);
                        }
                    }
                });
            });
        });
        
        // Start observing
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        console.log('[MODE_TOGGLE_FIX] Monitoring active');
        
        return observer;
    }
    
    /**
     * Main initialization
     */
    function initialize() {
        console.log('[MODE_TOGGLE_FIX] Starting comprehensive mode toggle fix...');
        console.log('[MODE_TOGGLE_FIX] Timestamp:', new Date().toISOString());
        
        // Step 1: Remove duplicate toggles
        const removalResult = removeDuplicateToggles();
        
        // Step 2: Verify header toggle
        const headerValid = verifyHeaderToggle();
        
        // Step 3: Set up monitoring
        const observer = addToggleMonitoring();
        
        // Step 4: Log final status
        console.group('[MODE_TOGGLE_FIX] Fix Status');
        console.log('Duplicates found:', removalResult.found);
        console.log('Duplicates removed:', removalResult.removed);
        console.log('Header toggle valid:', headerValid);
        console.log('Monitoring active:', !!observer);
        console.groupEnd();
        
        // Store fix status globally for debugging
        window.MODE_TOGGLE_FIX_STATUS = {
            timestamp: new Date().toISOString(),
            duplicatesFound: removalResult.found,
            duplicatesRemoved: removalResult.removed,
            headerToggleValid: headerValid,
            monitoringActive: !!observer
        };
        
        console.log('[MODE_TOGGLE_FIX] Fix complete. Status available at window.MODE_TOGGLE_FIX_STATUS');
        
        // Run periodic checks
        setInterval(() => {
            const quickCheck = removeDuplicateToggles();
            if (quickCheck.found > 0) {
                console.warn('[MODE_TOGGLE_FIX] Periodic check found new duplicates:', quickCheck);
            }
        }, 5000); // Check every 5 seconds
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initialize);
    } else {
        // DOM already loaded
        initialize();
    }
    
    // Also run on window load to catch any late additions
    window.addEventListener('load', () => {
        console.log('[MODE_TOGGLE_FIX] Running window.load check...');
        removeDuplicateToggles();
    });
    
})();

console.groupEnd();

// Export fix function globally for manual testing
window.fixModeToggle = function() {
    console.log('[MODE_TOGGLE_FIX] Manual fix triggered');
    const result = removeDuplicateToggles();
    console.log('[MODE_TOGGLE_FIX] Manual fix result:', result);
    return result;
};