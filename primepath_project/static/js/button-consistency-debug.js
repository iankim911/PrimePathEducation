/**
 * Button Consistency Debug Module
 * ====================================
 * Purpose: Monitor and debug button styling consistency across admin views
 * Issue: FULL ACCESS and DELETE buttons have different shapes/sizes
 * Solution: Real-time monitoring and enforcement of button consistency
 * Date: August 26, 2025
 */

(function() {
    'use strict';
    
    // Configuration
    const CONFIG = {
        DEBUG_MODE: true,
        LOG_PREFIX: '[BUTTON_DEBUG]',
        CHECK_INTERVAL: 2000,  // Check every 2 seconds
        EXPECTED_STYLES: {
            minWidth: 120,      // Expected minimum width in px
            minHeight: 40,      // Expected minimum height in px
            padding: '10px 20px',
            borderRadius: 8,    // Expected border radius in px
            fontSize: 14,       // Expected font size in px
            fontWeight: 600     // Expected font weight
        }
    };
    
    // Button monitoring system
    const ButtonMonitor = {
        checkedButtons: new WeakSet(),
        inconsistentButtons: [],
        
        /**
         * Initialize the button monitoring system
         */
        init: function() {
            console.log(`${CONFIG.LOG_PREFIX} Initializing button consistency monitor...`);
            
            // Initial check
            this.checkAllButtons();
            
            // Set up periodic checking
            if (CONFIG.DEBUG_MODE) {
                setInterval(() => this.checkAllButtons(), CONFIG.CHECK_INTERVAL);
            }
            
            // Monitor dynamic content
            this.setupMutationObserver();
            
            // Add event listeners for button interactions
            this.setupEventListeners();
            
            console.log(`${CONFIG.LOG_PREFIX} Button monitor initialized successfully`);
        },
        
        /**
         * Check all buttons on the page for consistency
         */
        checkAllButtons: function() {
            const buttons = document.querySelectorAll('button, .btn, [class*="btn-"]');
            let inconsistentCount = 0;
            
            buttons.forEach((button) => {
                // Skip if already checked (for performance)
                if (this.checkedButtons.has(button)) {
                    return;
                }
                
                const issues = this.checkButtonConsistency(button);
                if (issues.length > 0) {
                    inconsistentCount++;
                    this.handleInconsistentButton(button, issues);
                }
                
                this.checkedButtons.add(button);
            });
            
            if (inconsistentCount > 0) {
                console.warn(`${CONFIG.LOG_PREFIX} Found ${inconsistentCount} inconsistent buttons`);
            }
        },
        
        /**
         * Check a single button for consistency issues
         */
        checkButtonConsistency: function(button) {
            const issues = [];
            const computedStyle = window.getComputedStyle(button);
            const rect = button.getBoundingClientRect();
            
            // Check dimensions
            if (rect.width < CONFIG.EXPECTED_STYLES.minWidth) {
                issues.push(`Width (${rect.width}px) < expected (${CONFIG.EXPECTED_STYLES.minWidth}px)`);
            }
            
            if (rect.height < CONFIG.EXPECTED_STYLES.minHeight) {
                issues.push(`Height (${rect.height}px) < expected (${CONFIG.EXPECTED_STYLES.minHeight}px)`);
            }
            
            // Check font size
            const fontSize = parseFloat(computedStyle.fontSize);
            if (Math.abs(fontSize - CONFIG.EXPECTED_STYLES.fontSize) > 1) {
                issues.push(`Font size (${fontSize}px) != expected (${CONFIG.EXPECTED_STYLES.fontSize}px)`);
            }
            
            // Check border radius
            const borderRadius = parseFloat(computedStyle.borderRadius);
            if (Math.abs(borderRadius - CONFIG.EXPECTED_STYLES.borderRadius) > 2) {
                issues.push(`Border radius (${borderRadius}px) != expected (${CONFIG.EXPECTED_STYLES.borderRadius}px)`);
            }
            
            return issues;
        },
        
        /**
         * Handle a button with inconsistent styling
         */
        handleInconsistentButton: function(button, issues) {
            // Add debugging attributes
            button.setAttribute('data-button-debug', issues.join('; '));
            button.setAttribute('data-consistency-issues', issues.length);
            
            // Log the issue
            console.group(`${CONFIG.LOG_PREFIX} Inconsistent button found`);
            console.log('Button:', button);
            console.log('Text:', button.textContent.trim());
            console.log('Classes:', button.className);
            console.log('Issues:', issues);
            
            // Check if it's specifically a FULL ACCESS or DELETE button
            const buttonText = button.textContent.trim().toUpperCase();
            if (buttonText.includes('FULL ACCESS') || buttonText.includes('DELETE')) {
                console.warn(`${CONFIG.LOG_PREFIX} Critical button type: ${buttonText}`);
                
                // Apply automatic fix if enabled
                if (CONFIG.DEBUG_MODE) {
                    this.applyButtonFix(button);
                }
            }
            
            console.groupEnd();
            
            // Store for reporting
            this.inconsistentButtons.push({
                element: button,
                text: button.textContent.trim(),
                issues: issues,
                timestamp: new Date().toISOString()
            });
        },
        
        /**
         * Apply automatic fix to inconsistent button
         */
        applyButtonFix: function(button) {
            console.log(`${CONFIG.LOG_PREFIX} Applying automatic fix to button...`);
            
            // Force consistent styling via important flags
            const fixStyles = {
                'min-width': `${CONFIG.EXPECTED_STYLES.minWidth}px !important`,
                'min-height': `${CONFIG.EXPECTED_STYLES.minHeight}px !important`,
                'padding': `${CONFIG.EXPECTED_STYLES.padding} !important`,
                'border-radius': `${CONFIG.EXPECTED_STYLES.borderRadius}px !important`,
                'font-size': `${CONFIG.EXPECTED_STYLES.fontSize}px !important`,
                'font-weight': `${CONFIG.EXPECTED_STYLES.fontWeight} !important`,
                'display': 'inline-flex !important',
                'align-items': 'center !important',
                'justify-content': 'center !important'
            };
            
            // Apply each style
            for (const [property, value] of Object.entries(fixStyles)) {
                button.style.setProperty(property, value.replace(' !important', ''), 'important');
            }
            
            // Add fixed marker
            button.setAttribute('data-button-fixed', 'true');
            button.setAttribute('data-fix-timestamp', new Date().toISOString());
            
            console.log(`${CONFIG.LOG_PREFIX} Button fix applied successfully`);
        },
        
        /**
         * Setup mutation observer to catch dynamically added buttons
         */
        setupMutationObserver: function() {
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.type === 'childList') {
                        mutation.addedNodes.forEach((node) => {
                            if (node.nodeType === Node.ELEMENT_NODE) {
                                // Check if the added node is a button
                                if (node.matches && (node.matches('button, .btn, [class*="btn-"]'))) {
                                    this.checkButtonConsistency(node);
                                }
                                
                                // Check for buttons within added node
                                if (node.querySelectorAll) {
                                    const buttons = node.querySelectorAll('button, .btn, [class*="btn-"]');
                                    buttons.forEach(button => this.checkButtonConsistency(button));
                                }
                            }
                        });
                    }
                });
            });
            
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
            
            console.log(`${CONFIG.LOG_PREFIX} Mutation observer setup complete`);
        },
        
        /**
         * Setup event listeners for button interactions
         */
        setupEventListeners: function() {
            // Track button clicks
            document.addEventListener('click', (e) => {
                if (e.target.matches('button, .btn, [class*="btn-"]')) {
                    const buttonText = e.target.textContent.trim();
                    const buttonClasses = e.target.className;
                    
                    console.log(`${CONFIG.LOG_PREFIX} Button clicked:`, {
                        text: buttonText,
                        classes: buttonClasses,
                        dimensions: {
                            width: e.target.offsetWidth,
                            height: e.target.offsetHeight
                        }
                    });
                }
            });
            
            // Track hover events for debugging
            if (CONFIG.DEBUG_MODE) {
                document.addEventListener('mouseover', (e) => {
                    if (e.target.matches('button, .btn, [class*="btn-"]')) {
                        const rect = e.target.getBoundingClientRect();
                        e.target.title = `Width: ${rect.width}px | Height: ${rect.height}px`;
                    }
                });
            }
        },
        
        /**
         * Generate report of all button inconsistencies
         */
        generateReport: function() {
            console.group(`${CONFIG.LOG_PREFIX} Button Consistency Report`);
            console.log('Total buttons checked:', this.checkedButtons.size);
            console.log('Inconsistent buttons found:', this.inconsistentButtons.length);
            
            if (this.inconsistentButtons.length > 0) {
                console.table(this.inconsistentButtons.map(item => ({
                    text: item.text,
                    issues: item.issues.join(', '),
                    timestamp: item.timestamp
                })));
            }
            
            console.groupEnd();
        },
        
        /**
         * Force fix all buttons on the page
         */
        forceFixAllButtons: function() {
            console.log(`${CONFIG.LOG_PREFIX} Force fixing all buttons...`);
            const buttons = document.querySelectorAll('button, .btn, [class*="btn-"]');
            let fixedCount = 0;
            
            buttons.forEach((button) => {
                const issues = this.checkButtonConsistency(button);
                if (issues.length > 0) {
                    this.applyButtonFix(button);
                    fixedCount++;
                }
            });
            
            console.log(`${CONFIG.LOG_PREFIX} Fixed ${fixedCount} buttons`);
        }
    };
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => ButtonMonitor.init());
    } else {
        ButtonMonitor.init();
    }
    
    // Expose to global scope for debugging
    window.ButtonMonitor = ButtonMonitor;
    
    // Add console commands for debugging
    window.buttonDebug = {
        report: () => ButtonMonitor.generateReport(),
        fixAll: () => ButtonMonitor.forceFixAllButtons(),
        check: () => ButtonMonitor.checkAllButtons(),
        toggleDebug: () => {
            CONFIG.DEBUG_MODE = !CONFIG.DEBUG_MODE;
            console.log(`${CONFIG.LOG_PREFIX} Debug mode:`, CONFIG.DEBUG_MODE);
        }
    };
    
    // Log available commands
    console.log(`${CONFIG.LOG_PREFIX} Debug commands available:`);
    console.log('  buttonDebug.report()  - Generate consistency report');
    console.log('  buttonDebug.fixAll()  - Force fix all buttons');
    console.log('  buttonDebug.check()   - Check all buttons now');
    console.log('  buttonDebug.toggleDebug() - Toggle debug mode');
    
})();

// Log that the script has loaded
console.log('%c[BUTTON_DEBUG] Button consistency debug module loaded', 'background: #4CAF50; color: white; padding: 5px; font-weight: bold');