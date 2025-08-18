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
    try {
        const response = await fetch('/routinetest/api/admin/classes/');
        const data = await response.json();
        
        const tableBody = document.getElementById('adminClassTableBody');
        if (!tableBody) return;
        
        if (data.classes && data.classes.length > 0) {
            tableBody.innerHTML = data.classes.map(cls => `
                <tr id="class-row-${cls.code}">
                    <td>${cls.code}</td>
                    <td>${cls.name}</td>
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
                        <button class="btn-save" onclick="saveCurriculumMapping('${cls.code}')">Save</button>
                        <button class="btn-edit" onclick="editClass('${cls.code}')">Edit</button>
                        <button class="btn-delete" onclick="deleteClass('${cls.code}')">Delete</button>
                    </td>
                </tr>
            `).join('');
        } else {
            tableBody.innerHTML = '<tr><td colspan="7" style="text-align: center;">No classes found. Create your first class!</td></tr>';
        }
    } catch (error) {
        console.error('Error loading admin classes:', error);
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
    const progSelect = document.getElementById(`prog-${classCode}`);
    const subProgSelect = document.getElementById(`subprog-${classCode}`);
    const levelSelect = document.getElementById(`level-${classCode}`);
    
    const data = {
        class_code: classCode,
        program: progSelect.value,
        subprogram: subProgSelect.value,
        level: levelSelect.value
    };
    
    try {
        const response = await fetch('/routinetest/api/admin/curriculum-mapping/', {
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
    editingClassCode = classCode;
    document.getElementById('classModalTitle').textContent = 'Edit Class';
    
    try {
        const response = await fetch(`/routinetest/api/admin/class/${classCode}/`);
        const data = await response.json();
        
        document.getElementById('classCode').value = data.code;
        document.getElementById('className').value = data.name;
        
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
    if (!confirm(`Are you sure you want to delete class ${classCode}? This action cannot be undone.`)) {
        return;
    }
    
    try {
        const response = await fetch(`/routinetest/api/admin/class/${classCode}/`, {
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
    const className = document.getElementById('className').value;
    const program = document.getElementById('programSelect').value;
    const subprogram = document.getElementById('subProgramSelect').value;
    const level = document.getElementById('levelSelect').value;
    
    if (!classCode || !className) {
        alert('Please fill in Class Code and Class Name');
        return;
    }
    
    const data = {
        code: classCode,
        name: className,
        program: program,
        subprogram: subprogram,
        level: level
    };
    
    try {
        const url = editingClassCode 
            ? `/routinetest/api/admin/class/${editingClassCode}/`
            : '/routinetest/api/admin/class/';
        
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
            alert('Failed to save class: ' + (error.message || 'Unknown error'));
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
    // Check if admin section exists
    const adminSection = document.querySelector('.admin-section');
    if (adminSection) {
        loadAdminClasses();
    }
});