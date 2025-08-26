/**
 * Copy Exam Modal Fix V2
 * Version: 5.0 - More Robust Population
 * Date: 2025-08-23
 */

(function() {
    'use strict';
    
    console.log('[COPY_EXAM_FIX_V2] Initializing Copy Exam Modal Fix v5.0');
    
    // Global state
    const state = {
        initialized: false,
        curriculumData: null,
        currentExamId: null,
        currentExamName: null
    };
    
    // Initialize curriculum data from Django
    function initCurriculumData() {
        try {
            const scriptEl = document.getElementById('copy-curriculum-hierarchy-data');
            if (!scriptEl) {
                console.error('[COPY_EXAM_FIX_V2] Curriculum data script element not found');
                return false;
            }
            
            const data = JSON.parse(scriptEl.textContent);
            console.log('[COPY_EXAM_FIX_V2] Raw data loaded:', data);
            
            if (data && data.curriculum_data) {
                state.curriculumData = data.curriculum_data;
                console.log('[COPY_EXAM_FIX_V2] Curriculum data loaded from wrapper:', Object.keys(state.curriculumData));
            } else if (data && typeof data === 'object') {
                // Check if data itself has the structure we expect
                const firstKey = Object.keys(data)[0];
                if (firstKey && data[firstKey].subprograms) {
                    // Data is directly the curriculum structure
                    state.curriculumData = data;
                    console.log('[COPY_EXAM_FIX_V2] Curriculum data loaded directly:', Object.keys(state.curriculumData));
                } else {
                    console.error('[COPY_EXAM_FIX_V2] Unknown data structure:', data);
                    return false;
                }
            }
            
            // Validate structure
            if (state.curriculumData) {
                for (const program in state.curriculumData) {
                    console.log(`[COPY_EXAM_FIX_V2] Program ${program}:`, {
                        hasSubprograms: !!state.curriculumData[program].subprograms,
                        subprogramCount: Object.keys(state.curriculumData[program].subprograms || {}).length
                    });
                }
                return true;
            }
            
            console.error('[COPY_EXAM_FIX_V2] Invalid curriculum data structure');
            return false;
        } catch (e) {
            console.error('[COPY_EXAM_FIX_V2] Failed to parse curriculum data:', e);
            return false;
        }
    }
    
    // Open the copy modal
    window.openCopyModal = function(examId, examName) {
        console.log('[COPY_EXAM_FIX_V2] Opening modal for exam:', examId, examName);
        
        // Initialize curriculum data if needed
        if (!state.curriculumData) {
            if (!initCurriculumData()) {
                alert('Unable to load curriculum data. Please refresh the page and try again.');
                return;
            }
        }
        
        // Store exam info
        state.currentExamId = examId;
        state.currentExamName = examName;
        
        // Get modal element
        const modal = document.getElementById('copyExamModal');
        if (!modal) {
            console.error('[COPY_EXAM_FIX_V2] Modal element not found');
            alert('Copy modal not found. Please refresh the page.');
            return;
        }
        
        // Set exam info in modal
        const sourceExamId = document.getElementById('sourceExamId');
        const sourceExamName = document.getElementById('sourceExamName');
        
        if (sourceExamId) sourceExamId.value = examId;
        if (sourceExamName) sourceExamName.textContent = examName || 'Unknown Exam';
        
        // Reset form
        const form = document.getElementById('copyExamForm');
        if (form) {
            form.reset();
            // Re-set exam ID after reset
            if (sourceExamId) sourceExamId.value = examId;
        }
        
        // Populate program dropdown
        populateProgramDropdown();
        
        // Re-attach event handlers every time (in case DOM was recreated)
        setupEventHandlers();
        
        // Show modal
        modal.style.display = 'block';
        setTimeout(() => modal.classList.add('show'), 10);
        
        console.log('[COPY_EXAM_FIX_V2] Modal opened successfully');
    };
    
    // Close the copy modal
    window.closeCopyModal = function() {
        const modal = document.getElementById('copyExamModal');
        if (modal) {
            modal.classList.remove('show');
            setTimeout(() => modal.style.display = 'none', 300);
        }
    };
    
    // Populate program dropdown
    function populateProgramDropdown() {
        const programSelect = document.getElementById('copyProgramSelect');
        if (!programSelect) {
            console.error('[COPY_EXAM_FIX_V2] Program select element not found');
            return;
        }
        
        if (!state.curriculumData) {
            console.error('[COPY_EXAM_FIX_V2] No curriculum data available');
            return;
        }
        
        console.log('[COPY_EXAM_FIX_V2] Populating program dropdown');
        
        // Clear and add default option
        programSelect.innerHTML = '<option value="">-- Select Program --</option>';
        
        // Add programs
        const programs = Object.keys(state.curriculumData).sort();
        console.log('[COPY_EXAM_FIX_V2] Adding programs:', programs);
        
        programs.forEach(program => {
            const option = document.createElement('option');
            option.value = program;
            option.textContent = program;
            programSelect.appendChild(option);
        });
        
        // Clear dependent dropdowns
        clearSubprogramDropdown();
        clearLevelDropdown();
    }
    
    // Clear subprogram dropdown
    function clearSubprogramDropdown() {
        const subprogramSelect = document.getElementById('copySubprogramSelect');
        if (subprogramSelect) {
            subprogramSelect.innerHTML = '<option value="">-- First select a Program --</option>';
            subprogramSelect.disabled = true;
        }
    }
    
    // Clear level dropdown
    function clearLevelDropdown() {
        const levelSelect = document.getElementById('copyLevelSelect');
        if (levelSelect) {
            levelSelect.innerHTML = '<option value="">-- First select a SubProgram --</option>';
            levelSelect.disabled = true;
        }
    }
    
    // Populate subprogram dropdown
    function populateSubprogramDropdown(program) {
        console.log('[COPY_EXAM_FIX_V2] Populating subprogram for program:', program);
        
        const subprogramSelect = document.getElementById('copySubprogramSelect');
        if (!subprogramSelect) {
            console.error('[COPY_EXAM_FIX_V2] Subprogram select element not found');
            return;
        }
        
        if (!state.curriculumData || !program) {
            clearSubprogramDropdown();
            return;
        }
        
        const programData = state.curriculumData[program];
        if (!programData) {
            console.error('[COPY_EXAM_FIX_V2] No data for program:', program);
            clearSubprogramDropdown();
            return;
        }
        
        console.log('[COPY_EXAM_FIX_V2] Program data:', programData);
        
        if (!programData.subprograms || Object.keys(programData.subprograms).length === 0) {
            console.error('[COPY_EXAM_FIX_V2] No subprograms found for program:', program);
            clearSubprogramDropdown();
            return;
        }
        
        // Clear and add default option
        subprogramSelect.innerHTML = '<option value="">-- Select SubProgram --</option>';
        subprogramSelect.disabled = false;
        
        // Add subprograms
        const subprograms = Object.keys(programData.subprograms).sort();
        console.log('[COPY_EXAM_FIX_V2] Adding subprograms for', program + ':', subprograms);
        
        subprograms.forEach(subprogram => {
            const option = document.createElement('option');
            option.value = subprogram;
            option.textContent = subprogram;
            subprogramSelect.appendChild(option);
        });
        
        // Clear level dropdown
        clearLevelDropdown();
    }
    
    // Populate level dropdown
    function populateLevelDropdown(program, subprogram) {
        console.log('[COPY_EXAM_FIX_V2] Populating levels for:', program, subprogram);
        
        const levelSelect = document.getElementById('copyLevelSelect');
        if (!levelSelect) {
            console.error('[COPY_EXAM_FIX_V2] Level select element not found');
            return;
        }
        
        if (!state.curriculumData || !program || !subprogram) {
            clearLevelDropdown();
            return;
        }
        
        const subprogramData = state.curriculumData[program]?.subprograms?.[subprogram];
        if (!subprogramData) {
            console.error('[COPY_EXAM_FIX_V2] No subprogram data for:', program, subprogram);
            clearLevelDropdown();
            return;
        }
        
        console.log('[COPY_EXAM_FIX_V2] Subprogram data:', subprogramData);
        
        if (!subprogramData.levels || subprogramData.levels.length === 0) {
            console.error('[COPY_EXAM_FIX_V2] No levels found for:', program, subprogram);
            clearLevelDropdown();
            return;
        }
        
        // Clear and add default option
        levelSelect.innerHTML = '<option value="">-- Select Level --</option>';
        levelSelect.disabled = false;
        
        // Add levels
        const levels = subprogramData.levels;
        console.log('[COPY_EXAM_FIX_V2] Adding levels for', program, subprogram + ':', levels);
        
        levels.forEach(level => {
            const option = document.createElement('option');
            option.value = level.id;
            option.textContent = level.display_name || level.name || `Level ${level.number}`;
            option.dataset.levelName = level.name || level.display_name;
            levelSelect.appendChild(option);
        });
    }
    
    // Update preview text
    function updatePreview() {
        const previewText = document.getElementById('previewText');
        if (!previewText) return;
        
        const examType = document.getElementById('copyExamType')?.value;
        const timeslot = document.getElementById('timeslot')?.value;
        const year = document.getElementById('academicYear')?.value;
        const levelSelect = document.getElementById('copyLevelSelect');
        const levelName = levelSelect?.selectedOptions[0]?.dataset.levelName;
        const customSuffix = document.getElementById('customSuffix')?.value;
        
        let preview = '';
        
        if (examType === 'REVIEW' && timeslot) {
            // For REVIEW exams, timeslot is just the month code (e.g., 'JAN')
            preview = `[RT] - ${timeslot}`;
            if (year) {
                preview += ` ${year}`;
            }
        } else if (examType === 'QUARTERLY' && timeslot) {
            // For QUARTERLY exams, timeslot is the quarter code (e.g., 'Q1')
            preview = `[QTR] - ${timeslot}`;
            if (year) {
                preview += ` ${year}`;
            }
        }
        
        if (levelName) {
            preview += preview ? ' - ' + levelName : levelName;
        }
        
        if (customSuffix) {
            preview += '_' + customSuffix;
        }
        
        previewText.textContent = preview || 'Select options to see preview...';
    }
    
    // Setup event handlers - call this every time modal opens
    function setupEventHandlers() {
        console.log('[COPY_EXAM_FIX_V2] Setting up event handlers');
        
        // Remove existing handlers first to avoid duplicates
        const programSelect = document.getElementById('copyProgramSelect');
        const subprogramSelect = document.getElementById('copySubprogramSelect');
        const levelSelect = document.getElementById('copyLevelSelect');
        
        // Program select change
        if (programSelect) {
            // Remove old handler
            programSelect.replaceWith(programSelect.cloneNode(true));
            const newProgramSelect = document.getElementById('copyProgramSelect');
            
            newProgramSelect.addEventListener('change', function() {
                console.log('[COPY_EXAM_FIX_V2] Program changed to:', this.value);
                const program = this.value;
                if (program) {
                    populateSubprogramDropdown(program);
                } else {
                    clearSubprogramDropdown();
                    clearLevelDropdown();
                }
                updatePreview();
            });
        }
        
        // Subprogram select change
        if (subprogramSelect) {
            // Remove old handler
            subprogramSelect.replaceWith(subprogramSelect.cloneNode(true));
            const newSubprogramSelect = document.getElementById('copySubprogramSelect');
            
            newSubprogramSelect.addEventListener('change', function() {
                console.log('[COPY_EXAM_FIX_V2] Subprogram changed to:', this.value);
                const program = document.getElementById('copyProgramSelect')?.value;
                const subprogram = this.value;
                if (program && subprogram) {
                    populateLevelDropdown(program, subprogram);
                } else {
                    clearLevelDropdown();
                }
                updatePreview();
            });
        }
        
        // Level select change
        if (levelSelect) {
            // Remove old handler
            levelSelect.replaceWith(levelSelect.cloneNode(true));
            const newLevelSelect = document.getElementById('copyLevelSelect');
            
            newLevelSelect.addEventListener('change', function() {
                console.log('[COPY_EXAM_FIX_V2] Level changed to:', this.value);
                const levelId = this.value;
                const curriculumLevelInput = document.getElementById('copyCurriculumLevel');
                if (curriculumLevelInput) {
                    curriculumLevelInput.value = levelId;
                }
                updatePreview();
            });
        }
        
        // Exam type change
        const examTypeSelect = document.getElementById('copyExamType');
        if (examTypeSelect) {
            examTypeSelect.addEventListener('change', function() {
                const timeslotSelect = document.getElementById('timeslot');
                if (!timeslotSelect) return;
                
                timeslotSelect.innerHTML = '<option value="">Select time period...</option>';
                timeslotSelect.disabled = false;
                
                if (this.value === 'REVIEW') {
                    // Add monthly options (without year)
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
                } else if (this.value === 'QUARTERLY') {
                    // Add quarterly options (without year)
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
                }
                updatePreview();
            });
        }
        
        // Other change events for preview
        ['timeslot', 'academicYear', 'customSuffix'].forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.addEventListener('change', updatePreview);
                element.addEventListener('input', updatePreview);
            }
        });
        
        // Form submit
        const form = document.getElementById('copyExamForm');
        if (form) {
            form.addEventListener('submit', handleFormSubmit);
        }
        
        // Close modal on click outside
        const modal = document.getElementById('copyExamModal');
        if (modal) {
            modal.addEventListener('click', function(e) {
                if (e.target === modal) {
                    closeCopyModal();
                }
            });
        }
        
        console.log('[COPY_EXAM_FIX_V2] Event handlers setup complete');
    }
    
    // Handle form submission
    function handleFormSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const data = {
            source_exam_id: formData.get('source_exam_id'),
            target_class: formData.get('target_class'),
            curriculum_level: formData.get('curriculum_level'),
            exam_type: formData.get('exam_type'),
            timeslot: formData.get('timeslot'),
            academic_year: formData.get('academic_year'),
            custom_suffix: formData.get('custom_suffix')
        };
        
        console.log('[COPY_EXAM_FIX_V2] Submitting copy exam request:', data);
        
        // Submit to API
        fetch('/RoutineTest/api/copy-exam/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                alert('Exam copied successfully!');
                closeCopyModal();
                // Refresh the page to show new exam
                window.location.reload();
            } else {
                alert('Failed to copy exam: ' + (result.error || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('[COPY_EXAM_FIX_V2] Error copying exam:', error);
            alert('An error occurred while copying the exam.');
        });
    }
    
    // Get CSRF cookie
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            console.log('[COPY_EXAM_FIX_V2] DOM ready, initializing...');
            initCurriculumData();
        });
    } else {
        console.log('[COPY_EXAM_FIX_V2] DOM already ready, initializing...');
        initCurriculumData();
    }
    
    console.log('[COPY_EXAM_FIX_V2] Script loaded successfully');
})();