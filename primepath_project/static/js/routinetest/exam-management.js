/**
 * Exam Management System
 * Handles all exam-related operations for RoutineTest module
 */

let currentClassCode = null;
let currentTimeslot = null;
let currentAccessLevel = null;

// Open exam management modal
function openExamModal(classCode, timeslot, accessLevel = 'VIEW') {
    currentClassCode = classCode;
    currentTimeslot = timeslot;
    currentAccessLevel = accessLevel;
    
    // Update modal header
    document.getElementById('modalClassCode').textContent = classCode;
    document.getElementById('modalTimeslot').textContent = timeslot;
    
    // Load data for all tabs
    loadOverviewData(classCode, timeslot);
    loadExamData(classCode, timeslot);
    loadStudentData(classCode);
    
    // Show modal
    document.getElementById('examManagementModal').style.display = 'flex';
    
    // Reset to first tab
    showTab('overview');
}

// Close modal
function closeExamModal() {
    document.getElementById('examManagementModal').style.display = 'none';
    currentClassCode = null;
    currentTimeslot = null;
}

// Tab navigation
function showTab(tabName) {
    // Remove active class from all tabs and panes
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });
    
    // Add active class to selected tab and pane
    document.querySelector(`[data-tab="${tabName}"]`).parentElement.classList.add('active');
    document.getElementById(tabName).classList.add('active');
}

// Load overview data
async function loadOverviewData(classCode, timeslot) {
    try {
        const response = await fetch(`/routinetest/api/class/${classCode}/overview/?timeslot=${timeslot}`);
        const data = await response.json();
        
        // Update overview fields
        document.getElementById('overviewClassCode').textContent = classCode;
        document.getElementById('overviewCurriculum').textContent = data.curriculum || 'Not Assigned';
        document.getElementById('overviewPeriod').textContent = timeslot;
        document.getElementById('overviewAccessLevel').textContent = currentAccessLevel;
        
        // Update current exams list
        const examsList = document.getElementById('currentExamsList');
        if (data.exams && data.exams.length > 0) {
            examsList.innerHTML = data.exams.map(exam => `
                <div class="exam-item">
                    <strong>${exam.name}</strong> - ${exam.type}
                    <span class="exam-status">${exam.status}</span>
                </div>
            `).join('');
        } else {
            examsList.innerHTML = '<p class="no-data">No exams assigned for this period</p>';
        }
    } catch (error) {
        console.error('Error loading overview data:', error);
    }
}

// Load exam data
async function loadExamData(classCode, timeslot) {
    try {
        const response = await fetch(`/routinetest/api/class/${classCode}/exams/?timeslot=${timeslot}`);
        const data = await response.json();
        
        const tableBody = document.getElementById('examTableBody');
        if (data.exams && data.exams.length > 0) {
            tableBody.innerHTML = data.exams.map(exam => `
                <tr>
                    <td>${exam.name}</td>
                    <td>${exam.type}</td>
                    <td>${exam.duration} min</td>
                    <td>${exam.question_count}</td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="editExam('${exam.id}')">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-warning" onclick="editDuration('${exam.id}', ${exam.duration})">
                            <i class="fas fa-clock"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteExam('${exam.id}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
            
            // Populate schedule dropdown
            const scheduleSelect = document.getElementById('scheduleExamSelect');
            scheduleSelect.innerHTML = '<option value="">-- Select Exam --</option>' +
                data.exams.map(exam => `<option value="${exam.id}">${exam.name}</option>`).join('');
        } else {
            tableBody.innerHTML = '<tr><td colspan="5" class="text-center">No exams assigned</td></tr>';
        }
    } catch (error) {
        console.error('Error loading exam data:', error);
    }
}

// Load student data
async function loadStudentData(classCode) {
    try {
        const response = await fetch(`/routinetest/api/class/${classCode}/students/`);
        const data = await response.json();
        
        // Update student stats
        document.getElementById('totalStudents').textContent = data.total || 0;
        document.getElementById('activeStudents').textContent = data.active || 0;
        
        // Update student table
        const tableBody = document.getElementById('studentTableBody');
        if (data.students && data.students.length > 0) {
            tableBody.innerHTML = data.students.map(student => `
                <tr>
                    <td>${student.id}</td>
                    <td>${student.name}</td>
                    <td>${student.email}</td>
                    <td><span class="badge ${student.status === 'Active' ? 'badge-success' : 'badge-secondary'}">${student.status}</span></td>
                    <td>${student.last_activity || 'Never'}</td>
                </tr>
            `).join('');
        } else {
            tableBody.innerHTML = '<tr><td colspan="5" class="text-center">No students enrolled</td></tr>';
        }
    } catch (error) {
        console.error('Error loading student data:', error);
    }
}

// Show copy exam dialog
async function showCopyExamDialog() {
    document.getElementById('copyExamDialog').style.display = 'block';
    
    // Load all classes
    try {
        const response = await fetch('/routinetest/api/all-classes/');
        const data = await response.json();
        
        const select = document.getElementById('sourceClassSelect');
        select.innerHTML = '<option value="">-- Select Class --</option>' +
            data.classes.map(cls => 
                `<option value="${cls.code}">${cls.code} - ${cls.name}</option>`
            ).join('');
    } catch (error) {
        console.error('Error loading classes:', error);
    }
}

// Hide copy exam dialog
function hideCopyExamDialog() {
    document.getElementById('copyExamDialog').style.display = 'none';
}

// Load exams for selected source class
document.getElementById('sourceClassSelect')?.addEventListener('change', async function() {
    const classCode = this.value;
    const examSelect = document.getElementById('sourceExamSelect');
    
    if (!classCode) {
        examSelect.disabled = true;
        examSelect.innerHTML = '<option value="">-- Select Exam --</option>';
        return;
    }
    
    try {
        const response = await fetch(`/routinetest/api/class/${classCode}/all-exams/`);
        const data = await response.json();
        
        examSelect.disabled = false;
        examSelect.innerHTML = '<option value="">-- Select Exam --</option>' +
            data.exams.map(exam => 
                `<option value="${exam.id}">${exam.name} (${exam.type})</option>`
            ).join('');
    } catch (error) {
        console.error('Error loading source exams:', error);
    }
});

// Copy selected exam
async function copySelectedExam() {
    const sourceExamId = document.getElementById('sourceExamSelect').value;
    
    if (!sourceExamId) {
        alert('Please select an exam to copy');
        return;
    }
    
    try {
        const response = await fetch('/routinetest/api/copy-exam/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                source_exam_id: sourceExamId,
                target_class: currentClassCode,
                target_timeslot: currentTimeslot
            })
        });
        
        if (response.ok) {
            alert('Exam copied successfully!');
            hideCopyExamDialog();
            loadExamData(currentClassCode, currentTimeslot);
        } else {
            alert('Failed to copy exam');
        }
    } catch (error) {
        console.error('Error copying exam:', error);
        alert('Error copying exam');
    }
}

// Delete exam
async function deleteExam(examId) {
    if (!confirm('Are you sure you want to delete this exam?')) {
        return;
    }
    
    try {
        const response = await fetch(`/routinetest/api/exam/${examId}/delete/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        
        if (response.ok) {
            alert('Exam deleted successfully!');
            loadExamData(currentClassCode, currentTimeslot);
        } else {
            alert('Failed to delete exam');
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
        const response = await fetch(`/routinetest/api/exam/${examId}/duration/`, {
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
        const response = await fetch('/routinetest/api/schedule-exam/', {
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