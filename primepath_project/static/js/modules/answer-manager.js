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
            
            // Only log URL structure in debug mode
            if (this.isDebugMode()) {
                this.log('debug', 'Using new URL structure: /api/PlacementTest/');
            }
            
            // Answer storage
            this.answers = new Map();
            this.answeredQuestions = new Set();
            
            // Session info - handle multiple formats for backward compatibility
            this.session = options.session || null;
            this.sessionId = options.sessionId || (this.session && this.session.id) || null;
            this.examId = options.examId || (this.session && this.session.examId) || null;
            
            // Auto-save settings
            this.autoSave = options.autoSave !== false;
            this.autoSaveInterval = options.autoSaveInterval || 30000; // 30 seconds
            this.autoSaveTimer = null;
            this.pendingChanges = new Set();
            
            // Validation settings
            this.requireAllAnswers = options.requireAllAnswers || false;
            this.allowEmptySubmit = options.allowEmptySubmit || false;
            
            // API endpoints
            this.saveEndpoint = options.saveEndpoint || '/api/PlacementTest/save-answer/';
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
            
            // Only log in debug mode
            if (this.isDebugMode()) {
                this.log('debug', `Initializing with sessionId: ${sessionId}`);
                if (Object.keys(options).length > 0) {
                    this.log('debug', 'Additional options provided', options);
                }
            }
            
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
            
            if (this.isDebugMode()) {
                this.log('debug', 'Initialization complete');
            }
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
            const questionType = questionPanel.dataset.questionType;
            let answer = '';
            let answerType = '';
            
            // Check for radio buttons (single choice)
            const radioInput = questionPanel.querySelector(`[name="q_${questionId}"]:checked`);
            if (radioInput) {
                answer = radioInput.value;
                answerType = 'radio';
            }
            
            // Special handling for MIXED questions with MCQ components
            if (questionType === 'MIXED') {
                // Check for MIXED MCQ components (format: q_{id}_{index}_{option})
                const mixedCheckboxes = questionPanel.querySelectorAll(`input[type="checkbox"][name^="q_${questionId}_"]:checked`);
                
                if (mixedCheckboxes.length > 0) {
                    // Group checkboxes by component index
                    const componentAnswers = {};
                    
                    mixedCheckboxes.forEach(checkbox => {
                        const nameParts = checkbox.name.split('_');
                        // Format: q_{questionId}_{componentIndex}_{option}
                        if (nameParts.length === 4) {
                            const componentIndex = nameParts[2];
                            const option = nameParts[3];
                            
                            if (!componentAnswers[componentIndex]) {
                                componentAnswers[componentIndex] = [];
                            }
                            componentAnswers[componentIndex].push(option);
                        } else if (nameParts.length === 3) {
                            // Old format for regular checkboxes: q_{questionId}_{letter}
                            const letter = nameParts[2];
                            if (!componentAnswers[letter]) {
                                componentAnswers[letter] = checkbox.value;
                            }
                        }
                    });
                    
                    // Format answer based on component structure
                    if (Object.keys(componentAnswers).length > 0) {
                        // Check if we have numeric indices (new MCQ format)
                        const hasNumericIndices = Object.keys(componentAnswers).some(key => !isNaN(parseInt(key)));
                        
                        if (hasNumericIndices) {
                            // CRITICAL FIX: Format MIXED questions for backend compatibility
                            // Backend expects: [{"type":"Multiple Choice","value":"B,C"},...]
                            const formattedAnswers = [];
                            
                            Object.keys(componentAnswers).sort().forEach((index) => {
                                formattedAnswers.push({
                                    "type": "Multiple Choice",
                                    "value": componentAnswers[index].join(',')
                                });
                            });
                            
                            answer = JSON.stringify(formattedAnswers);
                            answerType = 'mixed-mcq';
                            
                            // Debug logging
                            console.log('[AnswerManager] MIXED answer format conversion:', {
                                questionId: questionId,
                                componentAnswers: componentAnswers,
                                formattedAnswer: formattedAnswers,
                                stringified: answer,
                                type: 'mixed-mcq'
                            });
                        } else {
                            // Old format or text inputs
                            answer = JSON.stringify(componentAnswers);
                            answerType = 'mixed';
                        }
                    }
                }
                
                // Also check for text inputs and textareas in MIXED questions
                const mixedTextInputs = questionPanel.querySelectorAll(`input[type="text"][name^="q_${questionId}_"]`);
                const mixedTextareas = questionPanel.querySelectorAll(`textarea[name^="q_${questionId}_"]`);
                
                if ((mixedTextInputs.length > 0 || mixedTextareas.length > 0) && !answer) {
                    const textAnswers = {};
                    
                    // Collect text input answers
                    mixedTextInputs.forEach(input => {
                        const letter = input.name.split('_').pop();
                        if (input.value) {
                            textAnswers[letter] = input.value;
                        }
                    });
                    
                    // Collect textarea answers
                    mixedTextareas.forEach(textarea => {
                        const letter = textarea.name.split('_').pop();
                        if (textarea.value) {
                            textAnswers[letter] = textarea.value;
                        }
                    });
                    
                    if (Object.keys(textAnswers).length > 0) {
                        answer = JSON.stringify(textAnswers);
                        answerType = 'mixed-text';
                    }
                }
            } else {
                // Regular checkbox handling for non-MIXED questions
                const checkboxInputs = questionPanel.querySelectorAll(`input[type="checkbox"][name^="q_${questionId}_"]:checked`);
                if (checkboxInputs.length > 0) {
                    answer = Array.from(checkboxInputs).map(cb => cb.value).join(',');
                    answerType = 'checkbox';
                }
            }
            
            // Check for text input
            const textInput = questionPanel.querySelector(`input[type="text"][name="q_${questionId}"]`);
            if (textInput && textInput.value && !answer) {
                answer = textInput.value;
                answerType = 'text';
            }
            
            // Check for textarea
            const textareaInput = questionPanel.querySelector(`textarea[name="q_${questionId}"]`);
            if (textareaInput && textareaInput.value && !answer) {
                answer = textareaInput.value;
                answerType = 'textarea';
            }
            
            // Check for multiple short answers (non-MIXED)
            if (!answer && questionType !== 'MIXED') {
                const shortAnswerInputs = questionPanel.querySelectorAll(`input[type="text"][name^="q_${questionId}_"]`);
                if (shortAnswerInputs.length > 0) {
                    const answers = {};
                    const answerArray = [];
                    
                    // Collect answers preserving order
                    const letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];
                    letters.forEach(letter => {
                        const input = questionPanel.querySelector(`input[name="q_${questionId}_${letter}"]`);
                        if (input && input.value) {
                            answers[letter] = input.value;
                            answerArray.push(input.value);
                        }
                    });
                    
                    if (answerArray.length > 0) {
                        // CRITICAL FIX: Use pipe format for SHORT questions
                        // Backend expects "A|A" not {"A": "A", "B": "A"}
                        answer = answerArray.join('|');
                        answerType = 'multiple-short';
                        
                        // Debug logging
                        console.log('[AnswerManager] SHORT answer format conversion:', {
                            questionId: questionId,
                            originalFormat: JSON.stringify(answers),
                            convertedFormat: answer,
                            type: 'multiple-short'
                        });
                    }
                }
            }
            
            // Check for multiple textareas (LONG questions)
            if (!answer) {
                const textareaInputs = questionPanel.querySelectorAll(`textarea[name^="q_${questionId}_"]`);
                if (textareaInputs.length > 0) {
                    const answers = {};
                    textareaInputs.forEach(input => {
                        const letter = input.name.split('_').pop();
                        if (input.value) {
                            answers[letter] = input.value;
                        }
                    });
                    
                    if (Object.keys(answers).length > 0) {
                        answer = JSON.stringify(answers);
                        answerType = 'multiple-long';
                    }
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
            
            // Defensive check for sessionId
            const sessionId = this.getSessionId();
            if (!sessionId) {
                this.log('error', 'Cannot save answer: session ID not available');
                return false;
            }
            
            try {
                const response = await this.ajax(this.saveEndpoint, {
                    method: 'POST',
                    body: JSON.stringify({
                        session_id: sessionId,
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
         * @returns {Object} Save results with succeeded and failed counts
         */
        async saveAllPending() {
            if (this.pendingChanges.size === 0) {
                return { succeeded: 0, failed: 0, total: 0 };
            }
            
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
            
            return {
                succeeded,
                failed,
                total: results.length
            };
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
         * Show difficulty choice modal after test submission
         * @param {string} sessionId - Current session ID
         * @param {string} defaultRedirectUrl - Default URL to redirect to if modal is closed
         */
        showDifficultyChoiceModal(sessionId, defaultRedirectUrl) {
            // Use debug logger if available
            const logger = (window.PrimePathDebug && window.PrimePathDebug.createLogger) ?
                          window.PrimePathDebug.createLogger('DifficultyModal') :
                          { 
                              debug: (msg, data) => console.log('[DifficultyModal]', msg, data || ''),
                              warn: (msg) => console.warn('[DifficultyModal]', msg),
                              trace: () => { /* no-op */ }
                          };
            
            logger.debug('showDifficultyChoiceModal called', {
                sessionId: sessionId,
                defaultRedirectUrl: defaultRedirectUrl
            });
            
            // Only show stack trace in TRACE mode
            if (window.PrimePathDebug && window.PrimePathDebug.shouldLog('modal', 4)) {
                logger.trace('Call stack for modal display');
            }
            
            const modal = document.getElementById('difficulty-choice-modal');
            if (!modal) {
                console.error('[AnswerManager] CRITICAL ERROR: Difficulty choice modal not found in DOM');
                console.log('[AnswerManager] Available modal elements:', document.querySelectorAll('[id*="modal"]'));
                this.log('warn', 'Difficulty choice modal not found, redirecting to results');
                window.location.href = defaultRedirectUrl;
                return;
            }
            
            // Enhanced modal state debugging
            console.group('[AnswerManager] Modal Display Process');
            console.log('Modal element found:', modal);
            console.log('Modal current display:', modal.style.display);
            console.log('Modal current visibility:', getComputedStyle(modal).visibility);
            console.log('Modal current opacity:', getComputedStyle(modal).opacity);
            console.log('Session data to store:', { sessionId, defaultRedirectUrl });
            
            // Check if timer is still valid before showing modal
            if (window.examTimer && window.examTimer.getStats) {
                const timerStats = window.examTimer.getStats();
                console.log('Timer validation before modal display:', timerStats);
                
                if (timerStats.isExpired) {
                    console.error('[AnswerManager] CRITICAL: Timer expired during modal display setup - aborting modal');
                    console.groupEnd();
                    window.location.href = defaultRedirectUrl;
                    return;
                }
            }
            
            // Show the modal
            logger.debug('Showing difficulty choice modal');
            modal.style.display = 'flex';
            console.log('[AnswerManager] Modal display set to flex');
            console.groupEnd();
            
            // Store session data for later use
            modal.dataset.sessionId = sessionId;
            modal.dataset.defaultRedirectUrl = defaultRedirectUrl;
            
            // Add event listeners if not already added
            if (!modal.dataset.listenersAdded) {
                this.setupDifficultyModalListeners(modal);
                modal.dataset.listenersAdded = 'true';
            }
            
            // CRITICAL FIX: Set up timer expiry monitoring for modal
            const self = this;
            console.log('[AnswerManager] Setting up timer monitoring for modal');
            console.log('[AnswerManager] Timer available for monitoring:', !!(window.examTimer && window.examTimer.getStats));
            
            const checkTimerInterval = setInterval(() => {
                if (window.examTimer && window.examTimer.getStats) {
                    const timerStats = window.examTimer.getStats();
                    
                    // Only log in debug mode to avoid console spam
                    if (window.PrimePathDebug && window.PrimePathDebug.shouldLog('modal', 4)) {
                        console.log('[AnswerManager] Timer monitoring check:', {
                            isExpired: timerStats.isExpired,
                            timeRemaining: timerStats.timeRemaining,
                            modalVisible: modal.style.display !== 'none'
                        });
                    }
                    
                    if (timerStats.isExpired) {
                        console.warn('[AnswerManager] TIMER EXPIRY DETECTED DURING MODAL DISPLAY');
                        console.group('[AnswerManager] Modal Auto-Close Process');
                        console.log('Timer stats at expiry:', timerStats);
                        console.log('Modal state before close:', {
                            display: modal.style.display,
                            sessionId: modal.dataset.sessionId,
                            redirectUrl: modal.dataset.defaultRedirectUrl
                        });
                        
                        self.log('warn', 'Timer expired while modal was open - auto-closing');
                        
                        // Clear interval
                        clearInterval(checkTimerInterval);
                        console.log('[AnswerManager] Timer monitoring interval cleared');
                        
                        // Hide modal
                        modal.style.display = 'none';
                        console.log('[AnswerManager] Modal hidden');
                        
                        // Clear timer state
                        if (window.examTimer.clearState) {
                            window.examTimer.clearState();
                            console.log('[AnswerManager] Timer state cleared');
                        } else {
                            console.warn('[AnswerManager] Timer clearState not available');
                        }
                        
                        console.log('[AnswerManager] Showing expiry alert and redirecting');
                        console.groupEnd();
                        
                        // Show message and redirect
                        alert('Test time has expired. Redirecting to your results...');
                        window.location.href = defaultRedirectUrl;
                    }
                } else {
                    // Timer not available - this could indicate a problem
                    console.warn('[AnswerManager] Timer not available during monitoring check');
                }
            }, 1000); // Check every second
            
            console.log('[AnswerManager] Timer monitoring interval started, ID:', checkTimerInterval);
            
            // Store interval ID so we can clean it up
            modal.dataset.timerCheckInterval = checkTimerInterval;
        }
        
        /**
         * Setup event listeners for difficulty choice modal
         * @param {HTMLElement} modal - The modal element
         */
        setupDifficultyModalListeners(modal) {
            const self = this;
            const sessionId = modal.dataset.sessionId;
            
            // Helper function to clean up timer monitoring
            function cleanupTimerMonitoring() {
                const intervalId = modal.dataset.timerCheckInterval;
                if (intervalId) {
                    clearInterval(parseInt(intervalId));
                    delete modal.dataset.timerCheckInterval;
                }
            }
            
            // Handle difficulty choice buttons
            modal.querySelectorAll('[data-action="difficulty-choice"]').forEach(button => {
                button.addEventListener('click', async function() {
                    const adjustment = parseInt(this.dataset.adjustment);
                    await self.handleDifficultyChoice(sessionId, adjustment);
                });
            });
            
            // Handle skip button
            const skipBtn = modal.querySelector('[data-action="skip-difficulty-choice"]');
            if (skipBtn) {
                skipBtn.addEventListener('click', function() {
                    cleanupTimerMonitoring();
                    modal.style.display = 'none';
                    window.location.href = modal.dataset.defaultRedirectUrl;
                });
            }
            
            // Handle overlay click (close modal)
            const overlay = modal.querySelector('.modal-overlay');
            if (overlay) {
                overlay.addEventListener('click', function() {
                    cleanupTimerMonitoring();
                    modal.style.display = 'none';
                    window.location.href = modal.dataset.defaultRedirectUrl;
                });
            }
        }
        
        /**
         * Handle difficulty choice selection
         * @param {string} sessionId - Current session ID
         * @param {number} adjustment - Difficulty adjustment (-1, 0, 1)
         */
        async handleDifficultyChoice(sessionId, adjustment) {
            console.group('[AnswerManager] Difficulty Choice Processing');
            console.log('Processing difficulty choice:', {
                sessionId: sessionId,
                adjustment: adjustment,
                timestamp: new Date().toISOString()
            });
            
            const modal = document.getElementById('difficulty-choice-modal');
            
            // CRITICAL FIX: Validate timer state before processing choice
            console.log('[AnswerManager] Validating timer state before processing choice...');
            if (window.examTimer && window.examTimer.getStats) {
                const timerStats = window.examTimer.getStats();
                console.log('[AnswerManager] Timer stats during choice processing:', timerStats);
                
                if (timerStats.isExpired) {
                    console.error('[AnswerManager] CRITICAL: Timer expired during difficulty choice - canceling operation');
                    console.log('[AnswerManager] Choice details at cancellation:', {
                        sessionId: sessionId,
                        adjustment: adjustment,
                        timerExpired: timerStats.isExpired,
                        timeRemaining: timerStats.timeRemaining,
                        action: 'cancel_and_redirect'
                    });
                    
                    this.log('warn', 'Timer expired - canceling difficulty choice');
                    
                    // Clear timer state
                    if (window.examTimer.clearState) {
                        window.examTimer.clearState();
                        console.log('[AnswerManager] Timer state cleared due to expiry during choice');
                    }
                    
                    // Hide modal and redirect to results
                    modal.style.display = 'none';
                    console.log('[AnswerManager] Modal hidden, showing expiry alert');
                    console.groupEnd();
                    
                    alert('Test time has expired. Showing your results...');
                    window.location.href = modal.dataset.defaultRedirectUrl;
                    return;
                } else {
                    console.log('[AnswerManager] Timer validation passed, proceeding with choice processing');
                }
            } else {
                console.warn('[AnswerManager] Timer not available for validation during choice processing');
            }
            
            // Show loading state
            const buttons = modal.querySelectorAll('button');
            buttons.forEach(btn => btn.disabled = true);
            
            // Clear timer monitoring
            console.log('[AnswerManager] Clearing timer monitoring interval...');
            const intervalId = modal.dataset.timerCheckInterval;
            if (intervalId) {
                clearInterval(parseInt(intervalId));
                delete modal.dataset.timerCheckInterval;
                console.log('[AnswerManager] Timer monitoring interval cleared:', intervalId);
            } else {
                console.log('[AnswerManager] No timer monitoring interval to clear');
            }
            
            try {
                const endpoint = `/PlacementTest/session/${sessionId}/post-submit-difficulty/`;
                console.log('[AnswerManager] Sending difficulty choice request:', {
                    endpoint: endpoint,
                    adjustment: adjustment,
                    sessionId: sessionId
                });
                
                const response = await this.ajax(endpoint, {
                    method: 'POST',
                    body: JSON.stringify({
                        adjustment: adjustment
                    })
                });
                
                console.log('[AnswerManager] Difficulty choice response received:', response);
                
                if (response.success) {
                    console.log('[AnswerManager] Difficulty choice successful, processing response...');
                    console.log('[AnswerManager] Response details:', {
                        action: response.action,
                        redirect_url: response.redirect_url,
                        message: response.message
                    });
                    
                    // Hide modal
                    modal.style.display = 'none';
                    console.log('[AnswerManager] Modal hidden after successful choice');
                    
                    // Clear timer state since we're done
                    if (window.examTimer && window.examTimer.clearState) {
                        window.examTimer.clearState();
                        console.log('[AnswerManager] Timer state cleared after successful choice');
                    } else {
                        console.warn('[AnswerManager] Timer clearState not available after choice');
                    }
                    
                    // Redirect based on action
                    if (response.redirect_url) {
                        if (response.action === 'start_new_test') {
                            // Show message before redirecting to new test
                            if (response.message) {
                                // You could show a brief message here if desired
// REMOVED:                                 console.log(response.message);
                            }
                        }
                        window.location.href = response.redirect_url;
                    }
                } else {
                    throw new Error(response.error || 'Failed to process difficulty choice');
                }
            } catch (error) {
                this.log('error', 'Failed to process difficulty choice:', error);
                alert('Failed to process your choice. Redirecting to results...');
                modal.style.display = 'none';
                window.location.href = modal.dataset.defaultRedirectUrl;
            } finally {
                // Re-enable buttons
                buttons.forEach(btn => btn.disabled = false);
            }
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
         * @param {boolean} isTimerExpiry Whether this is triggered by timer expiry
         */
        async submitTest(force = false, isTimerExpiry = false) {
            // Only log in debug mode
            if (this.isDebugMode()) {
                this.log('info', 'submitTest called', { force, isTimerExpiry });
                // Only show stack trace in TRACE mode
                if (window.PrimePathDebug && window.PrimePathDebug.shouldLog('answerManager', 4)) {
                    console.trace('[AnswerManager] Submit test call stack');
                }
            }
            
            // Defensive check for sessionId with multiple fallbacks
            const sessionId = this.getSessionId();
            
            if (this.isDebugMode()) {
                this.log('debug', `Session ID for submission: ${sessionId}`);
            }
            
            if (!sessionId) {
                this.log('error', 'Cannot submit test: session ID not available');
                alert('Unable to submit test. Session information is missing. Please refresh the page and try again.');
                return false;
            }
            
            // Validate unless forced or timer expired
            if (!force && !isTimerExpiry) {
                const validation = this.validateTest();
                if (!validation.valid) {
                    this.emit('validationFailed', validation);
                    return false;
                }
            }
            
            // Save any pending answers - CRITICAL: Check results
            const saveResults = await this.saveAllPending();
            
            // If saves failed and this is not a timer expiry, don't complete the test
            if (saveResults.failed > 0 && !isTimerExpiry) {
                this.log('error', `Cannot submit test: ${saveResults.failed} answers failed to save`);
                this.emit('submitError', { 
                    error: `Failed to save ${saveResults.failed} answer(s). Please try again.`,
                    saveResults 
                });
                
                // Alert user
                alert(`Failed to save ${saveResults.failed} answer(s). Please check your connection and try again.`);
                return false;
            }
            
            // For timer expiry, log warning but continue
            if (saveResults.failed > 0 && isTimerExpiry) {
                this.log('warn', `Timer expired with ${saveResults.failed} unsaved answers. Completing test anyway.`);
            }
            
            // Submit to server
            try {
                const endpoint = this.submitEndpoint || 
                    `/api/PlacementTest/session/${sessionId}/complete/`;
                
                const response = await this.ajax(endpoint, {
                    method: 'POST',
                    body: JSON.stringify({
                        session_id: sessionId,
                        answers: Object.fromEntries(this.answers),
                        timer_expired: isTimerExpiry,
                        unsaved_count: saveResults.failed
                    })
                });
                
                if (response.success) {
                    if (this.isDebugMode()) {
                        this.log('debug', 'Test submission successful', {
                            show_difficulty_choice: response.show_difficulty_choice,
                            redirect_url: response.redirect_url
                        });
                    }
                    this.emit('testSubmitted', response);
                    
                    // Clear auto-save
                    this.stopAutoSave();
                    
                    // Check if we should show difficulty choice modal
                    if (this.isDebugMode()) {
                        this.log('info', `Difficulty choice flag: ${response.show_difficulty_choice}`);
                    }
                    if (response.show_difficulty_choice) {
                        // CRITICAL FIX: Check if timer has expired since test was submitted
                        console.group('[AnswerManager] Difficulty Choice Modal Decision');
                        console.log('Backend requests modal display:', response.show_difficulty_choice);
                        console.log('Timer available:', !!(window.examTimer && window.examTimer.getStats));
                        
                        if (window.examTimer && window.examTimer.getStats) {
                            const timerStats = window.examTimer.getStats();
                            console.log('Timer stats:', {
                                isExpired: timerStats.isExpired,
                                timeRemaining: timerStats.timeRemaining,
                                totalTime: timerStats.totalTime,
                                isRunning: timerStats.isRunning
                            });
                            
                            // If timer is expired, don't show modal regardless of backend response
                            if (timerStats.isExpired) {
                                console.warn('[AnswerManager] RACE CONDITION DETECTED: Timer expired after submission - skipping difficulty choice modal');
                                console.log('Submission details:', {
                                    timer_expired: isTimerExpiry,
                                    backend_says_show_modal: response.show_difficulty_choice,
                                    actual_timer_expired: timerStats.isExpired,
                                    action: 'skip_modal_and_redirect'
                                });
                                
                                this.log('warn', 'Timer expired after submission - skipping difficulty choice modal');
                                
                                // Clear any timer state and redirect directly
                                if (window.examTimer.clearState) {
                                    window.examTimer.clearState();
                                    console.log('[AnswerManager] Timer state cleared due to race condition');
                                }
                                
                                if (response.redirect_url) {
                                    console.log('[AnswerManager] Redirecting to results:', response.redirect_url);
                                    window.location.href = response.redirect_url;
                                }
                                console.groupEnd();
                                return true;
                            } else {
                                console.log('[AnswerManager] Timer is still active, proceeding with modal display');
                            }
                        } else {
                            console.warn('[AnswerManager] Timer not available for validation - proceeding with modal display');
                        }
                        console.groupEnd();
                        
                        this.log('info', 'Showing difficulty modal after test submission');
                        this.showDifficultyChoiceModal(sessionId, response.redirect_url);
                        return true;
                    }
                    
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
                
                // For timer expiry, still try to redirect even if submission failed
                if (isTimerExpiry) {
                    this.log('warn', 'Timer expired but submission failed. Redirecting to results.');
                    window.location.href = `/api/PlacementTest/session/${sessionId}/result/`;
                }
                
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
         * Get session ID with multiple fallback mechanisms
         * @returns {string|null} Session ID or null if not found
         */
        getSessionId() {
            // Try primary source
            if (this.sessionId) {
                return this.sessionId;
            }
            
            // Try from session object (for backward compatibility)
            if (this.session && this.session.id) {
                this.sessionId = this.session.id;
                return this.sessionId;
            }
            
            // Try from APP_CONFIG
            if (window.APP_CONFIG && window.APP_CONFIG.session && window.APP_CONFIG.session.id) {
                this.sessionId = window.APP_CONFIG.session.id;
                return this.sessionId;
            }
            
            // Try from global sessionId variable
            if (window.sessionId) {
                this.sessionId = window.sessionId;
                return this.sessionId;
            }
            
            // Try to extract from URL as last resort
            const urlMatch = window.location.pathname.match(/session\/([a-f0-9-]+)/);
            if (urlMatch && urlMatch[1]) {
                this.sessionId = urlMatch[1];
                this.log('warn', 'Session ID extracted from URL: ' + this.sessionId);
                return this.sessionId;
            }
            
            // No session ID found
            this.log('error', 'Unable to determine session ID from any source');
            return null;
        }
        
        /**
         * Get exam ID with fallback mechanisms
         * @returns {string|null} Exam ID or null if not found
         */
        getExamId() {
            if (this.examId) {
                return this.examId;
            }
            
            if (window.APP_CONFIG && window.APP_CONFIG.exam && window.APP_CONFIG.exam.id) {
                this.examId = window.APP_CONFIG.exam.id;
                return this.examId;
            }
            
            return null;
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

    // Export to PrimePath namespace with safety check
    try {
        if (window.PrimePath && window.PrimePath.modules) {
            window.PrimePath.modules.AnswerManager = AnswerManager;
            
            // Only log in debug mode
            if (window.PrimePathDebug && window.PrimePathDebug.shouldLog('answerManager', 3)) {
                console.log('[AnswerManager] Module exported to PrimePath.modules.AnswerManager');
            }
            
            // Track initialization if bootstrap is available
            if (window.PrimePath.trackInit) {
                window.PrimePath.trackInit('AnswerManager', true);
            }
        } else {
            if (window.PrimePathDebug && window.PrimePathDebug.shouldLog('answerManager', 0)) {
                console.error('[AnswerManager] Cannot export - namespace not available');
            }
        }
    } catch (error) {
        if (window.PrimePathDebug && window.PrimePathDebug.shouldLog('answerManager', 0)) {
            console.error('[AnswerManager] Export failed:', error);
        }
        if (window.PrimePath && window.PrimePath.trackInit) {
            window.PrimePath.trackInit('AnswerManager', false, error.message);
        }
    }

    // Create global instance for backward compatibility
    window.answerManager = null;

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