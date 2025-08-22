// Debug script to test copy modal timing issues
// Paste this into the browser console when the exam library page loads

console.log('=== COPY MODAL DEBUG TIMING TEST ===');

// Check if curriculum data exists
console.log('1. Curriculum Data Check:');
console.log('   window.CopyCurriculumData exists:', !!window.CopyCurriculumData);
if (window.CopyCurriculumData) {
    console.log('   Programs available:', Object.keys(window.CopyCurriculumData));
    console.log('   CORE subprograms:', window.CopyCurriculumData.CORE ? Object.keys(window.CopyCurriculumData.CORE.subprograms) : 'N/A');
} else {
    console.log('   ❌ No curriculum data available');
}

// Check if DOM elements exist
console.log('\n2. DOM Elements Check:');
const programSelect = document.getElementById('copyProgramSelect');
console.log('   copyProgramSelect element exists:', !!programSelect);
if (programSelect) {
    console.log('   Current options count:', programSelect.options.length);
    console.log('   Options:', Array.from(programSelect.options).map(o => o.textContent));
} else {
    console.log('   ❌ copyProgramSelect element not found');
}

// Check if functions exist
console.log('\n3. Function Availability:');
console.log('   populateCopyProgramDropdown exists:', typeof window.populateCopyProgramDropdown);
console.log('   initializeCopyCurriculumCascading exists:', typeof window.initializeCopyCurriculumCascading);

// Try to manually trigger the functions
console.log('\n4. Manual Function Test:');
if (typeof window.populateCopyProgramDropdown === 'function') {
    console.log('   Calling populateCopyProgramDropdown()...');
    try {
        window.populateCopyProgramDropdown();
        console.log('   ✅ Function called successfully');
        
        // Check results
        if (programSelect) {
            console.log('   New options count:', programSelect.options.length);
            console.log('   New options:', Array.from(programSelect.options).map(o => o.textContent));
        }
    } catch (error) {
        console.log('   ❌ Function call failed:', error);
    }
} else {
    console.log('   ❌ populateCopyProgramDropdown function not available');
}

// Test opening copy modal
console.log('\n5. Copy Modal Test:');
if (typeof window.openCopyModal === 'function') {
    console.log('   openCopyModal function available');
    console.log('   To test: openCopyModal("test-id", "Test Exam")');
} else {
    console.log('   ❌ openCopyModal function not available');
}

console.log('\n=== END DEBUG TEST ===');