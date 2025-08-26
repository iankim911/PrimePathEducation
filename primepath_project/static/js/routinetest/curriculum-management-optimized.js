/**
 * OPTIMIZED Curriculum Management System
 * Admin-only functionality for managing class-curriculum mappings
 * Enhanced with auto-save, bulk operations, and improved UX
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

// Global state management
let editingClassCode = null;
let selectedClasses = new Set();
let allClasses = [];
let filteredClasses = [];
let autoSaveTimeouts = new Map();
let searchTimeout = null;

// Load all classes for admin management
async function loadAdminClasses() {
    console.log('[CURRICULUM_UI] Loading optimized curriculum management...');
    try {
        const currentYear = window.PrimePath?.config?.getCurrentYear?.() || new Date().getFullYear();
        console.log(`[CURRICULUM_UI] Using year: ${currentYear}`);
        const response = await fetch(`/RoutineTest/api/admin/classes/?year=${currentYear}`);
        const data = await response.json();
        console.log('[CURRICULUM_UI] Received classes data:', data);
        
        allClasses = data.classes || [];
        filteredClasses = [...allClasses];
        renderClassTable(filteredClasses);
        updateClassCount();
        initializeSearchAndFilters();
    } catch (error) {
        console.error('[CURRICULUM_UI] Error loading admin classes:', error);
    }
}

// Render the optimized class table
function renderClassTable(classes) {
    console.log('[CURRICULUM_UI] Rendering optimized table with', classes.length, 'classes');
    
    const tableBody = document.getElementById('adminClassTableBody');
    if (!tableBody) return;
    
    if (classes && classes.length > 0) {
        tableBody.innerHTML = classes.map(cls => {
            const curriculumStatus = getCurriculumStatus(cls);
            return `
                <tr id="class-row-${cls.code}" class="class-table-row fade-in">
                    <td class="checkbox-column">
                        <input type="checkbox" class="class-checkbox" data-class="${cls.code}" onchange="handleClassSelection()">
                    </td>
                    <td class="class-code-column sticky-column">
                        <strong>${cls.code}</strong>
                    </td>
                    <td class="curriculum-status-column">
                        <div class="curriculum-status-badge ${curriculumStatus.assigned ? 'assigned' : 'not-assigned'}" id="curr-display-${cls.code}">
                            ${curriculumStatus.display}
                            <span class="save-indicator" id="save-indicator-${cls.code}"></span>
                        </div>
                    </td>
                    <td class="program-column">
                        <select class="curriculum-select" id="prog-${cls.code}" onchange="handleCurriculumChange('${cls.code}', 'program')">
                            <option value="">Select Program</option>
                            ${Object.keys(CURRICULUM_STRUCTURE).map(key => 
                                `<option value="${key}" ${cls.program === key ? 'selected' : ''}>${CURRICULUM_STRUCTURE[key].name}</option>`
                            ).join('')}
                        </select>
                    </td>
                    <td class="subprogram-column">
                        <select class="curriculum-select" id="subprog-${cls.code}" onchange="handleCurriculumChange('${cls.code}', 'subprogram')" 
                                ${!cls.program ? 'disabled' : ''}>
                            <option value="">Select Sub-Program</option>
                            ${cls.program ? CURRICULUM_STRUCTURE[cls.program].subPrograms.map(sp => 
                                `<option value="${sp}" ${cls.subprogram === sp ? 'selected' : ''}>${sp}</option>`
                            ).join('') : ''}
                        </select>
                    </td>
                    <td class="level-column">
                        <select class="curriculum-select" id="level-${cls.code}" onchange="handleCurriculumChange('${cls.code}', 'level')"
                                ${!cls.subprogram ? 'disabled' : ''}>
                            <option value="">Select Level</option>
                            ${cls.program ? CURRICULUM_STRUCTURE[cls.program].levels.map(level => 
                                `<option value="${level}" ${cls.level === level ? 'selected' : ''}>Level ${level}</option>`
                            ).join('') : ''}
                        </select>
                    </td>
                    <td class="actions-column">
                        <div class="action-menu">
                            <button class="action-menu-trigger" onclick="toggleActionMenu('${cls.code}')" title="More actions">
                                ⋯
                            </button>
                            <div class="action-menu-dropdown" id="action-menu-${cls.code}">
                                <button class="action-menu-item" onclick="editClass('${cls.code}')">
                                    ✏️ Edit Details
                                </button>
                                <button class="action-menu-item delete-item" onclick="deleteClass('${cls.code}')">
                                    🗑️ Delete Class
                                </button>
                            </div>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');
        
        console.log('[CURRICULUM_UI] Rendered', classes.length, 'classes in optimized table');
        initializeEnhancedTable();
    } else {
        tableBody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 40px;">No classes found. Create your first class!</td></tr>';
        console.log('[CURRICULUM_UI] No classes to display');
    }
}

// Get curriculum status for display
function getCurriculumStatus(cls) {
    if (cls.program && cls.subprogram && cls.level) {
        return {
            assigned: true,
            display: `${cls.program} × ${cls.subprogram} × Level ${cls.level}`
        };
    } else {
        return {
            assigned: false,
            display: 'Not Assigned'
        };
    }
}

// Initialize enhanced table interactions
function initializeEnhancedTable() {
    // Close action menus when clicking elsewhere
    document.addEventListener('click', (event) => {
        if (!event.target.closest('.action-menu')) {
            document.querySelectorAll('.action-menu-dropdown.show').forEach(menu => {
                menu.classList.remove('show');
            });
        }
    });
}

// Handle curriculum field changes with auto-save
function handleCurriculumChange(classCode, field) {
    console.log('[CURRICULUM_UI] Curriculum changed:', classCode, field);
    
    updateCurriculumMapping(classCode, field);
    
    // Clear existing timeout
    if (autoSaveTimeouts.has(classCode)) {
        clearTimeout(autoSaveTimeouts.get(classCode));
    }
    
    // Show saving indicator
    showSaveIndicator(classCode, 'saving');
    
    // Set auto-save timeout
    const timeout = setTimeout(() => {
        autoSaveCurriculumMapping(classCode);
        autoSaveTimeouts.delete(classCode);
    }, 1500); // 1.5 second delay for auto-save
    
    autoSaveTimeouts.set(classCode, timeout);
}

// Auto-save curriculum mapping
async function autoSaveCurriculumMapping(classCode) {
    console.log('[CURRICULUM_UI] Auto-saving curriculum for:', classCode);
    
    const progSelect = document.getElementById(`prog-${classCode}`);
    const subProgSelect = document.getElementById(`subprog-${classCode}`);
    const levelSelect = document.getElementById(`level-${classCode}`);
    
    const data = {
        class_code: classCode,
        program: progSelect.value,
        subprogram: subProgSelect.value,
        level: levelSelect.value,
        academic_year: (window.PrimePath?.config?.getCurrentYear?.() || new Date().getFullYear()).toString()
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
            showSaveIndicator(classCode, 'saved');
            updateCurriculumDisplay(classCode);
            
            // Update the class in allClasses array
            const classIndex = allClasses.findIndex(cls => cls.code === classCode);
            if (classIndex !== -1) {
                allClasses[classIndex] = { ...allClasses[classIndex], ...data };
            }
            
            // Hide indicator after 2 seconds
            setTimeout(() => showSaveIndicator(classCode, ''), 2000);
        } else {
            showSaveIndicator(classCode, 'error');
            console.error('[CURRICULUM_UI] Failed to auto-save curriculum mapping');
        }
    } catch (error) {
        showSaveIndicator(classCode, 'error');
        console.error('[CURRICULUM_UI] Error auto-saving curriculum mapping:', error);
    }
}

// Show save indicator
function showSaveIndicator(classCode, status) {
    const indicator = document.getElementById(`save-indicator-${classCode}`);
    if (!indicator) return;
    
    indicator.className = `save-indicator ${status}`;
    
    switch (status) {
        case 'saving':
            indicator.textContent = '💾 Saving...';
            break;
        case 'saved':
            indicator.textContent = '✅ Saved';
            break;
        case 'error':
            indicator.textContent = '❌ Error';
            break;
        default:
            indicator.textContent = '';
            break;
    }
}

// Update curriculum mapping dropdowns (enhanced)
function updateCurriculumMapping(classCode, field) {
    const progSelect = document.getElementById(`prog-${classCode}`);
    const subProgSelect = document.getElementById(`subprog-${classCode}`);
    const levelSelect = document.getElementById(`level-${classCode}`);
    
    if (field === 'program') {
        const program = progSelect.value;
        
        // Reset and populate subprogram dropdown
        if (program) {
            subProgSelect.disabled = false;
            subProgSelect.innerHTML = '<option value="">Select Sub-Program</option>' +
                CURRICULUM_STRUCTURE[program].subPrograms.map(sp => 
                    `<option value="${sp}">${sp}</option>`
                ).join('');
            
            // Reset level dropdown
            levelSelect.disabled = true;
            levelSelect.innerHTML = '<option value="">Select Level</option>';
        } else {
            subProgSelect.disabled = true;
            subProgSelect.innerHTML = '<option value="">Select Sub-Program</option>';
            levelSelect.disabled = true;
            levelSelect.innerHTML = '<option value="">Select Level</option>';
        }
    } else if (field === 'subprogram') {
        const program = progSelect.value;
        const subprogram = subProgSelect.value;
        
        // Enable and populate level dropdown
        if (subprogram) {
            levelSelect.disabled = false;
            levelSelect.innerHTML = '<option value="">Select Level</option>' +
                CURRICULUM_STRUCTURE[program].levels.map(level => 
                    `<option value="${level}">Level ${level}</option>`
                ).join('');
        } else {
            levelSelect.disabled = true;
            levelSelect.innerHTML = '<option value="">Select Level</option>';
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
    
    if (!display) return;
    
    const program = progSelect.value;
    const subprogram = subProgSelect.value;
    const level = levelSelect.value;
    
    if (program && subprogram && level) {
        display.innerHTML = `${program} × ${subprogram} × Level ${level} <span class="save-indicator" id="save-indicator-${classCode}"></span>`;
        display.className = 'curriculum-status-badge assigned';
    } else {
        display.innerHTML = `Not Assigned <span class="save-indicator" id="save-indicator-${classCode}"></span>`;
        display.className = 'curriculum-status-badge not-assigned';
    }
}

// Toggle action menu
function toggleActionMenu(classCode) {
    const menu = document.getElementById(`action-menu-${classCode}`);
    if (menu) {
        // Close other menus
        document.querySelectorAll('.action-menu-dropdown.show').forEach(otherMenu => {
            if (otherMenu !== menu) {
                otherMenu.classList.remove('show');
            }
        });
        
        menu.classList.toggle('show');
    }
}

// Class selection handling
function handleClassSelection() {
    const checkboxes = document.querySelectorAll('.class-checkbox:checked');
    selectedClasses.clear();
    
    checkboxes.forEach(checkbox => {
        selectedClasses.add(checkbox.dataset.class);
    });
    
    updateBulkActionsVisibility();
    updateSelectedCount();
}

// Toggle select all classes
function toggleSelectAllClasses() {
    const headerCheckbox = document.getElementById('headerSelectAll');
    const selectAllCheckbox = document.getElementById('selectAllClasses');
    const checkboxes = document.querySelectorAll('.class-checkbox');
    
    const isChecked = headerCheckbox?.checked || selectAllCheckbox?.checked;
    
    checkboxes.forEach(checkbox => {
        checkbox.checked = isChecked;
    });
    
    if (headerCheckbox && selectAllCheckbox) {
        headerCheckbox.checked = isChecked;
        selectAllCheckbox.checked = isChecked;
    }
    
    handleClassSelection();
}

// Update bulk actions visibility
function updateBulkActionsVisibility() {
    const toolbar = document.getElementById('bulkActionsToolbar');
    if (toolbar) {
        if (selectedClasses.size > 0) {
            toolbar.style.display = 'flex';
        } else {
            toolbar.style.display = 'none';
        }
    }
}

// Update selected count
function updateSelectedCount() {
    const countElement = document.getElementById('selectedCount');
    if (countElement) {
        countElement.textContent = `${selectedClasses.size} selected`;
    }
    
    const bulkCountElement = document.getElementById('bulkSelectedCount');
    if (bulkCountElement) {
        bulkCountElement.textContent = selectedClasses.size;
    }
}

// Initialize search and filters
function initializeSearchAndFilters() {
    const searchInput = document.getElementById('classSearchFilter');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                filterClasses(e.target.value);
            }, 300);
        });
    }
}

// Filter classes based on search
function filterClasses(searchTerm) {
    const term = searchTerm.toLowerCase().trim();
    
    if (term === '') {
        filteredClasses = [...allClasses];
    } else {
        filteredClasses = allClasses.filter(cls => 
            cls.code.toLowerCase().includes(term) ||
            cls.curriculum?.toLowerCase().includes(term) ||
            cls.program?.toLowerCase().includes(term) ||
            cls.subprogram?.toLowerCase().includes(term)
        );
    }
    
    renderClassTable(filteredClasses);
    updateClassCount();
}

// Update class count indicator
function updateClassCount() {
    const indicator = document.getElementById('classCountIndicator');
    if (indicator) {
        indicator.textContent = `Showing ${filteredClasses.length} of ${allClasses.length} classes`;
    }
}

// Bulk assignment functions
function showBulkAssignModal() {
    if (selectedClasses.size === 0) {
        alert('Please select classes to assign curriculum to.');
        return;
    }
    
    document.getElementById('bulkAssignModal').style.display = 'block';
}

function closeBulkAssignModal() {
    document.getElementById('bulkAssignModal').style.display = 'none';
    
    // Reset form
    document.getElementById('bulkProgramSelect').value = '';
    document.getElementById('bulkSubProgramSelect').value = '';
    document.getElementById('bulkSubProgramSelect').disabled = true;
    document.getElementById('bulkLevelSelect').value = '';
    document.getElementById('bulkLevelSelect').disabled = true;
}

function loadBulkSubPrograms() {
    const program = document.getElementById('bulkProgramSelect').value;
    const subProgramSelect = document.getElementById('bulkSubProgramSelect');
    const levelSelect = document.getElementById('bulkLevelSelect');
    
    if (program) {
        subProgramSelect.disabled = false;
        subProgramSelect.innerHTML = '<option value="">Select Sub-Program</option>' +
            CURRICULUM_STRUCTURE[program].subPrograms.map(sp => 
                `<option value="${sp}">${sp}</option>`
            ).join('');
    } else {
        subProgramSelect.disabled = true;
        subProgramSelect.innerHTML = '<option value="">Select Sub-Program</option>';
        levelSelect.disabled = true;
        levelSelect.innerHTML = '<option value="">Select Level</option>';
    }
}

function loadBulkLevels() {
    const program = document.getElementById('bulkProgramSelect').value;
    const subprogram = document.getElementById('bulkSubProgramSelect').value;
    const levelSelect = document.getElementById('bulkLevelSelect');
    
    if (program && subprogram) {
        levelSelect.disabled = false;
        levelSelect.innerHTML = '<option value="">Select Level</option>' +
            CURRICULUM_STRUCTURE[program].levels.map(level => 
                `<option value="${level}">Level ${level}</option>`
            ).join('');
    } else {
        levelSelect.disabled = true;
        levelSelect.innerHTML = '<option value="">Select Level</option>';
    }
}

async function executeBulkAssignment() {
    const program = document.getElementById('bulkProgramSelect').value;
    const subprogram = document.getElementById('bulkSubProgramSelect').value;
    const level = document.getElementById('bulkLevelSelect').value;
    
    if (!program || !subprogram || !level) {
        alert('Please select program, sub-program, and level for bulk assignment.');
        return;
    }
    
    const promises = Array.from(selectedClasses).map(classCode => {
        const data = {
            class_code: classCode,
            program: program,
            subprogram: subprogram,
            level: level,
            academic_year: (window.PrimePath?.config?.getCurrentYear?.() || new Date().getFullYear()).toString()
        };
        
        return fetch('/RoutineTest/api/admin/curriculum-mapping/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(data)
        });
    });
    
    try {
        const responses = await Promise.all(promises);
        const successCount = responses.filter(r => r.ok).length;
        
        alert(`Bulk assignment completed! ${successCount} out of ${selectedClasses.size} classes updated successfully.`);
        
        closeBulkAssignModal();
        loadAdminClasses(); // Refresh the table
        
        // Clear selections
        selectedClasses.clear();
        document.querySelectorAll('.class-checkbox').forEach(cb => cb.checked = false);
        updateBulkActionsVisibility();
        updateSelectedCount();
        
    } catch (error) {
        console.error('[CURRICULUM_UI] Error in bulk assignment:', error);
        alert('Error occurred during bulk assignment. Please try again.');
    }
}

// Confirm bulk delete
function confirmBulkDelete() {
    if (selectedClasses.size === 0) {
        alert('Please select classes to delete.');
        return;
    }
    
    if (confirm(`Are you sure you want to delete ${selectedClasses.size} selected classes? This action cannot be undone.`)) {
        executeBulkDelete();
    }
}

async function executeBulkDelete() {
    const promises = Array.from(selectedClasses).map(classCode => 
        fetch(`/RoutineTest/api/admin/class/${classCode}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
    );
    
    try {
        const responses = await Promise.all(promises);
        const successCount = responses.filter(r => r.ok).length;
        
        alert(`Bulk deletion completed! ${successCount} out of ${selectedClasses.size} classes deleted successfully.`);
        
        loadAdminClasses(); // Refresh the table
        
        // Clear selections
        selectedClasses.clear();
        updateBulkActionsVisibility();
        updateSelectedCount();
        
    } catch (error) {
        console.error('[CURRICULUM_UI] Error in bulk deletion:', error);
        alert('Error occurred during bulk deletion. Please try again.');
    }
}

// Enhanced edit class function
async function editClass(classCode) {
    console.log('[CURRICULUM_UI] Edit button clicked for class:', classCode);
    editingClassCode = classCode;
    
    // Close action menu
    const menu = document.getElementById(`action-menu-${classCode}`);
    if (menu) menu.classList.remove('show');
    
    document.getElementById('classModalTitle').textContent = 'Edit Class';
    
    try {
        const response = await fetch(`/RoutineTest/api/admin/class/${classCode}/`);
        const data = await response.json();
        
        document.getElementById('classCode').value = data.code;
        
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
        console.error('[CURRICULUM_UI] Error loading class details:', error);
        alert('Error loading class details');
    }
}

// Enhanced delete class function
async function deleteClass(classCode) {
    console.log('[CURRICULUM_UI] Delete button clicked for class:', classCode);
    
    // Close action menu
    const menu = document.getElementById(`action-menu-${classCode}`);
    if (menu) menu.classList.remove('show');
    
    if (!confirm(`Are you sure you want to delete class ${classCode}? This action cannot be undone.`)) {
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
            // Add highlight animation before removal
            const row = document.getElementById(`class-row-${classCode}`);
            if (row) {
                row.classList.add('row-highlight');
                setTimeout(() => {
                    row.remove();
                }, 600);
            }
            
            // Update arrays
            allClasses = allClasses.filter(cls => cls.code !== classCode);
            filteredClasses = filteredClasses.filter(cls => cls.code !== classCode);
            updateClassCount();
            
            alert('Class deleted successfully!');
        } else {
            alert('Failed to delete class');
        }
    } catch (error) {
        console.error('[CURRICULUM_UI] Error deleting class:', error);
        alert('Error deleting class');
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

// Load subprograms based on selected program
function loadSubPrograms() {
    const program = document.getElementById('programSelect').value;
    const subProgramSelect = document.getElementById('subProgramSelect');
    const levelSelect = document.getElementById('levelSelect');
    
    if (program) {
        subProgramSelect.disabled = false;
        subProgramSelect.innerHTML = '<option value="">Select Sub-Program</option>' +
            CURRICULUM_STRUCTURE[program].subPrograms.map(sp => 
                `<option value="${sp}">${sp}</option>`
            ).join('');
    } else {
        subProgramSelect.disabled = true;
        subProgramSelect.innerHTML = '<option value="">Select Sub-Program</option>';
        levelSelect.disabled = true;
        levelSelect.innerHTML = '<option value="">Select Level</option>';
    }
}

// Load levels based on selected subprogram
function loadLevels() {
    const program = document.getElementById('programSelect').value;
    const subprogram = document.getElementById('subProgramSelect').value;
    const levelSelect = document.getElementById('levelSelect');
    
    if (program && subprogram) {
        levelSelect.disabled = false;
        levelSelect.innerHTML = '<option value="">Select Level</option>' +
            CURRICULUM_STRUCTURE[program].levels.map(level => 
                `<option value="${level}">Level ${level}</option>`
            ).join('');
    } else {
        levelSelect.disabled = true;
        levelSelect.innerHTML = '<option value="">Select Level</option>';
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
        academic_year: (window.PrimePath?.config?.getCurrentYear?.() || new Date().getFullYear()).toString()
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
        console.error('[CURRICULUM_UI] Error saving class:', error);
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
    console.log('[CURRICULUM_UI] DOM loaded, checking for optimized admin section...');
    
    // Check if optimized admin section exists
    const adminSection = document.querySelector('.optimized-curriculum-management');
    if (adminSection) {
        console.log('[CURRICULUM_UI] Optimized admin section found, loading classes...');
        loadAdminClasses();
        
        // Initialize keyboard shortcuts
        initializeKeyboardShortcuts();
    } else {
        // Fallback to original admin section
        const originalAdminSection = document.querySelector('.admin-section');
        if (originalAdminSection) {
            console.log('[CURRICULUM_UI] Fallback to original admin section...');
            loadAdminClasses();
        } else {
            console.log('[CURRICULUM_UI] No admin section found, skipping class load');
        }
    }
});

// Initialize keyboard shortcuts
function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + A to select all
        if ((e.ctrlKey || e.metaKey) && e.key === 'a' && e.target.closest('.optimized-curriculum-management')) {
            e.preventDefault();
            toggleSelectAllClasses();
        }
        
        // Escape to close modals/menus
        if (e.key === 'Escape') {
            // Close bulk assign modal
            if (document.getElementById('bulkAssignModal').style.display === 'block') {
                closeBulkAssignModal();
            }
            
            // Close class modal
            if (document.getElementById('classManagementModal').style.display === 'flex') {
                closeClassModal();
            }
            
            // Close action menus
            document.querySelectorAll('.action-menu-dropdown.show').forEach(menu => {
                menu.classList.remove('show');
            });
        }
    });
}

// Global functions for backward compatibility
window.saveCurriculumMapping = autoSaveCurriculumMapping;
window.updateCurriculumMapping = updateCurriculumMapping;