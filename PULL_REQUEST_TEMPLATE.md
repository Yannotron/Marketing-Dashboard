## Summary

Describe the change and motivation.

## Type of Change

- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📚 Documentation update
- [ ] 🔧 Refactoring (no functional changes)
- [ ] ⚡ Performance improvement
- [ ] 🔒 Security fix

## Backend Checklist

### Code Quality
- [ ] Minimal scope: only files relevant to the task changed
- [ ] No duplication introduced; removed superseded logic
- [ ] Simple solution first; no new pattern/tech unless justified
- [ ] Files ≲300 LOC where practical
- [ ] Code follows existing patterns and conventions

### Testing
- [ ] Unit tests added/updated for new functionality
- [ ] Integration tests added/updated for API changes
- [ ] Property tests added for idempotent operations
- [ ] Tests cover edge cases and error conditions
- [ ] All tests pass locally (`pytest -q`)
- [ ] Test coverage maintained or improved

### Security & Data
- [ ] PII stripping implemented for external display
- [ ] Input validation and sanitization added
- [ ] No hardcoded secrets or credentials
- [ ] Database operations use UPSERTs where appropriate
- [ ] Error handling doesn't expose sensitive information

### Code Standards
- [ ] Ruff linting passes (`ruff check .`)
- [ ] Black formatting applied (`black --check .`)
- [ ] MyPy type checking passes (`mypy .`)
- [ ] No mocks/stubs leaked to dev/prod code paths
- [ ] Environment separation maintained

## Frontend Checklist

### Code Quality
- [ ] Components are properly typed with TypeScript
- [ ] Props interfaces are well-defined
- [ ] No unused imports or variables
- [ ] Code follows React best practices

### Testing
- [ ] Unit tests added/updated for components
- [ ] Integration tests for critical user flows
- [ ] Tests use React Testing Library best practices
- [ ] All tests pass locally (`npm run test`)
- [ ] Test coverage maintained or improved

### Performance & Accessibility
- [ ] Lighthouse performance scores maintained
- [ ] Components are accessible (ARIA labels, keyboard navigation)
- [ ] Images have alt text
- [ ] Color contrast meets WCAG standards
- [ ] No console errors or warnings

### Code Standards
- [ ] ESLint passes (`npm run lint`)
- [ ] TypeScript compilation passes (`tsc --noEmit`)
- [ ] Prettier formatting applied
- [ ] No unused dependencies

## Security Review

- [ ] Input validation implemented
- [ ] XSS prevention measures in place
- [ ] CSRF protection where applicable
- [ ] Dependencies reviewed for vulnerabilities
- [ ] No sensitive data exposed in client-side code
- [ ] API endpoints properly secured

## Documentation

- [ ] Code is self-documenting with clear naming
- [ ] Complex logic has inline comments
- [ ] README updated if needed
- [ ] API changes documented
- [ ] Breaking changes documented

## Deployment & Environment

- [ ] No `.env` files modified
- [ ] Environment variables properly configured
- [ ] Database migrations included if needed
- [ ] Backward compatibility maintained
- [ ] Rollback plan considered

## Impact Summary

### Modules Affected
- List specific files/modules changed
- Note any shared utilities or common code

### Risks & Considerations
- Potential breaking changes
- Performance implications
- Security considerations
- Data migration requirements

### Follow-up Tasks
- [ ] Any additional work needed
- [ ] Monitoring or alerting updates
- [ ] Documentation updates required

## Testing Instructions

### Manual Testing
1. Steps to test the changes locally
2. Edge cases to verify
3. Integration points to check

### Automated Testing
- [ ] All existing tests pass
- [ ] New tests cover the changes
- [ ] CI pipeline passes

## Additional Notes

Any additional context, concerns, or considerations for reviewers.


