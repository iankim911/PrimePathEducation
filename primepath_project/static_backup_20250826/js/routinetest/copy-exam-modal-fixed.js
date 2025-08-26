/**
 * Copy Exam Modal - Fixed Implementation
 * Version: FIXED
 * Date: 2025-08-24
 * 
 * Simplified and fixed copy exam modal functionality
 */

(function() {
    'use strict';
    
    console.log('[COPY_MODAL_FIXED] Loading copy exam modal script...');
    
    let curriculumData = null;
    let currentExamInfo = null;
    
    // Main function to open the copy modal
    function openCopyModal(examId, examName) {
        console.log('[COPY_MODAL_FIXED] Opening modal for:', examId, examName);
        
        // Store exam info
        currentExamInfo = {
            id: examId,
            name: examName
        };
        
        // Get modal element
        const modal = document.getElementById('copyExamModal');
        if (!modal) {
            console.error('[COPY_MODAL_FIXED] Modal element not found');
            alert('Copy modal not found. Please refresh the page.');
            return;
        }
        
        // Set the source exam info
        const sourceExamIdField = document.getElementById('sourceExamId');
        const sourceExamNameField = document.getElementById('sourceExamName');
        
        if (sourceExamIdField) sourceExamIdField.value = examId;
        if (sourceExamNameField) sourceExamNameField.textContent = examName;
        
        // Load curriculum data if not already loaded
        if (!curriculumData) {
            loadCurriculumData();
        }
        
        // Initialize dropdowns
        initializeDropdowns();
        
        // Show the modal
        modal.style.display = 'block';
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
        
        console.log('[COPY_MODAL_FIXED] Modal opened successfully');
    }
    
    // Function to close the modal
    function closeCopyModal() {
        console.log('[COPY_MODAL_FIXED] Closing modal');
        
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
    }
    
    // Load curriculum data
    function loadCurriculumData() {
        console.log('[COPY_MODAL_FIXED] Loading curriculum data...');
        
        const scriptElement = document.getElementById('copy-curriculum-hierarchy-data');
        if (scriptElement) {
            try {
                const rawData = JSON.parse(scriptElement.textContent);
                console.log('[COPY_MODAL_FIXED] Raw curriculum data:', rawData);
                
                // Extract curriculum data
                if (rawData.curriculum_data) {
                    curriculumData = rawData.curriculum_data;
                } else if (rawData.CORE || rawData.ASCENT || rawData.EDGE || rawData.PINNACLE) {
                    curriculumData = rawData;
                } else {
                    console.warn('[COPY_MODAL_FIXED] Unknown data structure, using fallback');
                    curriculumData = createFallbackData();
                }
                
                console.log('[COPY_MODAL_FIXED] Curriculum data loaded successfully');
            } catch (error) {
                console.error('[COPY_MODAL_FIXED] Failed to parse curriculum data:', error);
                curriculumData = createFallbackData();
            }
        } else {
            console.warn('[COPY_MODAL_FIXED] No curriculum data script element found, using fallback');
            curriculumData = createFallbackData();
        }
    }
    
    // Create fallback curriculum data
    function createFallbackData() {
        return {
            'CORE': {
                'subprograms': {
                    'Phonics': { 'levels': [{'id': '1', 'number': 1}, {'id': '2', 'number': 2}, {'id': '3', 'number': 3}] },
                    'Sigma': { 'levels': [{'id': '4', 'number': 1}, {'id': '5', 'number': 2}, {'id': '6', 'number': 3}] },
                    'Elite': { 'levels': [{'id': '7', 'number': 1}, {'id': '8', 'number': 2}, {'id': '9', 'number': 3}] },
                    'Pro': { 'levels': [{'id': '10', 'number': 1}, {'id': '11', 'number': 2}, {'id': '12', 'number': 3}] }
                }
            },
            'ASCENT': {
                'subprograms': {
                    'Nova': { 'levels': [{'id': '13', 'number': 1}, {'id': '14', 'number': 2}, {'id': '15', 'number': 3}] },
                    'Drive': { 'levels': [{'id': '16', 'number': 1}, {'id': '17', 'number': 2}, {'id': '18', 'number': 3}] },
                    'Pro': { 'levels': [{'id': '19', 'number': 1}, {'id': '20', 'number': 2}, {'id': '21', 'number': 3}] }
                }
            },
            'EDGE': {
                'subprograms': {
                    'Spark': { 'levels': [{'id': '22', 'number': 1}, {'id': '23', 'number': 2}, {'id': '24', 'number': 3}] },
                    'Rise': { 'levels': [{'id': '25', 'number': 1}, {'id': '26', 'number': 2}, {'id': '27', 'number': 3}] },
                    'Pursuit': { 'levels': [{'id': '28', 'number': 1}, {'id': '29', 'number': 2}, {'id': '30', 'number': 3}] },
                    'Pro': { 'levels': [{'id': '31', 'number': 1}, {'id': '32', 'number': 2}, {'id': '33', 'number': 3}] }
                }
            },
            'PINNACLE': {
                'subprograms': {
                    'Vision': { 'levels': [{'id': '34', 'number': 1}, {'id': '35', 'number': 2}] },
                    'Endeavor': { 'levels': [{'id': '36', 'number': 1}, {'id': '37', 'number': 2}] },
                    'Success': { 'levels': [{'id': '38', 'number': 1}, {'id': '39', 'number': 2}] },
                    'Pro': { 'levels': [{'id': '40', 'number': 1}, {'id': '41', 'number': 2}] }
                }
            }
        };
    }
    
    // Initialize dropdowns
    function initializeDropdowns() {
        console.log('[COPY_MODAL_FIXED] Initializing dropdowns...');
        
        // Initialize exam type dropdown
        const examTypeSelect = document.getElementById('copyExamType');
        const timeslotSelect = document.getElementById('timeslot');
        
        if (examTypeSelect) {
            // Clear and populate exam type
            examTypeSelect.innerHTML = '<option value="">Select exam type...</option>';
            examTypeSelect.innerHTML += '<option value="QUARTERLY">Quarterly</option>';
            examTypeSelect.innerHTML += '<option value="REVIEW">Review</option>';
            
            // Handle exam type change
            examTypeSelect.addEventListener('change', function() {
                updateTimeslotDropdown(this.value);
                // Update the preview
                if (typeof window.updateCopyExamNamePreview === 'function') {
                    window.updateCopyExamNamePreview();
                }
            });
        }
        
        // Initialize academic year dropdown
        const academicYearSelect = document.getElementById('academicYear');
        if (academicYearSelect) {
            const currentYear = new Date().getFullYear();
            academicYearSelect.innerHTML = '';
            for (let year = currentYear - 1; year <= currentYear + 1; year++) {
                const option = document.createElement('option');
                option.value = year;
                option.textContent = year;
                if (year === currentYear) {
                    option.selected = true;
                }
                academicYearSelect.appendChild(option);
            }
        }
        
        // Initialize curriculum dropdowns
        const programSelect = document.getElementById('copyProgramSelect');
        const subprogramSelect = document.getElementById('copySubprogramSelect');
        const levelSelect = document.getElementById('copyLevelSelect');
        
        if (programSelect && curriculumData) {
            // Clear and populate program dropdown
            programSelect.innerHTML = '<option value="">Select Program...</option>';
            
            Object.keys(curriculumData).forEach(program => {
                const option = document.createElement('option');
                option.value = program;
                option.textContent = program;
                programSelect.appendChild(option);
            });
            
            // Enable subprogram select
            if (subprogramSelect) {
                subprogramSelect.disabled = false;
            }
            
            // Set up cascading
            programSelect.addEventListener('change', function() {
                updateSubprogramDropdown();
                // Update the preview
                if (typeof window.updateCopyExamNamePreview === 'function') {
                    window.updateCopyExamNamePreview();
                }
            });
            
            if (subprogramSelect) {
                subprogramSelect.addEventListener('change', function() {
                    updateLevelDropdown();
                    // Update the preview
                    if (typeof window.updateCopyExamNamePreview === 'function') {
                        window.updateCopyExamNamePreview();
                    }
                });
            }
        }
        
        // Try to extract and pre-select curriculum from exam name
        if (currentExamInfo && currentExamInfo.name) {
            extractAndSelectCurriculum(currentExamInfo.name);
        }
    }
    
    // Update timeslot dropdown based on exam type
    function updateTimeslotDropdown(examType) {
        const timeslotSelect = document.getElementById('timeslot');
        if (!timeslotSelect) return;
        
        timeslotSelect.innerHTML = '<option value="">Select time period...</option>';
        
        if (examType === 'QUARTERLY') {
            timeslotSelect.disabled = false;
            ['Q1', 'Q2', 'Q3', 'Q4'].forEach(quarter => {
                const option = document.createElement('option');
                option.value = quarter;
                option.textContent = quarter;
                timeslotSelect.appendChild(option);
            });
        } else if (examType === 'REVIEW') {
            timeslotSelect.disabled = false;
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
        } else {
            timeslotSelect.disabled = true;
        }
        
        // Add event listener for timeslot changes
        timeslotSelect.onchange = function() {
            if (typeof window.updateCopyExamNamePreview === 'function') {
                window.updateCopyExamNamePreview();
            }
        };
    }
    
    // Update subprogram dropdown based on selected program
    function updateSubprogramDropdown() {
        const programSelect = document.getElementById('copyProgramSelect');
        const subprogramSelect = document.getElementById('copySubprogramSelect');
        const levelSelect = document.getElementById('copyLevelSelect');
        
        if (!programSelect || !subprogramSelect) return;
        
        const selectedProgram = programSelect.value;
        
        // Clear subprogram and level
        subprogramSelect.innerHTML = '<option value="">Select SubProgram...</option>';
        if (levelSelect) {
            levelSelect.innerHTML = '<option value="">Select Level...</option>';
        }
        
        if (selectedProgram && curriculumData[selectedProgram]) {
            const subprograms = curriculumData[selectedProgram].subprograms || {};
            
            Object.keys(subprograms).forEach(subprogram => {
                const option = document.createElement('option');
                option.value = subprogram;
                option.textContent = subprogram;
                subprogramSelect.appendChild(option);
            });
        }
    }
    
    // Update level dropdown based on selected subprogram
    function updateLevelDropdown() {
        const programSelect = document.getElementById('copyProgramSelect');
        const subprogramSelect = document.getElementById('copySubprogramSelect');
        const levelSelect = document.getElementById('copyLevelSelect');
        
        if (!programSelect || !subprogramSelect || !levelSelect) return;
        
        const selectedProgram = programSelect.value;
        const selectedSubprogram = subprogramSelect.value;
        
        // Clear level and enable it
        levelSelect.innerHTML = '<option value="">Select Level...</option>';
        levelSelect.disabled = false;
        
        // Clear the hidden curriculum level field
        const curriculumLevelField = document.getElementById('copyCurriculumLevel');
        if (curriculumLevelField) {
            curriculumLevelField.value = '';
        }
        
        if (selectedProgram && selectedSubprogram && 
            curriculumData[selectedProgram] && 
            curriculumData[selectedProgram].subprograms &&
            curriculumData[selectedProgram].subprograms[selectedSubprogram]) {
            
            const levels = curriculumData[selectedProgram].subprograms[selectedSubprogram].levels || [];
            
            levels.forEach(level => {
                const option = document.createElement('option');
                option.value = level.id;
                option.textContent = `Level ${level.number}`;
                levelSelect.appendChild(option);
            });
            
            // Add level change listener
            levelSelect.addEventListener('change', function() {
                if (curriculumLevelField) {
                    curriculumLevelField.value = this.value;
                    console.log('[COPY_MODAL_FIXED] Set curriculum level ID:', this.value);
                }
                // Update the preview
                if (typeof window.updateCopyExamNamePreview === 'function') {
                    window.updateCopyExamNamePreview();
                }
            });
        }
    }
    
    // Extract curriculum from exam name and pre-select
    function extractAndSelectCurriculum(examName) {
        console.log('[COPY_MODAL_FIXED] Extracting curriculum from:', examName);
        
        // Pattern: PROGRAM SUBPROGRAM Lv#
        const match = examName.match(/(CORE|ASCENT|EDGE|PINNACLE)\s+(\w+)\s+Lv(\d+)/i);
        
        if (match) {
            const [_, program, subprogram, levelNum] = match;
            console.log('[COPY_MODAL_FIXED] Extracted:', program, subprogram, 'Level', levelNum);
            
            // Set program
            const programSelect = document.getElementById('copyProgramSelect');
            if (programSelect) {
                programSelect.value = program.toUpperCase();
                updateSubprogramDropdown();
                
                // Set subprogram after a short delay
                setTimeout(() => {
                    const subprogramSelect = document.getElementById('copySubprogramSelect');
                    if (subprogramSelect) {
                        // Find matching subprogram (case-insensitive)
                        const options = Array.from(subprogramSelect.options);
                        const matchingOption = options.find(opt => 
                            opt.value.toLowerCase() === subprogram.toLowerCase()
                        );
                        
                        if (matchingOption) {
                            subprogramSelect.value = matchingOption.value;
                            updateLevelDropdown();
                            
                            // Set level after another short delay
                            setTimeout(() => {
                                const levelSelect = document.getElementById('copyLevelSelect');
                                if (levelSelect) {
                                    // Find level with matching number
                                    const levelOptions = Array.from(levelSelect.options);
                                    const matchingLevel = levelOptions.find(opt => 
                                        opt.textContent === `Level ${levelNum}`
                                    );
                                    
                                    if (matchingLevel) {
                                        levelSelect.value = matchingLevel.value;
                                    }
                                }
                            }, 50);
                        }
                    }
                }, 50);
            }
        }
    }
    
    // Setup form submission
    function setupFormSubmission() {
        const form = document.getElementById('copyExamForm');
        if (!form) return;
        
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            console.log('[COPY_MODAL_FIXED] Submitting copy exam form...');
            
            const formData = new FormData(form);
            const data = {
                source_exam_id: currentExamInfo.id,
                target_class: formData.get('target_class'),
                timeslot: formData.get('timeslot'),
                academic_year: formData.get('academic_year'),
                exam_type: formData.get('exam_type'),
                curriculum_level_id: formData.get('curriculum_level'),
                custom_suffix: formData.get('custom_suffix') || ''
            };
            
            try {
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                
                const response = await fetch('/RoutineTest/api/copy-exam/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (response.ok && result.success) {
                    console.log('[COPY_MODAL_FIXED] Copy successful:', result);
                    alert('Exam copied successfully!');
                    closeCopyModal();
                    // Reload the page to show the new exam
                    window.location.reload();
                } else {
                    console.error('[COPY_MODAL_FIXED] Copy failed:', result);
                    alert(result.error || 'Failed to copy exam. Please try again.');
                }
            } catch (error) {
                console.error('[COPY_MODAL_FIXED] Error copying exam:', error);
                alert('An error occurred while copying the exam. Please try again.');
            }
        });
    }
    
    // Initialize when DOM is ready
    function initialize() {
        console.log('[COPY_MODAL_FIXED] Initializing...');
        
        // Replace global functions
        window.openCopyModal = openCopyModal;
        window.closeCopyModal = closeCopyModal;
        
        // Load curriculum data
        loadCurriculumData();
        
        // Setup form submission
        setupFormSubmission();
        
        // Setup modal close on background click
        const modal = document.getElementById('copyExamModal');
        if (modal) {
            modal.addEventListener('click', function(e) {
                if (e.target === modal) {
                    closeCopyModal();
                }
            });
        }
        
        console.log('[COPY_MODAL_FIXED] Initialization complete');
    }
    
    // Wait for DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initialize);
    } else {
        initialize();
    }
    
})();