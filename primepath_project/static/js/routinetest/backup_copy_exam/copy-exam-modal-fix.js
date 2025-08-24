/**
 * Copy Exam Modal Fix
 * Version: 4.0 - Simplified and Robust
 * Date: 2025-08-23
 */

(function() {
    'use strict';
    
    console.log('[COPY_EXAM_FIX] Initializing Copy Exam Modal Fix v4.0');
    
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
                console.error('[COPY_EXAM_FIX] Curriculum data script element not found');
                return false;
            }
            
            const data = JSON.parse(scriptEl.textContent);
            if (data && data.curriculum_data) {
                state.curriculumData = data.curriculum_data;
                console.log('[COPY_EXAM_FIX] Curriculum data loaded:', Object.keys(state.curriculumData));
                return true;
            } else if (data) {
                // Fallback: use data directly if it's not wrapped
                state.curriculumData = data;
                console.log('[COPY_EXAM_FIX] Curriculum data loaded (direct):', Object.keys(state.curriculumData));
                return true;
            }
            
            console.error('[COPY_EXAM_FIX] Invalid curriculum data structure');
            return false;
        } catch (e) {
            console.error('[COPY_EXAM_FIX] Failed to parse curriculum data:', e);
            return false;
        }
    }
    
    // Open the copy modal
    window.openCopyModal = function(examId, examName) {
        console.log('[COPY_EXAM_FIX] Opening modal for exam:', examId, examName);
        
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
            console.error('[COPY_EXAM_FIX] Modal element not found');
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
        
        // Setup event handlers if not already done
        if (!state.initialized) {
            setupEventHandlers();
            state.initialized = true;
        }
        
        // Show modal
        modal.style.display = 'block';
        setTimeout(() => modal.classList.add('show'), 10);
        
        console.log('[COPY_EXAM_FIX] Modal opened successfully');
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
        if (!programSelect || !state.curriculumData) {
            console.error('[COPY_EXAM_FIX] Cannot populate program dropdown');
            return;
        }
        
        // Clear and add default option
        programSelect.innerHTML = '<option value="">-- Select Program --</option>';
        
        // Add programs
        const programs = Object.keys(state.curriculumData).sort();
        console.log('[COPY_EXAM_FIX] Adding programs:', programs);
        
        programs.forEach(program => {
            const option = document.createElement('option');
            option.value = program;
            option.textContent = program;
            programSelect.appendChild(option);
        });
        
        // Clear dependent dropdowns
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
    }
    
    // Populate subprogram dropdown
    function populateSubprogramDropdown(program) {
        const subprogramSelect = document.getElementById('copySubprogramSelect');
        if (!subprogramSelect || !state.curriculumData || !program) return;
        
        const programData = state.curriculumData[program];
        if (!programData || !programData.subprograms) {
            console.error('[COPY_EXAM_FIX] No subprograms found for program:', program);
            return;
        }
        
        // Clear and add default option
        subprogramSelect.innerHTML = '<option value="">-- Select SubProgram --</option>';
        subprogramSelect.disabled = false;
        
        // Add subprograms
        const subprograms = Object.keys(programData.subprograms).sort();
        console.log('[COPY_EXAM_FIX] Adding subprograms for', program + ':', subprograms);
        
        subprograms.forEach(subprogram => {
            const option = document.createElement('option');
            option.value = subprogram;
            option.textContent = subprogram;
            subprogramSelect.appendChild(option);
        });
        
        // Clear level dropdown
        const levelSelect = document.getElementById('copyLevelSelect');
        if (levelSelect) {
            levelSelect.innerHTML = '<option value="">-- First select a SubProgram --</option>';
            levelSelect.disabled = true;
        }
    }
    
    // Populate level dropdown
    function populateLevelDropdown(program, subprogram) {
        const levelSelect = document.getElementById('copyLevelSelect');
        if (!levelSelect || !state.curriculumData || !program || !subprogram) return;
        
        const subprogramData = state.curriculumData[program]?.subprograms?.[subprogram];
        if (!subprogramData || !subprogramData.levels) {
            console.error('[COPY_EXAM_FIX] No levels found for:', program, subprogram);
            return;
        }
        
        // Clear and add default option
        levelSelect.innerHTML = '<option value="">-- Select Level --</option>';
        levelSelect.disabled = false;
        
        // Add levels
        const levels = subprogramData.levels;
        console.log('[COPY_EXAM_FIX] Adding levels for', program, subprogram + ':', levels);
        
        levels.forEach(level => {
            const option = document.createElement('option');
            option.value = level.id;
            option.textContent = level.display_name || level.name;
            option.dataset.levelName = level.name;
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
            const [month] = timeslot.split('-');
            preview = `[RT] - ${month} ${year || '2025'}`;
        } else if (examType === 'QUARTERLY' && timeslot) {
            preview = `[QTR] - ${timeslot} ${year || '2025'}`;
        }
        
        if (levelName) {
            preview += preview ? ' - ' + levelName : levelName;
        }
        
        if (customSuffix) {
            preview += '_' + customSuffix;
        }
        
        previewText.textContent = preview || 'Select options to see preview...';
    }
    
    // Setup event handlers
    function setupEventHandlers() {
        // Program select change
        const programSelect = document.getElementById('copyProgramSelect');
        if (programSelect) {
            programSelect.addEventListener('change', function() {
                const program = this.value;
                if (program) {
                    populateSubprogramDropdown(program);
                }
                updatePreview();
            });
        }
        
        // Subprogram select change
        const subprogramSelect = document.getElementById('copySubprogramSelect');
        if (subprogramSelect) {
            subprogramSelect.addEventListener('change', function() {
                const program = programSelect?.value;
                const subprogram = this.value;
                if (program && subprogram) {
                    populateLevelDropdown(program, subprogram);
                }
                updatePreview();
            });
        }
        
        // Level select change
        const levelSelect = document.getElementById('copyLevelSelect');
        if (levelSelect) {
            levelSelect.addEventListener('change', function() {
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
                    // Add monthly options
                    const months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'];
                    months.forEach(month => {
                        const option = document.createElement('option');
                        option.value = month + '-2025';
                        option.textContent = month + ' 2025';
                        timeslotSelect.appendChild(option);
                    });
                } else if (this.value === 'QUARTERLY') {
                    // Add quarterly options
                    const quarters = ['Q1', 'Q2', 'Q3', 'Q4'];
                    quarters.forEach(quarter => {
                        const option = document.createElement('option');
                        option.value = quarter;
                        option.textContent = quarter + ' 2025';
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
    }
    
    // Handle form submission
    function handleFormSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData.entries());
        
        console.log('[COPY_EXAM_FIX] Submitting copy exam:', data);
        
        // Validate required fields
        if (!data.source_exam_id || !data.target_class || !data.exam_type || 
            !data.timeslot || !data.curriculum_level) {
            alert('Please fill in all required fields');
            return;
        }
        
        // Send AJAX request
        fetch('/routinetest/api/copy-exam/', {
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
                location.reload(); // Reload to show new exam
            } else {
                alert('Error: ' + (result.error || 'Failed to copy exam'));
            }
        })
        .catch(error => {
            console.error('[COPY_EXAM_FIX] Copy failed:', error);
            alert('An error occurred while copying the exam');
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
    
    // Initialize on page load
    document.addEventListener('DOMContentLoaded', function() {
        console.log('[COPY_EXAM_FIX] DOM loaded, initializing...');
        
        // Try to pre-load curriculum data
        if (initCurriculumData()) {
            console.log('[COPY_EXAM_FIX] Curriculum data pre-loaded successfully');
        }
        
        // Setup handlers for any existing modal
        if (document.getElementById('copyExamModal')) {
            setupEventHandlers();
            state.initialized = true;
            console.log('[COPY_EXAM_FIX] Event handlers attached');
        }
    });
    
    console.log('[COPY_EXAM_FIX] Script loaded successfully');
})();