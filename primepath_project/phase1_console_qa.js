
// ===== PHASE 1 CLEANUP VERIFICATION =====
// Add this to browser console or base.html temporarily

(function() {
    console.log('%c===== PHASE 1 CLEANUP QA =====', 'color: blue; font-weight: bold');
    
    // Check critical modules
    const modules = ['answerManager', 'pdfViewer', 'timer', 'navigationModule'];
    modules.forEach(mod => {
        if (typeof window[mod] !== 'undefined') {
            console.log(`✅ ${mod} loaded`);
        } else {
            console.warn(`⚠️ ${mod} not found (check if needed)`);
        }
    });
    
    // Check API endpoints
    fetch('/api/placement/exams/')
        .then(r => {
            console.log('✅ Exam API accessible');
            return r.json();
        })
        .then(data => console.log(`  Found ${data.length || 0} exams`))
        .catch(e => console.error('❌ Exam API error:', e));
    
    // Check authentication
    if (document.querySelector('.nav-tabs')) {
        console.log('✅ Navigation loaded');
    }
    
    // Check for any 404s or errors
    const checkForErrors = () => {
        const errors = document.querySelectorAll('.error, .alert-error');
        if (errors.length > 0) {
            console.error('❌ Error messages found:', errors);
        } else {
            console.log('✅ No error messages');
        }
    };
    
    setTimeout(checkForErrors, 1000);
    
    console.log('%c===== END QA CHECK =====', 'color: blue; font-weight: bold');
})();
