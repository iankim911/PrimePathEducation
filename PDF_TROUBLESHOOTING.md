# PDF Viewer Troubleshooting Guide

## Issues Fixed

1. **PDF.js Library Loading Issue**
   - **Problem**: PDF.js was being called before the library finished loading
   - **Solution**: Moved loadPDF() call inside the script.onload callback
   - **Result**: PDF.js now loads properly before attempting to render PDFs

2. **Next/Previous Button Errors**
   - **Problem**: Buttons tried to access pdfDoc.numPages when pdfDoc was null
   - **Solution**: Added null checks to all navigation functions
   - **Result**: No more console errors when clicking buttons before PDF loads

3. **Loading Feedback**
   - **Problem**: Users saw a black screen while PDF was loading
   - **Solution**: Added loading indicator and error messages
   - **Result**: Better user experience with clear feedback

## How It Works Now

1. When page loads:
   - Timer starts
   - PDF.js library loads asynchronously
   - Loading message displays in PDF viewer

2. After PDF.js loads:
   - loadPDF() is called
   - PDF document is fetched from server
   - First page renders, loading message disappears
   - Navigation buttons become active

3. If PDF fails to load:
   - Error message displays
   - Automatically falls back to iframe viewer
   - Iframe provides native browser PDF support

## Testing the Fix

1. Open the browser developer console (F12)
2. Navigate to a placement test page
3. Check for:
   - "Loading PDF from: /media/..." message
   - No "pdfjsLib is not defined" errors
   - PDF should display within 2-3 seconds

## Common Issues

1. **PDF still not showing**: Check if the PDF file exists in the media folder
2. **404 errors**: Verify media URL configuration in Django settings
3. **CORS errors**: Usually not an issue since PDF is served from same domain

## Fallback Behavior

If PDF.js fails for any reason, the viewer automatically switches to an iframe which uses the browser's built-in PDF viewer. This ensures students can always see the exam content.