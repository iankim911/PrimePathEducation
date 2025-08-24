/**
 * Copy Exam Modal - Final Comprehensive Implementation
 * Version: FINAL - Complete rewrite with extensive debugging
 * Date: 2025-08-24
 * 
 * This is a complete rewrite of the copy exam functionality with:
 * - Extensive console logging for debugging
 * - Robust error handling
 * - Clear data flow
 * - No dependencies on external state
 */

(function() {
    'use strict';
    
    console.log('%c[COPY_EXAM_FINAL] Initializing Copy Exam Modal - FINAL VERSION', 'color: blue; font-weight: bold');
    
    // ============================================
    // GLOBAL STATE AND CONFIGURATION
    // ============================================
    const MODULE_NAME = 'COPY_EXAM_FINAL';
    let curriculumData = null;
    let currentExamInfo = null;
    let isInitialized = false;
    
    // ============================================
    // UTILITY FUNCTIONS
    // ============================================
    function log(message, data = null, level = 'info') {
        const timestamp = new Date().toISOString();
        const prefix = `[${MODULE_NAME}] [${timestamp}]`;
        
        if (data) {
            console[level](`${prefix} ${message}`, data);
        } else {
            console[level](`${prefix} ${message}`);
        }
    }
    
    function logError(message, error = null) {
        log(message, error, 'error');
    }
    
    function logSuccess(message, data = null) {
        console.log(`%c[${MODULE_NAME}] ✅ ${message}`, 'color: green; font-weight: bold', data || '');
    }
    
    function logWarning(message, data = null) {
        log(message, data, 'warn');
    }
    
    // ============================================
    // DATA LOADING AND VALIDATION
    // ============================================
    function loadCurriculumData() {
        log('Loading curriculum data from DOM...');
        
        try {
            // Method 1: Try to get from script element
            const scriptElement = document.getElementById('copy-curriculum-hierarchy-data');
            if (scriptElement) {
                log('Found curriculum data script element');
                const rawData = JSON.parse(scriptElement.textContent);
                log('Raw data structure:', {
                    type: typeof rawData,
                    keys: Object.keys(rawData),
                    hasMetadata: !!rawData.metadata,
                    hasCurriculumData: !!rawData.curriculum_data
                });
                
                // Extract the actual curriculum data
                if (rawData.curriculum_data) {
                    curriculumData = rawData.curriculum_data;
                    log('Extracted curriculum_data from wrapper');
                } else if (rawData.CORE || rawData.ASCENT || rawData.EDGE || rawData.PINNACLE) {
                    // Data is directly the curriculum structure
                    curriculumData = rawData;
                    log('Using raw data directly as curriculum');
                } else {
                    logError('Unknown data structure in script element');
                    return false;
                }
                
                // Validate structure
                const validation = validateCurriculumData(curriculumData);
                if (!validation.valid) {
                    logError('Curriculum data validation failed:', validation.errors);
                    return false;
                }
                
                logSuccess('Curriculum data loaded and validated', {
                    programs: Object.keys(curriculumData),
                    totalPrograms: Object.keys(curriculumData).length
                });
                return true;
            }
            
            // Method 2: Try to get from window object (fallback)
            if (window.CURRICULUM_DATA) {
                log('Using curriculum data from window.CURRICULUM_DATA');
                curriculumData = window.CURRICULUM_DATA;
                return true;
            }
            
            logError('No curriculum data found in DOM or window');
            return false;
            
        } catch (error) {
            logError('Failed to load curriculum data:', error);
            return false;
        }
    }
    
    function validateCurriculumData(data) {
        const errors = [];
        const expectedPrograms = ['CORE', 'ASCENT', 'EDGE', 'PINNACLE'];
        
        if (!data || typeof data !== 'object') {
            errors.push('Data is not an object');
            return { valid: false, errors };
        }
        
        for (const program of expectedPrograms) {
            if (!data[program]) {
                errors.push(`Missing program: ${program}`);
            } else {
                if (!data[program].subprograms) {
                    errors.push(`Program ${program} missing subprograms`);
                }
            }
        }
        
        if (errors.length > 0) {
            return { valid: false, errors };
        }
        
        // Log structure details
        for (const [program, programData] of Object.entries(data)) {
            const subprogramCount = Object.keys(programData.subprograms || {}).length;
            log(`Program ${program}: ${subprogramCount} subprograms`);
        }
        
        return { valid: true, errors: [] };
    }
    
    // ============================================
    // DROPDOWN POPULATION FUNCTIONS
    // ============================================
    function populateProgramDropdown() {
        log('Populating program dropdown...');
        
        const programSelect = document.getElementById('copyProgramSelect');
        if (!programSelect) {
            logError('Program select element not found');
            return false;
        }
        
        // Clear existing options
        programSelect.innerHTML = '<option value="">-- Select Program --</option>';
        
        if (!curriculumData) {
            logError('No curriculum data available');
            return false;
        }
        
        const programs = Object.keys(curriculumData);
        log(`Adding ${programs.length} programs to dropdown:`, programs);
        
        programs.forEach(program => {
            const option = document.createElement('option');
            option.value = program;
            option.textContent = program;
            programSelect.appendChild(option);
            log(`Added program option: ${program}`);
        });
        
        logSuccess(`Program dropdown populated with ${programs.length} options`);
        return true;
    }
    
    function populateSubprogramDropdown(selectedProgram) {
        log(`Populating subprogram dropdown for program: ${selectedProgram}`);
        
        const subprogramSelect = document.getElementById('copySubprogramSelect');
        if (!subprogramSelect) {
            logError('Subprogram select element not found');
            return false;
        }
        
        // Clear and reset
        subprogramSelect.innerHTML = '<option value="">-- Select SubProgram --</option>';
        subprogramSelect.disabled = true;
        
        if (!selectedProgram || !curriculumData[selectedProgram]) {
            log('No program selected or invalid program');
            return false;
        }
        
        const subprograms = curriculumData[selectedProgram].subprograms || {};
        const subprogramNames = Object.keys(subprograms);
        
        log(`Found ${subprogramNames.length} subprograms:`, subprogramNames);
        
        if (subprogramNames.length === 0) {
            logWarning('No subprograms found for program:', selectedProgram);
            return false;
        }
        
        subprogramNames.forEach(subprogram => {
            const option = document.createElement('option');
            option.value = subprogram;
            option.textContent = subprogram;
            subprogramSelect.appendChild(option);
            log(`Added subprogram option: ${subprogram}`);
        });
        
        subprogramSelect.disabled = false;
        logSuccess(`Subprogram dropdown populated with ${subprogramNames.length} options`);
        return true;
    }
    
    function populateLevelDropdown(selectedProgram, selectedSubprogram) {
        log(`Populating level dropdown for ${selectedProgram} -> ${selectedSubprogram}`);
        
        const levelSelect = document.getElementById('copyLevelSelect');
        if (!levelSelect) {
            logError('Level select element not found');
            return false;
        }
        
        // Clear and reset
        levelSelect.innerHTML = '<option value="">-- Select Level --</option>';
        levelSelect.disabled = true;
        
        if (!selectedProgram || !selectedSubprogram) {
            log('Program or subprogram not selected');
            return false;
        }
        
        const levels = curriculumData[selectedProgram]?.subprograms?.[selectedSubprogram]?.levels || [];
        
        log(`Found ${levels.length} levels:`, levels);
        
        if (levels.length === 0) {
            logWarning('No levels found for subprogram:', selectedSubprogram);
            return false;
        }
        
        levels.forEach(level => {
            const option = document.createElement('option');
            option.value = level.id;
            option.textContent = `Level ${level.number}`;
            option.dataset.levelNumber = level.number;
            levelSelect.appendChild(option);
            log(`Added level option: Level ${level.number} (ID: ${level.id})`);
        });
        
        levelSelect.disabled = false;
        logSuccess(`Level dropdown populated with ${levels.length} options`);
        return true;
    }
    
    // ============================================
    // EVENT HANDLERS
    // ============================================
    function handleProgramChange(event) {
        const selectedProgram = event.target.value;
        log(`Program changed to: ${selectedProgram}`);
        
        // Reset child dropdowns
        const subprogramSelect = document.getElementById('copySubprogramSelect');
        const levelSelect = document.getElementById('copyLevelSelect');
        const curriculumLevelInput = document.getElementById('copyCurriculumLevel');
        
        if (subprogramSelect) {
            subprogramSelect.innerHTML = '<option value="">-- Select SubProgram --</option>';
            subprogramSelect.disabled = !selectedProgram;
        }
        
        if (levelSelect) {
            levelSelect.innerHTML = '<option value="">-- Select Level --</option>';
            levelSelect.disabled = true;
        }
        
        if (curriculumLevelInput) {
            curriculumLevelInput.value = '';
        }
        
        // Populate subprograms if program selected
        if (selectedProgram) {
            populateSubprogramDropdown(selectedProgram);
        }
    }
    
    function handleSubprogramChange(event) {
        const selectedSubprogram = event.target.value;
        const programSelect = document.getElementById('copyProgramSelect');
        const selectedProgram = programSelect ? programSelect.value : '';
        
        log(`Subprogram changed to: ${selectedSubprogram} (Program: ${selectedProgram})`);
        
        // Reset level dropdown
        const levelSelect = document.getElementById('copyLevelSelect');
        const curriculumLevelInput = document.getElementById('copyCurriculumLevel');
        
        if (levelSelect) {
            levelSelect.innerHTML = '<option value="">-- Select Level --</option>';
            levelSelect.disabled = !selectedSubprogram;
        }
        
        if (curriculumLevelInput) {
            curriculumLevelInput.value = '';
        }
        
        // Populate levels if subprogram selected
        if (selectedProgram && selectedSubprogram) {
            populateLevelDropdown(selectedProgram, selectedSubprogram);
        }
    }
    
    function handleLevelChange(event) {
        const selectedLevelId = event.target.value;
        log(`Level changed to ID: ${selectedLevelId}`);
        
        // Update hidden curriculum level field
        const curriculumLevelInput = document.getElementById('copyCurriculumLevel');
        if (curriculumLevelInput) {
            curriculumLevelInput.value = selectedLevelId;
            log(`Set curriculum level ID to: ${selectedLevelId}`);
        }
    }
    
    // ============================================
    // MODAL MANAGEMENT
    // ============================================
    window.openCopyModal = function(examId, examName) {
        log('=====================================');
        log('OPENING COPY MODAL');
        log('=====================================');
        log(`Exam ID: ${examId}`);
        log(`Exam Name: ${examName}`);
        
        // Store current exam info
        currentExamInfo = { id: examId, name: examName };
        
        // Initialize if needed
        if (!isInitialized) {
            log('First time opening - initializing...');
            if (!initialize()) {
                alert('Failed to initialize copy modal. Please refresh the page and try again.');
                return;
            }
        }
        
        // Get modal element
        const modal = document.getElementById('copyExamModal');
        if (!modal) {
            logError('Modal element not found');
            alert('Copy modal not found. Please refresh the page.');
            return;
        }
        
        // Update modal with exam info
        const sourceExamId = document.getElementById('sourceExamId');
        const sourceExamName = document.getElementById('sourceExamName');
        
        if (sourceExamId) {
            sourceExamId.value = examId;
            log(`Set source exam ID: ${examId}`);
        }
        
        if (sourceExamName) {
            sourceExamName.textContent = examName || 'Unknown Exam';
            log(`Set source exam name: ${examName}`);
        }
        
        // Reset form
        resetCopyForm();
        
        // Populate program dropdown
        populateProgramDropdown();
        
        // Show modal
        modal.style.display = 'block';
        logSuccess('Copy modal opened successfully');
    };
    
    window.closeCopyModal = function() {
        log('Closing copy modal');
        const modal = document.getElementById('copyExamModal');
        if (modal) {
            modal.style.display = 'none';
        }
        currentExamInfo = null;
    };
    
    function resetCopyForm() {
        log('Resetting copy form...');
        
        const form = document.getElementById('copyExamForm');
        if (form) {
            form.reset();
        }
        
        // Reset dropdowns
        const subprogramSelect = document.getElementById('copySubprogramSelect');
        const levelSelect = document.getElementById('copyLevelSelect');
        
        if (subprogramSelect) {
            subprogramSelect.innerHTML = '<option value="">-- First select a Program --</option>';
            subprogramSelect.disabled = true;
        }
        
        if (levelSelect) {
            levelSelect.innerHTML = '<option value="">-- First select a SubProgram --</option>';
            levelSelect.disabled = true;
        }
        
        log('Form reset complete');
    }
    
    // ============================================
    // FORM SUBMISSION
    // ============================================
    function handleFormSubmit(event) {
        event.preventDefault();
        log('=====================================');
        log('FORM SUBMISSION');
        log('=====================================');
        
        const form = event.target;
        const formData = new FormData(form);
        
        // Log all form data
        const formDataObj = {};
        for (let [key, value] of formData.entries()) {
            formDataObj[key] = value;
        }
        log('Form data:', formDataObj);
        
        // Validate required fields
        const requiredFields = ['source_exam_id', 'curriculum_level'];
        const missingFields = requiredFields.filter(field => !formDataObj[field]);
        
        if (missingFields.length > 0) {
            logError('Missing required fields:', missingFields);
            alert('Please fill in all required fields');
            return;
        }
        
        // Get CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        if (!csrfToken) {
            logError('CSRF token not found');
            alert('Security token missing. Please refresh the page.');
            return;
        }
        
        // Prepare submission data
        const submitData = {
            source_exam_id: formDataObj.source_exam_id,
            curriculum_level_id: formDataObj.curriculum_level,
            custom_suffix: formDataObj.custom_suffix || ''
        };
        
        log('Submitting data:', submitData);
        
        // Submit via AJAX
        fetch('/RoutineTest/exams/copy/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(submitData)
        })
        .then(response => {
            log(`Response status: ${response.status}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            logSuccess('Copy successful!', data);
            alert(`Exam copied successfully! New exam: ${data.new_exam_name || 'Created'}`);
            closeCopyModal();
            // Reload page to show new exam
            window.location.reload();
        })
        .catch(error => {
            logError('Copy failed:', error);
            alert(`Failed to copy exam: ${error.message}`);
        });
    }
    
    // ============================================
    // INITIALIZATION
    // ============================================
    function attachEventListeners() {
        log('Attaching event listeners...');
        
        // Program select
        const programSelect = document.getElementById('copyProgramSelect');
        if (programSelect) {
            programSelect.removeEventListener('change', handleProgramChange);
            programSelect.addEventListener('change', handleProgramChange);
            log('Attached listener to program select');
        }
        
        // Subprogram select
        const subprogramSelect = document.getElementById('copySubprogramSelect');
        if (subprogramSelect) {
            subprogramSelect.removeEventListener('change', handleSubprogramChange);
            subprogramSelect.addEventListener('change', handleSubprogramChange);
            log('Attached listener to subprogram select');
        }
        
        // Level select
        const levelSelect = document.getElementById('copyLevelSelect');
        if (levelSelect) {
            levelSelect.removeEventListener('change', handleLevelChange);
            levelSelect.addEventListener('change', handleLevelChange);
            log('Attached listener to level select');
        }
        
        // Form submit
        const form = document.getElementById('copyExamForm');
        if (form) {
            form.removeEventListener('submit', handleFormSubmit);
            form.addEventListener('submit', handleFormSubmit);
            log('Attached listener to form submit');
        }
        
        // Modal close button
        const closeBtn = document.querySelector('#copyExamModal .close');
        if (closeBtn) {
            closeBtn.removeEventListener('click', closeCopyModal);
            closeBtn.addEventListener('click', closeCopyModal);
            log('Attached listener to close button');
        }
        
        logSuccess('All event listeners attached');
    }
    
    function initialize() {
        log('=====================================');
        log('INITIALIZING COPY EXAM MODULE');
        log('=====================================');
        
        try {
            // Load curriculum data
            if (!loadCurriculumData()) {
                logError('Failed to load curriculum data');
                return false;
            }
            
            // Attach event listeners
            attachEventListeners();
            
            // Mark as initialized
            isInitialized = true;
            
            logSuccess('INITIALIZATION COMPLETE');
            
            // Log summary
            log('Summary:', {
                curriculumLoaded: !!curriculumData,
                programs: curriculumData ? Object.keys(curriculumData) : [],
                modalFound: !!document.getElementById('copyExamModal'),
                formFound: !!document.getElementById('copyExamForm')
            });
            
            return true;
            
        } catch (error) {
            logError('Initialization failed:', error);
            return false;
        }
    }
    
    // ============================================
    // DOCUMENT READY
    // ============================================
    function documentReady() {
        log('Document ready - starting initialization');
        
        // Try to initialize
        if (!initialize()) {
            logWarning('Initial initialization failed - will retry on first modal open');
        }
        
        // Make functions globally available
        window.openCopyModal = window.openCopyModal || openCopyModal;
        window.closeCopyModal = window.closeCopyModal || closeCopyModal;
        
        log('Copy Exam module ready');
    }
    
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', documentReady);
    } else {
        documentReady();
    }
    
})();