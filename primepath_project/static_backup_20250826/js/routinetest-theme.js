/**
 * RoutineTest Theme Manager
 * 
 * Handles BCG Green theme application for RoutineTest module
 * Includes comprehensive console debugging and interaction tracking
 * 
 * Created: August 15, 2025
 * Version: 1.0.0
 */

(function(window, document) {
    'use strict';

    console.log('%c[RoutineTest Theme Manager] Initializing...', 'color: #00A65E; font-weight: bold;');

    /**
     * RoutineTest Theme Manager Class
     * Manages theme application and debugging for RoutineTest module
     */
    class RoutineTestThemeManager {
        constructor() {
            this.themeName = 'BCG Green';
            this.themeColor = '#00A65E';
            this.isRoutineTest = this.detectRoutineTestModule();
            this.debugMode = this.getDebugMode();
            this.interactions = [];
            this.themeApplied = false;
            
            console.log(`[Theme Manager] Module Detection: ${this.isRoutineTest ? 'RoutineTest' : 'Other'}`);
            console.log(`[Theme Manager] Debug Mode: ${this.debugMode ? 'ON' : 'OFF'}`);
            
            this.init();
        }

        /**
         * Initialize theme manager
         */
        init() {
            if (this.isRoutineTest) {
                console.log('%c[Theme Manager] RoutineTest module detected - Applying BCG Green theme', 
                    'background: #00A65E; color: white; padding: 5px;');
                
                this.applyTheme();
                this.setupEventListeners();
                this.trackInteractions();
                this.logThemeStatus();
                
                // Monitor for dynamic content
                this.observeDOMChanges();
                
                // Log successful initialization
                console.log('%c✅ RoutineTest Theme Manager initialized successfully', 
                    'color: #00A65E; font-weight: bold;');
            } else {
                console.log('[Theme Manager] Not a RoutineTest page - Theme not applied');
            }
        }

        /**
         * Detect if current page is part of RoutineTest module
         */
        detectRoutineTestModule() {
            const url = window.location.pathname.toLowerCase();
            const isRoutineTest = url.includes('/routinetest/') || 
                                  url.includes('/routine/') ||
                                  url.includes('routine_test');
            
            // Also check for RoutineTest in page content
            const pageTitle = document.title ? document.title.toLowerCase() : '';
            const hasRoutineTestTitle = pageTitle.includes('routine');
            
            // Check body classes
            const bodyClasses = document.body ? document.body.className : '';
            const hasRoutineTestClass = bodyClasses.includes('routine');
            
            const detected = isRoutineTest || hasRoutineTestTitle || hasRoutineTestClass;
            
            console.log('[Theme Detection]', {
                url: url,
                urlMatch: isRoutineTest,
                titleMatch: hasRoutineTestTitle,
                classMatch: hasRoutineTestClass,
                result: detected
            });
            
            return detected;
        }

        /**
         * Get debug mode status
         */
        getDebugMode() {
            // Check multiple sources for debug mode
            return window.DEBUG_MODE || 
                   window.location.search.includes('debug=true') ||
                   localStorage.getItem('routinetest_debug') === 'true';
        }

        /**
         * Apply BCG Green theme
         */
        applyTheme() {
            console.log('[Theme Manager] Applying BCG Green theme...');
            
            // Add theme class to root and body
            document.documentElement.classList.add('routinetest-theme');
            document.body.classList.add('routinetest-theme');
            
            // Set data attributes for CSS hooks
            document.body.setAttribute('data-theme', 'bcg-green');
            document.body.setAttribute('data-theme-loaded', 'true');
            document.body.setAttribute('data-module', 'routinetest');
            
            if (this.debugMode) {
                document.body.setAttribute('data-debug', 'true');
            }
            
            // Log theme colors to console
            this.logColorPalette();
            
            // Update any inline styles if needed
            this.updateInlineStyles();
            
            this.themeApplied = true;
            
            console.log('%c✅ BCG Green theme applied successfully', 
                'background: #00A65E; color: white; padding: 3px 8px; border-radius: 3px;');
        }

        /**
         * Log color palette to console
         */
        logColorPalette() {
            console.group('%c🎨 BCG Green Color Palette', 'color: #00A65E; font-weight: bold;');
            
            const colors = {
                'Primary': '#00A65E',
                'Primary Hover': '#007C3F',
                'Primary Light': '#E8F5E9',
                'Secondary': '#00C853',
                'Accent': '#1DE9B6',
                'Dark Text': '#2E4C2F',
                'Light Background': '#F5FAF7'
            };
            
            Object.entries(colors).forEach(([name, color]) => {
                console.log(
                    `%c██████%c ${name}: ${color}`,
                    `color: ${color}; font-size: 20px;`,
                    'color: inherit;'
                );
            });
            
            console.groupEnd();
        }

        /**
         * Update inline styles for better theme integration
         */
        updateInlineStyles() {
            // Update any hardcoded blue colors to green
            const elementsWithInlineStyles = document.querySelectorAll('[style*="007bff"], [style*="3498db"]');
            
            elementsWithInlineStyles.forEach(element => {
                const style = element.getAttribute('style');
                if (style) {
                    const updatedStyle = style
                        .replace(/#007bff/gi, '#00A65E')
                        .replace(/#3498db/gi, '#00A65E')
                        .replace(/rgb\(0,\s*123,\s*255\)/gi, 'rgb(0, 166, 94)');
                    
                    element.setAttribute('style', updatedStyle);
                    console.log('[Theme Manager] Updated inline style:', element);
                }
            });
        }

        /**
         * Setup event listeners for theme interactions
         */
        setupEventListeners() {
            console.log('[Theme Manager] Setting up event listeners...');
            
            // Track button clicks
            document.addEventListener('click', (e) => {
                if (e.target.matches('.btn, button, a')) {
                    this.logInteraction('click', e.target);
                }
            });
            
            // Track form submissions
            document.addEventListener('submit', (e) => {
                this.logInteraction('form_submit', e.target);
            });
            
            // Track navigation changes
            window.addEventListener('popstate', () => {
                console.log('[Theme Manager] Navigation change detected');
                this.reapplyThemeIfNeeded();
            });
            
            // Track page visibility changes
            document.addEventListener('visibilitychange', () => {
                if (!document.hidden) {
                    console.log('[Theme Manager] Page became visible - checking theme');
                    this.reapplyThemeIfNeeded();
                }
            });
        }

        /**
         * Log user interactions
         */
        logInteraction(type, element) {
            const interaction = {
                type: type,
                element: element.tagName,
                class: element.className,
                text: element.textContent?.substring(0, 50),
                timestamp: new Date().toISOString()
            };
            
            this.interactions.push(interaction);
            
            if (this.debugMode) {
                console.log('[Interaction]', interaction);
            }
            
            // Ensure theme is still applied after interaction
            this.ensureThemeIntegrity();
        }

        /**
         * Track interactions for debugging
         */
        trackInteractions() {
            // Add interaction tracking to all interactive elements
            const interactiveElements = document.querySelectorAll('button, a, input, select, textarea');
            
            console.log(`[Theme Manager] Tracking ${interactiveElements.length} interactive elements`);
            
            interactiveElements.forEach(element => {
                element.setAttribute('data-theme-tracked', 'true');
            });
        }

        /**
         * Observe DOM changes and reapply theme if needed
         */
        observeDOMChanges() {
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                        // Check if new content needs theme
                        mutation.addedNodes.forEach(node => {
                            if (node.nodeType === 1) { // Element node
                                this.applyThemeToElement(node);
                            }
                        });
                    }
                });
            });
            
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
            
            console.log('[Theme Manager] DOM observer initialized');
        }

        /**
         * Apply theme to newly added elements
         */
        applyThemeToElement(element) {
            // Apply theme class if it's a container element
            if (element.classList && !element.classList.contains('routinetest-themed')) {
                element.classList.add('routinetest-themed');
                
                if (this.debugMode) {
                    console.log('[Theme Manager] Applied theme to new element:', element);
                }
            }
            
            // Update any inline styles
            if (element.style) {
                const style = element.getAttribute('style');
                if (style && (style.includes('007bff') || style.includes('3498db'))) {
                    this.updateInlineStyles();
                }
            }
        }

        /**
         * Ensure theme integrity
         */
        ensureThemeIntegrity() {
            if (!document.body.classList.contains('routinetest-theme')) {
                console.warn('[Theme Manager] Theme class missing - reapplying');
                this.applyTheme();
            }
        }

        /**
         * Reapply theme if needed
         */
        reapplyThemeIfNeeded() {
            if (this.isRoutineTest && !this.themeApplied) {
                console.log('[Theme Manager] Reapplying theme after navigation');
                this.applyTheme();
            }
        }

        /**
         * Log theme status
         */
        logThemeStatus() {
            console.group('%c📊 RoutineTest Theme Status', 'color: #00A65E; font-weight: bold;');
            
            console.table({
                'Theme Name': this.themeName,
                'Primary Color': this.themeColor,
                'Module': 'RoutineTest',
                'Applied': this.themeApplied,
                'Debug Mode': this.debugMode,
                'Page URL': window.location.pathname,
                'Body Classes': document.body.className,
                'Theme Attributes': document.body.getAttribute('data-theme')
            });
            
            // Log computed styles for verification
            const computedStyle = window.getComputedStyle(document.documentElement);
            console.log('Computed Primary Color:', computedStyle.getPropertyValue('--color-primary'));
            
            console.groupEnd();
        }

        /**
         * Get theme statistics
         */
        getStatistics() {
            return {
                interactions: this.interactions.length,
                themeApplied: this.themeApplied,
                debugMode: this.debugMode,
                module: 'RoutineTest',
                theme: this.themeName
            };
        }

        /**
         * Export interaction log
         */
        exportInteractions() {
            const data = {
                theme: this.themeName,
                module: 'RoutineTest',
                interactions: this.interactions,
                exportTime: new Date().toISOString()
            };
            
            console.log('%c📋 Interaction Log Export', 'color: #00A65E; font-weight: bold;');
            console.log(JSON.stringify(data, null, 2));
            
            return data;
        }
    }

    /**
     * Initialize theme manager when DOM is ready
     */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            window.RoutineTestTheme = new RoutineTestThemeManager();
            console.log('[Theme Manager] Registered as window.RoutineTestTheme');
        });
    } else {
        window.RoutineTestTheme = new RoutineTestThemeManager();
        console.log('[Theme Manager] Registered as window.RoutineTestTheme');
    }

    /**
     * Expose theme utilities to global scope for debugging
     */
    window.RoutineTestThemeUtils = {
        /**
         * Toggle debug mode
         */
        toggleDebug: function() {
            const currentDebug = localStorage.getItem('routinetest_debug') === 'true';
            localStorage.setItem('routinetest_debug', !currentDebug);
            console.log(`Debug mode ${!currentDebug ? 'enabled' : 'disabled'}. Reload page to apply.`);
            return !currentDebug;
        },
        
        /**
         * Get theme status
         */
        getStatus: function() {
            if (window.RoutineTestTheme) {
                return window.RoutineTestTheme.getStatistics();
            }
            return { error: 'Theme manager not initialized' };
        },
        
        /**
         * Export interactions
         */
        exportLog: function() {
            if (window.RoutineTestTheme) {
                return window.RoutineTestTheme.exportInteractions();
            }
            return { error: 'Theme manager not initialized' };
        },
        
        /**
         * Force theme refresh
         */
        refresh: function() {
            if (window.RoutineTestTheme) {
                window.RoutineTestTheme.applyTheme();
                console.log('Theme refreshed');
            }
        },
        
        /**
         * Show color palette
         */
        showColors: function() {
            if (window.RoutineTestTheme) {
                window.RoutineTestTheme.logColorPalette();
            }
        }
    };

    console.log('%c[RoutineTest Theme] Utilities available:', 'color: #00A65E;');
    console.log('- RoutineTestThemeUtils.toggleDebug()');
    console.log('- RoutineTestThemeUtils.getStatus()');
    console.log('- RoutineTestThemeUtils.exportLog()');
    console.log('- RoutineTestThemeUtils.refresh()');
    console.log('- RoutineTestThemeUtils.showColors()');

})(window, document);