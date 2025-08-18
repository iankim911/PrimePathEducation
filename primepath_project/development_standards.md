# RoutineTest Development Standards
## 5-Agent TDD System - Best Practices

### Code Quality Standards
- [ ] 90%+ test coverage for all new code
- [ ] Type hints on all functions
- [ ] Docstrings following Google style
- [ ] No hardcoded values (use settings/constants)
- [ ] Proper exception handling with logging
- [ ] Database queries optimized (select_related, prefetch_related)
- [ ] No N+1 query problems

### Testing Standards
- [ ] Tests written BEFORE implementation
- [ ] Unit tests for all models and utilities
- [ ] Integration tests for all views
- [ ] End-to-end tests for user workflows
- [ ] Edge case and error testing
- [ ] Performance benchmarks for critical paths

### Security Standards
- [ ] CSRF protection on all forms
- [ ] XSS prevention (template escaping)
- [ ] SQL injection prevention (ORM usage)
- [ ] Proper authentication/authorization
- [ ] Sensitive data encryption
- [ ] Rate limiting on APIs
- [ ] Input validation and sanitization

### Documentation Standards
- [ ] README for each module
- [ ] API documentation with examples
- [ ] Inline code comments for complex logic
- [ ] Architecture Decision Records (ADRs)
- [ ] User-facing documentation
- [ ] Deployment documentation

### Database Standards
- [ ] Proper indexes on foreign keys
- [ ] UUID primary keys for security
- [ ] Soft deletes where appropriate
- [ ] Audit fields (created_at, updated_at, created_by)
- [ ] Database migrations tested and reversible

### Frontend Standards
- [ ] Progressive enhancement
- [ ] Accessibility (ARIA labels, keyboard nav)
- [ ] Mobile-responsive design
- [ ] Loading states for async operations
- [ ] Error messages user-friendly
- [ ] Console error-free
- [ ] Cross-browser compatibility

### Git Standards
- [ ] Atomic commits with clear messages
- [ ] Feature branches with PR reviews
- [ ] No direct commits to main
- [ ] Tests must pass before merge
- [ ] Version tagging for releases