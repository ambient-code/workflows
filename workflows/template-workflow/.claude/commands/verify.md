# /verify - Verify and Validate Implementation

## Purpose
Verify that the implementation meets requirements, passes all tests, follows best practices, and is ready for deployment or review. This command performs comprehensive validation and generates a verification report.

## Prerequisites
- Workspace initialized (run `/init` if not done)
- Implementation completed (run `/execute` first)

## Arguments
- `target` (required): What you want to verify (feature name, component, or "all")

## Process

1. **Review implementation artifacts**
   - Read implementation summary
   - Review code changes
   - Check documentation updates

2. **Run automated tests**
   - Execute unit tests
   - Execute integration tests
   - Execute end-to-end tests (if applicable)
   - Check test coverage

3. **Perform code quality checks**
   - Run linters and formatters
   - Check for code smells
   - Verify coding standards compliance
   - Review complexity metrics

4. **Security validation**
   - Run security scanners
   - Check for known vulnerabilities
   - Validate input sanitization
   - Review authentication/authorization

5. **Performance validation**
   - Run performance benchmarks
   - Check for memory leaks
   - Validate response times
   - Review resource usage

6. **Compliance checks**
   - Verify requirements are met
   - Check against acceptance criteria
   - Validate against specification
   - Ensure plan objectives achieved

7. **Documentation review**
   - Verify API documentation is complete
   - Check README updates
   - Validate code comments
   - Ensure examples are correct

8. **Generate verification report**
   - Compile all findings
   - List passed and failed checks
   - Document any issues found
   - Provide recommendations

## Output
- Verification report: `artifacts/verification/<feature-name>/verification-report.md`
- Test results: `artifacts/verification/<feature-name>/test-results.xml`
- Coverage report: `artifacts/verification/<feature-name>/coverage/`
- Security scan results: `artifacts/verification/<feature-name>/security-scan.json`
- Updates workflow state in `.workflow-config.json`

## Usage Examples

```
/verify user-authentication
```

```
/verify payment-processing
```

```
/verify all
```

## Output Format

### Verification Report

```markdown
# Verification Report: [Feature/Project Name]

**Date**: 2025-11-13
**Verified By**: Claude (Ambient Workflow Assistant)
**Status**: ✅ PASSED | ⚠️ PASSED WITH WARNINGS | ❌ FAILED

---

## Executive Summary

Brief overview of verification results and overall status.

---

## Test Results

### Unit Tests
- **Status**: ✅ PASSED
- **Tests Run**: 45
- **Passed**: 45
- **Failed**: 0
- **Skipped**: 0
- **Duration**: 2.3s
- **Coverage**: 91%

### Integration Tests
- **Status**: ✅ PASSED
- **Tests Run**: 12
- **Passed**: 12
- **Failed**: 0
- **Skipped**: 0
- **Duration**: 8.7s

### End-to-End Tests
- **Status**: ✅ PASSED
- **Tests Run**: 5
- **Passed**: 5
- **Failed**: 0
- **Skipped**: 0
- **Duration**: 15.2s

### Coverage Report
```
File                    | Statements | Branches | Functions | Lines
------------------------|------------|----------|-----------|-------
src/auth/service.ts     |      95.5% |    87.5% |     100%  | 95.0%
src/auth/controller.ts  |      92.3% |    83.3% |      90%  | 91.7%
src/auth/middleware.ts  |      88.9% |    75.0% |      85%  | 87.5%
------------------------|------------|----------|-----------|-------
**Overall**             |    **91.2%** |  **82.1%** |  **90.5%** | **90.8%**
```

---

## Code Quality

### Linting
- **Status**: ✅ PASSED
- **Issues**: 0 errors, 0 warnings
- **Linter**: ESLint v8.x

### Formatting
- **Status**: ✅ PASSED
- **Formatter**: Prettier v3.x
- **Files checked**: 23

### Complexity Metrics
- **Average Cyclomatic Complexity**: 4.2 (target: <10)
- **Max Cyclomatic Complexity**: 8 in `auth/service.ts:validateToken()`
- **Status**: ✅ PASSED

### Code Smells
- **Status**: ✅ PASSED
- **Issues Found**: 0
- **Tool**: SonarQube

---

## Security

### Vulnerability Scan
- **Status**: ✅ PASSED
- **Critical**: 0
- **High**: 0
- **Medium**: 0
- **Low**: 0
- **Tool**: npm audit / Snyk

### Security Best Practices
- [x] Input validation implemented
- [x] SQL injection prevention (parameterized queries)
- [x] XSS prevention (output encoding)
- [x] CSRF protection enabled
- [x] Authentication properly implemented
- [x] Authorization checks in place
- [x] Sensitive data encrypted
- [x] Secrets not in code

### Security Recommendations
- None at this time

---

## Performance

### Benchmarks
- **Status**: ✅ PASSED
- **Response Time (avg)**: 45ms (target: <100ms)
- **Response Time (p95)**: 87ms (target: <200ms)
- **Response Time (p99)**: 142ms (target: <500ms)
- **Throughput**: 220 req/sec (target: >100 req/sec)

### Memory Usage
- **Status**: ✅ PASSED
- **Baseline**: 45 MB
- **Under Load**: 78 MB
- **Memory Leaks**: None detected

### Database Performance
- **Query Time (avg)**: 12ms (target: <50ms)
- **N+1 Queries**: None detected
- **Indexes**: Properly utilized

---

## Requirements Compliance

### Functional Requirements
- [x] FR-1: Users can log in with email and password
- [x] FR-2: Users can reset password via email
- [x] FR-3: Session timeout after 30 minutes of inactivity
- [x] FR-4: Support OAuth2 authentication
- [x] FR-5: Multi-factor authentication (MFA) support

### Non-Functional Requirements
- [x] NFR-1: Response time <100ms for 95% of requests
- [x] NFR-2: Support 1000 concurrent users
- [x] NFR-3: 99.9% uptime SLA
- [x] NFR-4: GDPR compliance
- [x] NFR-5: SOC 2 compliance

### Acceptance Criteria
- [x] All tests passing
- [x] Code coverage >80%
- [x] No security vulnerabilities
- [x] Documentation complete
- [x] Performance benchmarks met

---

## Documentation

### API Documentation
- **Status**: ✅ PASSED
- [x] All endpoints documented
- [x] Request/response examples provided
- [x] Error codes documented
- [x] Authentication requirements specified

### Code Documentation
- **Status**: ✅ PASSED
- [x] Public APIs have JSDoc comments
- [x] Complex logic is explained
- [x] TODOs are documented
- [x] Examples provided where helpful

### User Documentation
- **Status**: ✅ PASSED
- [x] README updated
- [x] Setup instructions clear
- [x] Usage examples provided
- [x] Migration guide included (if applicable)

---

## Issues and Recommendations

### Critical Issues
None

### High Priority Issues
None

### Medium Priority Issues
None

### Low Priority Issues
None

### Recommendations
1. Consider adding more edge case tests for token expiration
2. Monitor performance in production for first week
3. Set up alerting for authentication failures

---

## Deployment Readiness

### Pre-Deployment Checklist
- [x] All tests passing
- [x] Code reviewed
- [x] Security scan clean
- [x] Performance validated
- [x] Documentation updated
- [x] Database migrations ready
- [x] Environment variables documented
- [x] Rollback plan prepared
- [x] Monitoring configured
- [x] Alerts configured

### Deployment Status
**✅ READY FOR DEPLOYMENT**

---

## Sign-off

This implementation has been verified and meets all requirements for deployment.

**Verified by**: Claude (Ambient Workflow Assistant)
**Date**: 2025-11-13
**Next Steps**:
1. Create pull request
2. Code review by team
3. Deploy to staging environment
4. Final validation in staging
5. Deploy to production

---

## Artifacts

- Test results: `artifacts/verification/<feature-name>/test-results.xml`
- Coverage report: `artifacts/verification/<feature-name>/coverage/index.html`
- Security scan: `artifacts/verification/<feature-name>/security-scan.json`
- Performance report: `artifacts/verification/<feature-name>/performance.json`
```

## Notes
- Run verification before creating pull requests
- Address all critical and high-priority issues before deployment
- Keep verification reports for compliance and audit purposes
- Re-run verification after fixing any issues
- Verification does not replace peer code review
