/**
 * Aggressive Mode Toggle Fix
 * Specifically targets and removes "function: Teacher Mode" text
 * Created: August 18, 2025
 */

(function() {
    'use strict';
    
    console.log('[AGGRESSIVE_FIX] Starting aggressive mode toggle fix');
    
    function aggressiveFix() {
        // Method 1: Fix all text nodes
        function walkTextNodes(node) {
            if (node.nodeType === 3) { // Text node
                const text = node.nodeValue;
                if (text && (text.includes('function:') || text.includes('function :'))) {
                    console.warn('[AGGRESSIVE_FIX] Found problematic text:', text);
                    node.nodeValue = text.replace(/function\s*:\s*/gi, '').trim();
                    console.log('[AGGRESSIVE_FIX] Fixed to:', node.nodeValue);
                }
            } else {
                for (let child of node.childNodes) {
                    walkTextNodes(child);
                }
            }
        }
        
        // Method 2: Target specific elements that might contain the text
        const possibleContainers = [
            '.class-stats',
            '.class-stat', 
            '.stats-box',
            '.stat-box',
            '.stat-card',
            '.stats-cards',
            '.statistics-container',
            '[class*="stat"]',
            'div',
            'span',
            'p',
            'button',
            'a'
        ];
        
        possibleContainers.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(el => {
                // Check innerHTML
                if (el.innerHTML && el.innerHTML.includes('function:')) {
                    console.warn('[AGGRESSIVE_FIX] Found in innerHTML of', selector, ':', el.innerHTML.substring(0, 100));
                    el.innerHTML = el.innerHTML.replace(/function\s*:\s*/gi, '');
                }
                
                // Check textContent
                if (el.textContent && el.textContent.includes('function:')) {
                    // Only modify if it's a leaf node (no children or only text children)
                    if (el.childNodes.length === 1 && el.firstChild.nodeType === 3) {
                        console.warn('[AGGRESSIVE_FIX] Found in textContent of', selector, ':', el.textContent);
                        el.textContent = el.textContent.replace(/function\s*:\s*/gi, '');
                    }
                }
            });
        });
        
        // Method 3: Walk entire DOM
        walkTextNodes(document.body);
        
        // Method 4: Check for specific patterns
        const allElements = document.getElementsByTagName('*');
        for (let el of allElements) {
            // Check if element contains exact text "function: Teacher Mode" or "function: Admin Mode"
            if (el.childNodes.length > 0) {
                for (let child of el.childNodes) {
                    if (child.nodeType === 3) {
                        const text = child.nodeValue;
                        if (text && (
                            text.includes('function: Teacher Mode') ||
                            text.includes('function: Admin Mode') ||
                            text.includes('function : Teacher Mode') ||
                            text.includes('function : Admin Mode')
                        )) {
                            console.error('[AGGRESSIVE_FIX] FOUND EXACT MATCH:', text);
                            console.error('[AGGRESSIVE_FIX] Parent element:', el);
                            console.error('[AGGRESSIVE_FIX] Parent class:', el.className);
                            console.error('[AGGRESSIVE_FIX] Parent ID:', el.id);
                            
                            // Fix it
                            child.nodeValue = text.replace(/function\s*:\s*/gi, '');
                            console.log('[AGGRESSIVE_FIX] FIXED TO:', child.nodeValue);
                        }
                    }
                }
            }
        }
        
        // Method 5: Remove any toggles from stats areas
        const statsAreas = document.querySelectorAll('.class-stats, .class-stat, .stats-box, .stat-box');
        statsAreas.forEach(area => {
            const toggles = area.querySelectorAll('.mode-toggle-container, .mode-toggle-wrapper, .mode-toggle-btn, button:contains("Mode"), [class*="toggle"]');
            toggles.forEach(toggle => {
                console.warn('[AGGRESSIVE_FIX] Removing toggle from stats area:', toggle);
                toggle.remove();
            });
        });
        
        // Log summary
        const remainingIssues = document.body.textContent.includes('function:');
        if (remainingIssues) {
            console.error('[AGGRESSIVE_FIX] ⚠️ "function:" still found in page after fix!');
            console.error('[AGGRESSIVE_FIX] Full page search:', document.body.innerHTML.indexOf('function:'));
        } else {
            console.log('[AGGRESSIVE_FIX] ✅ No "function:" text found - fix successful!');
        }
    }
    
    // Run the fix multiple times with different timings
    aggressiveFix();
    
    // Run when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', aggressiveFix);
    } else {
        aggressiveFix();
    }
    
    // Run after delays to catch dynamic content
    const delays = [0, 10, 50, 100, 250, 500, 1000, 2000];
    delays.forEach(delay => {
        setTimeout(aggressiveFix, delay);
    });
    
    // Continuous monitoring
    const observer = new MutationObserver((mutations) => {
        let shouldFix = false;
        mutations.forEach(mutation => {
            if (mutation.type === 'childList' || mutation.type === 'characterData') {
                // Check if any added nodes contain the problematic text
                if (mutation.target.textContent && mutation.target.textContent.includes('function:')) {
                    shouldFix = true;
                }
            }
        });
        
        if (shouldFix) {
            console.log('[AGGRESSIVE_FIX] Mutation detected with "function:", running fix...');
            aggressiveFix();
        }
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true,
        characterData: true,
        characterDataOldValue: true
    });
    
    console.log('[AGGRESSIVE_FIX] Monitoring active');
    
    // Expose global function for manual testing
    window.runAggressiveFix = aggressiveFix;
})();

// Also try to intercept any function that might be setting this text
(function() {
    // Override appendChild to check for problematic content
    const originalAppendChild = Node.prototype.appendChild;
    Node.prototype.appendChild = function(child) {
        if (child && child.textContent && child.textContent.includes('function:')) {
            console.error('[AGGRESSIVE_FIX] INTERCEPTED appendChild with "function:":', child.textContent);
            if (child.nodeType === 3) {
                child.nodeValue = child.nodeValue.replace(/function\s*:\s*/gi, '');
            }
        }
        return originalAppendChild.call(this, child);
    };
    
    // Override innerHTML setter
    const originalInnerHTML = Object.getOwnPropertyDescriptor(Element.prototype, 'innerHTML');
    Object.defineProperty(Element.prototype, 'innerHTML', {
        set: function(value) {
            if (value && value.includes('function:')) {
                console.error('[AGGRESSIVE_FIX] INTERCEPTED innerHTML set with "function:":', value.substring(0, 100));
                value = value.replace(/function\s*:\s*/gi, '');
            }
            originalInnerHTML.set.call(this, value);
        },
        get: originalInnerHTML.get
    });
    
    // Override textContent setter
    const originalTextContent = Object.getOwnPropertyDescriptor(Node.prototype, 'textContent');
    Object.defineProperty(Node.prototype, 'textContent', {
        set: function(value) {
            if (value && value.includes('function:')) {
                console.error('[AGGRESSIVE_FIX] INTERCEPTED textContent set with "function:":', value);
                value = value.replace(/function\s*:\s*/gi, '');
            }
            originalTextContent.set.call(this, value);
        },
        get: originalTextContent.get
    });
})();

console.log('[AGGRESSIVE_FIX] All interception methods active');