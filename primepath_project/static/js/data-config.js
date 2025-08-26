/**
 * Frontend Data Configuration Service
 * Phase 3: Data Layer Flexibility
 * 
 * Mirrors backend DataService for consistent configuration
 * Provides dynamic validation rules, field constraints, and business logic
 */

class DataConfigService {
    constructor() {
        this.config = null;
        this.cache = new Map();
        this.cacheTimeout = 300000; // 5 minutes
        
        // Initialize with server-provided config if available
        if (typeof window.DATA_CONFIG !== 'undefined') {
            this.config = window.DATA_CONFIG;
            this.log('CONFIG', 'Initialized with server-provided configuration');
        } else {
            this.log('CONFIG', 'Using fallback configuration');
        }
    }
    
    /**
     * Log configuration events with consistent formatting
     */
    log(category, message, data = null) {
        if (console && console.log) {
            const timestamp = new Date().toISOString();
            const logMessage = `[DATA_CONFIG:${category}] ${timestamp} - ${message}`;
            
            if (data) {
                console.log(logMessage, data);
            } else {
                console.log(logMessage);
            }
        }
    }
    
    /**
     * Get cached configuration value
     */
    getCached(key) {
        const cached = this.cache.get(key);
        if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
            return cached.value;
        }
        return null;
    }
    
    /**
     * Set cached configuration value
     */
    setCached(key, value) {
        this.cache.set(key, {
            value: value,
            timestamp: Date.now()
        });
    }
    
    /**
     * Get user and profile field constraints
     */
    getUserFieldConstraints() {
        const cached = this.getCached('user_fields');
        if (cached) return cached;
        
        const constraints = {
            username_max_length: this.getConfigValue('user.username_max_length', 150),
            email_max_length: this.getConfigValue('user.email_max_length', 254),
            first_name_max_length: this.getConfigValue('user.first_name_max_length', 30),
            last_name_max_length: this.getConfigValue('user.last_name_max_length', 150),
            full_name_max_length: this.getConfigValue('user.full_name_max_length', 200)
        };
        
        this.setCached('user_fields', constraints);
        this.log('USER_FIELDS', 'Loaded user field constraints', constraints);
        return constraints;
    }
    
    /**
     * Get student profile constraints
     */
    getStudentProfileConstraints() {
        const cached = this.getCached('student_profile');
        if (cached) return cached;
        
        const constraints = {
            name_max_length: this.getConfigValue('student.name_max_length', 100),
            student_id_max_length: this.getConfigValue('student.student_id_max_length', 20),
            phone_max_length: this.getConfigValue('student.phone_max_length', 20),
            grade_max_length: this.getConfigValue('student.grade_max_length', 10),
            program_max_length: this.getConfigValue('student.program_max_length', 100),
            class_code_max_length: this.getConfigValue('student.class_code_max_length', 50)
        };
        
        this.setCached('student_profile', constraints);
        this.log('STUDENT_PROFILE', 'Loaded student profile constraints', constraints);
        return constraints;
    }
    
    /**
     * Get exam constraints
     */
    getExamConstraints() {
        const cached = this.getCached('exam_constraints');
        if (cached) return cached;
        
        const constraints = {
            name_max_length: this.getConfigValue('exam.name_max_length', 200),
            description_max_length: this.getConfigValue('exam.description_max_length', 1000),
            max_questions_per_exam: this.getConfigValue('exam.max_questions_per_exam', 200),
            min_questions_per_exam: this.getConfigValue('exam.min_questions_per_exam', 1),
            default_points_per_question: this.getConfigValue('exam.default_points_per_question', 1),
            max_points_per_question: this.getConfigValue('exam.max_points_per_question', 10),
            default_time_limit_minutes: this.getConfigValue('exam.default_time_limit_minutes', 60),
            max_time_limit_minutes: this.getConfigValue('exam.max_time_limit_minutes', 300)
        };
        
        this.setCached('exam_constraints', constraints);
        this.log('EXAM_CONSTRAINTS', 'Loaded exam constraints', constraints);
        return constraints;
    }
    
    /**
     * Get question constraints
     */
    getQuestionConstraints() {
        const cached = this.getCached('question_constraints');
        if (cached) return cached;
        
        const constraints = {
            question_text_max_length: this.getConfigValue('question.text_max_length', 2000),
            answer_choice_max_length: this.getConfigValue('question.answer_choice_max_length', 500),
            short_answer_max_length: this.getConfigValue('question.short_answer_max_length', 1000),
            explanation_max_length: this.getConfigValue('question.explanation_max_length', 2000),
            max_answer_choices: this.getConfigValue('question.max_answer_choices', 6),
            min_answer_choices: this.getConfigValue('question.min_answer_choices', 2)
        };
        
        this.setCached('question_constraints', constraints);
        this.log('QUESTION_CONSTRAINTS', 'Loaded question constraints', constraints);
        return constraints;
    }
    
    /**
     * Get pagination settings
     */
    getPaginationSettings() {
        const cached = this.getCached('pagination');
        if (cached) return cached;
        
        const settings = {
            default_page_size: this.getConfigValue('pagination.default_page_size', 25),
            max_page_size: this.getConfigValue('pagination.max_page_size', 100),
            min_page_size: this.getConfigValue('pagination.min_page_size', 5),
            students_per_page: this.getConfigValue('pagination.students_per_page', 25),
            teachers_per_page: this.getConfigValue('pagination.teachers_per_page', 25),
            exams_per_page: this.getConfigValue('pagination.exams_per_page', 20),
            questions_per_page: this.getConfigValue('pagination.questions_per_page', 15),
            sessions_per_page: this.getConfigValue('pagination.sessions_per_page', 30)
        };
        
        this.setCached('pagination', settings);
        this.log('PAGINATION', 'Loaded pagination settings', settings);
        return settings;
    }
    
    /**
     * Get validation rules
     */
    getValidationRules() {
        const cached = this.getCached('validation');
        if (cached) return cached;
        
        const rules = {
            password_min_length: this.getConfigValue('validation.password_min_length', 8),
            password_max_length: this.getConfigValue('validation.password_max_length', 128),
            username_min_length: this.getConfigValue('validation.username_min_length', 3),
            email_max_length: this.getConfigValue('validation.email_max_length', 254),
            phone_number_patterns: this.getConfigValue('validation.phone_number_formats', [
                /^\d{3}-\d{3,4}-\d{4}$/,  // Korean format
                /^\+\d{1,3}-\d{3,4}-\d{4}$/,  // International
                /^\d{10,11}$/  // Simple numeric
            ]),
            student_id_pattern: this.getConfigValue('validation.student_id_pattern', /^[A-Za-z0-9_-]+$/),
            grade_choices: this.getConfigValue('validation.grade_choices', [
                '1', '2', '3', '4', '5', '6',
                '7', '8', '9', '10', '11', '12'
            ])
        };
        
        this.setCached('validation', rules);
        this.log('VALIDATION', 'Loaded validation rules', rules);
        return rules;
    }
    
    /**
     * Get business rules
     */
    getBusinessRules() {
        const cached = this.getCached('business_rules');
        if (cached) return cached;
        
        const rules = {
            max_concurrent_sessions: this.getConfigValue('business.max_concurrent_sessions', 3),
            session_timeout_minutes: this.getConfigValue('business.session_timeout_minutes', 120),
            exam_attempt_limit: this.getConfigValue('business.exam_attempt_limit', 3),
            grade_pass_threshold: this.getConfigValue('business.grade_pass_threshold', 0.7),
            placement_score_ranges: {
                beginner: this.getConfigValue('business.beginner_max_score', 60),
                intermediate: this.getConfigValue('business.intermediate_max_score', 80),
                advanced: this.getConfigValue('business.advanced_min_score', 81)
            },
            auto_save_interval_seconds: this.getConfigValue('business.auto_save_interval_seconds', 30)
        };
        
        this.setCached('business_rules', rules);
        this.log('BUSINESS_RULES', 'Loaded business rules', rules);
        return rules;
    }
    
    /**
     * Get file upload constraints
     */
    getFileUploadConstraints() {
        const cached = this.getCached('file_upload');
        if (cached) return cached;
        
        const constraints = {
            pdf_max_size_mb: this.getConfigValue('upload.pdf_max_size_mb', 10),
            audio_max_size_mb: this.getConfigValue('upload.audio_max_size_mb', 50),
            image_max_size_mb: this.getConfigValue('upload.image_max_size_mb', 5),
            allowed_pdf_extensions: this.getConfigValue('upload.allowed_pdf_extensions', ['pdf']),
            allowed_audio_extensions: this.getConfigValue('upload.allowed_audio_extensions', ['mp3', 'wav', 'm4a', 'ogg']),
            allowed_image_extensions: this.getConfigValue('upload.allowed_image_extensions', ['jpg', 'jpeg', 'png', 'gif']),
            max_files_per_upload: this.getConfigValue('upload.max_files_per_upload', 10)
        };
        
        this.setCached('file_upload', constraints);
        this.log('FILE_UPLOAD', 'Loaded file upload constraints', constraints);
        return constraints;
    }
    
    /**
     * Get configuration value with fallback
     */
    getConfigValue(key, defaultValue) {
        if (this.config) {
            const keys = key.split('.');
            let value = this.config;
            
            for (const k of keys) {
                if (value && typeof value === 'object' && k in value) {
                    value = value[k];
                } else {
                    return defaultValue;
                }
            }
            
            return value;
        }
        
        return defaultValue;
    }
    
    /**
     * Validate form field using dynamic constraints
     */
    validateField(fieldType, fieldName, value) {
        const result = {
            valid: true,
            errors: []
        };
        
        try {
            // Get appropriate constraints
            let constraints;
            switch (fieldType) {
                case 'student':
                    constraints = this.getStudentProfileConstraints();
                    break;
                case 'exam':
                    constraints = this.getExamConstraints();
                    break;
                case 'question':
                    constraints = this.getQuestionConstraints();
                    break;
                default:
                    constraints = this.getUserFieldConstraints();
            }
            
            // Check length constraints
            const maxLengthKey = `${fieldName}_max_length`;
            if (constraints[maxLengthKey] && value && value.length > constraints[maxLengthKey]) {
                result.valid = false;
                result.errors.push(`${fieldName} must not exceed ${constraints[maxLengthKey]} characters`);
            }
            
            // Additional validation based on field name
            if (fieldName.includes('phone')) {
                const phonePatterns = this.getValidationRules().phone_number_patterns;
                const phoneValid = phonePatterns.some(pattern => pattern.test(value));
                if (value && !phoneValid) {
                    result.valid = false;
                    result.errors.push('Please enter a valid phone number');
                }
            } else if (fieldName === 'student_id') {
                const pattern = this.getValidationRules().student_id_pattern;
                if (value && !pattern.test(value)) {
                    result.valid = false;
                    result.errors.push('Student ID can only contain letters, numbers, underscores, and dashes');
                }
            }
            
            this.log('VALIDATION', `Validated ${fieldType}.${fieldName}`, result);
            
        } catch (error) {
            this.log('ERROR', `Validation error for ${fieldType}.${fieldName}`, error);
            result.errors.push('Validation error occurred');
        }
        
        return result;
    }
    
    /**
     * Get pagination size for a specific context
     */
    getPaginationSize(context = 'default') {
        const settings = this.getPaginationSettings();
        const contextKey = `${context}_per_page`;
        return settings[contextKey] || settings.default_page_size;
    }
    
    /**
     * Check if file upload is allowed
     */
    validateFileUpload(file, fileType) {
        const constraints = this.getFileUploadConstraints();
        const result = {
            valid: true,
            errors: []
        };
        
        // Check file size
        const maxSizeKey = `${fileType}_max_size_mb`;
        const maxSizeMB = constraints[maxSizeKey];
        if (maxSizeMB && file.size > maxSizeMB * 1024 * 1024) {
            result.valid = false;
            result.errors.push(`File size must not exceed ${maxSizeMB}MB`);
        }
        
        // Check file extension
        const allowedExtensionsKey = `allowed_${fileType}_extensions`;
        const allowedExtensions = constraints[allowedExtensionsKey];
        if (allowedExtensions && file.name) {
            const extension = file.name.split('.').pop().toLowerCase();
            if (!allowedExtensions.includes(extension)) {
                result.valid = false;
                result.errors.push(`File type .${extension} not allowed. Allowed types: ${allowedExtensions.join(', ')}`);
            }
        }
        
        this.log('FILE_VALIDATION', `Validated ${fileType} file: ${file.name}`, result);
        return result;
    }
    
    /**
     * Clear all cached configuration
     */
    clearCache() {
        this.cache.clear();
        this.log('CACHE', 'Configuration cache cleared');
    }
    
    /**
     * Get all configurations for debugging
     */
    getAllConfigurations() {
        return {
            user_fields: this.getUserFieldConstraints(),
            student_profile: this.getStudentProfileConstraints(),
            exam_constraints: this.getExamConstraints(),
            question_constraints: this.getQuestionConstraints(),
            pagination: this.getPaginationSettings(),
            validation: this.getValidationRules(),
            business_rules: this.getBusinessRules(),
            file_upload: this.getFileUploadConstraints()
        };
    }
}

// Global instance
window.DataConfig = new DataConfigService();

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DataConfigService;
}

// Auto-initialization message
console.log('[DATA_CONFIG] Frontend Data Configuration Service initialized');
console.log('[DATA_CONFIG] Use window.DataConfig to access configuration methods');

// Example usage functions
window.DataConfig.examples = {
    validateStudentID: function(value) {
        return window.DataConfig.validateField('student', 'student_id', value);
    },
    
    validatePhoneNumber: function(value) {
        return window.DataConfig.validateField('student', 'phone_number', value);
    },
    
    getExamNameMaxLength: function() {
        return window.DataConfig.getExamConstraints().name_max_length;
    },
    
    getPageSize: function(context) {
        return window.DataConfig.getPaginationSize(context);
    },
    
    validatePDFUpload: function(file) {
        return window.DataConfig.validateFileUpload(file, 'pdf');
    }
};