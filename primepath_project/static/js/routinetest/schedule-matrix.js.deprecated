/**
 * RoutineTest Schedule Matrix Module
 * Handles exam assignment matrix functionality with proper tab management
 * 
 * @module ScheduleMatrix
 * @version 3.0.0
 * @description Complete rewrite for modular architecture and proper tab handling
 */

(function(window, document) {
    'use strict';

    // Module configuration
    const config = {
        debug: true,
        animationDuration: 300,
        defaultTab: 'monthly',
        endpoints: {
            cellDetail: '/RoutineTest/schedule-matrix/cell/',
            bulkAssign: '/RoutineTest/schedule-matrix/bulk-assign/',
            updateCell: '/RoutineTest/schedule-matrix/update/'
        }
    };

    // Module state
    const state = {
        currentTab: config.defaultTab,
        selectedCells: [],
        isLoading: false,
        initialized: false
    };

    // Debug logger with color coding
    const logger = {
        log: function(message, data = null) {
            if (!config.debug) return;
            const timestamp = new Date().toISOString();
            const prefix = '%c[SCHEDULE_MATRIX]';
            const style = 'background: #00A65E; color: white; padding: 2px 5px; border-radius: 3px;';
            
            if (data) {
                console.log(`${prefix} ${timestamp} - ${message}`, style, data);
            } else {
                console.log(`${prefix} ${timestamp} - ${message}`, style);
            }
        },
        
        error: function(message, error = null) {
            const prefix = '%c[SCHEDULE_MATRIX ERROR]';
            const style = 'background: #F44336; color: white; padding: 2px 5px; border-radius: 3px;';
            console.error(`${prefix} ${message}`, style, error);
        },
        
        group: function(title) {
            if (!config.debug) return;
            console.group(`%c${title}`, 'color: #00A65E; font-weight: bold;');
        },
        
        groupEnd: function() {
            if (!config.debug) return;
            console.groupEnd();
        }
    };

    /**
     * Tab Panel Manager
     * Handles tab switching with proper panel visibility
     */
    const TabManager = {
        panels: {},
        tabs: {},
        
        init: function() {
            logger.log('Initializing Tab Manager');
            
            // Cache panel and tab elements
            this.panels = {
                monthly: document.getElementById('monthly-panel'),
                quarterly: document.getElementById('quarterly-panel')
            };
            
            this.tabs = {
                monthly: document.querySelector('[data-tab="monthly"]'),
                quarterly: document.querySelector('[data-tab="quarterly"]')
            };
            
            // Verify elements exist
            if (!this.panels.monthly || !this.panels.quarterly) {
                logger.error('Tab panels not found in DOM');
                return false;
            }
            
            // Set initial state
            this.switchTo(config.defaultTab);
            
            // Bind tab click events
            this.bindEvents();
            
            logger.log('Tab Manager initialized successfully');
            return true;
        },
        
        bindEvents: function() {
            Object.keys(this.tabs).forEach(tabName => {
                const tab = this.tabs[tabName];
                if (tab) {
                    tab.addEventListener('click', (e) => {
                        e.preventDefault();
                        this.switchTo(tabName);
                    });
                }
            });
        },
        
        switchTo: function(tabName) {
            logger.group(`Switching to ${tabName} tab`);
            
            // Validate tab name
            if (!this.panels[tabName]) {
                logger.error(`Invalid tab name: ${tabName}`);
                logger.groupEnd();
                return;
            }
            
            // Update state
            const previousTab = state.currentTab;
            state.currentTab = tabName;
            
            // Hide all panels first
            Object.keys(this.panels).forEach(name => {
                const panel = this.panels[name];
                if (panel) {
                    panel.style.display = 'none';
                    panel.setAttribute('aria-hidden', 'true');
                    panel.classList.remove('active');
                }
            });
            
            // Remove active class from all tabs
            Object.keys(this.tabs).forEach(name => {
                const tab = this.tabs[name];
                if (tab) {
                    tab.classList.remove('active');
                    tab.setAttribute('aria-selected', 'false');
                }
            });
            
            // Show selected panel
            const selectedPanel = this.panels[tabName];
            const selectedTab = this.tabs[tabName];
            
            if (selectedPanel) {
                selectedPanel.style.display = 'block';
                selectedPanel.setAttribute('aria-hidden', 'false');
                selectedPanel.classList.add('active');
                
                // Trigger reflow to ensure display change is applied
                void selectedPanel.offsetHeight;
            }
            
            if (selectedTab) {
                selectedTab.classList.add('active');
                selectedTab.setAttribute('aria-selected', 'true');
            }
            
            // Emit custom event
            const event = new CustomEvent('tabChanged', {
                detail: {
                    from: previousTab,
                    to: tabName
                }
            });
            document.dispatchEvent(event);
            
            logger.log(`Tab switched from ${previousTab} to ${tabName}`);
            logger.groupEnd();
        },
        
        getCurrentTab: function() {
            return state.currentTab;
        }
    };

    /**
     * Cell Manager
     * Handles matrix cell interactions
     */
    const CellManager = {
        init: function() {
            logger.log('Initializing Cell Manager');
            this.bindEvents();
            return true;
        },
        
        bindEvents: function() {
            // Use event delegation for cell clicks
            document.addEventListener('click', (e) => {
                const cell = e.target.closest('.matrix-cell');
                if (cell) {
                    this.handleCellClick(cell);
                }
            });
        },
        
        handleCellClick: function(cell) {
            const cellId = cell.dataset.cellId;
            const classCode = cell.dataset.classCode;
            const period = cell.dataset.period;
            const type = cell.dataset.type;
            
            logger.group('Cell clicked');
            logger.log('Cell details', {
                id: cellId,
                class: classCode,
                period: period,
                type: type
            });
            
            // Add visual feedback
            cell.classList.add('cell-clicking');
            setTimeout(() => {
                cell.classList.remove('cell-clicking');
            }, 200);
            
            this.openCellDetail(cellId);
            logger.groupEnd();
        },
        
        openCellDetail: function(cellId) {
            if (state.isLoading) {
                logger.log('Already loading, ignoring click');
                return;
            }
            
            state.isLoading = true;
            logger.log(`Loading details for cell ${cellId}`);
            
            // Show modal
            const modal = document.getElementById('cell-detail-modal');
            if (modal) {
                modal.classList.add('active');
                modal.setAttribute('aria-hidden', 'false');
            }
            
            // Load cell details via AJAX
            fetch(`${config.endpoints.cellDetail}${cellId}/`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.text();
                })
                .then(html => {
                    const contentElement = document.getElementById('cell-detail-content');
                    if (contentElement) {
                        contentElement.innerHTML = html;
                    }
                    logger.log('Cell details loaded successfully');
                })
                .catch(error => {
                    logger.error('Failed to load cell details', error);
                    this.showError('Failed to load cell details. Please try again.');
                })
                .finally(() => {
                    state.isLoading = false;
                });
        },
        
        closeCellDetail: function() {
            const modal = document.getElementById('cell-detail-modal');
            if (modal) {
                modal.classList.remove('active');
                modal.setAttribute('aria-hidden', 'true');
            }
            logger.log('Cell detail modal closed');
        },
        
        showError: function(message) {
            const contentElement = document.getElementById('cell-detail-content');
            if (contentElement) {
                contentElement.innerHTML = `
                    <div class="error-message">
                        <i class="fas fa-exclamation-triangle"></i>
                        <p>${message}</p>
                    </div>
                `;
            }
        }
    };

    /**
     * Exam Assignment Manager
     * Handles exam assignment and removal operations
     */
    const ExamManager = {
        assignExam: function(cellId, examId) {
            logger.group('Assigning exam');
            logger.log('Assignment details', { cellId, examId });
            
            const data = {
                action: 'add_exam',
                exam_id: examId
            };
            
            return this.updateCell(cellId, data)
                .then(response => {
                    logger.log('Exam assigned successfully', response);
                    this.refreshCell(cellId);
                    logger.groupEnd();
                    return response;
                })
                .catch(error => {
                    logger.error('Failed to assign exam', error);
                    logger.groupEnd();
                    throw error;
                });
        },
        
        removeExam: function(cellId, examId) {
            logger.group('Removing exam');
            logger.log('Removal details', { cellId, examId });
            
            if (!confirm('Are you sure you want to remove this exam from the schedule?')) {
                logger.log('Removal cancelled by user');
                logger.groupEnd();
                return Promise.resolve(null);
            }
            
            const data = {
                action: 'remove_exam',
                exam_id: examId
            };
            
            return this.updateCell(cellId, data)
                .then(response => {
                    logger.log('Exam removed successfully', response);
                    this.refreshCell(cellId);
                    logger.groupEnd();
                    return response;
                })
                .catch(error => {
                    logger.error('Failed to remove exam', error);
                    logger.groupEnd();
                    throw error;
                });
        },
        
        updateCell: function(cellId, data) {
            const url = `${config.endpoints.updateCell}${cellId}/`;
            
            return fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': Utils.getCsrfToken()
                },
                body: JSON.stringify(data)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            });
        },
        
        refreshCell: function(cellId) {
            // Find and update the cell in the DOM
            const cell = document.querySelector(`[data-cell-id="${cellId}"]`);
            if (cell) {
                // Update visual state
                cell.classList.add('updating');
                
                setTimeout(() => {
                    cell.classList.remove('updating');
                    cell.classList.add('updated');
                    
                    setTimeout(() => {
                        cell.classList.remove('updated');
                    }, 1000);
                }, 300);
            }
        }
    };

    /**
     * Utility functions
     */
    const Utils = {
        getCsrfToken: function() {
            const cookie = document.cookie
                .split('; ')
                .find(row => row.startsWith('csrftoken='));
            
            return cookie ? cookie.split('=')[1] : '';
        },
        
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
        
        formatDate: function(dateString) {
            if (!dateString) return '';
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                year: 'numeric'
            });
        }
    };

    /**
     * Debug Panel
     * Provides runtime debugging information
     */
    const DebugPanel = {
        init: function() {
            if (!config.debug) return;
            
            // Create debug panel if it doesn't exist
            if (!document.getElementById('matrix-debug-panel')) {
                this.createPanel();
            }
            
            // Bind keyboard shortcut (Ctrl+Shift+D)
            document.addEventListener('keydown', (e) => {
                if (e.ctrlKey && e.shiftKey && e.key === 'D') {
                    this.toggle();
                }
            });
            
            // Update panel on tab change
            document.addEventListener('tabChanged', (e) => {
                this.update();
            });
            
            logger.log('Debug panel initialized');
        },
        
        createPanel: function() {
            const panel = document.createElement('div');
            panel.id = 'matrix-debug-panel';
            panel.className = 'debug-panel';
            panel.innerHTML = `
                <div class="debug-header">
                    <span>🐛 Schedule Matrix Debug</span>
                    <button onclick="ScheduleMatrix.DebugPanel.close()">×</button>
                </div>
                <div class="debug-content" id="debug-info"></div>
            `;
            document.body.appendChild(panel);
        },
        
        toggle: function() {
            const panel = document.getElementById('matrix-debug-panel');
            if (panel) {
                panel.classList.toggle('active');
                if (panel.classList.contains('active')) {
                    this.update();
                }
            }
        },
        
        close: function() {
            const panel = document.getElementById('matrix-debug-panel');
            if (panel) {
                panel.classList.remove('active');
            }
        },
        
        update: function() {
            const info = document.getElementById('debug-info');
            if (!info) return;
            
            const cells = document.querySelectorAll('.matrix-cell');
            const visibleCells = Array.from(cells).filter(cell => {
                const rect = cell.getBoundingClientRect();
                return rect.width > 0 && rect.height > 0;
            });
            
            info.innerHTML = `
                <div><strong>Current Tab:</strong> ${state.currentTab}</div>
                <div><strong>Total Cells:</strong> ${cells.length}</div>
                <div><strong>Visible Cells:</strong> ${visibleCells.length}</div>
                <div><strong>Selected Cells:</strong> ${state.selectedCells.length}</div>
                <div><strong>Loading:</strong> ${state.isLoading}</div>
                <div><strong>Initialized:</strong> ${state.initialized}</div>
                <hr>
                <div><strong>Monthly Panel:</strong> ${TabManager.panels.monthly ? 'Found' : 'Missing'}</div>
                <div><strong>Quarterly Panel:</strong> ${TabManager.panels.quarterly ? 'Found' : 'Missing'}</div>
            `;
        }
    };

    /**
     * Main module initialization
     */
    const ScheduleMatrix = {
        init: function() {
            logger.group('Initializing Schedule Matrix Module v3.0.0');
            
            // Check if already initialized
            if (state.initialized) {
                logger.log('Module already initialized, skipping');
                logger.groupEnd();
                return;
            }
            
            try {
                // Initialize sub-modules
                const tabInit = TabManager.init();
                const cellInit = CellManager.init();
                
                if (!tabInit || !cellInit) {
                    throw new Error('Failed to initialize sub-modules');
                }
                
                // Initialize debug panel
                DebugPanel.init();
                
                // Bind global events
                this.bindGlobalEvents();
                
                // Mark as initialized
                state.initialized = true;
                
                logger.log('Schedule Matrix initialized successfully');
                logger.log('Initial state', state);
                
                // Announce initialization
                const event = new CustomEvent('scheduleMatrixReady', {
                    detail: { version: '3.0.0' }
                });
                document.dispatchEvent(event);
                
            } catch (error) {
                logger.error('Failed to initialize Schedule Matrix', error);
                state.initialized = false;
            }
            
            logger.groupEnd();
        },
        
        bindGlobalEvents: function() {
            // Year selector change
            const yearSelector = document.getElementById('year-selector');
            if (yearSelector) {
                yearSelector.addEventListener('change', (e) => {
                    logger.log(`Year changed to ${e.target.value}`);
                    this.refreshMatrix();
                });
            }
            
            // Refresh button
            const refreshBtn = document.querySelector('[data-action="refresh"]');
            if (refreshBtn) {
                refreshBtn.addEventListener('click', () => {
                    this.refreshMatrix();
                });
            }
            
            // Modal close button
            const modalClose = document.querySelector('.modal-close');
            if (modalClose) {
                modalClose.addEventListener('click', () => {
                    CellManager.closeCellDetail();
                });
            }
            
            // Close modal on outside click
            const modal = document.getElementById('cell-detail-modal');
            if (modal) {
                modal.addEventListener('click', (e) => {
                    if (e.target === modal) {
                        CellManager.closeCellDetail();
                    }
                });
            }
        },
        
        refreshMatrix: function() {
            logger.log('Refreshing matrix...');
            // In a real implementation, this would reload the matrix data via AJAX
            location.reload();
        },
        
        // Public API
        getState: function() {
            return { ...state };
        },
        
        getCurrentTab: function() {
            return state.currentTab;
        },
        
        switchTab: function(tabName) {
            TabManager.switchTo(tabName);
        },
        
        // Expose sub-modules for external access if needed
        TabManager: TabManager,
        CellManager: CellManager,
        ExamManager: ExamManager,
        DebugPanel: DebugPanel,
        Utils: Utils
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            ScheduleMatrix.init();
        });
    } else {
        // DOM is already loaded
        ScheduleMatrix.init();
    }

    // Expose module to global scope
    window.ScheduleMatrix = ScheduleMatrix;

})(window, document);