/**
 * Enhanced Password Validation UI/UX System
 * Provides real-time feedback for password requirements and similarity checks
 */
(function() {
    'use strict';
    
    class PasswordValidator {
        constructor() {
            this.passwordField = null;
            this.confirmField = null;
            this.studentIdField = null;
            this.strengthIndicator = null;
            this.feedbackContainer = null;
            this.init();
        }
        
        init() {
            // Wait for DOM to be ready
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.setupValidation());
            } else {
                this.setupValidation();
            }
        }
        
        setupValidation() {
            this.passwordField = document.getElementById('password');
            this.confirmField = document.getElementById('confirmPassword');
            this.studentIdField = document.getElementById('studentId');
            this.strengthIndicator = document.getElementById('strengthFill');
            
            if (!this.passwordField) return;
            
            // Create feedback container if it doesn't exist
            this.createFeedbackContainer();
            
            // Attach event listeners
            this.attachEventListeners();
            
            console.log('✅ Enhanced Password Validation initialized');
        }
        
        createFeedbackContainer() {
            const passwordGroup = this.passwordField.closest('.form-group');
            if (!passwordGroup) return;
            
            // Check if feedback container already exists
            let feedbackContainer = passwordGroup.querySelector('.password-feedback');
            if (!feedbackContainer) {
                feedbackContainer = document.createElement('div');
                feedbackContainer.className = 'password-feedback';
                feedbackContainer.innerHTML = `
                    <div class="feedback-section">
                        <div class="feedback-header">
                            <span class="feedback-title">Password Requirements</span>
                            <span class="feedback-status" id="passwordStatus">❌</span>
                        </div>
                        <div class="feedback-requirements">
                            <div class="requirement" data-req="length">
                                <span class="req-icon">❌</span>
                                <span class="req-text">At least 8 characters long</span>
                            </div>
                            <div class="requirement" data-req="similarity">
                                <span class="req-icon">❌</span>
                                <span class="req-text">Different from your Student ID</span>
                            </div>
                            <div class="requirement" data-req="complexity">
                                <span class="req-icon">❌</span>
                                <span class="req-text">Mix of letters and numbers</span>
                            </div>
                            <div class="requirement" data-req="common">
                                <span class="req-icon">❌</span>
                                <span class="req-text">Not a common password</span>
                            </div>
                        </div>
                    </div>
                `;
                
                // Insert after password strength indicator
                const strengthContainer = passwordGroup.querySelector('.password-strength');
                if (strengthContainer) {
                    strengthContainer.parentNode.insertBefore(feedbackContainer, strengthContainer.nextSibling);
                } else {
                    passwordGroup.appendChild(feedbackContainer);
                }
            }
            
            this.feedbackContainer = feedbackContainer;
            this.addFeedbackStyles();
        }
        
        addFeedbackStyles() {
            if (document.getElementById('passwordValidationStyles')) return;
            
            const styles = document.createElement('style');
            styles.id = 'passwordValidationStyles';
            styles.textContent = `
                .password-feedback {
                    margin-top: 12px;
                    padding: 16px;
                    background: #f8fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    font-size: 14px;
                    opacity: 0;
                    transform: translateY(-10px);
                    transition: all 0.3s ease;
                }
                
                .password-feedback.visible {
                    opacity: 1;
                    transform: translateY(0);
                }
                
                .feedback-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 12px;
                }
                
                .feedback-title {
                    font-weight: 600;
                    color: #4a5568;
                }
                
                .feedback-status {
                    font-size: 18px;
                    transition: all 0.3s ease;
                }
                
                .feedback-requirements {
                    display: flex;
                    flex-direction: column;
                    gap: 8px;
                }
                
                .requirement {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    padding: 4px 0;
                    transition: all 0.3s ease;
                }
                
                .requirement.valid {
                    color: #10b981;
                }
                
                .requirement.invalid {
                    color: #ef4444;
                }
                
                .req-icon {
                    font-size: 16px;
                    min-width: 20px;
                    transition: all 0.3s ease;
                }
                
                .req-text {
                    transition: all 0.3s ease;
                }
                
                .requirement.valid .req-icon {
                    content: '✅';
                }
                
                .requirement.valid .req-text {
                    text-decoration: line-through;
                    opacity: 0.7;
                }
                
                .similarity-warning {
                    background: #fef3cd;
                    border-left: 4px solid #f59e0b;
                    padding: 12px;
                    margin-top: 8px;
                    border-radius: 4px;
                    font-size: 13px;
                }
                
                .similarity-warning.error {
                    background: #fee2e2;
                    border-left-color: #ef4444;
                    color: #dc2626;
                }
                
                .password-match-indicator {
                    margin-top: 8px;
                    padding: 8px 12px;
                    border-radius: 6px;
                    font-size: 13px;
                    font-weight: 500;
                    opacity: 0;
                    transform: translateY(-5px);
                    transition: all 0.3s ease;
                }
                
                .password-match-indicator.visible {
                    opacity: 1;
                    transform: translateY(0);
                }
                
                .password-match-indicator.match {
                    background: #d1fae5;
                    color: #065f46;
                    border: 1px solid #a7f3d0;
                }
                
                .password-match-indicator.no-match {
                    background: #fee2e2;
                    color: #dc2626;
                    border: 1px solid #fca5a5;
                }
                
                @keyframes bounce {
                    0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
                    40% { transform: translateY(-10px); }
                    60% { transform: translateY(-5px); }
                }
                
                .feedback-status.success {
                    animation: bounce 0.6s ease;
                }
            `;
            
            document.head.appendChild(styles);
        }
        
        attachEventListeners() {
            // Password field real-time validation
            this.passwordField.addEventListener('input', (e) => {
                this.validatePassword(e.target.value);
                this.showFeedback();
                if (this.confirmField && this.confirmField.value) {
                    this.validatePasswordMatch();
                }
            });
            
            this.passwordField.addEventListener('focus', () => {
                this.showFeedback();
            });
            
            this.passwordField.addEventListener('blur', () => {
                // Keep feedback visible if there are issues
                if (!this.isPasswordValid(this.passwordField.value)) {
                    this.showFeedback();
                } else {
                    this.hideFeedback();
                }
            });
            
            // Confirm password validation
            if (this.confirmField) {
                this.confirmField.addEventListener('input', () => {
                    this.validatePasswordMatch();
                });
                
                this.confirmField.addEventListener('focus', () => {
                    if (this.passwordField.value) {
                        this.validatePasswordMatch();
                    }
                });
            }
            
            // Student ID changes should re-validate password similarity
            if (this.studentIdField) {
                this.studentIdField.addEventListener('input', () => {
                    if (this.passwordField.value) {
                        this.validatePassword(this.passwordField.value);
                    }
                });
            }
        }
        
        validatePassword(password) {
            if (!password) {
                this.hideFeedback();
                return;
            }
            
            const studentId = this.studentIdField ? this.studentIdField.value : '';
            const requirements = this.checkRequirements(password, studentId);
            
            // Update visual indicators
            this.updateRequirementIndicators(requirements);
            this.updatePasswordStrength(password, requirements);
            this.updateOverallStatus(requirements);
            
            return requirements;
        }
        
        checkRequirements(password, studentId) {
            const requirements = {
                length: password.length >= 8,
                similarity: this.checkSimilarity(password, studentId),
                complexity: this.checkComplexity(password),
                common: this.checkCommonPassword(password)
            };
            
            requirements.overall = Object.values(requirements).every(req => req);
            return requirements;
        }
        
        checkSimilarity(password, studentId) {
            if (!studentId) return true; // No student ID to compare against
            
            const passwordLower = password.toLowerCase();
            const studentIdLower = studentId.toLowerCase();
            
            // Check if password contains student ID or vice versa
            if (passwordLower.includes(studentIdLower) || studentIdLower.includes(passwordLower)) {
                return false;\n            }\n            \n            // Check Levenshtein distance (similarity ratio)\n            const similarity = this.calculateSimilarity(passwordLower, studentIdLower);\n            return similarity < 0.6; // Less than 60% similar is considered acceptable\n        }\n        \n        calculateSimilarity(str1, str2) {\n            const matrix = [];\n            const len1 = str1.length;\n            const len2 = str2.length;\n            \n            if (len1 === 0) return len2;\n            if (len2 === 0) return len1;\n            \n            // Create matrix\n            for (let i = 0; i <= len2; i++) {\n                matrix[i] = [i];\n            }\n            for (let j = 0; j <= len1; j++) {\n                matrix[0][j] = j;\n            }\n            \n            // Fill matrix\n            for (let i = 1; i <= len2; i++) {\n                for (let j = 1; j <= len1; j++) {\n                    if (str2[i - 1] === str1[j - 1]) {\n                        matrix[i][j] = matrix[i - 1][j - 1];\n                    } else {\n                        matrix[i][j] = Math.min(\n                            matrix[i - 1][j - 1] + 1,\n                            matrix[i][j - 1] + 1,\n                            matrix[i - 1][j] + 1\n                        );\n                    }\n                }\n            }\n            \n            const distance = matrix[len2][len1];\n            const maxLen = Math.max(len1, len2);\n            return distance / maxLen;\n        }\n        \n        checkComplexity(password) {\n            const hasLetter = /[a-zA-Z]/.test(password);\n            const hasNumber = /\\d/.test(password);\n            const hasSpecial = /[^a-zA-Z\\d]/.test(password);\n            \n            // At least 2 out of 3 types\n            const typeCount = [hasLetter, hasNumber, hasSpecial].filter(Boolean).length;\n            return typeCount >= 2;\n        }\n        \n        checkCommonPassword(password) {\n            const commonPasswords = [\n                'password', '123456', '123456789', 'qwerty', 'abc123', 'password123',\n                'admin', 'letmein', 'welcome', 'monkey', '1234567890', 'dragon',\n                'sunshine', 'princess', 'football', 'charlie', 'aa123456', 'donald',\n                'password1', 'qwerty123'\n            ];\n            \n            return !commonPasswords.includes(password.toLowerCase());\n        }\n        \n        updateRequirementIndicators(requirements) {\n            if (!this.feedbackContainer) return;\n            \n            Object.keys(requirements).forEach(reqType => {\n                if (reqType === 'overall') return;\n                \n                const reqElement = this.feedbackContainer.querySelector(`[data-req=\"${reqType}\"]`);\n                if (!reqElement) return;\n                \n                const iconElement = reqElement.querySelector('.req-icon');\n                const isValid = requirements[reqType];\n                \n                reqElement.classList.toggle('valid', isValid);\n                reqElement.classList.toggle('invalid', !isValid);\n                \n                if (iconElement) {\n                    iconElement.textContent = isValid ? '✅' : '❌';\n                }\n                \n                // Special handling for similarity requirement\n                if (reqType === 'similarity' && !isValid) {\n                    const studentId = this.studentIdField ? this.studentIdField.value : '';\n                    if (studentId) {\n                        reqElement.querySelector('.req-text').textContent = \n                            `Different from your Student ID (\"${studentId}\")`;\n                    }\n                }\n            });\n        }\n        \n        updatePasswordStrength(password, requirements) {\n            if (!this.strengthIndicator) return;\n            \n            const score = Object.values(requirements).filter(req => req === true).length - 1; // Exclude 'overall'\n            const percentage = (score / 4) * 100;\n            \n            this.strengthIndicator.style.width = `${percentage}%`;\n            \n            this.strengthIndicator.classList.remove('strength-weak', 'strength-medium', 'strength-strong');\n            \n            if (percentage <= 33) {\n                this.strengthIndicator.classList.add('strength-weak');\n            } else if (percentage <= 75) {\n                this.strengthIndicator.classList.add('strength-medium');\n            } else {\n                this.strengthIndicator.classList.add('strength-strong');\n            }\n        }\n        \n        updateOverallStatus(requirements) {\n            const statusElement = this.feedbackContainer?.querySelector('#passwordStatus');\n            if (!statusElement) return;\n            \n            if (requirements.overall) {\n                statusElement.textContent = '✅';\n                statusElement.classList.add('success');\n            } else {\n                statusElement.textContent = '❌';\n                statusElement.classList.remove('success');\n            }\n        }\n        \n        validatePasswordMatch() {\n            if (!this.confirmField || !this.passwordField) return;\n            \n            const password = this.passwordField.value;\n            const confirmPassword = this.confirmField.value;\n            \n            if (!confirmPassword) {\n                this.hideMatchIndicator();\n                return;\n            }\n            \n            const matches = password === confirmPassword;\n            this.showMatchIndicator(matches);\n            \n            // Update validation feedback in the original UI\n            const confirmValidation = document.getElementById('confirmValidation');\n            if (confirmValidation) {\n                if (matches && confirmPassword) {\n                    confirmValidation.innerHTML = '<div class=\"validation-icon validation-success\">✓</div>';\n                } else if (confirmPassword) {\n                    confirmValidation.innerHTML = '<div class=\"validation-icon validation-error\">✗</div>';\n                } else {\n                    confirmValidation.innerHTML = '';\n                }\n            }\n        }\n        \n        showMatchIndicator(matches) {\n            const confirmGroup = this.confirmField.closest('.form-group');\n            if (!confirmGroup) return;\n            \n            let indicator = confirmGroup.querySelector('.password-match-indicator');\n            if (!indicator) {\n                indicator = document.createElement('div');\n                indicator.className = 'password-match-indicator';\n                confirmGroup.appendChild(indicator);\n            }\n            \n            indicator.classList.remove('match', 'no-match');\n            indicator.classList.add(matches ? 'match' : 'no-match');\n            indicator.textContent = matches ? '✓ Passwords match' : '✗ Passwords do not match';\n            indicator.classList.add('visible');\n        }\n        \n        hideMatchIndicator() {\n            const confirmGroup = this.confirmField.closest('.form-group');\n            const indicator = confirmGroup?.querySelector('.password-match-indicator');\n            if (indicator) {\n                indicator.classList.remove('visible');\n            }\n        }\n        \n        showFeedback() {\n            if (this.feedbackContainer) {\n                this.feedbackContainer.classList.add('visible');\n            }\n        }\n        \n        hideFeedback() {\n            if (this.feedbackContainer) {\n                this.feedbackContainer.classList.remove('visible');\n            }\n        }\n        \n        isPasswordValid(password) {\n            const studentId = this.studentIdField ? this.studentIdField.value : '';\n            const requirements = this.checkRequirements(password, studentId);\n            return requirements.overall;\n        }\n        \n        // Public API for external validation\n        getValidationResults(password) {\n            const studentId = this.studentIdField ? this.studentIdField.value : '';\n            return this.checkRequirements(password, studentId);\n        }\n    }\n    \n    // Initialize the password validator\n    window.PasswordValidator = PasswordValidator;\n    \n    // Auto-initialize if in registration form\n    if (document.getElementById('password') && document.getElementById('registrationForm')) {\n        window.passwordValidator = new PasswordValidator();\n    }\n    \n})();