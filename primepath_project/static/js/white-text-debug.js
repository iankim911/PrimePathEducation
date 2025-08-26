/**
 * White Text Debug Module
 * =======================
 * Purpose: Monitor and debug white text on dark backgrounds
 * Issue: Text appears dark/black on green backgrounds in screenshots
 * Solution: Real-time monitoring and fixing of text color issues
 * Date: August 26, 2025
 */

(function() {
    'use strict';
    
    // Configuration
    const CONFIG = {
        DEBUG_MODE: true,
        LOG_PREFIX: '[WHITE_TEXT_DEBUG]',
        CHECK_INTERVAL: 1000,  // Check every second
        DARK_BACKGROUNDS: [
            '#1B5E20',    // Primary dark green
            '#2E7D32',    // Secondary green  
            'rgb(27, 94, 32)',
            'rgb(46, 125, 50)'
        ]
    };
    
    // White Text Monitor System
    const WhiteTextMonitor = {
        checkedElements: new WeakSet(),
        problematicElements: [],
        
        /**
         * Initialize the white text monitoring system
         */
        init: function() {
            console.log(`${CONFIG.LOG_PREFIX} Initializing white text monitor...`);
            
            // Initial check
            this.checkAllElements();
            
            // Set up periodic checking
            if (CONFIG.DEBUG_MODE) {
                setInterval(() => this.checkAllElements(), CONFIG.CHECK_INTERVAL);
            }
            
            // Monitor dynamic content
            this.setupMutationObserver();
            
            console.log(`${CONFIG.LOG_PREFIX} White text monitor initialized successfully`);
        },
        
        /**
         * Check all elements for white text issues
         */
        checkAllElements: function() {
            // Check program headers
            const programHeaders = document.querySelectorAll('.program-header, .program-header *');
            programHeaders.forEach(element => this.checkElementTextColor(element, 'Program Header'));
            
            // Check navigation elements
            const navElements = document.querySelectorAll('.nav-tabs, .nav-tabs *, .app-header, .app-header *');
            navElements.forEach(element => this.checkElementTextColor(element, 'Navigation'));
            
            // Check buttons on dark backgrounds
            const darkButtons = document.querySelectorAll('button[style*="background: #2E7D32"], button[style*="background: #1B5E20"], .btn-success, .btn-primary');
            darkButtons.forEach(element => this.checkElementTextColor(element, 'Button'));
            
            // Check modal headers
            const modalHeaders = document.querySelectorAll('.modal-header[style*="background: #2E7D32"], .modal-header[style*="background: #1B5E20"]');
            modalHeaders.forEach(element => this.checkElementTextColor(element, 'Modal Header'));
            
            // Check table headers
            const tableHeaders = document.querySelectorAll('thead[style*="background: #1B5E20"], .admin-table thead');
            tableHeaders.forEach(element => this.checkElementTextColor(element, 'Table Header'));
        },
        
        /**
         * Check if an element has proper text color contrast
         */
        checkElementTextColor: function(element, elementType) {
            if (this.checkedElements.has(element)) {
                return;
            }
            
            const computedStyle = window.getComputedStyle(element);
            const textColor = computedStyle.color;
            const backgroundColor = computedStyle.backgroundColor;
            
            // Check if element has dark background but non-white text
            if (this.hasDarkBackground(element) && !this.hasWhiteText(textColor)) {
                this.handleProblematicElement(element, elementType, textColor, backgroundColor);
            }
            
            this.checkedElements.add(element);
        },
        
        /**
         * Check if element has a dark background
         */
        hasDarkBackground: function(element) {
            const computedStyle = window.getComputedStyle(element);
            const backgroundColor = computedStyle.backgroundColor;
            const backgroundImage = computedStyle.backgroundImage;
            
            // Check for known dark background colors
            for (const darkColor of CONFIG.DARK_BACKGROUNDS) {
                if (backgroundColor.includes(darkColor) || 
                    backgroundImage.includes(darkColor)) {
                    return true;
                }
            }
            
            // Check if background image contains gradient with dark green
            if (backgroundImage.includes('linear-gradient') && 
                (backgroundImage.includes('#1B5E20') || backgroundImage.includes('#2E7D32'))) {
                return true;
            }
            
            return false;
        },
        
        /**
         * Check if text color is white or near-white
         */
        hasWhiteText: function(color) {
            // Convert color to RGB values
            const rgb = this.colorToRgb(color);
            if (!rgb) return false;
            
            // Check if all RGB values are high (indicating white/light color)
            const threshold = 200; // Threshold for "white enough"
            return rgb.r >= threshold && rgb.g >= threshold && rgb.b >= threshold;
        },
        
        /**
         * Convert color string to RGB object
         */
        colorToRgb: function(color) {
            if (color.startsWith('rgb')) {
                const matches = color.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
                if (matches) {
                    return {
                        r: parseInt(matches[1]),
                        g: parseInt(matches[2]),
                        b: parseInt(matches[3])
                    };
                }
            } else if (color.startsWith('rgba')) {
                const matches = color.match(/rgba\((\d+),\s*(\d+),\s*(\d+),\s*[\d.]+\)/);
                if (matches) {
                    return {
                        r: parseInt(matches[1]),
                        g: parseInt(matches[2]),
                        b: parseInt(matches[3])
                    };
                }
            }
            return null;
        },
        
        /**
         * Handle element with problematic text color
         */
        handleProblematicElement: function(element, elementType, textColor, backgroundColor) {
            console.group(`${CONFIG.LOG_PREFIX} Problematic text color found`);
            console.log('Element:', element);
            console.log('Type:', elementType);
            console.log('Text:', element.textContent?.trim());
            console.log('Text Color:', textColor);
            console.log('Background Color:', backgroundColor);
            
            // Apply automatic fix
            this.applyWhiteTextFix(element);
            
            console.groupEnd();
            
            // Store for reporting
            this.problematicElements.push({
                element: element,
                type: elementType,
                textColor: textColor,
                backgroundColor: backgroundColor,
                text: element.textContent?.trim(),
                timestamp: new Date().toISOString()
            });
        },
        
        /**
         * Apply white text fix to an element
         */
        applyWhiteTextFix: function(element) {
            console.log(`${CONFIG.LOG_PREFIX} Applying white text fix...`);
            
            // Force white text with maximum specificity
            element.style.setProperty('color', 'white', 'important');
            element.style.setProperty('color', '#FFFFFF', 'important');
            
            // Also fix all child elements
            const children = element.querySelectorAll('*');
            children.forEach(child => {
                child.style.setProperty('color', 'white', 'important');
                child.style.setProperty('color', '#FFFFFF', 'important');
            });
            
            // Add debug markers
            element.setAttribute('data-white-text-fixed', 'true');
            element.setAttribute('data-fix-timestamp', new Date().toISOString());
            
            console.log(`${CONFIG.LOG_PREFIX} White text fix applied successfully`);
        },
        
        /**
         * Setup mutation observer to catch dynamically added content
         */
        setupMutationObserver: function() {
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.type === 'childList') {
                        mutation.addedNodes.forEach((node) => {
                            if (node.nodeType === Node.ELEMENT_NODE) {
                                // Check the added node
                                this.checkElementTextColor(node, 'Dynamic Content');
                                
                                // Check children of added node
                                if (node.querySelectorAll) {
                                    const darkElements = node.querySelectorAll('.program-header, .nav-tabs, .app-header, .modal-header, button, .btn');
                                    darkElements.forEach(element => this.checkElementTextColor(element, 'Dynamic Child'));
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
         * Generate report of all text color issues
         */
        generateReport: function() {
            console.group(`${CONFIG.LOG_PREFIX} White Text Report`);
            console.log('Elements checked:', this.checkedElements.size || 'Unknown');
            console.log('Problematic elements found:', this.problematicElements.length);
            
            if (this.problematicElements.length > 0) {
                console.table(this.problematicElements.map(item => ({
                    type: item.type,
                    text: item.text?.substring(0, 50) + (item.text?.length > 50 ? '...' : ''),
                    textColor: item.textColor,
                    backgroundColor: item.backgroundColor,
                    timestamp: item.timestamp
                })));
            }
            
            console.groupEnd();
        },
        
        /**
         * Force fix all elements on page
         */
        forceFixAllElements: function() {
            console.log(`${CONFIG.LOG_PREFIX} Force fixing all elements...`);
            
            const selectors = [
                '.program-header, .program-header *',
                '.nav-tabs, .nav-tabs *',
                '.app-header, .app-header *',
                '.modal-header[style*="background: #2E7D32"], .modal-header[style*="background: #2E7D32"] *',
                '.modal-header[style*="background: #1B5E20"], .modal-header[style*="background: #1B5E20"] *',
                'button[style*="background: #2E7D32"], button[style*="background: #2E7D32"] *',
                'button[style*="background: #1B5E20"], button[style*="background: #1B5E20"] *',
                '.btn-success, .btn-success *',
                '.btn-primary, .btn-primary *',
                'thead[style*="background: #1B5E20"], thead[style*="background: #1B5E20"] *'
            ];
            
            let fixedCount = 0;
            
            selectors.forEach(selector => {
                const elements = document.querySelectorAll(selector);
                elements.forEach(element => {
                    if (this.hasDarkBackground(element) || 
                        element.closest('.program-header, .nav-tabs, .app-header, .modal-header, .btn-success, .btn-primary')) {
                        this.applyWhiteTextFix(element);
                        fixedCount++;
                    }
                });
            });
            
            console.log(`${CONFIG.LOG_PREFIX} Fixed ${fixedCount} elements`);
        }
    };
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => WhiteTextMonitor.init());
    } else {
        WhiteTextMonitor.init();
    }
    
    // Expose to global scope for debugging
    window.WhiteTextMonitor = WhiteTextMonitor;
    
    // Add console commands for debugging
    window.whiteTextDebug = {
        report: () => WhiteTextMonitor.generateReport(),
        fixAll: () => WhiteTextMonitor.forceFixAllElements(),
        check: () => WhiteTextMonitor.checkAllElements(),
        toggleDebug: () => {
            CONFIG.DEBUG_MODE = !CONFIG.DEBUG_MODE;
            console.log(`${CONFIG.LOG_PREFIX} Debug mode:`, CONFIG.DEBUG_MODE);
        }
    };
    
    // Log available commands
    console.log(`${CONFIG.LOG_PREFIX} Debug commands available:`);
    console.log('  whiteTextDebug.report()  - Generate white text report');
    console.log('  whiteTextDebug.fixAll()  - Force fix all elements');
    console.log('  whiteTextDebug.check()   - Check all elements now');
    console.log('  whiteTextDebug.toggleDebug() - Toggle debug mode');
    
})();

// Log that the script has loaded
console.log('%c[WHITE_TEXT_DEBUG] White text debug module loaded', 'background: #4CAF50; color: white; padding: 5px; font-weight: bold');