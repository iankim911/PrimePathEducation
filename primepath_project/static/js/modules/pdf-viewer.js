/**
 * PDF Viewer Module
 * Centralizes PDF viewing functionality used across multiple templates
 * Replaces duplicate implementations in student_test, preview_and_answers, create_exam
 */

(function(window) {
    'use strict';

    window.PrimePath = window.PrimePath || {};
    window.PrimePath.modules = window.PrimePath.modules || {};

    const BaseModule = window.PrimePath.modules.BaseModule;

    /**
     * PDF Viewer Module
     * Handles PDF display, navigation, zoom, and rotation
     */
    class PDFViewer extends BaseModule {
        constructor(options = {}) {
            super('PDFViewer', options);
            
            // PDF.js variables
            this.pdfDoc = null;
            this.currentPage = 1;
            this.totalPages = 0;
            this.pageRendering = false;
            this.pageNumPending = null;
            
            // Display settings
            this.scale = options.scale || 1.5;
            this.rotation = 0;
            this.minScale = options.minScale || 0.5;
            this.maxScale = options.maxScale || 3.0;
            
            // DOM elements
            this.container = null;
            this.canvas = null;
            this.ctx = null;
            
            // Virtual page support (for split view)
            this.virtualPages = options.virtualPages || false;
            this.currentVirtualPage = 1;
            
            // Cache for rendered pages
            this.pageCache = new Map();
            this.cacheEnabled = options.enableCache !== false;
        }

        /**
         * Initialize PDF viewer
         * @param {string|HTMLElement} container Container selector or element
         * @param {string} pdfUrl PDF file URL
         */
        async init(container, pdfUrl) {
            if (this.initialized) return;
            
            // Validate PDF URL
            if (!pdfUrl) {
                this.log('error', 'PDF URL is required but was not provided');
                this.emit('error', { message: 'PDF URL is required' });
                this.showError('PDF file not found');
                return;
            }
            
            // Get container element
            if (typeof container === 'string') {
                this.container = document.querySelector(container);
            } else {
                this.container = container;
            }
            
            if (!this.container) {
                this.log('error', 'Container element not found');
                return;
            }
            
            // Create canvas if not exists
            this.canvas = this.container.querySelector('canvas');
            if (!this.canvas) {
                this.canvas = document.createElement('canvas');
                this.canvas.className = 'pdf-canvas';
                this.container.appendChild(this.canvas);
            }
            
            this.ctx = this.canvas.getContext('2d');
            
            // Check if PDF.js is loaded
            if (typeof pdfjsLib === 'undefined') {
                this.log('error', 'PDF.js library not loaded');
                this.emit('error', { message: 'PDF.js library not loaded' });
                return;
            }
            
            // Set worker path if not set
            if (!pdfjsLib.GlobalWorkerOptions.workerSrc) {
                pdfjsLib.GlobalWorkerOptions.workerSrc = 
                    'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
            }
            
            // Load PDF
            await this.loadPDF(pdfUrl);
            
            // Set up event handlers
            this.setupEventHandlers();
            
            super.init();
        }

        /**
         * Load PDF document
         * @param {string} url PDF URL
         */
        async loadPDF(url) {
            try {
                this.showLoading();
                this.emit('loading', { url });
                
                const loadingTask = pdfjsLib.getDocument({
                    url: url,
                    disableFontFace: false,
                    disableStream: false,
                    disableAutoFetch: false
                });
                
                this.pdfDoc = await loadingTask.promise;
                this.totalPages = this.pdfDoc.numPages;
                
                if (this.virtualPages) {
                    // Each physical page becomes 2 virtual pages (left/right columns)
                    this.totalPages = this.pdfDoc.numPages * 2;
                }
                
                this.log('info', `PDF loaded: ${this.totalPages} pages`);
                this.emit('loaded', { 
                    totalPages: this.totalPages,
                    virtualPages: this.virtualPages 
                });
                
                // Render first page
                await this.renderPage(this.currentPage);
                this.hideLoading();
                
            } catch (error) {
                this.log('error', 'Error loading PDF:', error);
                this.emit('error', { message: 'Failed to load PDF', error });
                this.hideLoading();
                this.showError('Failed to load PDF. Please check if the file exists and try refreshing the page.');
            }
        }

        /**
         * Render specific page
         * @param {number} pageNum Page number to render
         */
        async renderPage(pageNum) {
            if (!this.pdfDoc) return;
            
            // Validate page number
            if (pageNum < 1 || pageNum > this.totalPages) {
                this.log('warn', `Invalid page number: ${pageNum}`);
                return;
            }
            
            this.pageRendering = true;
            this.currentPage = pageNum;
            
            try {
                // Check cache first
                if (this.cacheEnabled && this.pageCache.has(pageNum)) {
                    const cachedData = this.pageCache.get(pageNum);
                    this.displayCachedPage(cachedData);
                    this.pageRendering = false;
                    this.emit('pageRendered', { pageNum });
                    return;
                }
                
                let physicalPageNum = pageNum;
                let viewport;
                
                if (this.virtualPages) {
                    // Convert virtual page to physical page
                    physicalPageNum = Math.ceil(pageNum / 2);
                    this.currentVirtualPage = pageNum;
                }
                
                const page = await this.pdfDoc.getPage(physicalPageNum);
                
                // Calculate viewport
                viewport = page.getViewport({ 
                    scale: this.scale, 
                    rotation: this.rotation 
                });
                
                // Handle virtual pages (split view)
                if (this.virtualPages) {
                    const isLeftColumn = (pageNum % 2 === 1);
                    viewport = this.getVirtualViewport(viewport, isLeftColumn);
                }
                
                // Set canvas dimensions
                this.canvas.height = viewport.height;
                this.canvas.width = viewport.width;
                
                // Render PDF page into canvas context
                const renderContext = {
                    canvasContext: this.ctx,
                    viewport: viewport
                };
                
                await page.render(renderContext).promise;
                
                // Cache the rendered page
                if (this.cacheEnabled) {
                    this.cacheRenderedPage(pageNum);
                }
                
                this.pageRendering = false;
                this.emit('pageRendered', { pageNum });
                
                // Update navigation
                this.updateNavigation();
                
                // Process pending page
                if (this.pageNumPending !== null) {
                    const pending = this.pageNumPending;
                    this.pageNumPending = null;
                    await this.renderPage(pending);
                }
                
            } catch (error) {
                this.log('error', `Error rendering page ${pageNum}:`, error);
                this.emit('error', { message: `Failed to render page ${pageNum}`, error });
                this.pageRendering = false;
            }
        }

        /**
         * Get viewport for virtual page (split view)
         * @param {Object} viewport Original viewport
         * @param {boolean} isLeftColumn True for left column
         * @returns {Object} Modified viewport
         */
        getVirtualViewport(viewport, isLeftColumn) {
            // Create custom viewport for half page
            const halfWidth = viewport.width / 2;
            
            // Adjust transform matrix to show only left or right half
            const transform = viewport.transform.slice();
            if (!isLeftColumn) {
                transform[4] -= halfWidth; // Translate X for right column
            }
            
            return {
                width: halfWidth,
                height: viewport.height,
                transform: transform,
                scale: viewport.scale,
                rotation: viewport.rotation
            };
        }

        /**
         * Cache rendered page
         * @param {number} pageNum Page number
         */
        cacheRenderedPage(pageNum) {
            const imageData = this.ctx.getImageData(
                0, 0, this.canvas.width, this.canvas.height
            );
            
            this.pageCache.set(pageNum, {
                imageData: imageData,
                width: this.canvas.width,
                height: this.canvas.height
            });
            
            // Limit cache size
            if (this.pageCache.size > 10) {
                const firstKey = this.pageCache.keys().next().value;
                this.pageCache.delete(firstKey);
            }
        }

        /**
         * Display cached page
         * @param {Object} cachedData Cached page data
         */
        displayCachedPage(cachedData) {
            this.canvas.width = cachedData.width;
            this.canvas.height = cachedData.height;
            this.ctx.putImageData(cachedData.imageData, 0, 0);
        }

        /**
         * Navigate to next page
         */
        async nextPage() {
            if (this.currentPage >= this.totalPages) {
                this.log('info', 'Already at last page');
                return;
            }
            
            await this.goToPage(this.currentPage + 1);
        }

        /**
         * Navigate to previous page
         */
        async prevPage() {
            if (this.currentPage <= 1) {
                this.log('info', 'Already at first page');
                return;
            }
            
            await this.goToPage(this.currentPage - 1);
        }

        /**
         * Go to specific page
         * @param {number} pageNum Page number
         */
        async goToPage(pageNum) {
            if (this.pageRendering) {
                this.pageNumPending = pageNum;
                return;
            }
            
            await this.renderPage(pageNum);
        }

        /**
         * Zoom in
         */
        async zoomIn() {
            if (this.scale >= this.maxScale) return;
            
            this.scale = Math.min(this.scale * 1.2, this.maxScale);
            this.pageCache.clear(); // Clear cache on zoom change
            await this.renderPage(this.currentPage);
            this.emit('zoomChanged', { scale: this.scale });
        }

        /**
         * Zoom out
         */
        async zoomOut() {
            if (this.scale <= this.minScale) return;
            
            this.scale = Math.max(this.scale / 1.2, this.minScale);
            this.pageCache.clear(); // Clear cache on zoom change
            await this.renderPage(this.currentPage);
            this.emit('zoomChanged', { scale: this.scale });
        }

        /**
         * Rotate clockwise
         */
        async rotateClockwise() {
            this.rotation = (this.rotation + 90) % 360;
            this.pageCache.clear(); // Clear cache on rotation
            await this.renderPage(this.currentPage);
            this.emit('rotationChanged', { rotation: this.rotation });
        }

        /**
         * Rotate counter-clockwise
         */
        async rotateCounterClockwise() {
            this.rotation = (this.rotation - 90 + 360) % 360;
            this.pageCache.clear(); // Clear cache on rotation
            await this.renderPage(this.currentPage);
            this.emit('rotationChanged', { rotation: this.rotation });
        }

        /**
         * Update navigation buttons state
         */
        updateNavigation() {
            const navState = {
                currentPage: this.currentPage,
                totalPages: this.totalPages,
                canGoPrev: this.currentPage > 1,
                canGoNext: this.currentPage < this.totalPages,
                scale: this.scale,
                rotation: this.rotation
            };
            
            this.emit('navigationUpdated', navState);
        }

        /**
         * Set up event handlers for navigation buttons
         */
        setupEventHandlers() {
            const delegation = window.PrimePath.utils.EventDelegation;
            
            // Navigation buttons
            delegation.onClick('[data-pdf-action="prev"]', () => this.prevPage());
            delegation.onClick('[data-pdf-action="next"]', () => this.nextPage());
            delegation.onClick('[data-pdf-action="zoom-in"]', () => this.zoomIn());
            delegation.onClick('[data-pdf-action="zoom-out"]', () => this.zoomOut());
            delegation.onClick('[data-pdf-action="rotate-cw"]', () => this.rotateClockwise());
            delegation.onClick('[data-pdf-action="rotate-ccw"]', () => this.rotateCounterClockwise());
            
            // Page input
            delegation.onChange('[data-pdf-action="page-input"]', (e) => {
                const pageNum = parseInt(e.target.value);
                if (!isNaN(pageNum)) {
                    this.goToPage(pageNum);
                }
            });
            
            // Keyboard navigation
            document.addEventListener('keydown', (e) => {
                if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
                
                switch(e.key) {
                    case 'ArrowLeft':
                        this.prevPage();
                        break;
                    case 'ArrowRight':
                        this.nextPage();
                        break;
                    case '+':
                    case '=':
                        this.zoomIn();
                        break;
                    case '-':
                        this.zoomOut();
                        break;
                }
            });
        }

        /**
         * Show error message in the PDF viewer
         * @param {string} message Error message to display
         */
        showError(message) {
            // Hide loading indicator if visible
            const loadingEl = this.container.querySelector('.pdf-loading');
            if (loadingEl) {
                loadingEl.style.display = 'none';
            }
            
            // Show error element if it exists
            const errorEl = this.container.querySelector('.pdf-error');
            if (errorEl) {
                errorEl.style.display = 'block';
                const errorMsg = errorEl.querySelector('p');
                if (errorMsg && message) {
                    errorMsg.textContent = message;
                }
            } else {
                // Create error element if it doesn't exist
                const errorDiv = document.createElement('div');
                errorDiv.className = 'pdf-error';
                errorDiv.innerHTML = `<p>${message || 'Error loading PDF. Please refresh the page.'}</p>`;
                
                // Clear container and add error
                if (this.canvas) {
                    this.canvas.style.display = 'none';
                }
                this.container.appendChild(errorDiv);
            }
            
            this.log('error', `PDF Error displayed: ${message}`);
        }

        /**
         * Show loading indicator
         */
        showLoading() {
            const loadingEl = this.container.querySelector('.pdf-loading');
            if (loadingEl) {
                loadingEl.style.display = 'flex';
            }
            
            // Hide error if visible
            const errorEl = this.container.querySelector('.pdf-error');
            if (errorEl) {
                errorEl.style.display = 'none';
            }
        }

        /**
         * Hide loading indicator
         */
        hideLoading() {
            const loadingEl = this.container.querySelector('.pdf-loading');
            if (loadingEl) {
                loadingEl.style.display = 'none';
            }
        }

        /**
         * Destroy module and cleanup
         */
        destroy() {
            this.pageCache.clear();
            this.pdfDoc = null;
            
            if (this.canvas) {
                this.canvas.remove();
            }
            
            super.destroy();
        }
    }

    // Export to PrimePath namespace
    window.PrimePath.modules.PDFViewer = PDFViewer;

    // Also export for module systems
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = PDFViewer;
    }

})(window);