/**
 * Copy Exam Modal - Complete Implementation
 * Version: COMPLETE_FIX_V1
 * Date: 2025-08-25
 * 
 * COMPREHENSIVE FIX: This file consolidates all copy exam functionality
 * with proper initialization, event handling, and extensive debugging.
 * 
 * ARCHITECTURE: Single source of truth for copy exam modal functionality
 * - No template overrides needed
 * - Complete preview functionality
 * - Full curriculum cascading
 * - Extensive console logging for debugging
 */

(function() {
    'use strict';
    
    const MODULE_NAME = 'COPY_EXAM_COMPLETE';
    const DEBUG = true; // Enable extensive logging
    
    // Module state
    let isInitialized = false;
    let curriculumData = null;
    let currentExamInfo = null;
    let eventListenersAttached = false;
    
    // ========================================================================
    // DEBUGGING UTILITIES
    // ========================================================================
    
    function log(message, data = null, level = 'info') {
        if (!DEBUG) return;
        
        const timestamp = new Date().toISOString();
        const prefix = `[${MODULE_NAME}] [${timestamp}]`;
        
        const logData = data ? `\n${JSON.stringify(data, null, 2)}` : '';
        console[level](`${prefix} ${message}${logData}`);
    }
    
    function logError(message, error = null) {
        const errorInfo = error ? `\nError: ${error.message || error}\nStack: ${error.stack || 'N/A'}` : '';
        log(`❌ ERROR: ${message}${errorInfo}`, null, 'error');
    }
    
    function logSuccess(message, data = null) {
        console.log(`%c[${MODULE_NAME}] ✅ ${message}`, 'color: green; font-weight: bold', data || '');
    }
    
    function logWarning(message, data = null) {
        console.warn(`[${MODULE_NAME}] ⚠️ ${message}`, data || '');
    }
    
    function logDebugState() {
        console.group(`[${MODULE_NAME}] Current State`);
        console.log('isInitialized:', isInitialized);
        console.log('eventListenersAttached:', eventListenersAttached);
        console.log('curriculumData loaded:', !!curriculumData);
        console.log('currentExamInfo:', currentExamInfo);
        
        // Check DOM elements
        const elements = {
            modal: document.getElementById('copyExamModal'),
            form: document.getElementById('copyExamForm'),
            examType: document.getElementById('copyExamType'),
            timeslot: document.getElementById('timeslot'),
            program: document.getElementById('copyProgramSelect'),
            subprogram: document.getElementById('copySubprogramSelect'),
            level: document.getElementById('copyLevelSelect'),
            previewText: document.getElementById('previewText')
        };
        
        console.log('DOM Elements:', Object.entries(elements).map(([key, el]) => 
            `${key}: ${el ? '✅' : '❌'}`
        ).join(', '));
        
        console.groupEnd();
    }
    
    // ========================================================================
    // CURRICULUM DATA MANAGEMENT
    // ========================================================================
    
    function loadCurriculumData() {
        log('Loading curriculum data...');
        
        // Method 1: From JSON script element
        const scriptElement = document.getElementById('copy-curriculum-hierarchy-data');
        if (scriptElement) {
            try {
                const rawData = JSON.parse(scriptElement.textContent);
                log('Raw curriculum data from script element:', rawData);
                
                // Extract curriculum data from wrapper
                if (rawData.curriculum_data) {
                    curriculumData = rawData.curriculum_data;
                } else if (rawData.CORE || rawData.ASCENT || rawData.EDGE || rawData.PINNACLE) {
                    curriculumData = rawData;
                } else {
                    logError('Unknown curriculum data structure');
                    return false;
                }
                
                logSuccess('Curriculum data loaded from script element');
                log('Programs found:', Object.keys(curriculumData));
                return true;
                
            } catch (error) {
                logError('Failed to parse curriculum data', error);
            }
        }
        
        // Method 2: From window object
        if (window.CURRICULUM_DATA) {
            curriculumData = window.CURRICULUM_DATA;
            logSuccess('Curriculum data loaded from window.CURRICULUM_DATA');
            return true;
        }
        
        // Method 3: Create fallback structure
        logWarning('No curriculum data found - creating fallback structure');
        curriculumData = {
            CORE: {
                subprograms: {
                    'Phonics': { levels: [{id: '1', number: 1}, {id: '2', number: 2}, {id: '3', number: 3}] },
                    'Sigma': { levels: [{id: '4', number: 1}, {id: '5', number: 2}, {id: '6', number: 3}] },
                    'Elite': { levels: [{id: '7', number: 1}, {id: '8', number: 2}, {id: '9', number: 3}] },
                    'Pro': { levels: [{id: '10', number: 1}, {id: '11', number: 2}, {id: '12', number: 3}] }
                }
            }
        };
        
        return true;
    }
    
    // ========================================================================
    // EXAM NAME PREVIEW GENERATION
    // ========================================================================
    
    function updateExamNamePreview() {
        log('🔄 Updating exam name preview...');
        
        try {
            // Get all form elements
            const elements = {
                examType: document.getElementById('copyExamType'),
                timeslot: document.getElementById('timeslot'),
                academicYear: document.getElementById('academicYear'),
                program: document.getElementById('copyProgramSelect'),
                subprogram: document.getElementById('copySubprogramSelect'),
                level: document.getElementById('copyLevelSelect'),
                customSuffix: document.getElementById('customSuffix'),
                previewText: document.getElementById('previewText')
            };
            
            // Log current form values
            log('Current form values:', {
                examType: elements.examType?.value || 'NOT SET',
                timeslot: elements.timeslot?.value || 'NOT SET',
                academicYear: elements.academicYear?.value || 'NOT SET',
                program: elements.program?.value || 'NOT SET',
                subprogram: elements.subprogram?.value || 'NOT SET',
                level: elements.level?.value || 'NOT SET',
                customSuffix: elements.customSuffix?.value || 'NOT SET'
            });
            
            if (!elements.previewText) {
                logError('Preview text element not found');
                return;
            }
            
            // Check if basic required fields are filled
            if (!elements.examType?.value || !elements.timeslot?.value) {
                const message = 'Please select exam type and time period to see preview...';
                elements.previewText.textContent = message;
                log('Preview incomplete - missing required fields');
                return;
            }
            
            // Build the exam name
            let nameParts = [];
            
            // Add exam type prefix
            if (elements.examType.value === 'QUARTERLY') {
                nameParts.push('[QTR]');
            } else if (elements.examType.value === 'REVIEW') {
                nameParts.push('[RVW]');
            }
            
            // Add time period
            const year = elements.academicYear?.value || new Date().getFullYear();
            if (elements.examType.value === 'QUARTERLY') {
                // For quarterly exams
                const quarterValue = elements.timeslot.value;
                nameParts.push(`${quarterValue} ${year}`);
            } else if (elements.examType.value === 'REVIEW') {
                // For review/monthly exams
                const selectedOption = elements.timeslot.options[elements.timeslot.selectedIndex];
                const monthText = selectedOption?.text || elements.timeslot.value;
                nameParts.push(`${monthText} ${year}`);
            }
            
            // Add curriculum information
            if (elements.program?.value && elements.subprogram?.value && elements.level?.value) {
                const program = elements.program.value;
                const subprogram = elements.subprogram.value;
                const levelOption = elements.level.options[elements.level.selectedIndex];
                const levelNumber = levelOption?.text?.replace('Level ', '') || '?';
                const curriculum = `${program} ${subprogram} Lv${levelNumber}`;
                nameParts.push(curriculum);
                log('Using selected curriculum:', curriculum);
            } else {
                // Try to extract from source exam name
                const sourceExamName = document.getElementById('sourceExamName')?.textContent || '';
                if (sourceExamName && sourceExamName !== 'Loading...') {
                    const curriculumMatch = sourceExamName.match(/(CORE|ASCENT|EDGE|PINNACLE)\s+(\w+)\s+Lv(\d+)/);
                    if (curriculumMatch) {
                        const curriculum = `${curriculumMatch[1]} ${curriculumMatch[2]} Lv${curriculumMatch[3]}`;
                        nameParts.push(curriculum);
                        log('Using source exam curriculum:', curriculum);
                    }
                }
            }
            
            // Join parts
            let previewName = nameParts.join(' - ');
            
            // Add custom suffix if provided
            const customSuffix = elements.customSuffix?.value?.trim();
            if (customSuffix) {
                previewName += customSuffix.startsWith('_') ? customSuffix : `_${customSuffix}`;
            }
            
            // Update the preview
            elements.previewText.textContent = previewName;
            logSuccess(`Preview updated: "${previewName}"`);
            
        } catch (error) {
            logError('Failed to update exam name preview', error);
        }
    }
    
    // ========================================================================
    // DROPDOWN MANAGEMENT
    // ========================================================================
    
    function updateTimeslotDropdown(examType) {
        log(`Updating timeslot dropdown for exam type: ${examType}`);
        
        const timeslotSelect = document.getElementById('timeslot');
        if (!timeslotSelect) {
            logError('Timeslot select element not found');
            return;
        }
        
        // Clear existing options
        timeslotSelect.innerHTML = '<option value="">Select time period...</option>';
        
        if (examType === 'REVIEW') {
            // Monthly timeslots
            const months = [
                {value: 'JAN', text: 'January'},
                {value: 'FEB', text: 'February'},
                {value: 'MAR', text: 'March'},
                {value: 'APR', text: 'April'},
                {value: 'MAY', text: 'May'},
                {value: 'JUN', text: 'June'},
                {value: 'JUL', text: 'July'},
                {value: 'AUG', text: 'August'},
                {value: 'SEP', text: 'September'},
                {value: 'OCT', text: 'October'},
                {value: 'NOV', text: 'November'},
                {value: 'DEC', text: 'December'}
            ];
            
            months.forEach(month => {
                const option = document.createElement('option');
                option.value = month.value;
                option.textContent = month.text;
                timeslotSelect.appendChild(option);
            });
            
            timeslotSelect.disabled = false;
            logSuccess('Monthly timeslots loaded');
            
        } else if (examType === 'QUARTERLY') {
            // Quarterly timeslots
            const quarters = [
                {value: 'Q1', text: 'Q1 (Jan-Mar)'},
                {value: 'Q2', text: 'Q2 (Apr-Jun)'},
                {value: 'Q3', text: 'Q3 (Jul-Sep)'},
                {value: 'Q4', text: 'Q4 (Oct-Dec)'}
            ];
            
            quarters.forEach(quarter => {
                const option = document.createElement('option');
                option.value = quarter.value;
                option.textContent = quarter.text;
                timeslotSelect.appendChild(option);
            });
            
            timeslotSelect.disabled = false;
            logSuccess('Quarterly timeslots loaded');
            
        } else {
            timeslotSelect.disabled = true;
            log('Timeslot dropdown disabled - no exam type selected');
        }
    }
    
    function initializeProgramDropdown() {
        log('Initializing program dropdown...');
        
        const programSelect = document.getElementById('copyProgramSelect');
        if (!programSelect || !curriculumData) {
            logError('Cannot initialize program dropdown', {
                programSelect: !!programSelect,
                curriculumData: !!curriculumData
            });
            return;
        }
        
        // Clear and populate
        programSelect.innerHTML = '<option value="">-- Select Program --</option>';
        
        const programs = Object.keys(curriculumData);
        programs.forEach(program => {
            const option = document.createElement('option');
            option.value = program;
            option.textContent = program;
            programSelect.appendChild(option);
        });
        
        logSuccess(`Program dropdown initialized with ${programs.length} programs`);
    }
    
    function updateSubprogramDropdown() {
        log('Updating subprogram dropdown...');
        
        const programSelect = document.getElementById('copyProgramSelect');
        const subprogramSelect = document.getElementById('copySubprogramSelect');
        const levelSelect = document.getElementById('copyLevelSelect');
        
        if (!subprogramSelect) return;
        
        // Reset subprogram and level
        subprogramSelect.innerHTML = '<option value="">-- Select SubProgram --</option>';
        levelSelect.innerHTML = '<option value="">-- First select a SubProgram --</option>';
        levelSelect.disabled = true;
        
        const selectedProgram = programSelect?.value;
        if (!selectedProgram || !curriculumData[selectedProgram]) {
            subprogramSelect.disabled = true;
            log('No program selected or program data not found');
            return;
        }
        
        const programData = curriculumData[selectedProgram];
        const subprograms = programData.subprograms || {};
        
        Object.keys(subprograms).forEach(subprogramName => {
            const option = document.createElement('option');
            option.value = subprogramName;
            option.textContent = subprogramName;
            subprogramSelect.appendChild(option);
        });
        
        subprogramSelect.disabled = false;
        logSuccess(`Subprogram dropdown updated with ${Object.keys(subprograms).length} subprograms`);
    }
    
    function updateLevelDropdown() {
        log('Updating level dropdown...');
        
        const programSelect = document.getElementById('copyProgramSelect');
        const subprogramSelect = document.getElementById('copySubprogramSelect');
        const levelSelect = document.getElementById('copyLevelSelect');
        const curriculumLevelInput = document.getElementById('copyCurriculumLevel');
        
        if (!levelSelect) return;
        
        // Reset level
        levelSelect.innerHTML = '<option value="">-- Select Level --</option>';
        
        const selectedProgram = programSelect?.value;
        const selectedSubprogram = subprogramSelect?.value;
        
        if (!selectedProgram || !selectedSubprogram) {
            levelSelect.disabled = true;
            log('Program or subprogram not selected');
            return;
        }
        
        const subprogramData = curriculumData[selectedProgram]?.subprograms?.[selectedSubprogram];
        if (!subprogramData?.levels) {
            levelSelect.disabled = true;
            logWarning('No levels found for selected subprogram');
            return;
        }
        
        subprogramData.levels.forEach(level => {
            const option = document.createElement('option');
            option.value = level.id;
            option.textContent = `Level ${level.number}`;
            levelSelect.appendChild(option);
        });
        
        levelSelect.disabled = false;
        logSuccess(`Level dropdown updated with ${subprogramData.levels.length} levels`);
    }
    
    // ========================================================================
    // EVENT HANDLERS
    // ========================================================================
    
    function attachEventListeners() {
        if (eventListenersAttached) {
            logWarning('Event listeners already attached - skipping');
            return;
        }
        
        log('Attaching event listeners...');
        
        // Exam type change
        const examTypeSelect = document.getElementById('copyExamType');
        if (examTypeSelect) {
            examTypeSelect.addEventListener('change', function() {
                log(`Exam type changed to: ${this.value}`);
                updateTimeslotDropdown(this.value);
                updateExamNamePreview();
            });
            logSuccess('Exam type listener attached');
        }
        
        // Timeslot change
        const timeslotSelect = document.getElementById('timeslot');
        if (timeslotSelect) {
            timeslotSelect.addEventListener('change', function() {
                log(`Timeslot changed to: ${this.value}`);
                updateExamNamePreview();
            });
            logSuccess('Timeslot listener attached');
        }
        
        // Academic year change
        const academicYearSelect = document.getElementById('academicYear');
        if (academicYearSelect) {
            academicYearSelect.addEventListener('change', function() {
                log(`Academic year changed to: ${this.value}`);
                updateExamNamePreview();
            });
            logSuccess('Academic year listener attached');
        }
        
        // Program change
        const programSelect = document.getElementById('copyProgramSelect');
        if (programSelect) {
            programSelect.addEventListener('change', function() {
                log(`Program changed to: ${this.value}`);
                updateSubprogramDropdown();
                updateExamNamePreview();
            });
            logSuccess('Program listener attached');
        }
        
        // Subprogram change
        const subprogramSelect = document.getElementById('copySubprogramSelect');
        if (subprogramSelect) {
            subprogramSelect.addEventListener('change', function() {
                log(`Subprogram changed to: ${this.value}`);
                updateLevelDropdown();
                updateExamNamePreview();
            });
            logSuccess('Subprogram listener attached');
        }
        
        // Level change
        const levelSelect = document.getElementById('copyLevelSelect');
        if (levelSelect) {
            levelSelect.addEventListener('change', function() {
                log(`Level changed to: ${this.value}`);
                // Store the curriculum level ID
                const curriculumLevelInput = document.getElementById('copyCurriculumLevel');
                if (curriculumLevelInput) {
                    curriculumLevelInput.value = this.value;
                }
                updateExamNamePreview();
            });
            logSuccess('Level listener attached');
        }
        
        // Custom suffix change
        const customSuffixInput = document.getElementById('customSuffix');
        if (customSuffixInput) {
            customSuffixInput.addEventListener('input', function() {
                log(`Custom suffix changed to: ${this.value}`);
                updateExamNamePreview();
            });
            logSuccess('Custom suffix listener attached');
        }
        
        // Form submission
        const form = document.getElementById('copyExamForm');
        if (form) {
            form.addEventListener('submit', handleFormSubmit);
            logSuccess('Form submit listener attached');
        }
        
        eventListenersAttached = true;
        logSuccess('All event listeners attached successfully');
    }
    
    function handleFormSubmit(e) {
        e.preventDefault();
        log('Form submission initiated');
        
        const formData = new FormData(e.target);
        const data = {
            source_exam_id: formData.get('source_exam_id'),
            target_class: formData.get('target_class'),
            target_timeslot: formData.get('timeslot'),
            curriculum_level_id: formData.get('curriculum_level') || formData.get('level_select'),
            custom_suffix: formData.get('custom_suffix'),
            exam_type: formData.get('exam_type'),
            academic_year: formData.get('academic_year')
        };
        
        log('Form data to submit:', data);
        
        // Validate required fields
        if (!data.source_exam_id || !data.target_class || !data.target_timeslot) {
            alert('Please fill in all required fields');
            return;
        }
        
        // Submit via AJAX
        submitCopyExamRequest(data);
    }
    
    function submitCopyExamRequest(data) {
        log('Submitting copy exam request...', data);
        
        fetch('/RoutineTest/exams/copy/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                logSuccess('Exam copied successfully', result);
                alert(`Exam copied successfully!\nNew exam: ${result.new_exam_name}`);
                closeCopyModal();
                // Reload the page to show the new exam
                window.location.reload();
            } else {
                logError('Copy failed', result);
                alert(`Failed to copy exam: ${result.error || 'Unknown error'}`);
            }
        })
        .catch(error => {
            logError('Request failed', error);
            alert('Failed to copy exam. Please try again.');
        });
    }
    
    // ========================================================================
    // MODAL MANAGEMENT
    // ========================================================================
    
    function openCopyModal(examId, examName) {
        log(`Opening copy modal for exam: ${examName} (${examId})`);
        
        // Store exam info
        currentExamInfo = {
            id: examId,
            name: examName
        };
        
        // Get modal element
        const modal = document.getElementById('copyExamModal');
        if (!modal) {
            logError('Modal element not found');
            alert('Copy modal not found. Please refresh the page.');
            return;
        }
        
        // Set source exam info
        const sourceExamIdField = document.getElementById('sourceExamId');
        const sourceExamNameField = document.getElementById('sourceExamName');
        
        if (sourceExamIdField) sourceExamIdField.value = examId;
        if (sourceExamNameField) sourceExamNameField.textContent = examName;
        
        // Initialize dropdowns
        initializeProgramDropdown();
        
        // Show modal
        modal.style.display = 'block';
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
        
        // Trigger initial preview update
        updateExamNamePreview();
        
        logSuccess('Modal opened successfully');
        logDebugState();
    }
    
    function closeCopyModal() {
        log('Closing copy modal');
        
        const modal = document.getElementById('copyExamModal');
        if (modal) {
            modal.style.display = 'none';
            modal.classList.remove('show');
            document.body.style.overflow = '';
        }
        
        // Reset form
        const form = document.getElementById('copyExamForm');
        if (form) {
            form.reset();
        }
        
        // Clear current exam info
        currentExamInfo = null;
        
        logSuccess('Modal closed');
    }
    
    // ========================================================================
    // UTILITY FUNCTIONS
    // ========================================================================
    
    function getCsrfToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        if (!token) {
            logError('CSRF token not found');
        }
        return token || '';
    }
    
    // ========================================================================
    // INITIALIZATION
    // ========================================================================
    
    function initialize() {
        console.group(`[${MODULE_NAME}] INITIALIZATION`);
        log('=====================================');
        log('INITIALIZING COPY EXAM MODULE');
        log('=====================================');
        
        try {
            // Check if already initialized
            if (isInitialized) {
                logWarning('Module already initialized - skipping');
                console.groupEnd();
                return true;
            }
            
            // Load curriculum data
            if (!loadCurriculumData()) {
                logError('Failed to load curriculum data');
                console.groupEnd();
                return false;
            }
            
            // Attach event listeners
            attachEventListeners();
            
            // Attach modal close handlers
            const closeBtn = document.querySelector('#copyExamModal .modal-close');
            if (closeBtn) {
                closeBtn.addEventListener('click', closeCopyModal);
            }
            
            const modal = document.getElementById('copyExamModal');
            if (modal) {
                modal.addEventListener('click', function(e) {
                    if (e.target === modal) {
                        closeCopyModal();
                    }
                });
            }
            
            // Mark as initialized
            isInitialized = true;
            
            // Expose functions globally
            window.openCopyModal = openCopyModal;
            window.closeCopyModal = closeCopyModal;
            window.updateCopyExamNamePreview = updateExamNamePreview;
            window.debugCopyModal = logDebugState;
            
            logSuccess('INITIALIZATION COMPLETE');
            log('Global functions exposed:', [
                'openCopyModal(examId, examName)',
                'closeCopyModal()',
                'updateCopyExamNamePreview()',
                'debugCopyModal()'
            ]);
            
            console.groupEnd();
            return true;
            
        } catch (error) {
            logError('Initialization failed', error);
            console.groupEnd();
            return false;
        }
    }
    
    // ========================================================================
    // AUTO-INITIALIZATION
    // ========================================================================
    
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initialize);
        log('Waiting for DOM to load...');
    } else {
        // DOM is already ready
        initialize();
    }
    
})();

// ========================================================================
// GLOBAL DEBUG HELPER
// ========================================================================

window.copyModalDebug = function() {
    console.group('[COPY_MODAL_DEBUG]');
    
    // Check if functions are available
    console.log('Global functions:');
    console.log('  openCopyModal:', typeof window.openCopyModal);
    console.log('  closeCopyModal:', typeof window.closeCopyModal);
    console.log('  updateCopyExamNamePreview:', typeof window.updateCopyExamNamePreview);
    
    // Check DOM elements
    console.log('\nDOM Elements:');
    const elements = [
        'copyExamModal', 'copyExamForm', 'copyExamType', 'timeslot',
        'copyProgramSelect', 'copySubprogramSelect', 'copyLevelSelect',
        'customSuffix', 'previewText', 'sourceExamId', 'sourceExamName'
    ];
    
    elements.forEach(id => {
        const el = document.getElementById(id);
        console.log(`  #${id}:`, el ? '✅ Found' : '❌ Not found');
    });
    
    // Test preview update
    console.log('\nTesting preview update...');
    if (typeof window.updateCopyExamNamePreview === 'function') {
        window.updateCopyExamNamePreview();
        console.log('Preview update called');
    } else {
        console.log('Preview update function not available');
    }
    
    console.groupEnd();
};

console.log('[COPY_EXAM_COMPLETE] Module loaded. Use copyModalDebug() to check status.');