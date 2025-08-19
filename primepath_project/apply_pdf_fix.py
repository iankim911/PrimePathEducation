#!/usr/bin/env python3
"""
Apply PDF loading fix to the RoutineTest preview template
"""

import os
import re
from pathlib import Path

def apply_pdf_loading_fix():
    """Apply the comprehensive PDF loading fix"""
    
    template_path = Path('templates/primepath_routinetest/preview_and_answers.html')
    
    if not template_path.exists():
        print(f"❌ Template file not found: {template_path}")
        return False
    
    print(f"📄 Reading template: {template_path}")
    
    # Read the current template
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📊 Template size: {len(content)} characters")
    
    # Create backup
    backup_path = template_path.with_suffix('.html.backup')
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"💾 Backup created: {backup_path}")
    
    # Enhanced PDF loading function
    new_function = '''function initializePdfImageDisplay() {
    console.group('[PDF_LOADING_FIX] Enhanced PDF initialization');
    
    {% if exam.pdf_file %}
    const pdfUrl = "{{ exam.pdf_file.url }}";
    console.log('✅ PDF URL from Django:', pdfUrl);
    console.log('🔍 Exam ID:', '{{ exam.id }}');
    console.log('📝 Exam Name:', '{{ exam.name }}');
    {% else %}
    const pdfUrl = null;
    console.error('❌ No PDF file in exam object');
    {% endif %}
    
    if (!pdfUrl) {
        console.error('❌ PDF URL is null');
        document.getElementById('pdf-loading').innerHTML = `
            <div class="alert alert-danger">
                <h5>📄 PDF Missing</h5>
                <p>No PDF file was uploaded for this exam.</p>
            </div>`;
        console.groupEnd();
        return;
    }
    
    // Test PDF accessibility first
    console.log('🧪 Testing PDF URL accessibility...');
    fetch(pdfUrl, { method: 'HEAD' })
        .then(response => {
            console.log('🌐 PDF HEAD request status:', response.status);
            console.log('📋 Content-Type:', response.headers.get('Content-Type'));
            
            if (response.ok) {
                console.log('✅ PDF is accessible, loading with PDF.js...');
                loadPdfWithPdfJs(pdfUrl);
            } else {
                throw new Error(`PDF not accessible: HTTP ${response.status}`);
            }
        })
        .catch(error => {
            console.error('❌ PDF accessibility test failed:', error);
            showPdfFallback(pdfUrl, error.message);
        });
    
    console.groupEnd();
}

function loadPdfWithPdfJs(pdfUrl) {
    console.group('[PDF_JS_LOADER] Loading with PDF.js');
    
    if (typeof pdfjsLib === 'undefined') {
        console.warn('⚠️ PDF.js not loaded yet, retrying in 500ms...');
        setTimeout(() => loadPdfWithPdfJs(pdfUrl), 500);
        return;
    }
    
    console.log('✅ PDF.js available, version:', pdfjsLib.version || 'Unknown');
    
    // Configure PDF.js worker
    try {
        if (!pdfjsLib.GlobalWorkerOptions.workerSrc) {
            pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
            console.log('✅ PDF.js worker configured');
        }
    } catch (error) {
        console.error('❌ Worker configuration failed:', error);
    }
    
    // Enhanced loading with detailed configuration
    const loadingTask = pdfjsLib.getDocument({
        url: pdfUrl,
        verbosity: 1,
        cMapUrl: 'https://cdn.jsdelivr.net/npm/pdfjs-dist@3.11.174/cmaps/',
        cMapPacked: true
    });
    
    // Progress monitoring
    loadingTask.onProgress = function(progress) {
        if (progress.total > 0) {
            const percent = Math.round((progress.loaded / progress.total) * 100);
            console.log(`📥 Loading: ${percent}%`);
            
            const loadingEl = document.getElementById('pdf-loading');
            if (loadingEl) {
                loadingEl.innerHTML = `<p>Loading PDF... ${percent}%</p>`;
            }
        }
    };
    
    loadingTask.promise.then(function(pdf) {
        console.log('🎉 PDF loaded successfully!');
        console.log('📄 Pages:', pdf.numPages);
        
        pdfDoc = pdf;
        totalPages = pdf.numPages;
        currentPage = 1;
        pageImages.clear();
        
        updatePageControls();
        renderPageAsImage(1);
        
        document.getElementById('pdf-loading').style.display = 'none';
        console.groupEnd();
        
    }).catch(function(error) {
        console.error('❌ PDF.js loading failed:', error);
        console.error('   Error name:', error.name);
        console.error('   Error message:', error.message);
        
        showPdfFallback(pdfUrl, `PDF.js failed: ${error.name} - ${error.message}`);
        console.groupEnd();
    });
}

function showPdfFallback(pdfUrl, errorMessage) {
    console.log('🛟 Showing PDF fallback');
    
    const pdfViewer = document.getElementById('pdf-viewer');
    if (pdfViewer) {
        pdfViewer.innerHTML = `
            <div class="alert alert-warning mb-3">
                <div class="d-flex align-items-center mb-2">
                    <strong>⚠️ PDF Viewer Issue</strong>
                </div>
                <p>The advanced PDF viewer encountered an issue:</p>
                
                <div class="d-grid gap-2 d-md-flex mb-3">
                    <a href="${pdfUrl}" class="btn btn-primary" target="_blank">
                        📄 Open in New Tab
                    </a>
                    <a href="${pdfUrl}" class="btn btn-success" download>
                        📥 Download PDF
                    </a>
                    <button class="btn btn-info" onclick="location.reload()">
                        🔄 Refresh Page
                    </button>
                </div>
                
                <details>
                    <summary class="text-muted">🔧 Technical Details</summary>
                    <div class="mt-2 small">
                        <p><strong>Error:</strong> ${errorMessage}</p>
                        <p><strong>PDF URL:</strong> <code>${pdfUrl}</code></p>
                        <p><strong>Time:</strong> ${new Date().toLocaleString()}</p>
                    </div>
                </details>
            </div>
            
            <div class="card">
                <div class="card-header">📄 PDF Preview (Browser Native)</div>
                <div class="card-body p-0">
                    <iframe src="${pdfUrl}" width="100%" height="600" style="border: none;">
                        <div class="p-3">
                            <p>Your browser doesn't support PDF embedding.</p>
                            <a href="${pdfUrl}" target="_blank" class="btn btn-primary">Open PDF</a>
                        </div>
                    </iframe>
                </div>
            </div>
        `;
    }
}'''
    
    # Find and replace the initializePdfImageDisplay function
    # Use a more flexible pattern to match the function
    function_pattern = r'function initializePdfImageDisplay\(\)\s*\{[^}]*(?:\{[^}]*\}[^}]*)*\}'
    
    # Count braces to find the complete function
    lines = content.split('\n')
    start_line = None
    end_line = None
    brace_count = 0
    in_function = False
    
    for i, line in enumerate(lines):
        if 'function initializePdfImageDisplay()' in line:
            start_line = i
            in_function = True
            brace_count = 0
        
        if in_function:
            brace_count += line.count('{')
            brace_count -= line.count('}')
            
            if brace_count == 0 and start_line is not None:
                end_line = i
                break
    
    if start_line is not None and end_line is not None:
        print(f"🎯 Found function at lines {start_line + 1}-{end_line + 1}")
        
        # Replace the function
        new_lines = lines[:start_line] + new_function.split('\n') + lines[end_line + 1:]
        new_content = '\n'.join(new_lines)
        
        # Write the updated content
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Function replaced successfully")
        print(f"📊 New template size: {len(new_content)} characters")
        print(f"📝 Lines changed: {start_line + 1}-{end_line + 1}")
        
        return True
    else:
        print("❌ Could not find initializePdfImageDisplay function")
        return False

def main():
    print("=== PDF Loading Fix Application ===")
    print()
    
    success = apply_pdf_loading_fix()
    
    if success:
        print()
        print("✅ PDF loading fix applied successfully!")
        print()
        print("🧪 Testing Steps:")
        print("1. Navigate to: http://127.0.0.1:8000/RoutineTest/exams/54b00626-6cf6-4fa7-98d8-6203c1397713/preview/")
        print("2. Open browser Developer Tools (F12)")
        print("3. Check Console tab for detailed debugging information")
        print("4. Verify PDF loads or shows appropriate fallback")
        print()
        print("🔄 Rollback:")
        print("If issues occur, restore from: templates/primepath_routinetest/preview_and_answers.html.backup")
    else:
        print("❌ Fix application failed!")

if __name__ == "__main__":
    main()