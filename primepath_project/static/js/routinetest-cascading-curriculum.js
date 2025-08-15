// ========================================
// CASCADING CURRICULUM SELECTION & AUTO-NAME GENERATION SYSTEM (v3.0)
// ========================================
console.log('[CASCADE_SYSTEM] ========================================');
console.log('[CASCADE_SYSTEM] Initializing Cascading Curriculum System v3.0');
console.log('[CASCADE_SYSTEM] Features: Program → SubProgram → Level cascade');
console.log('[CASCADE_SYSTEM] Auto-name format: [RT/QTR] - [Time Period] - [Program] [SubProgram] Level [X]');
console.log('[CASCADE_SYSTEM] ========================================');

// Store curriculum hierarchy data
let curriculumHierarchy = null;
let generatedBaseName = '';
let userComment = '';
let finalExamName = '';

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('[CASCADE_SYSTEM] DOM loaded, initializing cascading system...');
    initializeCascadingSystem();
});

function initializeCascadingSystem() {
    // Get UI elements
    const programSelect = document.getElementById('program_select');
    const subprogramSelect = document.getElementById('subprogram_select');
    const levelSelect = document.getElementById('level_select');
    const userCommentInput = document.getElementById('user_comment');
    const generatedNameText = document.getElementById('generated_name_text');
    const finalNamePreview = document.getElementById('final_name_preview');
    const curriculumLevelHidden = document.getElementById('curriculum_level');
    const finalExamNameHidden = document.getElementById('final_exam_name');
    const generatedBaseNameHidden = document.getElementById('generated_base_name');
    const selectedProgramHidden = document.getElementById('selected_program');
    const selectedSubprogramHidden = document.getElementById('selected_subprogram');
    const selectedLevelNumberHidden = document.getElementById('selected_level_number');
    const curriculumStatus = document.getElementById('curriculum_status');
    const curriculumStatusText = document.getElementById('curriculum_status_text');
    
    // Check if elements exist
    if (!programSelect) {
        console.error('[CASCADE_SYSTEM] Required elements not found. Exiting.');
        return;
    }
    
    // Load curriculum hierarchy on page load
    loadCurriculumHierarchy();
    
    // Add event listeners for cascading dropdowns
    programSelect.addEventListener('change', function() {
        console.log('[CASCADE_SYSTEM] Program selected:', this.value);
        
        // Clear subsequent dropdowns
        subprogramSelect.innerHTML = '<option value="">-- Select SubProgram --</option>';
        levelSelect.innerHTML = '<option value="">-- First select a SubProgram --</option>';
        subprogramSelect.disabled = true;
        levelSelect.disabled = true;
        
        // Hide subsequent steps
        document.querySelector('.cascade-step[data-step="2"]').style.display = 'none';
        document.querySelector('.cascade-step[data-step="3"]').style.display = 'none';
        curriculumStatus.style.display = 'none';
        
        // Clear hidden fields
        curriculumLevelHidden.value = '';
        selectedProgramHidden.value = '';
        selectedSubprogramHidden.value = '';
        selectedLevelNumberHidden.value = '';
        
        if (this.value && curriculumHierarchy) {
            // Store selected program
            selectedProgramHidden.value = this.value;
            
            // Show and populate subprogram dropdown
            const subprograms = curriculumHierarchy.subprograms[this.value] || [];
            
            if (subprograms.length > 0) {
                subprogramSelect.innerHTML = '<option value="">-- Select SubProgram --</option>';
                
                subprograms.forEach(sp => {
                    const option = document.createElement('option');
                    option.value = sp.name;
                    option.textContent = sp.display_name;
                    option.setAttribute('data-id', sp.id);
                    subprogramSelect.appendChild(option);
                });
                
                subprogramSelect.disabled = false;
                document.querySelector('.cascade-step[data-step="2"]').style.display = 'block';
                
                console.log('[CASCADE_SYSTEM] Populated subprograms:', subprograms.length);
            }
        }
        
        // Regenerate name
        generateExamName();
    });
    
    subprogramSelect.addEventListener('change', function() {
        console.log('[CASCADE_SYSTEM] SubProgram selected:', this.value);
        
        // Clear level dropdown
        levelSelect.innerHTML = '<option value="">-- Select Level --</option>';
        levelSelect.disabled = true;
        document.querySelector('.cascade-step[data-step="3"]').style.display = 'none';
        curriculumStatus.style.display = 'none';
        
        // Clear hidden fields
        curriculumLevelHidden.value = '';
        selectedSubprogramHidden.value = '';
        selectedLevelNumberHidden.value = '';
        
        if (this.value && curriculumHierarchy) {
            // Store selected subprogram
            selectedSubprogramHidden.value = this.value;
            
            // Get selected program
            const program = programSelect.value;
            const levelKey = `${program}_${this.value}`;
            const levels = curriculumHierarchy.levels[levelKey] || [];
            
            if (levels.length > 0) {
                levelSelect.innerHTML = '<option value="">-- Select Level --</option>';
                
                levels.forEach(level => {
                    const option = document.createElement('option');
                    option.value = level.id;
                    option.textContent = level.display_name;
                    option.setAttribute('data-level-number', level.level_number);
                    option.setAttribute('data-full-name', level.full_name);
                    levelSelect.appendChild(option);
                });
                
                levelSelect.disabled = false;
                document.querySelector('.cascade-step[data-step="3"]').style.display = 'block';
                
                console.log('[CASCADE_SYSTEM] Populated levels:', levels.length);
            }
        }
        
        // Regenerate name
        generateExamName();
    });
    
    levelSelect.addEventListener('change', function() {
        console.log('[CASCADE_SYSTEM] Level selected:', this.value);
        
        if (this.value) {
            const selectedOption = this.options[this.selectedIndex];
            const levelNumber = selectedOption.getAttribute('data-level-number');
            const fullName = selectedOption.getAttribute('data-full-name');
            
            // Store in hidden fields
            curriculumLevelHidden.value = this.value;
            selectedLevelNumberHidden.value = levelNumber;
            
            // Show curriculum status
            curriculumStatus.style.display = 'block';
            curriculumStatusText.textContent = fullName;
            
            console.log('[CASCADE_SYSTEM] Complete selection:', {
                curriculum_level_id: this.value,
                level_number: levelNumber,
                full_name: fullName
            });
        } else {
            curriculumLevelHidden.value = '';
            selectedLevelNumberHidden.value = '';
            curriculumStatus.style.display = 'none';
        }
        
        // Regenerate name
        generateExamName();
    });
    
    // Add event listeners for other fields that affect name generation
    document.getElementById('exam_type')?.addEventListener('change', generateExamName);
    document.getElementById('time_period_month')?.addEventListener('change', generateExamName);
    document.getElementById('time_period_quarter')?.addEventListener('change', generateExamName);
    document.getElementById('academic_year')?.addEventListener('change', generateExamName);
    
    // User comment input
    if (userCommentInput) {
        userCommentInput.addEventListener('input', function() {
            userComment = this.value.trim();
            updateFinalName();
            
            console.log('[CASCADE_SYSTEM] User comment updated:', {
                comment: userComment,
                length: userComment.length,
                final_name: finalExamName
            });
        });
    }
}

// Function to load curriculum hierarchy from API
async function loadCurriculumHierarchy() {
    console.log('[CASCADE_SYSTEM] Loading curriculum hierarchy from API...');
    
    try {
        const response = await fetch('/RoutineTest/api/curriculum-hierarchy/');
        const data = await response.json();
        
        if (data.success) {
            curriculumHierarchy = data.data;
            console.log('[CASCADE_SYSTEM] Curriculum hierarchy loaded:', {
                programs: curriculumHierarchy.programs.length,
                total_subprograms: Object.keys(curriculumHierarchy.subprograms).length,
                total_levels: Object.keys(curriculumHierarchy.levels).length
            });
            
            // Populate program dropdown
            populateProgramDropdown();
        } else {
            console.error('[CASCADE_SYSTEM] Failed to load curriculum hierarchy:', data.error);
        }
    } catch (error) {
        console.error('[CASCADE_SYSTEM] Error fetching curriculum hierarchy:', error);
    }
}

// Function to populate program dropdown
function populateProgramDropdown() {
    console.log('[CASCADE_SYSTEM] Populating program dropdown...');
    
    const programSelect = document.getElementById('program_select');
    if (!programSelect) return;
    
    programSelect.innerHTML = '<option value="">-- Select Program --</option>';
    
    curriculumHierarchy.programs.forEach(program => {
        const option = document.createElement('option');
        option.value = program.name;
        option.textContent = program.name;
        option.setAttribute('data-id', program.id);
        programSelect.appendChild(option);
    });
    
    console.log('[CASCADE_SYSTEM] Program dropdown populated with', curriculumHierarchy.programs.length, 'programs');
}

// Function to generate the exam name based on selections
function generateExamName() {
    console.log('[CASCADE_SYSTEM] ========================================');
    console.log('[CASCADE_SYSTEM] Starting name generation (Cascading version)');
    console.log('[CASCADE_SYSTEM] Name format: [RT/QTR] - [Time Period] - [Program] [SubProgram] Level [X]');
    
    // Get current selections
    const examType = document.getElementById('exam_type')?.value;
    const timePeriodMonth = document.getElementById('time_period_month')?.value;
    const timePeriodQuarter = document.getElementById('time_period_quarter')?.value;
    const academicYear = document.getElementById('academic_year')?.value;
    const program = document.getElementById('program_select')?.value;
    const subprogram = document.getElementById('subprogram_select')?.value;
    const levelSelect = document.getElementById('level_select');
    const levelId = levelSelect?.value;
    
    console.log('[CASCADE_SYSTEM] Current selections:', {
        examType: examType,
        timePeriodMonth: timePeriodMonth,
        timePeriodQuarter: timePeriodQuarter,
        academicYear: academicYear,
        program: program,
        subprogram: subprogram,
        levelId: levelId
    });
    
    const nameParts = [];
    
    // Add exam type prefix [RT] or [QTR]
    if (examType) {
        const prefix = examType === 'QUARTERLY' ? 'QTR' : 'RT';
        nameParts.push(`[${prefix}]`);
        console.log('[CASCADE_SYSTEM] Added prefix:', prefix);
    }
    
    // Add time period (actual period, not placeholder)
    if (examType === 'REVIEW' && timePeriodMonth) {
        const monthNames = {
            'JAN': 'January', 'FEB': 'February', 'MAR': 'March', 'APR': 'April',
            'MAY': 'May', 'JUN': 'June', 'JUL': 'July', 'AUG': 'August',
            'SEP': 'September', 'OCT': 'October', 'NOV': 'November', 'DEC': 'December'
        };
        const monthName = monthNames[timePeriodMonth] || timePeriodMonth;
        const periodStr = academicYear ? `${monthName} ${academicYear}` : monthName;
        nameParts.push(periodStr);
        console.log('[CASCADE_SYSTEM] Added month period:', periodStr);
    } else if (examType === 'QUARTERLY' && timePeriodQuarter) {
        const periodStr = academicYear ? `${timePeriodQuarter} ${academicYear}` : timePeriodQuarter;
        nameParts.push(periodStr);
        console.log('[CASCADE_SYSTEM] Added quarter period:', periodStr);
    }
    
    // Add curriculum level from cascading selections
    if (program && subprogram && levelId && levelSelect) {
        const levelOption = levelSelect.options[levelSelect.selectedIndex];
        const levelNumber = levelOption.getAttribute('data-level-number');
        const curriculumStr = `${program} ${subprogram} Level ${levelNumber}`;
        nameParts.push(curriculumStr);
        console.log('[CASCADE_SYSTEM] Added curriculum:', curriculumStr);
    }
    
    // Generate base name
    generatedBaseName = nameParts.join(' - ');
    
    console.log('[CASCADE_SYSTEM] Generated base name:', generatedBaseName);
    
    // Update displays
    updateDisplays();
    updateFinalName();
    
    return generatedBaseName;
}

// Function to update the displays
function updateDisplays() {
    const generatedNameText = document.getElementById('generated_name_text');
    const generatedBaseNameHidden = document.getElementById('generated_base_name');
    
    if (generatedBaseName) {
        if (generatedNameText) {
            generatedNameText.textContent = generatedBaseName;
            generatedNameText.style.color = '#1B5E20';
        }
        if (generatedBaseNameHidden) {
            generatedBaseNameHidden.value = generatedBaseName;
        }
        
        console.log('[CASCADE_SYSTEM] Updated displays with base name:', generatedBaseName);
    } else {
        if (generatedNameText) {
            generatedNameText.textContent = 'Please make selections above to generate name...';
            generatedNameText.style.color = '#757575';
        }
        if (generatedBaseNameHidden) {
            generatedBaseNameHidden.value = '';
        }
    }
}

// Function to update the final name with user comment
function updateFinalName() {
    const finalNamePreview = document.getElementById('final_name_preview');
    const finalExamNameHidden = document.getElementById('final_exam_name');
    
    if (generatedBaseName) {
        // Combine base name with user comment
        finalExamName = userComment ? `${generatedBaseName}_${userComment}` : generatedBaseName;
        
        if (finalNamePreview) {
            finalNamePreview.innerHTML = `<span style="color: #1B5E20; font-weight: 600;">${finalExamName}</span>`;
        }
        if (finalExamNameHidden) {
            finalExamNameHidden.value = finalExamName;
        }
        
        console.log('[CASCADE_SYSTEM] Final name updated:', {
            base: generatedBaseName,
            comment: userComment || '(none)',
            final: finalExamName
        });
    } else {
        if (finalNamePreview) {
            finalNamePreview.innerHTML = '<span style="color: #9E9E9E;">Waiting for selections...</span>';
        }
        if (finalExamNameHidden) {
            finalExamNameHidden.value = '';
        }
        finalExamName = '';
    }
}

// Export functions for global use if needed
window.generateExamName = generateExamName;
window.updateFinalName = updateFinalName;

console.log('[CASCADE_SYSTEM] ========================================');
console.log('[CASCADE_SYSTEM] Cascading Curriculum System v3.0 loaded');
console.log('[CASCADE_SYSTEM] Ready for initialization on DOM load');
console.log('[CASCADE_SYSTEM] ========================================');