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
            // Enhanced error handling for specific status codes
            let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
            if (response.status === 404) {
                errorMessage = `Class "${classCode}" not found or no data available`;
            } else if (response.status === 403) {
                errorMessage = 'Access denied - insufficient permissions';
            } else if (response.status === 500) {
                errorMessage = 'Server error - please try again later';
            }
            throw new Error(errorMessage);
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
                        <button class="btn btn-sm btn-primary exam-btn" onclick="editExam('${exam.id}')" title="Edit exam details">
                            <i class="fas fa-edit"></i> Edit
                        </button>
                        <button class="btn btn-sm btn-warning exam-btn" onclick="editDuration('${exam.id}', ${exam.duration || 60})" title="Change exam duration">
                            <i class="fas fa-clock"></i> Duration
                        </button>
                        <button class="btn btn-sm btn-danger exam-btn" onclick="deleteExam('${exam.id}')" title="Remove exam from class">
                            <i class="fas fa-trash"></i> Delete
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
            // Enhanced error handling for specific status codes
            let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
            if (response.status === 404) {
                errorMessage = `No student data found for class "${classCode}"`;
            } else if (response.status === 403) {
                errorMessage = 'Access denied - insufficient permissions';
            } else if (response.status === 500) {
                errorMessage = 'Server error - please try again later';
            }
            throw new Error(errorMessage);
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

// Step 4: Enable copy button when exam is selected (only if not already assigned)
document.getElementById('sourceExamSelect')?.addEventListener('change', function() {
    const examId = this.value;
    const selectedOption = this.options[this.selectedIndex];
    const copyBtn = document.getElementById('copyExamBtn');
    
    // Check if the selected exam is already assigned (disabled option)
    const isAlreadyAssigned = selectedOption && selectedOption.disabled;
    
    // Only enable copy button if exam is selected and not already assigned
    copyBtn.disabled = !examId || isAlreadyAssigned;
    
    if (examId && !isAlreadyAssigned) {
        console.log(`Exam selected: ${examId}. Copy button enabled.`);
    } else if (isAlreadyAssigned) {
        console.log(`Exam selected but already assigned: ${examId}. Copy button disabled.`);
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

// Check which exams are already assigned to target class
async function checkExistingAssignments(exams) {
    try {
        // Get the target timeslot for checking
        const examType = document.getElementById('examTypeSelect').value;
        const month = document.getElementById('monthSelect').value;
        const quarter = document.getElementById('quarterSelect').value;
        
        let targetTimeslot = '';
        if (examType === 'REVIEW' && month) {
            targetTimeslot = month;
        } else if (examType === 'QUARTERLY' && quarter) {
            targetTimeslot = quarter;
        }
        
        if (!targetTimeslot || !currentClassCode) {
            // No target info available, return exams without status
            return exams.map(exam => 
                `<option value="${exam.id}">${exam.name}</option>`
            ).join('');
        }
        
        // Check existing assignments in target class
        const response = await fetch(`/RoutineTest/api/class/${currentClassCode}/existing-exams/?timeslot=${targetTimeslot}`);
        
        if (!response.ok) {
            throw new Error('Could not check existing assignments');
        }
        
        const existingData = await response.json();
        const existingExamIds = new Set(existingData.existing_exams.map(exam => exam.id));
        
        // Create options with status indicators
        return exams.map(exam => {
            const isAlreadyAssigned = existingExamIds.has(exam.id);
            const optionText = isAlreadyAssigned ? 
                `${exam.name} (Already assigned)` : 
                exam.name;
            const optionClass = isAlreadyAssigned ? ' style="color: #dc3545; font-style: italic;"' : '';
            const disabled = isAlreadyAssigned ? ' disabled' : '';
            
            return `<option value="${exam.id}"${optionClass}${disabled}>${optionText}</option>`;
        }).join('');
        
    } catch (error) {
        console.warn('Error checking existing assignments:', error);
        // Return exams without status indicators on error
        return exams.map(exam => 
            `<option value="${exam.id}">${exam.name}</option>`
        ).join('');
    }
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
            // Show user-friendly message from API if available
            const message = data.message || 'No matching exams found';
            examSelect.innerHTML = `<option value="">${message}</option>`;
            
            // Show helpful exam count information
            if (data.filters_applied && data.filters_applied.total_system_wide > 0) {
                examCount.textContent = `${data.filters_applied.total_system_wide} exam(s) exist system-wide but none assigned to this class`;
            } else {
                examCount.textContent = message;
            }
            examSelect.disabled = true;
        } else {
            // Check which exams are already assigned to the target class
            checkExistingAssignments(data.exams).then(examOptionsWithStatus => {
                examSelect.innerHTML = '<option value="">-- Select Exam --</option>' + examOptionsWithStatus;
                examCount.textContent = `${data.exams.length} exam(s) found`;
            }).catch(error => {
                console.warn('Could not check existing assignments, showing all exams:', error);
                // Fallback: show all exams without status indicators
                examSelect.innerHTML = '<option value="">-- Select Exam --</option>' +
                    data.exams.map(exam => 
                        `<option value="${exam.id}">${exam.name}</option>`
                    ).join('');
                examCount.textContent = `${data.exams.length} exam(s) found`;
            });
        }
        
        console.log(`Loaded ${data.exams.length} filtered exams for class ${classCode}`);
    } catch (error) {
        console.error('Error loading filtered exams at loadMatchingExams:', error);
        examSelect.disabled = true;
        
        // Provide different error messages based on error type
        if (error.message.includes('Authentication required')) {
            examSelect.innerHTML = '<option value="">Please log in and try again</option>';
            examCount.textContent = 'Authentication required';
        } else if (error.message.includes('HTTP error! status: 500')) {
            examSelect.innerHTML = '<option value="">Server error - please try again</option>';
            examCount.textContent = 'Server error occurred';
        } else if (error.message.includes('HTTP error! status: 404')) {
            examSelect.innerHTML = '<option value="">Class not found</option>';
            examCount.textContent = 'Selected class not found';
        } else {
            examSelect.innerHTML = '<option value="">Unable to load exams</option>';
            examCount.textContent = 'Unable to load exams. Please try again.';
        }
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
    
    // Check if selected exam is already assigned
    const selectedOption = document.getElementById('sourceExamSelect').options[document.getElementById('sourceExamSelect').selectedIndex];
    if (selectedOption && selectedOption.disabled) {
        alert('This exam is already assigned to the target class and time period.\\n\\nEach exam can only be assigned once per class/period.');
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
            // CRITICAL FIX: Use the actual time period that was copied to, not the original currentTimeslot
            // This ensures the UI shows the copied exam immediately
            loadExamData(currentClassCode, timePeriod);
            // Also refresh overview data to update exam counts
            loadOverviewData(currentClassCode, timePeriod);
            console.log('Copy exam success:', result);
        } else {
            // Enhanced error handling for different error types
            if (result.error_type === 'DUPLICATE_ASSIGNMENT') {
                // More user-friendly error for duplicates
                const message = `This exam has already been copied to ${currentClassCode} for ${timePeriod}.\n\n` +
                    `Each exam can only be assigned once per class and time period. ` +
                    `If you need to update the exam, you can delete the existing one first and then copy the new version.`;
                alert(message);
            } else {
                const errorMsg = result.error || 'Failed to copy exam';
                alert(`Failed to copy exam: ${errorMsg}`);
            }
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

// Delete exam (enhanced with better confirmation and error handling)
async function deleteExam(examId) {
    console.log(`[EXAM_DELETE] Attempting to delete exam ID: ${examId}`);
    
    // Enhanced confirmation dialog with more details
    const confirmMessage = `Delete Exam Confirmation\n\n` +
        `This will permanently delete the exam and all associated data.\n` +
        `This action cannot be undone.\n\n` +
        `Are you sure you want to proceed?`;
    
    if (!confirm(confirmMessage)) {
        console.log('[EXAM_DELETE] User cancelled deletion');
        return;
    }
    
    // Show loading state
    const deleteButton = document.querySelector(`button[onclick*="deleteExam('${examId}')"]`);
    if (deleteButton) {
        deleteButton.disabled = true;
        deleteButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Deleting...';
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
            const result = await response.json().catch(() => ({}));
            console.log('[EXAM_DELETE] Delete successful:', result);
            
            alert('Exam deleted successfully!');
            
            // Refresh the exam list and overview
            loadExamData(currentClassCode, currentTimeslot);
            loadOverviewData(currentClassCode, currentTimeslot);
            
        } else if (response.status === 302 || response.redirected) {
            // Authentication redirect - user needs to log in
            console.error('[EXAM_DELETE] Authentication required');
            alert('Session expired. Please log in again.');
            window.location.href = '/login/';
            
        } else if (response.status === 405) {
            // Method not allowed - check if this is actually an auth redirect
            console.error('[EXAM_DELETE] Method not allowed');
            alert('Delete operation not allowed. Please check your permissions.');
            
        } else if (response.status === 403) {
            console.error('[EXAM_DELETE] Access denied');
            alert('Access denied. You do not have permission to delete this exam.');
            
        } else if (response.status === 404) {
            console.error('[EXAM_DELETE] Exam not found');
            alert('Exam not found. It may have already been deleted.');
            
            // Still refresh the list to remove from UI
            loadExamData(currentClassCode, currentTimeslot);
            loadOverviewData(currentClassCode, currentTimeslot);
            
        } else {
            const errorText = await response.text();
            console.error('[EXAM_DELETE] Delete failed:', response.status, errorText);
            alert(`Failed to delete exam: HTTP ${response.status}`);
        }
        
    } catch (error) {
        console.error('[EXAM_DELETE] Error deleting exam:', error);
        
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            alert('Network error. Please check your connection and try again.');
        } else {
            alert(`Error deleting exam: ${error.message}`);
        }
    } finally {
        // Restore button state
        if (deleteButton) {
            deleteButton.disabled = false;
            deleteButton.innerHTML = '<i class="fas fa-trash"></i> Delete';
        }
    }
}

// Edit exam (main edit function)
async function editExam(examId) {
    console.log(`[EXAM_EDIT] Opening edit dialog for exam ID: ${examId}`);
    
    // Show loading state
    const editButton = document.querySelector(`button[onclick*="editExam('${examId}')"]`);
    if (editButton) {
        editButton.disabled = true;
        editButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
    }
    
    try {
        // Fetch current exam data
        const response = await fetch(`/RoutineTest/api/exam/${examId}/details/`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const examData = await response.json();
        console.log('[EXAM_EDIT] Exam data loaded:', examData);
        
        // Create and show edit modal
        showExamEditDialog(examId, examData);
        
    } catch (error) {
        console.error('[EXAM_EDIT] Error loading exam details:', error);
        
        // Show user-friendly error based on error type
        if (error.message.includes('404')) {
            alert('Exam not found. It may have been deleted.');
        } else if (error.message.includes('403')) {
            alert('Access denied. You do not have permission to edit this exam.');
        } else {
            alert(`Failed to load exam details: ${error.message}`);
        }
    } finally {
        // Restore button state
        if (editButton) {
            editButton.disabled = false;
            editButton.innerHTML = '<i class="fas fa-edit"></i> Edit';
        }
    }
}

// Show exam edit dialog
function showExamEditDialog(examId, examData) {
    console.log('[EXAM_EDIT_DIALOG] Showing edit dialog for exam:', examData);
    
    // Create modal HTML
    const modalHTML = `
        <div id="examEditModal" class="modal" style="display: flex;">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h4 class="modal-title">Edit Exam: ${examData.name || 'Unnamed Exam'}</h4>
                        <button type="button" class="close-modal" onclick="closeExamEditDialog()">\u00d7</button>
                    </div>
                    <div class="modal-body">
                        <form id="examEditForm">
                            <div class="form-group">
                                <label for="examName">Exam Name:</label>
                                <input type="text" id="examName" class="form-control" 
                                       value="${examData.name || ''}" 
                                       placeholder="Enter exam name" required>
                            </div>
                            
                            <div class="form-group">
                                <label for="examType">Exam Type:</label>
                                <select id="examType" class="form-control">
                                    <option value="REVIEW" ${examData.type === 'REVIEW' ? 'selected' : ''}>Review / Monthly</option>
                                    <option value="QUARTERLY" ${examData.type === 'QUARTERLY' ? 'selected' : ''}>Quarterly</option>
                                </select>
                            </div>
                            
                            <div class="form-group">
                                <label for="examDurationEdit">Duration (minutes):</label>
                                <input type="number" id="examDurationEdit" class="form-control" 
                                       value="${examData.duration || 60}" 
                                       min="15" max="300" required>
                            </div>
                            
                            <div class="form-group">
                                <label for="examDescription">Description:</label>
                                <textarea id="examDescription" class="form-control" rows="3" 
                                          placeholder="Optional exam description">${examData.description || ''}</textarea>
                            </div>
                            
                            <div class="form-group">
                                <label>Question Count:</label>
                                <p class="form-text">${examData.question_count || 0} questions</p>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" onclick="closeExamEditDialog()">Cancel</button>
                        <button type="button" class="btn btn-primary" onclick="saveExamChanges('${examId}')">
                            <i class="fas fa-save"></i> Save Changes
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if any
    const existingModal = document.getElementById('examEditModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add modal to page
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

// Close exam edit dialog
function closeExamEditDialog() {
    const modal = document.getElementById('examEditModal');
    if (modal) {
        modal.remove();
    }
}

// Save exam changes
async function saveExamChanges(examId) {
    console.log(`[EXAM_SAVE] Saving changes for exam ID: ${examId}`);
    
    // Get form data
    const examName = document.getElementById('examName').value.trim();
    const examType = document.getElementById('examType').value;
    const examDuration = parseInt(document.getElementById('examDurationEdit').value);
    const examDescription = document.getElementById('examDescription').value.trim();
    
    // Validation
    if (!examName) {
        alert('Please enter an exam name.');
        return;
    }
    
    if (!examType) {
        alert('Please select an exam type.');
        return;
    }
    
    if (!examDuration || examDuration < 15 || examDuration > 300) {
        alert('Please enter a valid duration between 15 and 300 minutes.');
        return;
    }
    
    // Show loading state
    const saveButton = document.querySelector('button[onclick*="saveExamChanges"]');
    if (saveButton) {
        saveButton.disabled = true;
        saveButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
    }
    
    try {
        const response = await fetch(`/RoutineTest/api/exam/${examId}/update/`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                name: examName,
                type: examType,
                duration: examDuration,
                description: examDescription
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('[EXAM_SAVE] Save successful:', result);
            
            alert('Exam updated successfully!');
            closeExamEditDialog();
            
            // Refresh the exam list
            loadExamData(currentClassCode, currentTimeslot);
            loadOverviewData(currentClassCode, currentTimeslot);
            
        } else {
            const errorData = await response.json().catch(() => ({}));
            const errorMessage = errorData.error || `HTTP ${response.status}: ${response.statusText}`;
            throw new Error(errorMessage);
        }
        
    } catch (error) {
        console.error('[EXAM_SAVE] Error saving exam:', error);
        
        // Show user-friendly error
        if (error.message.includes('403')) {
            alert('Access denied. You do not have permission to edit this exam.');
        } else if (error.message.includes('404')) {
            alert('Exam not found. It may have been deleted.');
        } else {
            alert(`Failed to save exam: ${error.message}`);
        }
    } finally {
        // Restore button state
        if (saveButton) {
            saveButton.disabled = false;
            saveButton.innerHTML = '<i class="fas fa-save"></i> Save Changes';
        }
    }
}

// Edit exam duration (enhanced version with better UI)
async function editDuration(examId, currentDuration) {
    console.log(`[DURATION_EDIT] Editing duration for exam ID: ${examId}, current: ${currentDuration}`);
    
    // Create a more user-friendly dialog
    const newDuration = prompt(
        `Edit Exam Duration\n\nCurrent duration: ${currentDuration} minutes\n\nEnter new duration (15-300 minutes):`, 
        currentDuration
    );
    
    // Validate input
    if (!newDuration) {
        console.log('[DURATION_EDIT] User cancelled');
        return;
    }
    
    const duration = parseInt(newDuration);
    
    if (isNaN(duration)) {
        alert('Please enter a valid number.');
        return;
    }
    
    if (duration < 15 || duration > 300) {
        alert('Duration must be between 15 and 300 minutes.');
        return;
    }
    
    if (duration === currentDuration) {
        console.log('[DURATION_EDIT] No change in duration');
        return;
    }
    
    // Show loading state
    const durationButton = document.querySelector(`button[onclick*="editDuration('${examId}'"]`);
    if (durationButton) {
        durationButton.disabled = true;
        durationButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Updating...';
    }
    
    try {
        const response = await fetch(`/RoutineTest/api/exam/${examId}/duration/`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                duration: duration
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('[DURATION_EDIT] Update successful:', result);
            
            alert(`Duration updated successfully! New duration: ${duration} minutes`);
            
            // Refresh the exam list to show updated duration
            loadExamData(currentClassCode, currentTimeslot);
            
        } else {
            const errorData = await response.json().catch(() => ({}));
            const errorMessage = errorData.error || `HTTP ${response.status}: ${response.statusText}`;
            throw new Error(errorMessage);
        }
        
    } catch (error) {
        console.error('[DURATION_EDIT] Error updating duration:', error);
        
        // Show user-friendly error
        if (error.message.includes('403')) {
            alert('Access denied. You do not have permission to edit this exam.');
        } else if (error.message.includes('404')) {
            alert('Exam not found. It may have been deleted.');
        } else {
            alert(`Failed to update duration: ${error.message}`);
        }
    } finally {
        // Restore button state
        if (durationButton) {
            durationButton.disabled = false;
            durationButton.innerHTML = '<i class="fas fa-clock"></i> Duration';
        }
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