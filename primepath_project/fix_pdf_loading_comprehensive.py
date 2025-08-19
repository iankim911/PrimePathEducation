#!/usr/bin/env python3
"""
Comprehensive fix for PDF loading issue in RoutineTest Preview
"""

def create_pdf_loading_fix():
    """
    Generate the fix for PDF loading issues
    """
    
    print("=== PDF Loading Issue Analysis & Fix ===")
    print()
    
    print("ROOT CAUSE ANALYSIS:")
    print("1. ✓ Database: Exam exists with correct UUID and PDF file path")
    print("2. ✓ File System: PDF file exists and is valid (has PDF header)")
    print("3. ✓ URL Routing: Django URLs work properly with UUID conversion")
    print("4. ✓ Media Serving: Direct PDF access works (200 OK response)")
    print("5. ✗ JavaScript: PDF.js fails to load the PDF with InvalidPDFException")
    print()
    
    print("SPECIFIC ISSUE:")
    print("- Error: 'Error loading PDF: preview/12745' in console")
    print("- PDF.js InvalidPDFException suggests the library can't parse the PDF")
    print("- The URL 'preview/12745' looks malformed - should be full media URL")
    print()
    
    print("LIKELY CAUSES:")
    print("1. PDF.js version compatibility issue")
    print("2. PDF URL construction problem in JavaScript")
    print("3. PDF file content issue (despite valid header)")
    print("4. CORS or security policy blocking PDF access")
    print()
    
    fixes = generate_fixes()
    
    print("IMPLEMENTATION STEPS:")
    for i, fix in enumerate(fixes, 1):
        print(f"{i}. {fix['title']}")
        print(f"   {fix['description']}")
        print()
    
    return fixes

def generate_fixes():
    """Generate specific fixes for the PDF loading issue"""
    
    fixes = [
        {
            'title': 'Update PDF.js Version and Configuration',
            'description': 'Upgrade to latest stable PDF.js version with proper worker configuration',
            'files': ['templates/primepath_routinetest/preview_and_answers.html'],
            'priority': 'HIGH'
        },
        {
            'title': 'Add PDF URL Debugging and Validation',
            'description': 'Add comprehensive logging to identify URL construction issues',
            'files': ['templates/primepath_routinetest/preview_and_answers.html'],
            'priority': 'HIGH'
        },
        {
            'title': 'Implement PDF Loading Fallback System',
            'description': 'Add fallback to browser native PDF viewer if PDF.js fails',
            'files': ['templates/primepath_routinetest/preview_and_answers.html'],
            'priority': 'MEDIUM'
        },
        {
            'title': 'Add CORS Headers for PDF Access',
            'description': 'Ensure PDF files can be loaded by JavaScript without CORS issues',
            'files': ['primepath_project/settings_sqlite.py'],
            'priority': 'MEDIUM'
        },
        {
            'title': 'Enhance Error Handling and User Feedback',
            'description': 'Provide clear error messages and troubleshooting steps',
            'files': ['templates/primepath_routinetest/preview_and_answers.html'],
            'priority': 'LOW'
        }
    ]
    
    return fixes

def generate_template_fix():
    """Generate the JavaScript fix for the template"""
    
    fix_js = '''
// Enhanced PDF Loading System with Debugging
function initializePdfImageDisplay() {
    console.group('[PDF_LOADING_FIX] Starting PDF initialization');
    
    {% if exam.pdf_file %}
    const pdfUrl = "{{ exam.pdf_file.url }}";
    console.log('✓ PDF URL from Django:', pdfUrl);
    {% else %}
    const pdfUrl = null;
    console.error('✗ No PDF file in exam object');
    {% endif %}
    
    if (!pdfUrl) {
        document.getElementById('pdf-loading').innerHTML = `
            <div class="alert alert-danger">
                <h5>PDF Missing</h5>
                <p>No PDF file was uploaded for this exam.</p>
            </div>`;
        console.groupEnd();
        return;
    }
    
    // Validate PDF URL format
    try {
        const urlObj = new URL(pdfUrl, window.location.origin);
        console.log('✓ PDF URL is valid:', urlObj.href);
        
        // Test if PDF is accessible
        fetch(pdfUrl, { method: 'HEAD' })
            .then(response => {
                console.log('✓ PDF HEAD request status:', response.status);
                console.log('✓ PDF Content-Type:', response.headers.get('Content-Type'));
                
                if (response.ok) {
                    loadPdfWithLibrary(pdfUrl);
                } else {
                    throw new Error(`PDF not accessible: ${response.status}`);
                }
            })
            .catch(error => {
                console.error('✗ PDF accessibility test failed:', error);
                showPdfFallback(pdfUrl, error.message);
            });
            
    } catch (error) {
        console.error('✗ Invalid PDF URL:', error);
        document.getElementById('pdf-loading').innerHTML = `
            <div class="alert alert-danger">
                <h5>Invalid PDF URL</h5>
                <p>The PDF URL could not be constructed properly.</p>
                <small>URL: ${pdfUrl}</small>
            </div>`;
        console.groupEnd();
    }
}

function loadPdfWithLibrary(pdfUrl) {
    console.log('[PDF_LOADING_FIX] Loading with PDF.js library');
    
    // Check if PDF.js is loaded
    if (typeof pdfjsLib === 'undefined') {
        console.warn('[PDF_LOADING_FIX] PDF.js not loaded, retrying...');
        setTimeout(() => loadPdfWithLibrary(pdfUrl), 500);
        return;
    }
    
    console.log('✓ PDF.js version:', pdfjsLib.version);
    
    // Configure PDF.js worker with error handling
    try {
        if (!pdfjsLib.GlobalWorkerOptions.workerSrc) {
            pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
            console.log('✓ PDF.js worker configured');
        }
    } catch (error) {
        console.error('✗ PDF.js worker configuration failed:', error);
    }
    
    // Load PDF with enhanced error handling
    const loadingTask = pdfjsLib.getDocument({
        url: pdfUrl,
        cMapUrl: 'https://cdn.jsdelivr.net/npm/pdfjs-dist@3.11.174/cmaps/',
        cMapPacked: true,
        verbosity: 1 // Enable detailed logging
    });
    
    loadingTask.promise.then(function(pdf) {
        console.log('✅ PDF loaded successfully');
        console.log('   Pages:', pdf.numPages);
        console.log('   PDF Info:', pdf._pdfInfo);
        
        pdfDoc = pdf;
        totalPages = pdf.numPages;
        currentPage = 1;
        pageImages.clear();
        
        updatePageControls();
        renderPageAsImage(1);
        
        document.getElementById('pdf-loading').style.display = 'none';
        console.groupEnd();
        
    }).catch(function(error) {
        console.error('✗ PDF.js loading failed:', error);
        console.error('   Error name:', error.name);
        console.error('   Error message:', error.message);
        
        // Show fallback
        showPdfFallback(pdfUrl, error.message);
        console.groupEnd();
    });
    
    // Monitor loading progress
    loadingTask.onProgress = function(progress) {
        if (progress.total > 0) {
            const percent = Math.round((progress.loaded / progress.total) * 100);
            console.log(`[PDF_LOADING_FIX] Loading progress: ${percent}%`);
            
            const loadingEl = document.getElementById('pdf-loading');
            if (loadingEl) {
                loadingEl.innerHTML = `<p>Loading PDF... ${percent}%</p>`;
            }
        }
    };
}

function showPdfFallback(pdfUrl, errorMessage) {
    console.log('[PDF_LOADING_FIX] Showing fallback solution');
    
    const pdfViewer = document.getElementById('pdf-viewer');
    if (pdfViewer) {
        pdfViewer.innerHTML = `
            <div class="alert alert-warning">
                <h5>PDF Viewer Issue</h5>
                <p>The advanced PDF viewer encountered an issue. You can still access the PDF using the options below:</p>
                <div class="mt-3">
                    <a href="${pdfUrl}" class="btn btn-primary" target="_blank">
                        📄 Open PDF in New Tab
                    </a>
                    <a href="${pdfUrl}" class="btn btn-success" download>
                        📥 Download PDF
                    </a>
                </div>
                <details class="mt-3">
                    <summary>Technical Details</summary>
                    <p><strong>Error:</strong> ${errorMessage}</p>
                    <p><strong>PDF URL:</strong> ${pdfUrl}</p>
                </details>
            </div>
            <div class="mt-3">
                <iframe src="${pdfUrl}" width="100%" height="600px" style="border: 1px solid #ddd;">
                    <p>Your browser doesn't support PDF embedding. 
                    <a href="${pdfUrl}" target="_blank">Click here to open the PDF</a>.</p>
                </iframe>
            </div>
        `;
    }
}
'''
    
    return fix_js

if __name__ == "__main__":
    fixes = create_pdf_loading_fix()
    
    print("TEMPLATE JAVASCRIPT FIX:")
    print("="*60)
    js_fix = generate_template_fix()
    print(js_fix)
    
    print("\nNEXT STEPS:")
    print("1. Replace the initializePdfImageDisplay() function in the template")
    print("2. Test with the problematic exam")
    print("3. Check browser console for detailed debugging information")
    print("4. Implement additional fixes as needed")