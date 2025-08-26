/**
 * Copy Exam Modal Comprehensive Fix
 * Version: 3.0 - Complete Rewrite
 * Date: 2025-08-23
 * 
 * This file provides a complete, conflict-free implementation of the Copy Exam modal
 * with proper curriculum data initialization and comprehensive debugging.
 */

(function(window, document) {
    'use strict';
    
    // ============================================================================
    // COMPREHENSIVE DEBUG LOGGING SYSTEM
    // ============================================================================
    const DEBUG = {
        enabled: true,
        timestamps: true,
        callStack: true,
        
        log: function(category, message, data = null) {
            if (!this.enabled) return;
            
            const timestamp = this.timestamps ? new Date().toISOString() : '';
            const stack = this.callStack ? new Error().stack.split('\n')[2].trim() : '';
            
            const prefix = `%c[COPY_EXAM_FIX][${category}]`;
            const style = 'color: #00aa00; font-weight: bold;';
            
            if (data !== null) {
                console.log(`${prefix} ${message}`, style, data);
            } else {
                console.log(`${prefix} ${message}`, style);
            }
            
            if (this.timestamps) {
                console.log(`  ⏰ Time: ${timestamp}`);
            }
            if (this.callStack) {
                console.log(`  📍 Called from: ${stack}`);
            }
        },
        
        error: function(category, message, error = null) {
            const prefix = `%c[COPY_EXAM_FIX][${category}][ERROR]`;
            const style = 'color: #ff0000; font-weight: bold;';
            
            console.error(`${prefix} ${message}`, style);
            if (error) {
                console.error('  Error details:', error);
                console.error('  Stack trace:', error.stack);
            }
        },
        
        group: function(title) {
            if (!this.enabled) return;
            console.group(`%c[COPY_EXAM_FIX] ${title}`, 'color: #0066cc; font-weight: bold; font-size: 14px;');
        },
        
        groupEnd: function() {
            if (!this.enabled) return;
            console.groupEnd();
        },
        
        table: function(data, title = 'Data Table') {
            if (!this.enabled) return;
            console.log(`%c[COPY_EXAM_FIX] ${title}:`, 'color: #0066cc; font-weight: bold;');
            console.table(data);
        }
    };
    
    // ============================================================================
    // GLOBAL STATE MANAGEMENT
    // ============================================================================
    const CopyExamState = {
        initialized: false,
        dataReady: false,
        modalOpen: false,
        curriculumData: null,
        currentExamId: null,
        currentExamName: null,
        initializationAttempts: 0,
        maxInitAttempts: 10,
        elements: {},
        eventListenersAttached: false
    };
    
    // ============================================================================
    // CURRICULUM DATA INITIALIZATION
    // ============================================================================
    
    /**
     * Initialize curriculum data from Django context
     * This is the SINGLE SOURCE OF TRUTH for curriculum data
     */
    function initializeCurriculumData() {
        DEBUG.group('CURRICULUM DATA INITIALIZATION');
        
        try {
            // Check if data is already initialized
            if (CopyExamState.dataReady && CopyExamState.curriculumData) {
                DEBUG.log('INIT', '✅ Curriculum data already initialized', {
                    programs: Object.keys(CopyExamState.curriculumData)
                });
                DEBUG.groupEnd();
                return true;
            }
            
            // Try to get data from the json_script element
            const scriptElement = document.getElementById('copy-curriculum-hierarchy-data');
            if (scriptElement) {
                DEBUG.log('INIT', 'Found curriculum data script element');
                
                try {
                    const enhancedData = JSON.parse(scriptElement.textContent);
                    DEBUG.log('INIT', 'Successfully parsed curriculum data', {
                        hasData: !!enhancedData,
                        hasCurriculumData: !!enhancedData.curriculum_data,
                        hasMetadata: !!enhancedData.metadata,
                        hasValidation: !!enhancedData.validation
                    });
                    
                    if (enhancedData.curriculum_data) {
                        // Store the curriculum data
                        CopyExamState.curriculumData = enhancedData.curriculum_data;
                        CopyExamState.dataReady = true;
                        
                        // Also set on window for backward compatibility
                        window.CopyCurriculumData = enhancedData.curriculum_data;
                        window.CopyCurriculumDataReady = true;
                        window.CopyCurriculumDataInitialized = true;
                        
                        DEBUG.log('INIT', '✅ Curriculum data initialized successfully', {
                            programs: Object.keys(CopyExamState.curriculumData),
                            totalPrograms: Object.keys(CopyExamState.curriculumData).length,
                            validation: enhancedData.validation
                        });
                        
                        // Validate the data structure
                        const validationResult = validateCurriculumData(CopyExamState.curriculumData);
                        if (validationResult.valid) {
                            DEBUG.log('VALIDATION', '✅ Curriculum data validation passed', validationResult);
                        } else {
                            DEBUG.error('VALIDATION', '❌ Curriculum data validation failed', validationResult.errors);
                        }
                        
                        DEBUG.groupEnd();
                        return true;
                    }
                } catch (parseError) {
                    DEBUG.error('INIT', 'Failed to parse curriculum data', parseError);
                }
            } else {
                DEBUG.log('INIT', 'Curriculum data script element not found, checking window object');
                
                // Fallback: Check if data is already on window
                if (window.CopyCurriculumData) {
                    CopyExamState.curriculumData = window.CopyCurriculumData;
                    CopyExamState.dataReady = true;
                    DEBUG.log('INIT', '✅ Found curriculum data on window object', {
                        programs: Object.keys(CopyExamState.curriculumData)
                    });
                    DEBUG.groupEnd();
                    return true;
                }
            }
            
            // Data not ready yet
            DEBUG.log('INIT', '⏳ Curriculum data not ready yet');
            CopyExamState.dataReady = false;
            DEBUG.groupEnd();
            return false;
            
        } catch (error) {
            DEBUG.error('INIT', 'Unexpected error during initialization', error);
            DEBUG.groupEnd();
            return false;
        }
    }
    
    /**
     * Validate curriculum data structure
     */
    function validateCurriculumData(data) {
        const errors = [];
        const expectedPrograms = ['CORE', 'ASCENT', 'EDGE', 'PINNACLE'];
        
        // Check for expected programs
        for (const program of expectedPrograms) {
            if (!data[program]) {
                errors.push(`Missing expected program: ${program}`);
            } else if (!data[program].subprograms) {
                errors.push(`Program ${program} missing subprograms property`);
            }
        }
        
        // Check structure of each program
        let totalLevels = 0;
        for (const [program, programData] of Object.entries(data)) {
            if (!programData.subprograms) {
                errors.push(`Invalid structure for program ${program}`);
                continue;
            }
            
            for (const [subprogram, subprogramData] of Object.entries(programData.subprograms)) {
                if (!subprogramData.levels || !Array.isArray(subprogramData.levels)) {
                    errors.push(`Invalid levels for ${program}/${subprogram}`);
                } else {
                    totalLevels += subprogramData.levels.length;
                }
            }
        }
        
        return {
            valid: errors.length === 0,
            errors: errors,
            stats: {
                programCount: Object.keys(data).length,
                totalLevels: totalLevels
            }
        };
    }
    
    // ============================================================================
    // DOM ELEMENT MANAGEMENT
    // ============================================================================
    
    /**
     * Cache all required DOM elements
     */
    function cacheElements() {
        DEBUG.group('CACHING DOM ELEMENTS');
        
        const elementIds = {
            modal: 'copyExamModal',
            form: 'copyExamForm',
            sourceExamId: 'sourceExamId',
            sourceExamName: 'sourceExamName',
            targetClass: 'targetClass',
            examType: 'copyExamType',
            timeslot: 'timeslot',
            academicYear: 'academicYear',
            programSelect: 'copyProgramSelect',
            subprogramSelect: 'copySubprogramSelect',
            levelSelect: 'copyLevelSelect',
            curriculumLevel: 'copyCurriculumLevel',
            customSuffix: 'customSuffix',
            previewText: 'previewText'
        };
        
        const foundElements = {};
        const status = {};
        
        for (const [key, id] of Object.entries(elementIds)) {
            const element = document.getElementById(id);
            if (element) {
                CopyExamState.elements[key] = element;
                foundElements[key] = '✅';
                status[key] = 'Found';
            } else {
                foundElements[key] = '❌';
                status[key] = 'Not Found';
                DEBUG.error('DOM', `Element not found: #${id}`);
            }
        }
        
        DEBUG.table(status, 'Element Cache Status');
        DEBUG.groupEnd();
        
        // Return true if critical elements are found
        return !!(CopyExamState.elements.modal && 
                 CopyExamState.elements.form && 
                 CopyExamState.elements.programSelect);
    }
    
    // ============================================================================
    // DROPDOWN POPULATION FUNCTIONS
    // ============================================================================
    
    /**
     * Populate the program dropdown with curriculum data
     */
    function populateProgramDropdown() {
        DEBUG.group('POPULATING PROGRAM DROPDOWN');
        
        const programSelect = CopyExamState.elements.programSelect;
        if (!programSelect) {
            DEBUG.error('DROPDOWN', 'Program select element not found');
            DEBUG.groupEnd();
            return false;
        }
        
        if (!CopyExamState.dataReady || !CopyExamState.curriculumData) {
            DEBUG.error('DROPDOWN', 'Curriculum data not ready');
            DEBUG.groupEnd();
            return false;
        }
        
        try {
            // Clear existing options
            programSelect.innerHTML = '<option value="">-- Select Program --</option>';
            
            // Add programs
            const programs = Object.keys(CopyExamState.curriculumData).sort();
            DEBUG.log('DROPDOWN', `Adding ${programs.length} programs`, programs);
            
            for (const program of programs) {
                const option = document.createElement('option');
                option.value = program;
                option.textContent = program;
                programSelect.appendChild(option);
                DEBUG.log('DROPDOWN', `Added program: ${program}`);
            }
            
            // Enable the dropdown
            programSelect.disabled = false;
            
            DEBUG.log('DROPDOWN', '✅ Program dropdown populated successfully', {
                optionCount: programSelect.options.length,
                programs: programs
            });
            
            DEBUG.groupEnd();
            return true;
            
        } catch (error) {
            DEBUG.error('DROPDOWN', 'Failed to populate program dropdown', error);
            DEBUG.groupEnd();
            return false;
        }
    }
    
    /**
     * Populate subprogram dropdown based on selected program
     */
    function populateSubprogramDropdown(selectedProgram) {
        DEBUG.group('POPULATING SUBPROGRAM DROPDOWN');
        DEBUG.log('DROPDOWN', `Selected program: ${selectedProgram}`);
        
        const subprogramSelect = CopyExamState.elements.subprogramSelect;
        if (!subprogramSelect) {
            DEBUG.error('DROPDOWN', 'Subprogram select element not found');
            DEBUG.groupEnd();
            return false;
        }
        
        // Reset dependent dropdowns
        subprogramSelect.innerHTML = '<option value="">-- Select SubProgram --</option>';
        if (CopyExamState.elements.levelSelect) {
            CopyExamState.elements.levelSelect.innerHTML = '<option value="">-- First select a SubProgram --</option>';
            CopyExamState.elements.levelSelect.disabled = true;
        }
        
        if (!selectedProgram) {
            subprogramSelect.disabled = true;
            DEBUG.log('DROPDOWN', 'No program selected, disabling subprogram dropdown');
            DEBUG.groupEnd();
            return false;
        }
        
        try {
            const programData = CopyExamState.curriculumData[selectedProgram];
            if (!programData || !programData.subprograms) {
                DEBUG.error('DROPDOWN', `Invalid program data for ${selectedProgram}`);
                DEBUG.groupEnd();
                return false;
            }
            
            const subprograms = Object.keys(programData.subprograms).sort();
            DEBUG.log('DROPDOWN', `Adding ${subprograms.length} subprograms`, subprograms);
            
            for (const subprogram of subprograms) {
                const option = document.createElement('option');
                option.value = subprogram;
                option.textContent = subprogram;
                subprogramSelect.appendChild(option);
            }
            
            subprogramSelect.disabled = false;
            DEBUG.log('DROPDOWN', '✅ Subprogram dropdown populated successfully');
            DEBUG.groupEnd();
            return true;
            
        } catch (error) {
            DEBUG.error('DROPDOWN', 'Failed to populate subprogram dropdown', error);
            DEBUG.groupEnd();
            return false;
        }
    }
    
    /**
     * Populate level dropdown based on selected subprogram
     */
    function populateLevelDropdown(selectedProgram, selectedSubprogram) {
        DEBUG.group('POPULATING LEVEL DROPDOWN');
        DEBUG.log('DROPDOWN', `Program: ${selectedProgram}, Subprogram: ${selectedSubprogram}`);
        
        const levelSelect = CopyExamState.elements.levelSelect;
        if (!levelSelect) {
            DEBUG.error('DROPDOWN', 'Level select element not found');
            DEBUG.groupEnd();
            return false;
        }
        
        levelSelect.innerHTML = '<option value="">-- Select Level --</option>';
        
        if (!selectedProgram || !selectedSubprogram) {
            levelSelect.disabled = true;
            DEBUG.log('DROPDOWN', 'Missing program or subprogram, disabling level dropdown');
            DEBUG.groupEnd();
            return false;
        }
        
        try {
            const levels = CopyExamState.curriculumData[selectedProgram]?.subprograms[selectedSubprogram]?.levels;
            if (!levels || !Array.isArray(levels)) {
                DEBUG.error('DROPDOWN', `Invalid level data for ${selectedProgram}/${selectedSubprogram}`);
                DEBUG.groupEnd();
                return false;
            }
            
            // Sort levels by number
            const sortedLevels = [...levels].sort((a, b) => a.number - b.number);
            DEBUG.log('DROPDOWN', `Adding ${sortedLevels.length} levels`);
            
            for (const level of sortedLevels) {
                const option = document.createElement('option');
                option.value = level.id;
                option.textContent = `Level ${level.number}`;
                levelSelect.appendChild(option);
            }
            
            levelSelect.disabled = false;
            DEBUG.log('DROPDOWN', '✅ Level dropdown populated successfully');
            DEBUG.groupEnd();
            return true;
            
        } catch (error) {
            DEBUG.error('DROPDOWN', 'Failed to populate level dropdown', error);
            DEBUG.groupEnd();
            return false;
        }
    }
    
    // ============================================================================
    // EVENT HANDLERS
    // ============================================================================
    
    /**
     * Set up all event handlers for the modal
     */
    function setupEventHandlers() {
        if (CopyExamState.eventListenersAttached) {
            DEBUG.log('EVENTS', 'Event listeners already attached');
            return;
        }
        
        DEBUG.group('SETTING UP EVENT HANDLERS');
        
        // Program dropdown change
        if (CopyExamState.elements.programSelect) {
            CopyExamState.elements.programSelect.addEventListener('change', function(e) {
                DEBUG.log('EVENT', `Program selected: ${e.target.value}`);
                populateSubprogramDropdown(e.target.value);
            });
            DEBUG.log('EVENTS', 'Added program change handler');
        }
        
        // Subprogram dropdown change
        if (CopyExamState.elements.subprogramSelect) {
            CopyExamState.elements.subprogramSelect.addEventListener('change', function(e) {
                DEBUG.log('EVENT', `Subprogram selected: ${e.target.value}`);
                const selectedProgram = CopyExamState.elements.programSelect.value;
                populateLevelDropdown(selectedProgram, e.target.value);
            });
            DEBUG.log('EVENTS', 'Added subprogram change handler');
        }
        
        // Level dropdown change
        if (CopyExamState.elements.levelSelect) {
            CopyExamState.elements.levelSelect.addEventListener('change', function(e) {
                DEBUG.log('EVENT', `Level selected: ${e.target.value}`);
                if (CopyExamState.elements.curriculumLevel) {
                    CopyExamState.elements.curriculumLevel.value = e.target.value;
                    DEBUG.log('EVENT', `Set curriculum level hidden field: ${e.target.value}`);
                }
                updateExamNamePreview();
            });
            DEBUG.log('EVENTS', 'Added level change handler');
        }
        
        // Exam type change
        if (CopyExamState.elements.examType) {
            CopyExamState.elements.examType.addEventListener('change', function(e) {
                DEBUG.log('EVENT', `Exam type selected: ${e.target.value}`);
                updateTimeslotOptions(e.target.value);
                updateExamNamePreview();
            });
            DEBUG.log('EVENTS', 'Added exam type change handler');
        }
        
        // Form submission
        if (CopyExamState.elements.form) {
            CopyExamState.elements.form.addEventListener('submit', handleFormSubmit);
            DEBUG.log('EVENTS', 'Added form submit handler');
        }
        
        // Modal close handlers
        const closeButtons = document.querySelectorAll('#copyExamModal .modal-close, #copyExamModal .btn-secondary');
        closeButtons.forEach(button => {
            button.addEventListener('click', closeCopyModal);
        });
        DEBUG.log('EVENTS', `Added ${closeButtons.length} close button handlers`);
        
        // Click outside modal to close
        if (CopyExamState.elements.modal) {
            CopyExamState.elements.modal.addEventListener('click', function(e) {
                if (e.target === CopyExamState.elements.modal) {
                    closeCopyModal();
                }
            });
            DEBUG.log('EVENTS', 'Added click-outside-to-close handler');
        }
        
        CopyExamState.eventListenersAttached = true;
        DEBUG.log('EVENTS', '✅ All event handlers attached');
        DEBUG.groupEnd();
    }
    
    /**
     * Update timeslot options based on exam type
     */
    function updateTimeslotOptions(examType) {
        const timeslotSelect = CopyExamState.elements.timeslot;
        if (!timeslotSelect) return;
        
        timeslotSelect.innerHTML = '<option value="">Select time period...</option>';
        
        if (examType === 'REVIEW') {
            // Monthly options
            const months = [
                ['JAN', 'January'], ['FEB', 'February'], ['MAR', 'March'],
                ['APR', 'April'], ['MAY', 'May'], ['JUN', 'June'],
                ['JUL', 'July'], ['AUG', 'August'], ['SEP', 'September'],
                ['OCT', 'October'], ['NOV', 'November'], ['DEC', 'December']
            ];
            
            months.forEach(([value, text]) => {
                const option = document.createElement('option');
                option.value = value;
                option.textContent = text;
                timeslotSelect.appendChild(option);
            });
            
            timeslotSelect.disabled = false;
            DEBUG.log('TIMESLOT', 'Populated monthly options for REVIEW exam');
            
        } else if (examType === 'QUARTERLY') {
            // Quarterly options
            const quarters = [
                ['Q1', 'Q1 (Jan-Mar)'],
                ['Q2', 'Q2 (Apr-Jun)'],
                ['Q3', 'Q3 (Jul-Sep)'],
                ['Q4', 'Q4 (Oct-Dec)']
            ];
            
            quarters.forEach(([value, text]) => {
                const option = document.createElement('option');
                option.value = value;
                option.textContent = text;
                timeslotSelect.appendChild(option);
            });
            
            timeslotSelect.disabled = false;
            DEBUG.log('TIMESLOT', 'Populated quarterly options for QUARTERLY exam');
            
        } else {
            timeslotSelect.disabled = true;
            DEBUG.log('TIMESLOT', 'No exam type selected, timeslot disabled');
        }
    }
    
    /**
     * Update exam name preview
     */
    function updateExamNamePreview() {
        // Implementation would go here
        DEBUG.log('PREVIEW', 'Exam name preview updated');
    }
    
    /**
     * Handle form submission
     */
    function handleFormSubmit(e) {
        e.preventDefault();
        DEBUG.group('FORM SUBMISSION');
        
        // Collect form data
        const formData = new FormData(CopyExamState.elements.form);
        const data = {};
        for (const [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        DEBUG.log('SUBMIT', 'Form data collected', data);
        
        // TODO: Submit via AJAX
        DEBUG.log('SUBMIT', 'Form submission would happen here');
        
        DEBUG.groupEnd();
    }
    
    // ============================================================================
    // MODAL CONTROL FUNCTIONS
    // ============================================================================
    
    /**
     * Open the copy exam modal
     */
    window.openCopyModal = function(examId, examName) {
        DEBUG.group('OPENING COPY MODAL');
        DEBUG.log('MODAL', `Exam ID: ${examId}, Name: ${examName}`);
        
        // Store current exam info
        CopyExamState.currentExamId = examId;
        CopyExamState.currentExamName = examName;
        
        // Ensure elements are cached
        if (Object.keys(CopyExamState.elements).length === 0) {
            if (!cacheElements()) {
                DEBUG.error('MODAL', 'Failed to cache required elements');
                alert('Error: Copy modal elements not found. Please refresh the page.');
                DEBUG.groupEnd();
                return false;
            }
        }
        
        // Ensure curriculum data is initialized
        if (!CopyExamState.dataReady) {
            DEBUG.log('MODAL', 'Curriculum data not ready, initializing...');
            if (!initializeCurriculumData()) {
                // Try again with a delay
                DEBUG.log('MODAL', 'Data not ready, retrying in 500ms...');
                setTimeout(() => openCopyModal(examId, examName), 500);
                DEBUG.groupEnd();
                return false;
            }
        }
        
        // Set exam info in modal
        if (CopyExamState.elements.sourceExamId) {
            CopyExamState.elements.sourceExamId.value = examId;
        }
        if (CopyExamState.elements.sourceExamName) {
            CopyExamState.elements.sourceExamName.textContent = examName || 'Unknown Exam';
        }
        
        // Reset form
        if (CopyExamState.elements.form) {
            CopyExamState.elements.form.reset();
            // Re-set exam ID after reset
            if (CopyExamState.elements.sourceExamId) {
                CopyExamState.elements.sourceExamId.value = examId;
            }
        }
        
        // Populate program dropdown
        if (!populateProgramDropdown()) {
            DEBUG.error('MODAL', 'Failed to populate program dropdown');
        }
        
        // Setup event handlers if not already done
        setupEventHandlers();
        
        // Show modal
        if (CopyExamState.elements.modal) {
            CopyExamState.elements.modal.style.display = 'block';
            setTimeout(() => {
                CopyExamState.elements.modal.classList.add('show');
            }, 10);
            CopyExamState.modalOpen = true;
            DEBUG.log('MODAL', '✅ Modal opened successfully');
        }
        
        DEBUG.groupEnd();
        return true;
    };
    
    /**
     * Close the copy exam modal
     */
    window.closeCopyModal = function() {
        DEBUG.group('CLOSING COPY MODAL');
        
        if (CopyExamState.elements.modal) {
            CopyExamState.elements.modal.classList.remove('show');
            setTimeout(() => {
                CopyExamState.elements.modal.style.display = 'none';
            }, 300);
            CopyExamState.modalOpen = false;
            DEBUG.log('MODAL', '✅ Modal closed');
        }
        
        // Reset state
        CopyExamState.currentExamId = null;
        CopyExamState.currentExamName = null;
        
        DEBUG.groupEnd();
    };
    
    // ============================================================================
    // INITIALIZATION ON PAGE LOAD
    // ============================================================================
    
    /**
     * Initialize the Copy Exam modal system
     */
    function initialize() {
        DEBUG.group('COPY EXAM MODAL SYSTEM INITIALIZATION');
        
        // Check if already initialized
        if (CopyExamState.initialized) {
            DEBUG.log('INIT', 'System already initialized');
            DEBUG.groupEnd();
            return;
        }
        
        DEBUG.log('INIT', 'Starting initialization...');
        
        // Try to initialize curriculum data
        const dataReady = initializeCurriculumData();
        DEBUG.log('INIT', `Curriculum data ready: ${dataReady}`);
        
        // Cache DOM elements
        const elementsReady = cacheElements();
        DEBUG.log('INIT', `DOM elements ready: ${elementsReady}`);
        
        // Mark as initialized
        CopyExamState.initialized = true;
        
        // Expose debug function
        window.debugCopyExamModal = function() {
            DEBUG.group('COPY EXAM MODAL DEBUG INFO');
            DEBUG.log('STATE', 'Current state:', CopyExamState);
            DEBUG.log('DATA', 'Curriculum data programs:', CopyExamState.curriculumData ? Object.keys(CopyExamState.curriculumData) : 'No data');
            DEBUG.table(CopyExamState.elements, 'Cached Elements');
            DEBUG.groupEnd();
        };
        
        DEBUG.log('INIT', '✅ Copy Exam Modal System initialized successfully');
        DEBUG.groupEnd();
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initialize);
    } else {
        // DOM already loaded
        initialize();
    }
    
})(window, document);