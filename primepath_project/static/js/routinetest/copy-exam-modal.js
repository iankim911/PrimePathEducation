/**
 * Copy Exam Modal Management System
 * Version: 2.0
 * Date: 2025-08-20
 * 
 * This module handles all copy exam modal functionality for the RoutineTest module
 * with comprehensive error handling and debugging capabilities.
 */

(function(window, document) {
    'use strict';
    
    // ============================================================================
    // MODULE CONFIGURATION
    // ============================================================================
    const CONFIG = {
        modalId: 'copyExamModal',
        formId: 'copyExamForm',
        sourceExamIdField: 'sourceExamId',
        sourceExamNameField: 'sourceExamName',
        timeslotField: 'timeslot',
        examTypeField: 'copyExamType',
        targetClassField: 'targetClass',
        apiEndpoint: '/RoutineTest/api/copy-exam/',
        debugMode: true,
        animationDuration: 300
    };
    
    // ============================================================================
    // STATE MANAGEMENT
    // ============================================================================
    const state = {
        initialized: false,
        isOpen: false,
        currentExamId: null,
        currentExamName: null,
        currentExamCurriculum: null,  // Store curriculum info from exam name
        formSubmitting: false,
        initTime: Date.now()
    };
    
    // ============================================================================
    // LOGGING UTILITIES
    // ============================================================================
    const logger = {
        log: function(message, ...args) {
            if (CONFIG.debugMode) {
                console.log(`%c[COPY MODAL] ${message}`, 'color: #00A65E', ...args);
            }
        },
        error: function(message, ...args) {
            console.error(`[COPY MODAL ERROR] ${message}`, ...args);
        },
        group: function(title) {
            if (CONFIG.debugMode) {
                console.group(`%c[COPY MODAL] ${title}`, 'color: #00A65E; font-weight: bold');
            }
        },
        groupEnd: function() {
            if (CONFIG.debugMode) {
                console.groupEnd();
            }
        },
        table: function(data) {
            if (CONFIG.debugMode) {
                console.table(data);
            }
        }
    };
    
    // ============================================================================
    // DOM ELEMENT CACHE
    // ============================================================================
    const elements = {};
    
    function cacheElements() {
        elements.modal = document.getElementById(CONFIG.modalId);
        elements.form = document.getElementById(CONFIG.formId);
        elements.sourceExamId = document.getElementById(CONFIG.sourceExamIdField);
        elements.sourceExamName = document.getElementById(CONFIG.sourceExamNameField);
        elements.timeslot = document.getElementById(CONFIG.timeslotField);
        elements.examType = document.getElementById(CONFIG.examTypeField);
        elements.targetClass = document.getElementById(CONFIG.targetClassField);
        elements.academicYear = document.getElementById('academicYear');
        elements.customSuffix = document.getElementById('customSuffix');
        elements.examNamePreview = document.getElementById('previewText');
        
        // Log which elements were found
        const elementStatus = {};
        Object.keys(elements).forEach(key => {
            elementStatus[key] = elements[key] ? '✅ Found' : '❌ Not Found';
        });
        logger.table(elementStatus);
        
        return elements.modal && elements.form; // Minimum required elements
    }
    
    // ============================================================================
    // MAIN MODAL FUNCTIONS
    // ============================================================================
    
    /**
     * Open the copy exam modal
     * @param {string} examId - The ID of the exam to copy
     * @param {string} examName - The name of the exam to copy
     * @returns {boolean} - Success status
     */
    function openCopyModal(examId, examName) {
        const startTime = performance.now();
        
        logger.group('Opening Copy Modal');
        logger.log('Exam ID:', examId);
        logger.log('Exam Name:', examName);
        logger.log('Call origin:', new Error().stack.split('\n')[2].trim());
        
        try {
            // Validate inputs
            if (!examId) {
                logger.error('No exam ID provided');
                alert('Error: No exam ID provided');
                logger.groupEnd();
                return false;
            }
            
            // Cache elements if not already done
            if (!elements.modal) {
                if (!cacheElements()) {
                    logger.error('Required elements not found in DOM');
                    alert('Error: Copy modal not found. Please refresh the page.');
                    logger.groupEnd();
                    return false;
                }
            }
            
            // Update state
            state.currentExamId = examId;
            state.currentExamName = examName;
            state.isOpen = true;
            
            // Set form values
            if (elements.sourceExamId) {
                elements.sourceExamId.value = examId;
                logger.log('Set source exam ID:', examId);
            }
            
            if (elements.sourceExamName) {
                elements.sourceExamName.textContent = examName || 'Unknown Exam';
                logger.log('Set source exam name:', examName);
            }
            
            // Reset form
            if (elements.form) {
                elements.form.reset();
                // Re-set exam ID after reset
                if (elements.sourceExamId) {
                    elements.sourceExamId.value = examId;
                }
                logger.log('Form reset completed');
            }
            
            // Reset timeslot dropdown
            if (elements.timeslot) {
                elements.timeslot.innerHTML = '<option value="">First select exam type...</option>';
                elements.timeslot.disabled = true;
                logger.log('Timeslot dropdown reset');
            }
            
            // Show modal with animation
            showModalWithAnimation();
            
            // Set up event handlers
            setupModalEventHandlers();
            
            const executionTime = performance.now() - startTime;
            logger.log(`Modal opened successfully in ${executionTime.toFixed(2)}ms`);
            
            // Verify modal is visible
            const computedStyle = window.getComputedStyle(elements.modal);
            logger.log('Modal display:', computedStyle.display);
            logger.log('Modal visibility:', computedStyle.visibility);
            logger.log('Modal opacity:', computedStyle.opacity);
            
            logger.groupEnd();
            return true;
            
        } catch (error) {
            logger.error('Critical error opening modal:', error);
            logger.error('Stack trace:', error.stack);
            alert('An error occurred while opening the copy modal. Please try again.');
            logger.groupEnd();
            return false;
        }
    }
    
    /**
     * Close the copy exam modal
     * @returns {boolean} - Success status
     */
    function closeCopyModal() {
        logger.group('Closing Copy Modal');
        
        try {
            if (!elements.modal) {
                logger.error('Modal element not found');
                logger.groupEnd();
                return false;
            }
            
            // Update state
            state.isOpen = false;
            state.currentExamId = null;
            state.currentExamName = null;
            
            // Hide modal with animation
            hideModalWithAnimation();
            
            // Reset form
            if (elements.form) {
                elements.form.reset();
                logger.log('Form reset on close');
            }
            
            // Clear event handlers
            clearModalEventHandlers();
            
            logger.log('Modal closed successfully');
            logger.groupEnd();
            return true;
            
        } catch (error) {
            logger.error('Error closing modal:', error);
            logger.groupEnd();
            return false;
        }
    }
    
    // ============================================================================
    // ANIMATION FUNCTIONS
    // ============================================================================
    
    function showModalWithAnimation() {
        if (!elements.modal) return;
        
        // Reset any previous styles
        elements.modal.style.display = 'block';
        elements.modal.style.opacity = '0';
        
        // Force reflow
        elements.modal.offsetHeight;
        
        // Add show class and animate
        elements.modal.classList.add('show');
        elements.modal.style.opacity = '1';
        
        // Prevent body scroll
        document.body.style.overflow = 'hidden';
        
        logger.log('Modal show animation started');
    }
    
    function hideModalWithAnimation() {
        if (!elements.modal) return;
        
        // Animate out
        elements.modal.style.opacity = '0';
        
        // Remove after animation
        setTimeout(() => {
            elements.modal.style.display = 'none';
            elements.modal.classList.remove('show');
            
            // Restore body scroll
            document.body.style.overflow = '';
            
            logger.log('Modal hide animation completed');
        }, CONFIG.animationDuration);
    }
    
    // ============================================================================
    // EVENT HANDLERS
    // ============================================================================
    
    function setupModalEventHandlers() {
        // Background click to close
        if (elements.modal) {
            elements.modal.onclick = function(e) {
                if (e.target === elements.modal) {
                    logger.log('Background clicked - closing modal');
                    closeCopyModal();
                }
            };
        }
        
        // Exam type change handler
        if (elements.examType) {
            elements.examType.onchange = handleExamTypeChange;
        }
        
        // Form submission
        if (elements.form) {
            elements.form.onsubmit = handleFormSubmit;
        }
        
        logger.log('Event handlers attached');
    }
    
    function clearModalEventHandlers() {
        if (elements.modal) elements.modal.onclick = null;
        if (elements.examType) elements.examType.onchange = null;
        if (elements.form) elements.form.onsubmit = null;
        
        logger.log('Event handlers cleared');
    }
    
    function handleExamTypeChange(event) {
        const examType = event.target.value;
        logger.log('Exam type changed to:', examType);
        
        if (!elements.timeslot) return;
        
        elements.timeslot.disabled = false;
        elements.timeslot.innerHTML = '<option value="">Select time period...</option>';
        
        if (examType === 'QUARTERLY') {
            // Add quarterly options
            const quarters = [
                { value: 'Q1', text: 'Quarter 1' },
                { value: 'Q2', text: 'Quarter 2' },
                { value: 'Q3', text: 'Quarter 3' },
                { value: 'Q4', text: 'Quarter 4' }
            ];
            
            quarters.forEach(q => {
                const option = document.createElement('option');
                option.value = q.value;
                option.textContent = q.text;
                elements.timeslot.appendChild(option);
            });
            
            logger.log('Added quarterly timeslot options');
            
        } else if (examType === 'REVIEW') {
            // Add monthly options
            const months = [
                'January', 'February', 'March', 'April', 'May', 'June',
                'July', 'August', 'September', 'October', 'November', 'December'
            ];
            
            months.forEach((month, index) => {
                const option = document.createElement('option');
                option.value = month.substring(0, 3).toUpperCase();
                option.textContent = month;
                elements.timeslot.appendChild(option);
            });
            
            logger.log('Added monthly timeslot options');
        }
    }
    
    async function handleFormSubmit(event) {
        event.preventDefault();
        
        if (state.formSubmitting) {
            logger.log('Form already submitting, ignoring duplicate submission');
            return false;
        }
        
        logger.group('Form Submission');
        
        const formData = new FormData(elements.form);
        const data = {
            source_exam_id: formData.get('source_exam_id'),
            target_class: formData.get('target_class'),
            target_timeslot: formData.get('timeslot'),
            academic_year: formData.get('academic_year'),
            custom_suffix: formData.get('custom_suffix')
        };
        
        logger.log('Form data:', data);
        
        // Validate
        if (!data.source_exam_id || !data.target_class || !data.target_timeslot) {
            logger.error('Validation failed - missing required fields');
            showNotification('Please fill in all required fields', 'error');
            logger.groupEnd();
            return false;
        }
        
        // Update UI for loading state
        state.formSubmitting = true;
        const submitBtn = elements.form.querySelector('button[type="submit"]');
        const originalText = submitBtn ? submitBtn.textContent : '';
        if (submitBtn) {
            submitBtn.textContent = 'Copying...';
            submitBtn.disabled = true;
        }
        
        try {
            // Get CSRF token
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                             document.querySelector('meta[name="csrf-token"]')?.content || '';
            
            logger.log('Sending request to:', CONFIG.apiEndpoint);
            
            const response = await fetch(CONFIG.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(data)
            });
            
            logger.log('Response status:', response.status);
            
            const result = await response.json();
            logger.log('Response data:', result);
            
            if (response.ok && result.success) {
                showNotification(result.message || 'Exam copied successfully!', 'success');
                closeCopyModal();
                
                // Reload page after short delay
                setTimeout(() => {
                    logger.log('Reloading page...');
                    window.location.reload();
                }, 1500);
                
            } else {
                throw new Error(result.error || result.message || 'Failed to copy exam');
            }
            
        } catch (error) {
            logger.error('Copy operation failed:', error);
            showNotification('Error: ' + error.message, 'error');
            
            // Restore button state
            if (submitBtn) {
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }
            
        } finally {
            state.formSubmitting = false;
            logger.groupEnd();
        }
        
        return false;
    }
    
    // ============================================================================
    // NOTIFICATION SYSTEM
    // ============================================================================
    
    function showNotification(message, type = 'info') {
        logger.log(`Notification [${type}]: ${message}`);
        
        // Remove any existing notifications
        const existingNotification = document.querySelector('.copy-modal-notification');
        if (existingNotification) {
            existingNotification.remove();
        }
        
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `copy-modal-notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 5px;
            z-index: 10001;
            animation: slideIn 0.3s ease;
            max-width: 400px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        `;
        
        // Set colors based on type
        if (type === 'success') {
            notification.style.backgroundColor = '#4CAF50';
            notification.style.color = 'white';
        } else if (type === 'error') {
            notification.style.backgroundColor = '#f44336';
            notification.style.color = 'white';
        } else {
            notification.style.backgroundColor = '#2196F3';
            notification.style.color = 'white';
        }
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    }
    
    // ============================================================================
    // NAME PREVIEW GENERATION
    // ============================================================================
    
    function updateNamePreview() {
        logger.log('[NAME_PREVIEW] Updating exam name preview...');
        
        if (!elements.examNamePreview) {
            logger.error('[NAME_PREVIEW] Preview element not found');
            return;
        }
        
        const examType = elements.examType?.value;
        const timeslot = elements.timeslot?.value;
        const academicYear = elements.academicYear?.value;
        const customSuffix = elements.customSuffix?.value?.trim();
        
        // Check if all required fields are filled
        if (!examType || !timeslot || !academicYear) {
            elements.examNamePreview.textContent = 'Please complete all fields to see preview...';
            logger.log('[NAME_PREVIEW] Missing required fields');
            return;
        }
        
        // Build the name preview
        let nameParts = [];
        
        // Add exam type prefix
        const prefix = examType === 'QUARTERLY' ? '[QTR]' : '[RT]';
        nameParts.push(prefix);
        
        // Add time period with year
        if (examType === 'REVIEW') {
            // Convert month code to abbreviated name
            const monthAbbrev = {
                'JAN': 'Jan', 'FEB': 'Feb', 'MAR': 'Mar', 'APR': 'Apr',
                'MAY': 'May', 'JUN': 'Jun', 'JUL': 'Jul', 'AUG': 'Aug',
                'SEP': 'Sep', 'OCT': 'Oct', 'NOV': 'Nov', 'DEC': 'Dec'
            };
            const monthName = monthAbbrev[timeslot] || timeslot;
            nameParts.push(`${monthName} ${academicYear}`);
        } else {
            nameParts.push(`${timeslot} ${academicYear}`);
        }
        
        // Extract curriculum from exam name
        if (state.currentExamName) {
            const curriculumMatch = state.currentExamName.match(/(CORE|ASCENT|EDGE|PINNACLE)\s+(\w+)\s+Lv(\d+)/);
            if (curriculumMatch) {
                const curriculum = `${curriculumMatch[1]} ${curriculumMatch[2]} Lv${curriculumMatch[3]}`;
                nameParts.push(curriculum);
                state.currentExamCurriculum = curriculum;
            } else {
                // Try to extract any curriculum-like pattern
                const levelMatch = state.currentExamName.match(/Lv\d+/);
                if (levelMatch) {
                    const beforeLevel = state.currentExamName.substring(
                        state.currentExamName.lastIndexOf('-') + 1,
                        state.currentExamName.indexOf(levelMatch[0])
                    ).trim();
                    if (beforeLevel) {
                        nameParts.push(`${beforeLevel}${levelMatch[0]}`);
                        state.currentExamCurriculum = `${beforeLevel}${levelMatch[0]}`;
                    }
                }
            }
        }
        
        // Join parts
        let previewName = nameParts.join(' - ');
        
        // Add custom suffix if provided
        if (customSuffix) {
            previewName += customSuffix.startsWith('_') ? customSuffix : `_${customSuffix}`;
        }
        
        elements.examNamePreview.textContent = previewName;
        logger.log('[NAME_PREVIEW] Generated preview:', previewName);
    }
    
    // ============================================================================
    // INITIALIZATION
    // ============================================================================
    
    function initialize() {
        logger.group('Initializing Copy Modal System');
        
        try {
            // Cache elements
            if (!cacheElements()) {
                logger.error('Failed to cache required elements');
                state.initialized = false;
                logger.groupEnd();
                return false;
            }
            
            // Add CSS animations if not already present
            if (!document.getElementById('copy-modal-styles')) {
                const style = document.createElement('style');
                style.id = 'copy-modal-styles';
                style.textContent = `
                    @keyframes slideIn {
                        from { transform: translateX(100%); opacity: 0; }
                        to { transform: translateX(0); opacity: 1; }
                    }
                    @keyframes slideOut {
                        from { transform: translateX(0); opacity: 1; }
                        to { transform: translateX(100%); opacity: 0; }
                    }
                    #${CONFIG.modalId} {
                        transition: opacity ${CONFIG.animationDuration}ms ease;
                    }
                    #${CONFIG.modalId}.show {
                        display: block !important;
                    }
                `;
                document.head.appendChild(style);
                logger.log('Added modal styles');
            }
            
            // Register global functions
            window.openCopyModal = openCopyModal;
            window.closeCopyModal = closeCopyModal;
            
            // Create aliases for compatibility
            window.CopyModalManager = {
                open: openCopyModal,
                close: closeCopyModal,
                getState: () => state,
                getConfig: () => CONFIG,
                showNotification: showNotification,
                logger: logger
            };
            
            state.initialized = true;
            
            logger.log('✅ Copy Modal System initialized successfully');
            logger.log('Available functions:');
            logger.log('  - window.openCopyModal(examId, examName)');
            logger.log('  - window.closeCopyModal()');
            logger.log('  - window.CopyModalManager (advanced API)');
            
            logger.groupEnd();
            return true;
            
        } catch (error) {
            logger.error('Failed to initialize:', error);
            state.initialized = false;
            logger.groupEnd();
            return false;
        }
    }
    
    // ============================================================================
    // AUTO-INITIALIZATION
    // ============================================================================
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initialize);
        logger.log('Waiting for DOM to load...');
    } else {
        // DOM already loaded
        initialize();
    }
    
    // ============================================================================
    // PUBLIC API FOR DEBUGGING
    // ============================================================================
    
    window.CopyModalDebug = {
        getState: () => state,
        getElements: () => elements,
        getConfig: () => CONFIG,
        testOpen: () => openCopyModal('test-id-123', 'Test Exam Name'),
        testClose: () => closeCopyModal(),
        testNotification: (msg, type) => showNotification(msg || 'Test notification', type || 'info'),
        reinitialize: () => initialize(),
        setDebugMode: (enabled) => { CONFIG.debugMode = enabled; }
    };
    
    logger.log('%c[COPY MODAL] Module loaded. Debug API available at window.CopyModalDebug', 'color: #00A65E; font-weight: bold');
    
})(window, document);