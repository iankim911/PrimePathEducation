/**
 * Curriculum Management System
 * Admin-only functionality for managing class-curriculum mappings
 */

// Curriculum structure
const CURRICULUM_STRUCTURE = {
    'CORE': {
        name: 'PRIME CORE',
        subPrograms: ['Phonics', 'Sigma', 'Elite', 'Pro'],
        levels: [1, 2, 3]
    },
    'ASCENT': {
        name: 'PRIME ASCENT',
        subPrograms: ['Nova', 'Drive', 'Pro', 'Plus'],
        levels: [1, 2, 3]
    },
    'EDGE': {
        name: 'PRIME EDGE',
        subPrograms: ['Spark', 'Rise', 'Pursuit', 'Pro'],
        levels: [1, 2, 3]
    },
    'PINNACLE': {
        name: 'PRIME PINNACLE',
        subPrograms: ['Vision', 'Endeavor', 'Success', 'Pro'],
        levels: [1, 2]
    }
};

let editingClassCode = null;

// Load all classes for admin management
async function loadAdminClasses() {
    console.log('[CURRICULUM_ADMIN] Loading admin classes...');
    try {
        // Use ConfigService for dynamic year resolution
        const currentYear = window.PrimePath?.config?.getCurrentYear?.() || new Date().getFullYear();
        console.log(`[CURRICULUM_ADMIN] Using year: ${currentYear}`);
        const response = await fetch(`/RoutineTest/api/admin/classes/?year=${currentYear}`);
        const data = await response.json();
        console.log('[BUTTON_FIX] Received classes data:', data);
        
        const tableBody = document.getElementById('adminClassTableBody');
        if (!tableBody) return;
        
        if (data.classes && data.classes.length > 0) {
            tableBody.innerHTML = data.classes.map(cls => `
                <tr id="class-row-${cls.code}">
                    <td>${cls.code}</td>
                    <td>
                        <span class="curriculum-display" id="curr-display-${cls.code}">
                            ${cls.curriculum || 'Not Assigned'}
                        </span>
                    </td>
                    <td>
                        <select class="curriculum-select" id="prog-${cls.code}" onchange="updateCurriculumMapping('${cls.code}', 'program')">
                            <option value="">-- Select --</option>
                            ${Object.keys(CURRICULUM_STRUCTURE).map(key => 
                                `<option value="${key}" ${cls.program === key ? 'selected' : ''}>${CURRICULUM_STRUCTURE[key].name}</option>`
                            ).join('')}
                        </select>
                    </td>
                    <td>
                        <select class="curriculum-select" id="subprog-${cls.code}" onchange="updateCurriculumMapping('${cls.code}', 'subprogram')" 
                                ${!cls.program ? 'disabled' : ''}>
                            <option value="">-- Select --</option>
                            ${cls.program ? CURRICULUM_STRUCTURE[cls.program].subPrograms.map(sp => 
                                `<option value="${sp}" ${cls.subprogram === sp ? 'selected' : ''}>${sp}</option>`
                            ).join('') : ''}
                        </select>
                    </td>
                    <td>
                        <select class="curriculum-select" id="level-${cls.code}" onchange="updateCurriculumMapping('${cls.code}', 'level')"
                                ${!cls.subprogram ? 'disabled' : ''}>
                            <option value="">-- Select --</option>
                            ${cls.program ? CURRICULUM_STRUCTURE[cls.program].levels.map(level => 
                                `<option value="${level}" ${cls.level === level ? 'selected' : ''}>Level ${level}</option>`
                            ).join('') : ''}
                        </select>
                    </td>
                    <td>
                        <div class="action-buttons">
                            <button type="button" class="btn-save" onclick="saveCurriculumMapping('${cls.code}'); return false;" title="Save curriculum mapping" style="width: 80px !important; padding: 6px 10px !important; background: #2E7D32 !important; color: white !important; border: none !important; border-radius: 5px !important; font-size: 12px !important; font-weight: 500 !important; cursor: pointer !important; display: inline-block !important; text-align: center !important; line-height: 1.2 !important; box-sizing: border-box !important; white-space: nowrap !important; margin: 0 2px !important;">Save</button>
                            <button type="button" class="btn-edit" onclick="editClass('${cls.code}'); return false;" title="Edit class details" style="width: 80px !important; padding: 6px 10px !important; background: #1976D2 !important; color: white !important; border: none !important; border-radius: 5px !important; font-size: 12px !important; font-weight: 500 !important; cursor: pointer !important; display: inline-block !important; text-align: center !important; line-height: 1.2 !important; box-sizing: border-box !important; white-space: nowrap !important; margin: 0 2px !important;">Edit</button>
                            <button type="button" class="btn-delete" onclick="deleteClass('${cls.code}'); return false;" title="Delete class" style="width: 80px !important; padding: 6px 10px !important; background: #D32F2F !important; color: white !important; border: none !important; border-radius: 5px !important; font-size: 12px !important; font-weight: 500 !important; cursor: pointer !important; display: inline-block !important; text-align: center !important; line-height: 1.2 !important; box-sizing: border-box !important; white-space: nowrap !important; margin: 0 2px !important;">Delete</button>
                        </div>
                    </td>
                </tr>
            `).join('');
            console.log('[BUTTON_FIX] Rendered', data.classes.length, 'classes with INLINE STYLES for uniform button width');
            
            // Enhanced debug logging for button rendering with width measurements
            setTimeout(() => {
                const buttons = document.querySelectorAll('.action-buttons');
                console.log('[BUTTON_FIX] Action button containers found:', buttons.length);
                console.log('[BUTTON_FIX] === DETAILED BUTTON ANALYSIS ===');
                
                buttons.forEach((container, index) => {
                    const saveBtn = container.querySelector('.btn-save');
                    const editBtn = container.querySelector('.btn-edit');
                    const deleteBtn = container.querySelector('.btn-delete');
                    
                    console.log(`[BUTTON_FIX] Row ${index + 1} Analysis:`);
                    
                    if (saveBtn) {
                        const saveBtnStyles = window.getComputedStyle(saveBtn);
                        const saveBtnRect = saveBtn.getBoundingClientRect();
                        console.log(`  Save Button: ${saveBtnRect.width}px wide, ${saveBtnRect.height}px high`);
                        console.log(`    CSS width: ${saveBtnStyles.width}, padding: ${saveBtnStyles.padding}`);
                        console.log(`    Background: ${saveBtnStyles.backgroundColor}`);
                    }
                    
                    if (editBtn) {
                        const editBtnStyles = window.getComputedStyle(editBtn);
                        const editBtnRect = editBtn.getBoundingClientRect();
                        console.log(`  Edit Button: ${editBtnRect.width}px wide, ${editBtnRect.height}px high`);
                        console.log(`    CSS width: ${editBtnStyles.width}, padding: ${editBtnStyles.padding}`);
                        console.log(`    Background: ${editBtnStyles.backgroundColor}`);
                    }
                    
                    if (deleteBtn) {
                        const deleteBtnStyles = window.getComputedStyle(deleteBtn);
                        const deleteBtnRect = deleteBtn.getBoundingClientRect();
                        console.log(`  Delete Button: ${deleteBtnRect.width}px wide, ${deleteBtnRect.height}px high`);
                        console.log(`    CSS width: ${deleteBtnStyles.width}, padding: ${deleteBtnStyles.padding}`);
                        console.log(`    Background: ${deleteBtnStyles.backgroundColor}`);
                    }
                    
                    // Check for width consistency
                    const widths = [saveBtn, editBtn, deleteBtn].map(btn => btn ? btn.getBoundingClientRect().width : 0);
                    const uniqueWidths = [...new Set(widths.filter(w => w > 0))];
                    
                    if (uniqueWidths.length === 1) {
                        console.log(`  ✅ Row ${index + 1}: All buttons have consistent width (${uniqueWidths[0]}px)`);
                    } else {
                        console.log(`  ❌ Row ${index + 1}: INCONSISTENT widths detected:`, widths);
                    }
                    
                    console.log(`  Container alignment: ${window.getComputedStyle(container).justifyContent}`);
                    console.log('  ---');
                });
                
                // Overall width consistency check
                const allButtons = document.querySelectorAll('.btn-save, .btn-edit, .btn-delete');
                const allWidths = Array.from(allButtons).map(btn => btn.getBoundingClientRect().width);
                const allUniqueWidths = [...new Set(allWidths)];
                
                console.log(`[BUTTON_FIX] === OVERALL CONSISTENCY CHECK ===`);
                console.log(`Total buttons found: ${allButtons.length}`);
                console.log(`Unique widths: ${allUniqueWidths.length} (${allUniqueWidths.join(', ')}px)`);
                
                if (allUniqueWidths.length === 1) {
                    console.log('✅ SUCCESS: All buttons have consistent width!');
                } else {
                    console.log('❌ FAILURE: Buttons still have inconsistent widths');
                    console.log('Width distribution:', allWidths);
                }
                
                // Add hover effects using JavaScript since inline styles can't handle :hover
                allButtons.forEach(btn => {
                    const originalBg = btn.style.backgroundColor;
                    const hoverColors = {
                        'rgb(46, 125, 50)': '#1B5E20',  // Save hover
                        'rgb(25, 118, 210)': '#1565C0', // Edit hover  
                        'rgb(211, 47, 47)': '#B71C1C'   // Delete hover
                    };
                    
                    btn.addEventListener('mouseenter', () => {
                        const hoverColor = hoverColors[originalBg];
                        if (hoverColor) {
                            btn.style.backgroundColor = hoverColor + ' !important';
                            btn.style.transform = 'translateY(-1px)';
                            btn.style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.2)';
                        }
                    });
                    
                    btn.addEventListener('mouseleave', () => {
                        btn.style.backgroundColor = originalBg + ' !important';
                        btn.style.transform = 'none';
                        btn.style.boxShadow = 'none';
                    });
                });
                
                console.log('[BUTTON_FIX] Hover effects applied to all buttons');
            }, 200);
        } else {
            tableBody.innerHTML = '<tr><td colspan="7" style="text-align: center;">No classes found. Create your first class!</td></tr>';
            console.log('[BUTTON_FIX] No classes to display');
        }
    } catch (error) {
        console.error('[BUTTON_FIX] Error loading admin classes:', error);
    }
}

// Update curriculum mapping dropdowns
function updateCurriculumMapping(classCode, field) {
    const progSelect = document.getElementById(`prog-${classCode}`);
    const subProgSelect = document.getElementById(`subprog-${classCode}`);
    const levelSelect = document.getElementById(`level-${classCode}`);
    
    if (field === 'program') {
        const program = progSelect.value;
        
        // Reset and populate subprogram dropdown
        if (program) {
            subProgSelect.disabled = false;
            subProgSelect.innerHTML = '<option value="">-- Select --</option>' +
                CURRICULUM_STRUCTURE[program].subPrograms.map(sp => 
                    `<option value="${sp}">${sp}</option>`
                ).join('');
            
            // Reset level dropdown
            levelSelect.disabled = true;
            levelSelect.innerHTML = '<option value="">-- Select --</option>';
        } else {
            subProgSelect.disabled = true;
            subProgSelect.innerHTML = '<option value="">-- Select --</option>';
            levelSelect.disabled = true;
            levelSelect.innerHTML = '<option value="">-- Select --</option>';
        }
    } else if (field === 'subprogram') {
        const program = progSelect.value;
        const subprogram = subProgSelect.value;
        
        // Enable and populate level dropdown
        if (subprogram) {
            levelSelect.disabled = false;
            levelSelect.innerHTML = '<option value="">-- Select --</option>' +
                CURRICULUM_STRUCTURE[program].levels.map(level => 
                    `<option value="${level}">Level ${level}</option>`
                ).join('');
        } else {
            levelSelect.disabled = true;
            levelSelect.innerHTML = '<option value="">-- Select --</option>';
        }
    }
    
    // Update display
    updateCurriculumDisplay(classCode);
}

// Update curriculum display
function updateCurriculumDisplay(classCode) {
    const progSelect = document.getElementById(`prog-${classCode}`);
    const subProgSelect = document.getElementById(`subprog-${classCode}`);
    const levelSelect = document.getElementById(`level-${classCode}`);
    const display = document.getElementById(`curr-display-${classCode}`);
    
    const program = progSelect.value;
    const subprogram = subProgSelect.value;
    const level = levelSelect.value;
    
    if (program && subprogram && level) {
        display.textContent = `${program} × ${subprogram} × Level ${level}`;
        display.style.color = '#2E7D32';
    } else {
        display.textContent = 'Not Assigned';
        display.style.color = '#E65100';
    }
}

// Save curriculum mapping
async function saveCurriculumMapping(classCode) {
    console.log('[BUTTON_FIX] Save button clicked for class:', classCode);
    const progSelect = document.getElementById(`prog-${classCode}`);
    const subProgSelect = document.getElementById(`subprog-${classCode}`);
    const levelSelect = document.getElementById(`level-${classCode}`);
    
    const data = {
        class_code: classCode,
        program: progSelect.value,
        subprogram: subProgSelect.value,
        level: levelSelect.value,
        academic_year: (window.PrimePath?.config?.getCurrentYear?.() || new Date().getFullYear()).toString()  // Use ConfigService
    };
    
    try {
        const response = await fetch('/RoutineTest/api/admin/curriculum-mapping/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            alert('Curriculum mapping saved successfully!');
            updateCurriculumDisplay(classCode);
        } else {
            alert('Failed to save curriculum mapping');
        }
    } catch (error) {
        console.error('Error saving curriculum mapping:', error);
        alert('Error saving curriculum mapping');
    }
}

// Show create class dialog
function showCreateClassDialog() {
    editingClassCode = null;
    document.getElementById('classModalTitle').textContent = 'Create New Class';
    document.getElementById('classForm').reset();
    document.getElementById('subProgramSelect').disabled = true;
    document.getElementById('levelSelect').disabled = true;
    document.getElementById('classManagementModal').style.display = 'flex';
}

// Edit existing class
async function editClass(classCode) {
    console.log('[BUTTON_FIX] Edit button clicked for class:', classCode);
    editingClassCode = classCode;
    document.getElementById('classModalTitle').textContent = 'Edit Class';
    
    try {
        const response = await fetch(`/RoutineTest/api/admin/class/${classCode}/`);
        const data = await response.json();
        
        document.getElementById('classCode').value = data.code;
        // Class name field has been removed from UI
        
        if (data.program) {
            document.getElementById('programSelect').value = data.program;
            loadSubPrograms();
            
            if (data.subprogram) {
                setTimeout(() => {
                    document.getElementById('subProgramSelect').value = data.subprogram;
                    loadLevels();
                    
                    if (data.level) {
                        setTimeout(() => {
                            document.getElementById('levelSelect').value = data.level;
                        }, 100);
                    }
                }, 100);
            }
        }
        
        document.getElementById('classManagementModal').style.display = 'flex';
    } catch (error) {
        console.error('Error loading class details:', error);
        alert('Error loading class details');
    }
}

// Delete class
async function deleteClass(classCode) {
    console.log('[BUTTON_FIX] Delete button clicked for class:', classCode);
    if (!confirm(`Are you sure you want to delete class ${classCode}? This action cannot be undone.`)) {
        console.log('[BUTTON_FIX] Delete cancelled by user');
        return;
    }
    
    try {
        const response = await fetch(`/RoutineTest/api/admin/class/${classCode}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        
        if (response.ok) {
            alert('Class deleted successfully!');
            document.getElementById(`class-row-${classCode}`).remove();
        } else {
            alert('Failed to delete class');
        }
    } catch (error) {
        console.error('Error deleting class:', error);
        alert('Error deleting class');
    }
}

// Load subprograms based on selected program
function loadSubPrograms() {
    const program = document.getElementById('programSelect').value;
    const subProgramSelect = document.getElementById('subProgramSelect');
    const levelSelect = document.getElementById('levelSelect');
    
    if (program) {
        subProgramSelect.disabled = false;
        subProgramSelect.innerHTML = '<option value="">-- Select Sub-Program --</option>' +
            CURRICULUM_STRUCTURE[program].subPrograms.map(sp => 
                `<option value="${sp}">${sp}</option>`
            ).join('');
    } else {
        subProgramSelect.disabled = true;
        subProgramSelect.innerHTML = '<option value="">-- Select Sub-Program --</option>';
        levelSelect.disabled = true;
        levelSelect.innerHTML = '<option value="">-- Select Level --</option>';
    }
}

// Load levels based on selected subprogram
function loadLevels() {
    const program = document.getElementById('programSelect').value;
    const subprogram = document.getElementById('subProgramSelect').value;
    const levelSelect = document.getElementById('levelSelect');
    
    if (program && subprogram) {
        levelSelect.disabled = false;
        levelSelect.innerHTML = '<option value="">-- Select Level --</option>' +
            CURRICULUM_STRUCTURE[program].levels.map(level => 
                `<option value="${level}">Level ${level}</option>`
            ).join('');
    } else {
        levelSelect.disabled = true;
        levelSelect.innerHTML = '<option value="">-- Select Level --</option>';
    }
}

// Close class modal
function closeClassModal() {
    document.getElementById('classManagementModal').style.display = 'none';
    editingClassCode = null;
}

// Save class (create or update)
async function saveClass() {
    const classCode = document.getElementById('classCode').value;
    // Class name is now auto-generated from class code
    const className = classCode; // Use class code as the name
    const program = document.getElementById('programSelect').value;
    const subprogram = document.getElementById('subProgramSelect').value;
    const level = document.getElementById('levelSelect').value;
    
    if (!classCode) {
        alert('Please fill in Class Code');
        return;
    }
    
    const data = {
        code: classCode,
        name: className,
        program: program,
        subprogram: subprogram,
        level: level,
        academic_year: (window.PrimePath?.config?.getCurrentYear?.() || new Date().getFullYear()).toString()  // Use ConfigService
    };
    
    try {
        const url = editingClassCode 
            ? `/RoutineTest/api/admin/class/${editingClassCode}/`
            : '/RoutineTest/api/admin/class/';
        
        const method = editingClassCode ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            alert(editingClassCode ? 'Class updated successfully!' : 'Class created successfully!');
            closeClassModal();
            loadAdminClasses();
        } else {
            const error = await response.json();
            alert('Failed to save class: ' + (error.error || error.message || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error saving class:', error);
        alert('Error saving class');
    }
}

// Refresh class list
function refreshClassList() {
    loadAdminClasses();
}

// Helper function to get CSRF token
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
    console.log('[BUTTON_FIX] DOM loaded, checking for admin section...');
    // Check if admin section exists
    const adminSection = document.querySelector('.admin-section');
    if (adminSection) {
        console.log('[BUTTON_FIX] Admin section found, loading classes...');
        loadAdminClasses();
        
        // Additional debug check for button visibility
        setTimeout(() => {
            const allButtons = document.querySelectorAll('.btn-save, .btn-edit, .btn-delete');
            console.log('[BUTTON_FIX] Total buttons rendered:', allButtons.length);
            console.log('[BUTTON_FIX] Button breakdown:', {
                save: document.querySelectorAll('.btn-save').length,
                edit: document.querySelectorAll('.btn-edit').length,
                delete: document.querySelectorAll('.btn-delete').length
            });
            
            // Check for any text overlay issues
            allButtons.forEach(btn => {
                const rect = btn.getBoundingClientRect();
                const styles = window.getComputedStyle(btn);
                if (rect.width < 50 || rect.height < 20) {
                    console.warn('[BUTTON_FIX] Potential button size issue:', btn.textContent, rect);
                }
                if (styles.position === 'absolute') {
                    console.warn('[BUTTON_FIX] Button has absolute positioning which may cause overlay:', btn.textContent);
                }
            });
        }, 500);
    } else {
        console.log('[BUTTON_FIX] No admin section found, skipping class load');
    }
});