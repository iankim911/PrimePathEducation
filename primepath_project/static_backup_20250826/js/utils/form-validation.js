/**
 * Form Validation Utilities
 * Reusable validation functions for forms across the application
 */

(function(window) {
    'use strict';

    window.PrimePath = window.PrimePath || {};
    window.PrimePath.utils = window.PrimePath.utils || {};

    /**
     * Form validation utility functions
     */
    const FormValidation = {
        /**
         * Format phone number to Korean format
         * Extracted from start_test.html
         * @param {string} value Phone number input
         * @returns {string} Formatted phone number
         */
        formatPhoneNumber(value) {
            // Remove all non-digits
            let numbers = value.replace(/[^\d]/g, '');
            
            // Limit to 11 digits
            if (numbers.length > 11) {
                numbers = numbers.substring(0, 11);
            }
            
            // Format based on length
            if (numbers.length <= 3) {
                return numbers;
            } else if (numbers.length <= 7) {
                return numbers.slice(0, 3) + '-' + numbers.slice(3);
            } else if (numbers.length <= 10) {
                return numbers.slice(0, 3) + '-' + numbers.slice(3, 6) + '-' + numbers.slice(6);
            } else {
                return numbers.slice(0, 3) + '-' + numbers.slice(3, 7) + '-' + numbers.slice(7);
            }
        },

        /**
         * Validate Korean phone number
         * @param {string} phone Phone number
         * @returns {boolean} True if valid
         */
        validatePhoneNumber(phone) {
            const phoneRegex = /^01[0-9]-\d{3,4}-\d{4}$/;
            return phoneRegex.test(phone);
        },

        /**
         * Validate email address
         * @param {string} email Email address
         * @returns {boolean} True if valid
         */
        validateEmail(email) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return emailRegex.test(email);
        },

        /**
         * Validate required field
         * @param {string} value Field value
         * @returns {boolean} True if not empty
         */
        validateRequired(value) {
            return value !== null && value !== undefined && value.toString().trim() !== '';
        },

        /**
         * Validate file selection
         * @param {File} file File object
         * @param {Object} options Validation options
         * @returns {Object} Validation result
         */
        validateFile(file, options = {}) {
            const result = {
                valid: true,
                errors: []
            };

            if (!file) {
                result.valid = false;
                result.errors.push('No file selected');
                return result;
            }

            // Check file size
            if (options.maxSize && file.size > options.maxSize) {
                result.valid = false;
                result.errors.push(`File size exceeds ${this.formatFileSize(options.maxSize)}`);
            }

            // Check file type
            if (options.allowedTypes && options.allowedTypes.length > 0) {
                const fileExt = file.name.split('.').pop().toLowerCase();
                if (!options.allowedTypes.includes(fileExt)) {
                    result.valid = false;
                    result.errors.push(`File type .${fileExt} not allowed. Allowed types: ${options.allowedTypes.join(', ')}`);
                }
            }

            return result;
        },

        /**
         * Format file size for display
         * @param {number} bytes File size in bytes
         * @returns {string} Formatted file size
         */
        formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
        },

        /**
         * Validate form data
         * @param {Object} data Form data object
         * @param {Object} rules Validation rules
         * @returns {Object} Validation result
         */
        validateForm(data, rules) {
            const result = {
                valid: true,
                errors: {}
            };

            Object.keys(rules).forEach(field => {
                const fieldRules = rules[field];
                const value = data[field];
                const fieldErrors = [];

                // Required validation
                if (fieldRules.required && !this.validateRequired(value)) {
                    fieldErrors.push(`${fieldRules.label || field} is required`);
                }

                // Email validation
                if (fieldRules.email && value && !this.validateEmail(value)) {
                    fieldErrors.push(`${fieldRules.label || field} must be a valid email`);
                }

                // Phone validation
                if (fieldRules.phone && value && !this.validatePhoneNumber(value)) {
                    fieldErrors.push(`${fieldRules.label || field} must be a valid phone number`);
                }

                // Custom validation
                if (fieldRules.custom && typeof fieldRules.custom === 'function') {
                    const customResult = fieldRules.custom(value, data);
                    if (customResult !== true) {
                        fieldErrors.push(customResult);
                    }
                }

                if (fieldErrors.length > 0) {
                    result.valid = false;
                    result.errors[field] = fieldErrors;
                }
            });

            return result;
        },

        /**
         * Show validation errors on form
         * @param {HTMLFormElement} form Form element
         * @param {Object} errors Validation errors
         */
        showFormErrors(form, errors) {
            // Clear previous errors
            form.querySelectorAll('.error-message').forEach(el => el.remove());
            form.querySelectorAll('.error').forEach(el => el.classList.remove('error'));

            // Show new errors
            Object.keys(errors).forEach(field => {
                const input = form.querySelector(`[name="${field}"]`);
                if (input) {
                    input.classList.add('error');
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'error-message';
                    errorDiv.textContent = errors[field].join(', ');
                    input.parentNode.insertBefore(errorDiv, input.nextSibling);
                }
            });
        },

        /**
         * Clear form errors
         * @param {HTMLFormElement} form Form element
         */
        clearFormErrors(form) {
            form.querySelectorAll('.error-message').forEach(el => el.remove());
            form.querySelectorAll('.error').forEach(el => el.classList.remove('error'));
        }
    };

    // Export to PrimePath namespace
    window.PrimePath.utils.FormValidation = FormValidation;

    // Also export for module systems
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = FormValidation;
    }

})(window);