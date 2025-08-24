/**
 * Copy Exam Modal - Comprehensive Final Implementation
 * Version: FINAL - Clean implementation to replace all previous versions
 * Date: 2025-08-24
 * 
 * This file provides complete copy exam functionality with proper error handling
 * and dropdown population.
 */

(function() {
    'use strict';
    
    const MODULE_NAME = 'COPY_EXAM_COMPREHENSIVE_FINAL';
    let isInitialized = false;
    let curriculumData = null;
    let currentExamInfo = null;
    
    // Utility functions for logging
    function log(message, data = null, level = 'info') {
        const timestamp = new Date().toISOString();
        const prefix = `[${MODULE_NAME}]`;
        
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
    
    // Load curriculum data from multiple possible sources
    function loadCurriculumData() {
        log('Loading curriculum data...');
        
        // Method 1: From JSON script element  
        const scriptElement = document.getElementById('copy-curriculum-hierarchy-data');
        if (scriptElement) {
            try {
                const rawData = JSON.parse(scriptElement.textContent);
                log('Raw data from script element:', rawData);
                
                // Extract curriculum data from wrapper if needed
                if (rawData.curriculum_data) {
                    curriculumData = rawData.curriculum_data;
                } else if (rawData.CORE || rawData.ASCENT || rawData.EDGE || rawData.PINNACLE) {
                    curriculumData = rawData;
                } else {
                    logError('Unknown data structure in script element');
                    return false;
                }
                
                logSuccess('Curriculum data loaded from script element');
                return validateCurriculumData();
            } catch (error) {
                logError('Failed to parse curriculum data from script element:', error);
            }
        }
        
        // Method 2: From window object (fallback)
        if (window.CURRICULUM_DATA) {
            log('Using curriculum data from window.CURRICULUM_DATA');
            curriculumData = window.CURRICULUM_DATA;
            return validateCurriculumData();
        }
        
        // Method 3: Create basic fallback structure
        logError('No curriculum data found - creating fallback');
        curriculumData = {
            CORE: {
                subprograms: {
                    'Phonics': { levels: [{id: '1', number: 1}, {id: '2', number: 2}, {id: '3', number: 3}] },
                    'Sigma': { levels: [{id: '4', number: 1}, {id: '5', number: 2}, {id: '6', number: 3}] }
                }
            },
            ASCENT: {
                subprograms: {
                    'Nova': { levels: [{id: '7', number: 1}, {id: '8', number: 2}, {id: '9', number: 3}] }
                }
            }
        };
        
        return true;
    }
    
    function validateCurriculumData() {
        if (!curriculumData || typeof curriculumData !== 'object') {
            logError('Invalid curriculum data structure');
            return false;
        }
        
        const expectedPrograms = ['CORE', 'ASCENT', 'EDGE', 'PINNACLE'];
        const availablePrograms = Object.keys(curriculumData);
        
        log('Available programs:', availablePrograms);
        
        if (availablePrograms.length === 0) {
            logError('No programs found in curriculum data');
            return false;
        }
        
        logSuccess('Curriculum data validation passed');
        return true;
    }
    
    // Dropdown population functions
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
            logError('No curriculum data available for dropdown population');
            return false;
        }
        
        const programs = Object.keys(curriculumData);
        log(`Adding ${programs.length} programs to dropdown:`, programs);
        
        programs.forEach(program => {
            const option = document.createElement('option');
            option.value = program;
            option.textContent = program;
            programSelect.appendChild(option);
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
            logError('No subprograms found for program:', selectedProgram);
            return false;
        }
        
        subprogramNames.forEach(subprogram => {
            const option = document.createElement('option');
            option.value = subprogram;
            option.textContent = subprogram;
            subprogramSelect.appendChild(option);
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
            logError('No levels found for subprogram:', selectedSubprogram);
            return false;
        }
        
        levels.forEach(level => {
            const option = document.createElement('option');
            option.value = level.id;
            option.textContent = `Level ${level.number}`;
            levelSelect.appendChild(option);
        });
        
        levelSelect.disabled = false;
        logSuccess(`Level dropdown populated with ${levels.length} options`);
        return true;
    }
    
    // Event handlers
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
    
    // Modal management
    function openCopyModal(examId, examName) {
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
        modal.style.display = 'flex';
        modal.classList.add('show');
        document.body.style.overflow = 'hidden'; // Prevent background scrolling
        
        logSuccess('Copy modal opened successfully');
    }
    
    function closeCopyModal() {
        log('Closing copy modal');
        const modal = document.getElementById('copyExamModal');
        if (modal) {
            modal.style.display = 'none';
            modal.classList.remove('show');
            document.body.style.overflow = ''; // Restore scrolling
        }
        currentExamInfo = null;
    }
    
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
    
    // Form submission
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
            alert('Please fill in all required fields: ' + missingFields.join(', '));
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
            exam_type: formDataObj.exam_type,
            timeslot: formDataObj.timeslot,
            academic_year: formDataObj.academicYear,
            custom_suffix: formDataObj.customSuffix || ''
        };
        
        log('Submitting data:', submitData);
        
        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Copying...';
        submitBtn.disabled = true;
        
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
            if (data.success) {
                alert(`Exam copied successfully! New exam: ${data.new_exam_name || 'Created'}`);
                closeCopyModal();
                // Reload page to show new exam
                window.location.reload();
            } else {
                throw new Error(data.error || 'Copy failed');
            }
        })
        .catch(error => {
            logError('Copy failed:', error);
            alert(`Failed to copy exam: ${error.message}`);
        })
        .finally(() => {
            // Restore button state
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        });
    }
    
    // Attach event listeners
    function attachEventListeners() {
        log('Attaching event listeners...');
        
        // Program select
        const programSelect = document.getElementById('copyProgramSelect');
        if (programSelect) {
            programSelect.addEventListener('change', handleProgramChange);
            log('Attached listener to program select');
        }
        
        // Subprogram select
        const subprogramSelect = document.getElementById('copySubprogramSelect');
        if (subprogramSelect) {
            subprogramSelect.addEventListener('change', handleSubprogramChange);
            log('Attached listener to subprogram select');
        }
        
        // Level select
        const levelSelect = document.getElementById('copyLevelSelect');
        if (levelSelect) {
            levelSelect.addEventListener('change', handleLevelChange);
            log('Attached listener to level select');
        }
        
        // Form submit
        const form = document.getElementById('copyExamForm');
        if (form) {
            form.addEventListener('submit', handleFormSubmit);
            log('Attached listener to form submit');
        }
        
        // Modal close elements
        const closeBtn = document.querySelector('#copyExamModal .modal-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', closeCopyModal);
            log('Attached listener to close button');
        }
        
        // Click outside modal to close
        const modal = document.getElementById('copyExamModal');
        if (modal) {
            modal.addEventListener('click', function(e) {
                if (e.target === modal) {
                    closeCopyModal();
                }
            });
            log('Attached listener to modal backdrop');
        }
        
        logSuccess('All event listeners attached');
    }
    
    // Initialize the module
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
    
    // Document ready handler
    function documentReady() {
        log('Document ready - starting initialization');
        
        // Try to initialize
        if (!initialize()) {
            log('Initial initialization failed - will retry on first modal open');
        }
        
        // Replace placeholder functions with real implementations
        if (window.openCopyModal && window.openCopyModal.isPlaceholder) {
            log('Replacing placeholder openCopyModal with real implementation');
        }
        window.openCopyModal = openCopyModal;
        window.closeCopyModal = closeCopyModal;
        
        log('Copy Exam module ready - functions replaced');
    }
    
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', documentReady);
    } else {
        documentReady();
    }
    
})();