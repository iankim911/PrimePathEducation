/**
 * Exam Management System
 * Handles all exam-related operations for RoutineTest module
 */

let currentClassCode = null;
let currentTimeslot = null;
let currentAccessLevel = null;

// Open exam management modal
function openExamModal(classCode, timeslot, accessLevel = 'VIEW') {
    console.log(`[EXAM_MODAL] Opening modal for class: ${classCode}, timeslot: ${timeslot}, access: ${accessLevel}`);
    
    // Validate required elements exist
    const modal = document.getElementById('examManagementModal');
    if (!modal) {
        console.error('[EXAM_MODAL] Modal element not found!');
        alert('Modal not available. Please refresh the page.');
        return;
    }
    
    const modalClassCode = document.getElementById('modalClassCode');
    const modalTimeslot = document.getElementById('modalTimeslot');
    
    if (!modalClassCode || !modalTimeslot) {
        console.error('[EXAM_MODAL] Modal header elements not found!');
    }
    
    // Store current context
    currentClassCode = classCode;
    currentTimeslot = timeslot;
    currentAccessLevel = accessLevel;
    
    // Update modal header with defensive checks
    if (modalClassCode) modalClassCode.textContent = classCode || 'Unknown Class';
    if (modalTimeslot) modalTimeslot.textContent = timeslot || 'Overview';
    
    // Show modal first
    modal.style.display = 'flex';
    
    // Reset to first tab
    showTab('overview');
    
    // Load data for all tabs with error handling
    try {
        loadOverviewData(classCode, timeslot);
        loadExamData(classCode, timeslot);
        loadStudentData(classCode);
    } catch (error) {
        console.error('[EXAM_MODAL] Error during initial data load:', error);
    }
    
    console.log('[EXAM_MODAL] Modal opened successfully');
}

// Close modal
function closeExamModal() {
    document.getElementById('examManagementModal').style.display = 'none';
    currentClassCode = null;
    currentTimeslot = null;
}

// Tab navigation
function showTab(tabName) {
    console.log(`[EXAM_MODAL] Switching to tab: ${tabName}`);
    
    try {
        // Remove active class from all tabs and panes
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.remove('active');
        });
        
        // Add active class to selected tab and pane
        const tabLink = document.querySelector(`[data-tab="${tabName}"]`);
        const tabPane = document.getElementById(tabName);
        
        if (tabLink && tabLink.parentElement) {
            tabLink.parentElement.classList.add('active');
        } else {
            console.error(`[EXAM_MODAL] Tab link not found for: ${tabName}`);
        }
        
        if (tabPane) {
            tabPane.classList.add('active');
        } else {
            console.error(`[EXAM_MODAL] Tab pane not found for: ${tabName}`);
        }
        
        console.log(`[EXAM_MODAL] Tab switch complete: ${tabName}`);
    } catch (error) {
        console.error(`[EXAM_MODAL] Error switching tabs:`, error);
    }
}

// Load overview data
async function loadOverviewData(classCode, timeslot) {
    console.log(`[EXAM_MODAL] Loading overview data for class: ${classCode}, timeslot: ${timeslot}`);
    
    try {
        const url = `/RoutineTest/api/class/${classCode}/overview/?timeslot=${timeslot}`;
        console.log(`[EXAM_MODAL] Fetching from: ${url}`);
        
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log(`[EXAM_MODAL] Overview data received:`, data);
        
        // Update overview fields with defensive checks
        const overviewClassCode = document.getElementById('overviewClassCode');
        const overviewCurriculum = document.getElementById('overviewCurriculum');
        const overviewPeriod = document.getElementById('overviewPeriod');
        const overviewAccessLevel = document.getElementById('overviewAccessLevel');
        
        if (overviewClassCode) overviewClassCode.textContent = classCode;
        if (overviewCurriculum) overviewCurriculum.textContent = data.curriculum || 'Not Assigned';
        if (overviewPeriod) overviewPeriod.textContent = timeslot || 'Overview';
        if (overviewAccessLevel) overviewAccessLevel.textContent = currentAccessLevel || 'VIEW';
        
        // Update current exams list
        const examsList = document.getElementById('currentExamsList');
        if (examsList) {
            if (data.exams && data.exams.length > 0) {
                examsList.innerHTML = data.exams.map(exam => `
                    <div class="exam-item" style="padding: 8px; margin: 4px 0; background: #f5f5f5; border-radius: 4px;">
                        <strong>${exam.name}</strong> - <span style="color: #666;">${exam.type}</span>
                        <span class="exam-status" style="float: right; color: #2E7D32;">${exam.status}</span>
                    </div>
                `).join('');
            } else {
                examsList.innerHTML = '<p class="no-data" style="text-align: center; color: #666; font-style: italic;">No exams assigned for this period</p>';
            }
        }
    } catch (error) {
        console.error('[EXAM_MODAL] Error loading overview data:', error);
        
        // Show error in UI
        const examsList = document.getElementById('currentExamsList');
        if (examsList) {
            examsList.innerHTML = `<p style="color: red; text-align: center;">Error loading exam data: ${error.message}</p>`;
        }
    }
}

// Load exam data
async function loadExamData(classCode, timeslot) {
    console.log(`[EXAM_MODAL] Loading exam data for class: ${classCode}, timeslot: ${timeslot}`);
    
    try {
        const url = `/RoutineTest/api/class/${classCode}/exams/?timeslot=${timeslot}`;
        console.log(`[EXAM_MODAL] Fetching from: ${url}`);
        
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log(`[EXAM_MODAL] Exam data received:`, data);
        
        const tableBody = document.getElementById('examTableBody');
        if (!tableBody) {
            console.error('[EXAM_MODAL] examTableBody element not found');
            return;
        }
        
        if (data.exams && data.exams.length > 0) {
            tableBody.innerHTML = data.exams.map(exam => `
                <tr>
                    <td>${exam.name || 'Unnamed Exam'}</td>
                    <td>${exam.type || 'Unknown'}</td>
                    <td>${exam.duration || 60} min</td>
                    <td>${exam.question_count || 0}</td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="editExam('${exam.id}')" title="Edit Exam">
                            ✏️
                        </button>
                        <button class="btn btn-sm btn-warning" onclick="editDuration('${exam.id}', ${exam.duration || 60})" title="Edit Duration">
                            ⏱️
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteExam('${exam.id}')" title="Delete Exam">
                            🗑️
                        </button>
                    </td>
                </tr>
            `).join('');
            
            // Populate schedule dropdown
            const scheduleSelect = document.getElementById('scheduleExamSelect');
            if (scheduleSelect) {
                scheduleSelect.innerHTML = '<option value="">-- Select Exam --</option>' +
                    data.exams.map(exam => `<option value="${exam.id}">${exam.name}</option>`).join('');
            }
        } else {
            tableBody.innerHTML = '<tr><td colspan="5" class="text-center" style="color: #666; font-style: italic;">No exams assigned</td></tr>';
            
            // Clear schedule dropdown
            const scheduleSelect = document.getElementById('scheduleExamSelect');
            if (scheduleSelect) {
                scheduleSelect.innerHTML = '<option value="">-- No Exams Available --</option>';
            }
        }
    } catch (error) {
        console.error('[EXAM_MODAL] Error loading exam data:', error);
        
        // Show error in UI
        const tableBody = document.getElementById('examTableBody');
        if (tableBody) {
            tableBody.innerHTML = `<tr><td colspan="5" class="text-center" style="color: red;">Error loading exam data: ${error.message}</td></tr>`;
        }
    }
}

// Load student data
async function loadStudentData(classCode) {
    console.log(`[EXAM_MODAL] Loading student data for class: ${classCode}`);
    
    try {
        const url = `/RoutineTest/api/class/${classCode}/students/`;
        console.log(`[EXAM_MODAL] Fetching from: ${url}`);
        
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log(`[EXAM_MODAL] Student data received:`, data);
        
        // Update student stats with defensive checks
        const totalStudentsEl = document.getElementById('totalStudents');
        const activeStudentsEl = document.getElementById('activeStudents');
        
        if (totalStudentsEl) totalStudentsEl.textContent = data.total || 0;
        if (activeStudentsEl) activeStudentsEl.textContent = data.active || 0;
        
        // Update student table
        const tableBody = document.getElementById('studentTableBody');
        if (!tableBody) {
            console.error('[EXAM_MODAL] studentTableBody element not found');
            return;
        }
        
        if (data.students && data.students.length > 0) {
            tableBody.innerHTML = data.students.map(student => `
                <tr>
                    <td>${student.id || 'N/A'}</td>
                    <td>${student.name || 'Unknown'}</td>
                    <td>${student.email || 'No email'}</td>
                    <td><span class="badge ${student.status === 'Active' ? 'badge-success' : 'badge-secondary'}" style="padding: 2px 6px; border-radius: 3px; color: white; background: ${student.status === 'Active' ? '#28a745' : '#6c757d'};">${student.status || 'Unknown'}</span></td>
                    <td>${student.last_activity || 'Never'}</td>
                </tr>
            `).join('');
        } else {
            tableBody.innerHTML = '<tr><td colspan="5" class="text-center" style="color: #666; font-style: italic;">No students enrolled</td></tr>';
        }
    } catch (error) {
        console.error('[EXAM_MODAL] Error loading student data:', error);
        
        // Show error in UI
        const tableBody = document.getElementById('studentTableBody');
        if (tableBody) {
            tableBody.innerHTML = `<tr><td colspan="5" class="text-center" style="color: red;">Error loading student data: ${error.message}</td></tr>`;
        }
        
        // Reset stats
        const totalStudentsEl = document.getElementById('totalStudents');
        const activeStudentsEl = document.getElementById('activeStudents');
        if (totalStudentsEl) totalStudentsEl.textContent = '0';
        if (activeStudentsEl) activeStudentsEl.textContent = '0';
    }
}

// Show copy exam dialog
async function showCopyExamDialog() {
    document.getElementById('copyExamDialog').style.display = 'block';
    
    // Reset all selectors to initial state
    resetCopyExamDialog();
    
    // Load all classes
    try {
        const response = await fetch('/RoutineTest/api/all-classes/');
        
        if (!response.ok) {
            // Check for authentication redirect (status 302) or unauthorized (401/403)
            if (response.status === 302 || response.status === 401 || response.status === 403) {
                throw new Error('Authentication required. Please log in and try again.');
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // Check content type to ensure we're getting JSON
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            throw new Error(`Expected JSON response, but got: ${contentType}`);
        }
        
        const data = await response.json();
        console.log('Copy exam dialog - API response:', data);
        
        // Check if data.classes exists and is an array
        if (!data.classes || !Array.isArray(data.classes)) {
            console.error('Invalid API response structure. Expected data.classes to be an array, got:', data);
            throw new Error('Invalid API response: classes data not found');
        }
        
        const select = document.getElementById('sourceClassSelect');
        select.innerHTML = '<option value="">-- Select Class --</option>' +
            data.classes.map(cls => 
                `<option value="${cls.code}">${cls.code} - ${cls.name}</option>`
            ).join('');
            
        console.log(`Loaded ${data.classes.length} classes for copying`);
    } catch (error) {
        console.error('Error loading classes:', error);
        
        // Show user-friendly error message
        const select = document.getElementById('sourceClassSelect');
        select.innerHTML = '<option value="">Error loading classes</option>';
        
        // Optionally show an alert to the user
        alert('Failed to load classes. Please try again or contact support if the problem persists.');
    }
}

// Reset copy exam dialog to initial state
function resetCopyExamDialog() {
    // Reset all dropdowns
    document.getElementById('sourceClassSelect').innerHTML = '<option value="">-- Select Class --</option>';
    document.getElementById('examTypeSelect').innerHTML = '<option value="">-- Select Exam Type --</option><option value="REVIEW">Review / Monthly</option><option value="QUARTERLY">Quarterly</option>';
    document.getElementById('monthSelect').innerHTML = '<option value="">-- Select Month --</option><option value="JAN">January</option><option value="FEB">February</option><option value="MAR">March</option><option value="APR">April</option><option value="MAY">May</option><option value="JUN">June</option><option value="JUL">July</option><option value="AUG">August</option><option value="SEP">September</option><option value="OCT">October</option><option value="NOV">November</option><option value="DEC">December</option>';
    document.getElementById('quarterSelect').innerHTML = '<option value="">-- Select Quarter --</option><option value="Q1">Q1 (Jan-Mar)</option><option value="Q2">Q2 (Apr-Jun)</option><option value="Q3">Q3 (Jul-Sep)</option><option value="Q4">Q4 (Oct-Dec)</option>';
    document.getElementById('sourceExamSelect').innerHTML = '<option value="">-- Select Exam --</option>';
    
    // Disable dependent selectors
    document.getElementById('examTypeSelect').disabled = true;
    document.getElementById('monthSelect').disabled = true;
    document.getElementById('quarterSelect').disabled = true;
    document.getElementById('sourceExamSelect').disabled = true;
    document.getElementById('copyExamBtn').disabled = true;
    
    // Hide time period selectors
    document.getElementById('monthSelect').style.display = 'none';
    document.getElementById('quarterSelect').style.display = 'none';
    
    // Clear exam count
    document.getElementById('examCount').textContent = '';
}

// Hide copy exam dialog
function hideCopyExamDialog() {
    document.getElementById('copyExamDialog').style.display = 'none';
    resetCopyExamDialog();
}

// Step 1: Load exam types when source class is selected
document.getElementById('sourceClassSelect')?.addEventListener('change', function() {
    const classCode = this.value;
    const examTypeSelect = document.getElementById('examTypeSelect');
    
    if (!classCode) {
        // Reset all dependent dropdowns
        resetDependentSelectors(['examTypeSelect', 'monthSelect', 'quarterSelect', 'sourceExamSelect']);
        return;
    }
    
    // Enable exam type selector
    examTypeSelect.disabled = false;
    
    // Reset dependent selectors
    resetDependentSelectors(['monthSelect', 'quarterSelect', 'sourceExamSelect']);
    
    console.log(`Source class selected: ${classCode}. Exam type selector enabled.`);
});

// Step 2: Show/hide time period selector when exam type is selected
document.getElementById('examTypeSelect')?.addEventListener('change', function() {
    const examType = this.value;
    const monthSelect = document.getElementById('monthSelect');
    const quarterSelect = document.getElementById('quarterSelect');
    
    if (!examType) {
        // Hide both time period selectors and reset dependent selectors
        monthSelect.style.display = 'none';
        quarterSelect.style.display = 'none';
        resetDependentSelectors(['monthSelect', 'quarterSelect', 'sourceExamSelect']);
        return;
    }
    
    // Show appropriate time period selector based on exam type
    if (examType === 'REVIEW') {
        monthSelect.style.display = 'block';
        quarterSelect.style.display = 'none';
        monthSelect.disabled = false;
        quarterSelect.disabled = true;
        quarterSelect.value = '';
    } else if (examType === 'QUARTERLY') {
        monthSelect.style.display = 'none';
        quarterSelect.style.display = 'block';
        quarterSelect.disabled = false;
        monthSelect.disabled = true;
        monthSelect.value = '';
    }
    
    // Reset exam selector
    resetDependentSelectors(['sourceExamSelect']);
    
    console.log(`Exam type selected: ${examType}. Time period selector updated.`);
});

// Step 3: Load matching exams when time period is selected
document.getElementById('monthSelect')?.addEventListener('change', function() {
    loadMatchingExams();
});

document.getElementById('quarterSelect')?.addEventListener('change', function() {
    loadMatchingExams();
});

// Step 4: Enable copy button when exam is selected
document.getElementById('sourceExamSelect')?.addEventListener('change', function() {
    const examId = this.value;
    const copyBtn = document.getElementById('copyExamBtn');
    
    copyBtn.disabled = !examId;
    
    if (examId) {
        console.log(`Exam selected: ${examId}. Copy button enabled.`);
    }
});

// Helper function to reset dependent selectors
function resetDependentSelectors(selectorIds) {
    selectorIds.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.disabled = true;
            if (id === 'monthSelect' || id === 'quarterSelect') {
                element.style.display = 'none';
                element.value = '';
            } else if (id === 'sourceExamSelect') {
                element.innerHTML = '<option value="">-- Select Exam --</option>';
                document.getElementById('examCount').textContent = '';
            } else if (id === 'examTypeSelect') {
                element.value = '';
            }
        }
    });
    
    // Always disable copy button when resetting
    document.getElementById('copyExamBtn').disabled = true;
}

// Load matching exams based on all selections
async function loadMatchingExams() {
    const classCode = document.getElementById('sourceClassSelect').value;
    const examType = document.getElementById('examTypeSelect').value;
    const month = document.getElementById('monthSelect').value;
    const quarter = document.getElementById('quarterSelect').value;
    const examSelect = document.getElementById('sourceExamSelect');
    const examCount = document.getElementById('examCount');
    
    if (!classCode || !examType) {
        return;
    }
    
    // Determine time period value based on exam type
    let timePeriod = '';
    if (examType === 'REVIEW' && month) {
        timePeriod = month;
    } else if (examType === 'QUARTERLY' && quarter) {
        timePeriod = quarter;
    }
    
    if (!timePeriod) {
        examSelect.disabled = true;
        examSelect.innerHTML = '<option value="">-- Select Exam --</option>';
        examCount.textContent = '';
        return;
    }
    
    try {
        // Build query parameters for filtering
        const params = new URLSearchParams({
            exam_type: examType,
            time_period: timePeriod
        });
        
        const response = await fetch(`/RoutineTest/api/class/${classCode}/filtered-exams/?${params}`);
        
        if (!response.ok) {
            // Check for authentication redirect (status 302) or unauthorized (401/403)
            if (response.status === 302 || response.status === 401 || response.status === 403) {
                throw new Error('Authentication required. Please log in and try again.');
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // Check content type to ensure we're getting JSON
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            throw new Error(`Expected JSON response, but got: ${contentType}`);
        }
        
        const data = await response.json();
        console.log(`Loading filtered exams for class ${classCode}, type ${examType}, period ${timePeriod}:`, data);
        
        // Check if data.exams exists and is an array
        if (!data.exams || !Array.isArray(data.exams)) {
            console.error('Invalid API response structure. Expected data.exams to be an array, got:', data);
            examSelect.disabled = true;
            examSelect.innerHTML = '<option value="">Error loading exams</option>';
            examCount.textContent = 'Error loading exam count';
            return;
        }
        
        examSelect.disabled = false;
        
        if (data.exams.length === 0) {
            examSelect.innerHTML = '<option value="">No matching exams found</option>';
            examCount.textContent = 'No exams found matching your criteria';
            examSelect.disabled = true;
        } else {
            examSelect.innerHTML = '<option value="">-- Select Exam --</option>' +
                data.exams.map(exam => 
                    `<option value="${exam.id}">${exam.name}</option>`
                ).join('');
            examCount.textContent = `${data.exams.length} exam(s) found`;
        }
        
        console.log(`Loaded ${data.exams.length} filtered exams for class ${classCode}`);
    } catch (error) {
        console.error('Error loading filtered exams:', error);
        examSelect.disabled = true;
        examSelect.innerHTML = '<option value="">Error loading exams</option>';
        examCount.textContent = 'Error loading exams';
    }
}

// Copy selected exam
async function copySelectedExam() {
    const sourceExamId = document.getElementById('sourceExamSelect').value;
    const sourceClassCode = document.getElementById('sourceClassSelect').value;
    const examType = document.getElementById('examTypeSelect').value;
    const monthSelect = document.getElementById('monthSelect');
    const quarterSelect = document.getElementById('quarterSelect');
    
    if (!sourceExamId) {
        alert('Please select an exam to copy');
        return;
    }
    
    // Determine the time period based on exam type
    let timePeriod = '';
    if (examType === 'REVIEW') {
        timePeriod = monthSelect.value;
    } else if (examType === 'QUARTERLY') {
        timePeriod = quarterSelect.value;
    }
    
    if (!timePeriod) {
        alert('Please select a time period');
        return;
    }
    
    console.log('Copying exam:', {
        source_exam_id: sourceExamId,
        from_class: sourceClassCode,
        to_class: currentClassCode,
        exam_type: examType,
        time_period: timePeriod
    });
    
    try {
        const response = await fetch('/RoutineTest/api/copy-exam/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                source_exam_id: sourceExamId,
                target_class: currentClassCode,
                target_timeslot: timePeriod  // Use the selected time period (month or quarter)
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            alert('Exam copied successfully!');
            hideCopyExamDialog();
            loadExamData(currentClassCode, currentTimeslot);
            console.log('Copy exam success:', result);
        } else {
            const errorMsg = result.error || 'Failed to copy exam';
            alert(`Failed to copy exam: ${errorMsg}`);
            console.error('Copy exam failed:', result);
        }
    } catch (error) {
        console.error('Error copying exam:', error);
        alert('Error copying exam');
    }
}

// Debug function to test the new workflow (for testing purposes)
function testCopyExamWorkflow() {
    console.log('=== Testing Copy Exam Workflow ===');
    
    const elements = {
        sourceClassSelect: document.getElementById('sourceClassSelect'),
        examTypeSelect: document.getElementById('examTypeSelect'),
        monthSelect: document.getElementById('monthSelect'),
        quarterSelect: document.getElementById('quarterSelect'),
        sourceExamSelect: document.getElementById('sourceExamSelect'),
        copyExamBtn: document.getElementById('copyExamBtn'),
        examCount: document.getElementById('examCount')
    };
    
    console.log('Dialog elements found:', Object.keys(elements).filter(key => elements[key]));
    console.log('Dialog elements missing:', Object.keys(elements).filter(key => !elements[key]));
    
    // Test initial state
    console.log('Initial disabled states:');
    Object.entries(elements).forEach(([name, element]) => {
        if (element && element.disabled !== undefined) {
            console.log(`  ${name}: disabled=${element.disabled}`);
        }
    });
    
    return elements;
}

// Delete exam
async function deleteExam(examId) {
    if (!confirm('Are you sure you want to delete this exam?')) {
        return;
    }
    
    try {
        // Add required query parameters that the backend expects
        // Use default values if not set
        const queryParams = new URLSearchParams({
            class_code: currentClassCode || 'ALL',
            timeslot: currentTimeslot || 'Morning'
        });
        
        const response = await fetch(`/RoutineTest/api/exam/${examId}/delete/?${queryParams}`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        
        if (response.ok) {
            alert('Exam deleted successfully!');
            loadExamData(currentClassCode, currentTimeslot);
        } else if (response.status === 302 || response.redirected) {
            // Authentication redirect - user needs to log in
            alert('Session expired. Please log in again.');
            window.location.href = '/login/';
        } else if (response.status === 405) {
            // Method not allowed - check if this is actually an auth redirect
            alert('Delete operation not allowed. Please check your permissions.');
        } else {
            const errorText = await response.text();
            console.error('Delete failed:', response.status, errorText);
            alert(`Failed to delete exam (${response.status})`);
        }
    } catch (error) {
        console.error('Error deleting exam:', error);
        alert('Error deleting exam');
    }
}

// Edit exam duration
async function editDuration(examId, currentDuration) {
    const newDuration = prompt(`Enter new duration in minutes (current: ${currentDuration}):`, currentDuration);
    
    if (!newDuration || newDuration == currentDuration) {
        return;
    }
    
    try {
        const response = await fetch(`/RoutineTest/api/exam/${examId}/duration/`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                duration: parseInt(newDuration)
            })
        });
        
        if (response.ok) {
            alert('Duration updated successfully!');
            loadExamData(currentClassCode, currentTimeslot);
        } else {
            alert('Failed to update duration');
        }
    } catch (error) {
        console.error('Error updating duration:', error);
        alert('Error updating duration');
    }
}

// Save schedule
async function saveSchedule() {
    const examId = document.getElementById('scheduleExamSelect').value;
    const date = document.getElementById('examDate').value;
    const time = document.getElementById('examTime').value;
    const duration = document.getElementById('examDuration').value;
    
    if (!examId || !date || !time || !duration) {
        alert('Please fill all schedule fields');
        return;
    }
    
    try {
        const response = await fetch('/RoutineTest/api/schedule-exam/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                exam_id: examId,
                date: date,
                time: time,
                duration: parseInt(duration)
            })
        });
        
        if (response.ok) {
            alert('Exam scheduled successfully!');
            document.getElementById('examDate').value = '';
            document.getElementById('examTime').value = '';
            document.getElementById('examDuration').value = '';
            loadScheduledExams();
        } else {
            alert('Failed to schedule exam');
        }
    } catch (error) {
        console.error('Error scheduling exam:', error);
        alert('Error scheduling exam');
    }
}

// Student search
document.getElementById('studentSearch')?.addEventListener('input', function() {
    const searchTerm = this.value.toLowerCase();
    const rows = document.querySelectorAll('#studentTableBody tr');
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(searchTerm) ? '' : 'none';
    });
});

// Export student list
function exportStudentList() {
    // Implement CSV export
    const rows = document.querySelectorAll('#studentTableBody tr');
    let csv = 'Student ID,Name,Email,Status,Last Activity\n';
    
    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        const rowData = Array.from(cells).map(cell => cell.textContent).join(',');
        csv += rowData + '\n';
    });
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${currentClassCode}_students.csv`;
    a.click();
}

// Save Changes button handler
function saveChanges() {
    console.log('SaveChanges button clicked');
    
    // Determine which tab is currently active
    const activeTab = document.querySelector('.tab-btn.active');
    if (!activeTab) {
        console.log('No active tab found');
        closeExamModal();
        return;
    }
    
    const tabName = activeTab.getAttribute('data-tab');
    console.log('Active tab:', tabName);
    
    // Handle save based on active tab
    switch(tabName) {
        case 'overview':
            // No save action needed for overview
            console.log('Overview tab - no save action needed');
            closeExamModal();
            break;
            
        case 'manage':
            // Check if copy exam dialog is open
            const copyDialog = document.getElementById('copyExamDialog');
            if (copyDialog && copyDialog.style.display !== 'none') {
                // If copy dialog is open, trigger the copy action
                const copyBtn = document.getElementById('copyExamBtn');
                if (copyBtn && !copyBtn.disabled) {
                    copySelectedExam();
                } else {
                    alert('Please complete all steps to copy an exam');
                }
            } else {
                // Otherwise just close
                closeExamModal();
            }
            break;
            
        case 'schedule':
            // Save schedule if there are changes
            const scheduleData = document.getElementById('scheduleForm');
            if (scheduleData) {
                saveSchedule();
            } else {
                closeExamModal();
            }
            break;
            
        case 'students':
            // No save action for students tab
            console.log('Students tab - no save action needed');
            closeExamModal();
            break;
            
        default:
            console.log('Unknown tab - closing modal');
            closeExamModal();
    }
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

// Initialize tab clicks
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const tabName = this.getAttribute('data-tab');
            showTab(tabName);
        });
    });
    
    // Close modal on outside click
    document.getElementById('examManagementModal')?.addEventListener('click', function(e) {
        if (e.target === this) {
            closeExamModal();
        }
    });
});