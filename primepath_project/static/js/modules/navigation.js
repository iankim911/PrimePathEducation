/**
 * Navigation Module
 * Handles all question navigation in the student test interface
 * Centralizes navigation logic and provides consistent API
 */

(function(window) {
    'use strict';

    window.PrimePath = window.PrimePath || {};
    window.PrimePath.modules = window.PrimePath.modules || {};

    const BaseModule = window.PrimePath.modules.BaseModule;

    /**
     * Navigation Module
     * Manages question navigation, keyboard shortcuts, and state
     */
    class NavigationModule extends BaseModule {
        constructor(options = {}) {
            super('Navigation', options);
            
            // Navigation state
            this.currentQuestion = 1;
            this.totalQuestions = 0;
            this.questionPanels = new Map();
            
            // Configuration
            this.enableKeyboard = options.enableKeyboard !== false;
            this.enableUrlState = options.enableUrlState !== false;
            this.autoSaveOnNavigate = options.autoSaveOnNavigate !== false;
            this.focusOnNavigate = options.focusOnNavigate !== false;
            
            // Callbacks
            this.onBeforeNavigate = options.onBeforeNavigate || null;
            this.onAfterNavigate = options.onAfterNavigate || null;
            
            // Dependencies
            this.answerManager = null;
            this.audioPlayer = null;
            
            // UI Elements
            this.navigationButtons = null;
            this.questionNavBar = null;
            this.progressIndicator = null;
        }

        /**
         * Initialize navigation module
         */
        init() {
            if (this.initialized) return;
            
            // Discover question panels
            this.discoverQuestionPanels();
            
            // Set up event handlers
            this.setupEventHandlers();
            
            // Set up keyboard navigation if enabled
            if (this.enableKeyboard) {
                this.setupKeyboardNavigation();
            }
            
            // Set up URL state management if enabled
            if (this.enableUrlState) {
                this.setupUrlStateManagement();
            }
            
            // Get references to other modules
            this.answerManager = window.answerManager || null;
            this.audioPlayer = window.audioPlayer || null;
            
            // Initialize to first question or from URL
            const initialQuestion = this.getInitialQuestion();
            this.showQuestion(initialQuestion, false);
            
            super.init();
            
            this.log('info', `Navigation initialized with ${this.totalQuestions} questions`);
        }

        /**
         * Discover all question panels in the DOM
         */
        discoverQuestionPanels() {
            const panels = document.querySelectorAll('.question-panel');
            this.totalQuestions = panels.length;
            
            panels.forEach(panel => {
                const questionNum = parseInt(panel.dataset.questionNumber);
                if (!isNaN(questionNum)) {
                    this.questionPanels.set(questionNum, panel);
                }
            });
            
            this.log('info', `Discovered ${this.questionPanels.size} question panels`);
        }

        /**
         * Get initial question number (from URL hash or default)
         */
        getInitialQuestion() {
            if (this.enableUrlState && window.location.hash) {
                const match = window.location.hash.match(/^#question-(\d+)$/);
                if (match) {
                    const num = parseInt(match[1]);
                    if (num >= 1 && num <= this.totalQuestions) {
                        return num;
                    }
                }
            }
            return 1;
        }

        /**
         * Navigate to a specific question
         * @param {number} questionNum Question number to navigate to
         * @param {boolean} saveAnswer Whether to save current answer before navigating
         */
        async showQuestion(questionNum, saveAnswer = true) {
            // Validate question number
            if (!this.isValidQuestion(questionNum)) {
                this.log('warn', `Invalid question number: ${questionNum}`);
                return false;
            }
            
            // Before navigate callback
            if (this.onBeforeNavigate) {
                const proceed = await this.onBeforeNavigate(this.currentQuestion, questionNum);
                if (!proceed) {
                    this.log('info', 'Navigation cancelled by beforeNavigate callback');
                    return false;
                }
            }
            
            // Save current answer if needed
            if (saveAnswer && this.autoSaveOnNavigate && this.answerManager) {
                try {
                    await this.answerManager.saveAnswer(this.currentQuestion);
                } catch (error) {
                    this.log('error', 'Failed to save answer before navigation:', error);
                }
            }
            
            // Stop any playing audio
            if (this.audioPlayer) {
                this.audioPlayer.stopAll();
            }
            
            // Hide all panels and show target
            this.questionPanels.forEach((panel, num) => {
                if (num === questionNum) {
                    panel.classList.remove('hidden');
                    panel.classList.add('active');
                } else {
                    panel.classList.add('hidden');
                    panel.classList.remove('active');
                }
            });
            
            // Update current question
            const previousQuestion = this.currentQuestion;
            this.currentQuestion = questionNum;
            
            // Update UI
            this.updateNavigationUI();
            
            // Update URL if enabled
            if (this.enableUrlState) {
                this.updateUrlState();
            }
            
            // Focus management
            if (this.focusOnNavigate) {
                this.focusQuestionPanel(questionNum);
            }
            
            // Emit navigation event
            this.emit('navigate', {
                from: previousQuestion,
                to: questionNum,
                total: this.totalQuestions
            });
            
            // After navigate callback
            if (this.onAfterNavigate) {
                this.onAfterNavigate(questionNum, previousQuestion);
            }
            
            this.log('info', `Navigated from question ${previousQuestion} to ${questionNum}`);
            return true;
        }

        /**
         * Navigate to next question
         */
        async nextQuestion() {
            if (this.hasNext()) {
                return await this.showQuestion(this.currentQuestion + 1);
            }
            return false;
        }

        /**
         * Navigate to previous question
         */
        async previousQuestion() {
            if (this.hasPrevious()) {
                return await this.showQuestion(this.currentQuestion - 1);
            }
            return false;
        }

        /**
         * Navigate to first unanswered question
         */
        async goToFirstUnanswered() {
            if (!this.answerManager) return false;
            
            const stats = this.answerManager.getStats();
            if (stats.unansweredQuestions && stats.unansweredQuestions.length > 0) {
                return await this.showQuestion(stats.unansweredQuestions[0]);
            }
            return false;
        }

        /**
         * Check if question number is valid
         */
        isValidQuestion(num) {
            return num >= 1 && num <= this.totalQuestions && this.questionPanels.has(num);
        }

        /**
         * Check if there's a next question
         */
        hasNext() {
            return this.currentQuestion < this.totalQuestions;
        }

        /**
         * Check if there's a previous question
         */
        hasPrevious() {
            return this.currentQuestion > 1;
        }

        /**
         * Update navigation UI elements
         */
        updateNavigationUI() {
            // Update question navigation buttons
            document.querySelectorAll('.question-nav-btn').forEach(btn => {
                const btnNum = parseInt(btn.dataset.question);
                if (btnNum === this.currentQuestion) {
                    btn.classList.add('active');
                    btn.setAttribute('aria-current', 'true');
                } else {
                    btn.classList.remove('active');
                    btn.removeAttribute('aria-current');
                }
            });
            
            // Update next/previous button states
            const prevButtons = document.querySelectorAll('[data-action="prev-question"]');
            const nextButtons = document.querySelectorAll('[data-action="next-question"]');
            
            prevButtons.forEach(btn => {
                btn.disabled = !this.hasPrevious();
                if (this.hasPrevious()) {
                    btn.dataset.target = this.currentQuestion - 1;
                }
            });
            
            nextButtons.forEach(btn => {
                btn.disabled = !this.hasNext();
                if (this.hasNext()) {
                    btn.dataset.target = this.currentQuestion + 1;
                }
            });
            
            // Update progress indicator
            const progressEl = document.getElementById('answer-progress');
            if (progressEl && this.answerManager) {
                const stats = this.answerManager.getStats();
                progressEl.textContent = `${stats.answeredCount} / ${this.totalQuestions} answered`;
            }
        }

        /**
         * Focus the question panel for accessibility
         */
        focusQuestionPanel(questionNum) {
            const panel = this.questionPanels.get(questionNum);
            if (!panel) return;
            
            // Find first focusable element in panel
            const focusable = panel.querySelector(
                'input:not([disabled]), ' +
                'textarea:not([disabled]), ' +
                'button:not([disabled]), ' +
                '[tabindex]:not([tabindex="-1"])'
            );
            
            if (focusable) {
                focusable.focus();
            } else {
                // Make panel focusable temporarily
                panel.setAttribute('tabindex', '-1');
                panel.focus();
            }
        }

        /**
         * Update URL hash with current question
         */
        updateUrlState() {
            const newHash = `#question-${this.currentQuestion}`;
            if (window.location.hash !== newHash) {
                window.history.replaceState(null, null, newHash);
            }
        }

        /**
         * Set up event handlers for navigation
         */
        setupEventHandlers() {
            const delegation = window.PrimePath?.utils?.EventDelegation;
            if (!delegation) {
                this.log('error', 'EventDelegation not available, falling back to direct event listeners');
                this.setupDirectEventListeners();
                return;
            }
            
            // Store reference to this for use in callbacks
            const self = this;
            
            delegation.onClick('[data-action="navigate-question"]', function(e) {
                e.preventDefault();
                const questionNum = parseInt(this.dataset.question);
                if (!isNaN(questionNum)) {
                    self.showQuestion(questionNum);
                }
            });
            
            delegation.onClick('[data-action="next-question"]', function(e) {
                e.preventDefault();
                self.nextQuestion();
            });
            
            delegation.onClick('[data-action="prev-question"]', function(e) {
                e.preventDefault();
                self.previousQuestion();
            });
            
            // Review test button
            delegation.onClick('[data-action="review-test"]', function(e) {
                e.preventDefault();
                self.handleReviewTest();
            });
            
            // Direct input navigation
            delegation.onChange('[data-action="question-input"]', (e, element) => {
                const num = parseInt(element.value);
                if (!isNaN(num)) {
                    this.showQuestion(num);
                }
            });
        }

        /**
         * Fallback: Set up direct event listeners if delegation not available
         */
        setupDirectEventListeners() {
            // Question number buttons
            document.querySelectorAll('[data-action="navigate-question"]').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const questionNum = parseInt(btn.dataset.question);
                    if (!isNaN(questionNum)) {
                        this.showQuestion(questionNum);
                    }
                });
            });
            
            // Next buttons
            document.querySelectorAll('[data-action="next-question"]').forEach(btn => {
                btn.addEventListener('click', () => this.nextQuestion());
            });
            
            // Previous buttons
            document.querySelectorAll('[data-action="prev-question"]').forEach(btn => {
                btn.addEventListener('click', () => this.previousQuestion());
            });
        }

        /**
         * Set up keyboard navigation
         */
        setupKeyboardNavigation() {
            document.addEventListener('keydown', (e) => {
                // Don't navigate if user is typing in an input
                if (e.target.matches('input, textarea, select')) {
                    return;
                }
                
                switch(e.key) {
                    case 'ArrowRight':
                    case 'PageDown':
                        e.preventDefault();
                        this.nextQuestion();
                        break;
                        
                    case 'ArrowLeft':
                    case 'PageUp':
                        e.preventDefault();
                        this.previousQuestion();
                        break;
                        
                    case 'Home':
                        if (e.ctrlKey) {
                            e.preventDefault();
                            this.showQuestion(1);
                        }
                        break;
                        
                    case 'End':
                        if (e.ctrlKey) {
                            e.preventDefault();
                            this.showQuestion(this.totalQuestions);
                        }
                        break;
                        
                    default:
                        // Number keys 1-9 with Alt
                        if (e.altKey && e.key >= '1' && e.key <= '9') {
                            e.preventDefault();
                            const num = parseInt(e.key);
                            if (num <= this.totalQuestions) {
                                this.showQuestion(num);
                            }
                        }
                }
            });
            
            this.log('info', 'Keyboard navigation enabled');
        }

        /**
         * Set up URL state management
         */
        setupUrlStateManagement() {
            window.addEventListener('hashchange', () => {
                const match = window.location.hash.match(/^#question-(\d+)$/);
                if (match) {
                    const num = parseInt(match[1]);
                    if (num !== this.currentQuestion && this.isValidQuestion(num)) {
                        this.showQuestion(num, false);
                    }
                }
            });
            
            this.log('info', 'URL state management enabled');
        }

        /**
         * Handle review test action
         */
        async handleReviewTest() {
            if (!this.answerManager) {
                this.emit('reviewTest');
                return;
            }
            
            const stats = this.answerManager.getStats();
            const unanswered = stats.unansweredQuestions;
            
            if (unanswered && unanswered.length > 0) {
                const message = `You have ${unanswered.length} unanswered question(s): ${unanswered.join(', ')}.\n\nDo you want to review them?`;
                if (confirm(message)) {
                    await this.showQuestion(unanswered[0]);
                    return;
                }
            }
            
            if (confirm('Are you ready to submit your test?')) {
                if (this.answerManager.submitTest) {
                    this.answerManager.submitTest();
                } else {
                    this.emit('submitTest');
                }
            }
        }

        /**
         * Get navigation statistics
         */
        getStats() {
            return {
                currentQuestion: this.currentQuestion,
                totalQuestions: this.totalQuestions,
                hasNext: this.hasNext(),
                hasPrevious: this.hasPrevious(),
                percentComplete: Math.round((this.currentQuestion / this.totalQuestions) * 100)
            };
        }

        /**
         * Destroy navigation module
         */
        destroy() {
            // Remove event listeners if using direct listeners
            // Clear references
            this.questionPanels.clear();
            this.answerManager = null;
            this.audioPlayer = null;
            
            super.destroy();
        }
    }

    // Export to PrimePath namespace
    window.PrimePath.modules.NavigationModule = NavigationModule;

    // Also export for module systems
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = NavigationModule;
    }

})(window);