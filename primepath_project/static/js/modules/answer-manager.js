/**
 * Answer Manager Module
 * Handles answer collection, validation, saving, and submission
 * Replaces inline answer management from student_test.html
 */

(function(window) {
    'use strict';

    window.PrimePath = window.PrimePath || {};
    window.PrimePath.modules = window.PrimePath.modules || {};

    const BaseModule = window.PrimePath.modules.BaseModule;

    /**
     * Answer Manager Module
     * Manages test answers, validation, and submission
     */
    class AnswerManager extends BaseModule {
        constructor(options = {}) {
            super('AnswerManager', options);
            
            // Answer storage
            this.answers = new Map();
            this.answeredQuestions = new Set();
            
            // Session info
            this.sessionId = options.sessionId || null;
            this.examId = options.examId || null;
            
            // Auto-save settings
            this.autoSave = options.autoSave !== false;
            this.autoSaveInterval = options.autoSaveInterval || 30000; // 30 seconds
            this.autoSaveTimer = null;
            this.pendingChanges = new Set();
            
            // Validation settings
            this.requireAllAnswers = options.requireAllAnswers || false;
            this.allowEmptySubmit = options.allowEmptySubmit || false;
            
            // API endpoints
            this.saveEndpoint = options.saveEndpoint || '/api/placement/save-answer/';
            this.submitEndpoint = options.submitEndpoint || null;
            
            // UI elements
            this.questionNavButtons = null;
            this.submitButton = null;
        }

        /**
         * Initialize answer manager
         * @param {string} sessionId Test session ID
         * @param {Object} options Additional options
         */
        init(sessionId, options = {}) {
            if (this.initialized) return;
            
            this.sessionId = sessionId || this.sessionId;
            Object.assign(this, options);
            
            // Load existing answers from DOM if available
            this.loadExistingAnswers();
            
            // Setup event handlers
            this.setupEventHandlers();
            
            // Start auto-save if enabled
            if (this.autoSave) {
                this.startAutoSave();
            }
            
            // Initialize UI
            this.updateUI();
            
            super.init();
        }

        /**
         * Collect answer from question element
         * @param {number} questionNum Question number
         * @returns {Object} Answer data
         */
        collectAnswer(questionNum) {
            const questionPanel = document.getElementById(`question-${questionNum}`);
            if (!questionPanel) {
                this.log('error', `Question panel not found: ${questionNum}`);
                return null;
            }
            
            const questionId = questionPanel.dataset.questionId;
            let answer = '';
            let answerType = '';
            
            // Check for radio buttons (single choice)
            const radioInput = questionPanel.querySelector(`[name="q_${questionId}"]:checked`);
            if (radioInput) {
                answer = radioInput.value;
                answerType = 'radio';
            }
            
            // Check for checkboxes (multiple choice)
            const checkboxInputs = questionPanel.querySelectorAll(`input[type="checkbox"][name^="q_${questionId}_"]:checked`);
            if (checkboxInputs.length > 0) {
                answer = Array.from(checkboxInputs).map(cb => cb.value).join(',');
                answerType = 'checkbox';
            }
            
            // Check for text input
            const textInput = questionPanel.querySelector(`input[type="text"][name="q_${questionId}"]`);
            if (textInput && textInput.value) {
                answer = textInput.value;
                answerType = 'text';
            }
            
            // Check for textarea
            const textareaInput = questionPanel.querySelector(`textarea[name="q_${questionId}"]`);
            if (textareaInput && textareaInput.value) {
                answer = textareaInput.value;
                answerType = 'textarea';
            }
            
            // Check for multiple short answers
            const shortAnswerInputs = questionPanel.querySelectorAll(`input[name^="q_${questionId}_"]`);
            if (shortAnswerInputs.length > 0 && answerType !== 'checkbox') {
                const answers = {};
                shortAnswerInputs.forEach(input => {
                    const letter = input.name.split('_').pop();
                    if (input.value) {
                        answers[letter] = input.value;
                    }
                });
                
                if (Object.keys(answers).length > 0) {
                    answer = JSON.stringify(answers);
                    answerType = 'multiple-short';
                }
            }
            
            return {
                questionId: questionId,
                questionNum: questionNum,
                answer: answer,
                answerType: answerType,
                timestamp: Date.now()
            };
        }

        /**
         * Save answer for a question
         * @param {number} questionNum Question number
         * @param {boolean} markAnswered Whether to mark as answered in UI
         */
        async saveAnswer(questionNum, markAnswered = true) {
            const answerData = this.collectAnswer(questionNum);
            
            if (!answerData || !answerData.answer) {
                this.log('info', `No answer for question ${questionNum}`);
                return false;
            }
            
            // Store locally
            this.answers.set(questionNum, answerData);
            this.answeredQuestions.add(questionNum);
            this.pendingChanges.add(questionNum);
            
            // Update UI
            if (markAnswered) {
                this.markQuestionAnswered(questionNum);
            }
            
            // Save to server if not in batch mode
            if (!this.autoSave) {
                return await this.saveToServer(questionNum);
            }
            
            this.emit('answerSaved', answerData);
            return true;
        }

        /**
         * Save answer to server
         * @param {number} questionNum Question number
         * @returns {Promise<boolean>} Success status
         */
        async saveToServer(questionNum) {
            const answerData = this.answers.get(questionNum);
            if (!answerData) return false;
            
            try {
                const response = await this.ajax(this.saveEndpoint, {
                    method: 'POST',
                    body: JSON.stringify({
                        session_id: this.sessionId,
                        question_id: answerData.questionId,
                        answer: answerData.answer
                    })
                });
                
                if (response.success) {
                    this.pendingChanges.delete(questionNum);
                    this.emit('answerSavedToServer', answerData);
                    this.log('info', `Answer saved for question ${questionNum}`);
                    return true;
                } else {
                    throw new Error(response.error || 'Failed to save answer');
                }
                
            } catch (error) {
                this.log('error', `Failed to save answer for question ${questionNum}:`, error);
                this.emit('saveError', { questionNum, error: error.message });
                return false;
            }
        }

        /**
         * Save all pending answers to server
         */
        async saveAllPending() {
            if (this.pendingChanges.size === 0) return;
            
            const promises = Array.from(this.pendingChanges).map(questionNum => 
                this.saveToServer(questionNum)
            );
            
            const results = await Promise.allSettled(promises);
            
            const succeeded = results.filter(r => r.status === 'fulfilled' && r.value).length;
            const failed = results.length - succeeded;
            
            this.emit('batchSaveComplete', { succeeded, failed });
            
            if (failed > 0) {
                this.log('warn', `Failed to save ${failed} answers`);
            }
        }

        /**
         * Mark question as answered in UI
         * @param {number} questionNum Question number
         */
        markQuestionAnswered(questionNum) {
            // Update navigation button
            const navBtn = document.querySelector(`.question-nav-btn[data-question="${questionNum}"]`);
            if (navBtn) {
                navBtn.classList.add('answered');
            }
            
            // Update any other UI elements
            this.emit('questionAnswered', { questionNum });
        }

        /**
         * Check if all questions are answered
         * @returns {boolean} True if all answered
         */
        areAllQuestionsAnswered() {
            const totalQuestions = document.querySelectorAll('.question-panel').length;
            return this.answeredQuestions.size >= totalQuestions;
        }

        /**
         * Get unanswered questions
         * @returns {Array<number>} Array of question numbers
         */
        getUnansweredQuestions() {
            const unanswered = [];
            const totalQuestions = document.querySelectorAll('.question-panel').length;
            
            for (let i = 1; i <= totalQuestions; i++) {
                if (!this.answeredQuestions.has(i)) {
                    unanswered.push(i);
                }
            }
            
            return unanswered;
        }

        /**
         * Validate test before submission
         * @returns {Object} Validation result
         */
        validateTest() {
            const unanswered = this.getUnansweredQuestions();
            
            if (this.requireAllAnswers && unanswered.length > 0) {
                return {
                    valid: false,
                    unanswered: unanswered,
                    message: `Please answer all questions. ${unanswered.length} question(s) remaining.`
                };
            }
            
            if (!this.allowEmptySubmit && this.answeredQuestions.size === 0) {
                return {
                    valid: false,
                    message: 'Please answer at least one question before submitting.'
                };
            }
            
            return {
                valid: true,
                answered: this.answeredQuestions.size,
                unanswered: unanswered
            };
        }

        /**
         * Submit test
         * @param {boolean} force Force submission without validation
         */
        async submitTest(force = false) {
            // Validate unless forced
            if (!force) {
                const validation = this.validateTest();
                if (!validation.valid) {
                    this.emit('validationFailed', validation);
                    return false;
                }
            }
            
            // Save any pending answers
            await this.saveAllPending();
            
            // Submit to server
            try {
                const endpoint = this.submitEndpoint || 
                    `/api/placement/session/${this.sessionId}/complete/`;
                
                const response = await this.ajax(endpoint, {
                    method: 'POST',
                    body: JSON.stringify({
                        session_id: this.sessionId,
                        answers: Object.fromEntries(this.answers)
                    })
                });
                
                if (response.success) {
                    this.emit('testSubmitted', response);
                    
                    // Clear auto-save
                    this.stopAutoSave();
                    
                    // Redirect if URL provided
                    if (response.redirect_url) {
                        window.location.href = response.redirect_url;
                    }
                    
                    return true;
                } else {
                    throw new Error(response.error || 'Failed to submit test');
                }
                
            } catch (error) {
                this.log('error', 'Failed to submit test:', error);
                this.emit('submitError', { error: error.message });
                return false;
            }
        }

        /**
         * Load existing answers from DOM
         */
        loadExistingAnswers() {
            document.querySelectorAll('.question-panel').forEach(panel => {
                const questionNum = parseInt(panel.dataset.questionNumber);
                const answerData = this.collectAnswer(questionNum);
                
                if (answerData && answerData.answer) {
                    this.answers.set(questionNum, answerData);
                    this.answeredQuestions.add(questionNum);
                }
            });
            
            this.log('info', `Loaded ${this.answeredQuestions.size} existing answers`);
        }

        /**
         * Start auto-save timer
         */
        startAutoSave() {
            if (this.autoSaveTimer) return;
            
            this.autoSaveTimer = setInterval(() => {
                this.saveAllPending();
            }, this.autoSaveInterval);
            
            this.log('info', 'Auto-save started');
        }

        /**
         * Stop auto-save timer
         */
        stopAutoSave() {
            if (this.autoSaveTimer) {
                clearInterval(this.autoSaveTimer);
                this.autoSaveTimer = null;
                this.log('info', 'Auto-save stopped');
            }
        }

        /**
         * Setup event handlers
         */
        setupEventHandlers() {
            const delegation = window.PrimePath.utils.EventDelegation;
            
            // Answer changes
            delegation.onChange('.answer-options input, .answer-options textarea', (e) => {
                const panel = e.target.closest('.question-panel');
                if (panel) {
                    const questionNum = parseInt(panel.dataset.questionNumber);
                    this.saveAnswer(questionNum);
                }
            });
            
            // Submit button
            delegation.onClick('[data-action="submit-test"]', () => {
                this.submitTest();
            });
            
            // Force submit button
            delegation.onClick('[data-action="force-submit"]', () => {
                this.submitTest(true);
            });
            
            // Save before unload
            window.addEventListener('beforeunload', (e) => {
                if (this.pendingChanges.size > 0) {
                    // Try to save pending changes
                    this.saveAllPending();
                    
                    // Show warning
                    e.preventDefault();
                    e.returnValue = 'You have unsaved answers. Are you sure you want to leave?';
                }
            });
        }

        /**
         * Update UI elements
         */
        updateUI() {
            // Update progress indicator
            const totalQuestions = document.querySelectorAll('.question-panel').length;
            const answeredCount = this.answeredQuestions.size;
            
            const progressElement = document.getElementById('answer-progress');
            if (progressElement) {
                progressElement.textContent = `${answeredCount} / ${totalQuestions} answered`;
            }
            
            // Update submit button state
            const submitBtn = document.getElementById('submit-test-btn');
            if (submitBtn) {
                if (this.requireAllAnswers && !this.areAllQuestionsAnswered()) {
                    submitBtn.disabled = true;
                    submitBtn.title = 'Answer all questions before submitting';
                } else {
                    submitBtn.disabled = false;
                    submitBtn.title = '';
                }
            }
        }

        /**
         * Get answer statistics
         * @returns {Object} Answer stats
         */
        getStats() {
            const totalQuestions = document.querySelectorAll('.question-panel').length;
            
            return {
                totalQuestions: totalQuestions,
                answeredCount: this.answeredQuestions.size,
                unansweredCount: totalQuestions - this.answeredQuestions.size,
                answeredQuestions: Array.from(this.answeredQuestions),
                unansweredQuestions: this.getUnansweredQuestions(),
                pendingChanges: Array.from(this.pendingChanges),
                progress: (this.answeredQuestions.size / totalQuestions) * 100
            };
        }

        /**
         * Destroy module and cleanup
         */
        destroy() {
            this.stopAutoSave();
            this.answers.clear();
            this.answeredQuestions.clear();
            this.pendingChanges.clear();
            
            super.destroy();
        }
    }

    // Export to PrimePath namespace
    window.PrimePath.modules.AnswerManager = AnswerManager;

    // Create global instance for backward compatibility
    window.answerManager = null;

    // Backward compatibility functions
    window.saveAnswer = function(questionNum) {
        if (!window.answerManager) {
            window.answerManager = new AnswerManager({
                sessionId: window.sessionId,
                autoSave: true
            });
            window.answerManager.init();
        }
        window.answerManager.saveAnswer(questionNum);
    };
    
    window.markAnswered = function(questionNum) {
        if (window.answerManager) {
            window.answerManager.markQuestionAnswered(questionNum);
        }
    };
    
    window.submitTest = function() {
        if (!window.answerManager) {
            window.answerManager = new AnswerManager({
                sessionId: window.sessionId
            });
            window.answerManager.init();
        }
        window.answerManager.submitTest();
    };

    // Also export for module systems
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = AnswerManager;
    }

})(window);