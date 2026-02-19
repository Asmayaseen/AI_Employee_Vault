---
command: /sp.plan
type: implementation_planner
created: 2026-02-05
status: active
version: 1.0.0
---

# /sp.plan - Implementation Plan Generator

## Purpose
Generate detailed implementation plans from feature specifications, breaking down complex features into executable steps with architecture decisions, dependencies, and timelines.

---

## Command Usage

```bash
/sp.plan <feature-name> [--spec-file "path/to/spec.md"]
```

### Examples
```bash
/sp.plan gmail-watcher
/sp.plan ceo-briefing --spec-file "/Specs/ceo_briefing_spec.md"
/sp.plan odoo-integration
```

---

## What This Command Does

### 1. Load Feature Specification
- Read `/Specs/<feature-name>_spec.md`
- Extract user scenarios (P1/P2/P3)
- Identify functional requirements
- Understand technical context
- Note constraints and risks

### 2. Design Architecture
- Choose appropriate design patterns
- Define component structure
- Identify integration points
- Plan data flow
- Design error handling

### 3. Break Down into Phases
- **Phase 0:** Research & validation
- **Phase 1:** Core infrastructure
- **Phase 2:** P1 scenarios implementation
- **Phase 3:** P2 scenarios implementation
- **Phase 4:** P3 scenarios (optional)
- **Phase 5:** Testing & refinement

### 4. Identify Dependencies
- Required libraries/packages
- External services/APIs
- Existing system components
- Credentials/access needed
- Blocking dependencies

### 5. Create Implementation Plan
- Generate `/Plans/PLAN_<feature-name>_implementation.md`
- Structured step-by-step approach
- Architecture decisions documented
- Risk mitigation strategies
- Timeline estimates

---

## Plan Structure Generated

```markdown
# Implementation Plan: <Feature Name>

## Summary
- What: Brief description
- Why: Business value
- How: High-level approach

## Technical Context
- Language/Framework
- Dependencies
- Integration points
- Performance targets

## Constitution Check
- HITL approval needed?
- Sensitive data handling?
- Security requirements?
- Logging requirements?

## Project Structure
### Source Code Layout
- File/folder organization
- Module boundaries
- Configuration files

### Testing Strategy
- Unit tests
- Integration tests
- Contract tests

## Architecture Decisions

### Decision 1: [Architecture Choice]
**Options Considered:**
- Option A: [Description] - Pros/Cons
- Option B: [Description] - Pros/Cons

**Chosen:** Option A
**Rationale:** [Why this choice]

## Phase Breakdown

### Phase 0: Research (X hours)
- [ ] Task 1
- [ ] Task 2

### Phase 1: Foundation (X hours)
- [ ] Core infrastructure
- [ ] Base classes
- [ ] Configuration setup

### Phase 2: P1 Implementation (X hours)
- [ ] User scenario 1 (critical)
- [ ] Tests for scenario 1
- [ ] Integration

### Phase 3: P2 Implementation (X hours)
- [ ] User scenario 2 (important)

## Dependencies & Blockers
- Required before starting
- External dependencies
- Approval gates

## Risk Mitigation
- Technical risks → Mitigation
- Timeline risks → Mitigation

## Timeline
- Total estimate: X hours
- Critical path
- Milestones
```

---

## Input Sources

### Required Input:
1. **Feature Spec:** `/Specs/<feature-name>_spec.md`
   - User scenarios
   - Requirements
   - Technical context

### Context Sources:
2. **Constitution:** `/sp.constitution.md`
   - HITL boundaries
   - Security requirements
   - Logging standards

3. **History:** `/Prompts/history_context.md`
   - Lessons learned
   - Existing patterns
   - Known issues

4. **Existing Code:** (if applicable)
   - Current architecture
   - Reusable components
   - Integration points

5. **Dependencies:** `package.json`, `requirements.txt`, etc.

---

## Output Files Created

### 1. Implementation Plan
**Location:** `/Plans/PLAN_<feature-name>_implementation.md`
**Content:**
- Complete implementation roadmap
- Architecture decisions with rationale
- Phase-by-phase breakdown
- Dependencies and blockers
- Timeline and estimates

### 2. Architecture Decision Records (if significant)
**Location:** `/Specs/ADR_<decision-name>.md`
**Trigger:** When major architectural choice made
**Content:**
- Decision context
- Options considered
- Trade-offs analysis
- Chosen solution and rationale

### 3. Task Trigger (automatic)
**After plan approved:** Suggest `/sp.tasks` to generate task list

---

## Architecture Decision Framework

### When to Document as ADR:

**Significant Decisions** (require ADR):
- Framework/library selection (e.g., FastAPI vs Flask)
- Data storage approach (e.g., SQLite vs PostgreSQL)
- Authentication method (e.g., OAuth vs JWT)
- Deployment strategy (e.g., Docker vs direct)
- Communication protocol (e.g., REST vs GraphQL)

**Minor Decisions** (document in plan only):
- File naming conventions
- Code organization within module
- Specific algorithm choice (if reversible)
- Logging format details

### ADR Template:
```markdown
# ADR-XXX: <Decision Title>

## Status
Proposed | Accepted | Deprecated | Superseded

## Context
What is the issue we're facing?

## Decision
What are we choosing to do?

## Consequences
What becomes easier or harder?

## Alternatives Considered
- Option 1: Pros/Cons
- Option 2: Pros/Cons
```

---

## Workflow Integration

```
/sp.specify → Spec created
                 ↓
            /sp.plan
                 ↓
          Analyze spec
                 ↓
          Design architecture
                 ↓
          Create plan file
                 ↓
          Check constitution
                 ↓
       ┌─────────┴─────────┐
       ↓                   ↓
  Complete plan      Need approval?
       ↓                   ↓
  Suggest          Create approval
  /sp.tasks        request
```

---

## Constitution Check (Automated)

### Security Checks:
```python
# Automated checks performed:
1. Does feature access external APIs?
   → Yes: Document credential management

2. Does feature handle sensitive data?
   → Yes: Define encryption/protection

3. Does feature send/post/pay?
   → Yes: Require HITL approval gate

4. Does feature delete/modify data?
   → Yes: Require backup strategy

5. Does feature run continuously?
   → Yes: Define monitoring and restart logic
```

### HITL Approval Matrix:
| Action Type | Auto-Execute? | Require Approval? |
|-------------|---------------|-------------------|
| Read data | ✅ Yes | ❌ No |
| Create drafts | ✅ Yes | ❌ No |
| Send messages | ❌ No | ✅ Yes |
| Make payments | ❌ No | ✅ Always |
| Delete files | ❌ No | ✅ Yes |
| Modify external systems | ❌ No | ✅ Yes |

---

## Example: Gmail Watcher Implementation Plan

**Input Spec:** `/Specs/gmail_watcher_spec.md`

**Generated Plan Includes:**

### Summary
- **What:** Gmail inbox monitoring with action file creation
- **Why:** Automate email triage and response workflows
- **How:** Python watcher using Gmail API, BaseWatcher pattern, PM2 supervision

### Technical Context
- **Language:** Python 3.13+
- **Dependencies:** google-auth-oauthlib, google-api-python-client, PM2
- **Tier:** Silver (multiple watchers)
- **Performance:** Check every 2 minutes, <5 second processing time

### Constitution Check
✅ **HITL:** Read-only access (no autonomous sending)
✅ **Sensitive Data:** OAuth tokens in OS keychain, not in vault
✅ **Security:** Credentials in .env, never committed
✅ **Logging:** All checks logged to /Logs/GmailWatcher.log
✅ **Audit:** JSON format with timestamp, action, result

### Architecture Decisions

**Decision 1: Gmail API vs IMAP**
- **Chosen:** Gmail API
- **Rationale:** Better filtering, official support, OAuth security
- **Trade-off:** More complex auth setup vs simpler IMAP

**Decision 2: Polling vs Push Notifications**
- **Chosen:** Polling (2-minute interval)
- **Rationale:** Simpler implementation, no webhook setup needed
- **Trade-off:** 2-minute delay vs real-time push (acceptable for Bronze tier)

### Phase Breakdown

**Phase 0: Research & Setup (2 hours)**
- [ ] Enable Gmail API in Google Cloud Console
- [ ] Create OAuth credentials
- [ ] Test authentication flow
- [ ] Verify API quotas (10k requests/day sufficient)

**Phase 1: Core Watcher (4 hours)**
- [ ] Implement GmailWatcher class inheriting BaseWatcher
- [ ] OAuth authentication with token persistence
- [ ] Check inbox for important/unread emails
- [ ] Extract email metadata (from, subject, date)
- [ ] Create structured action files

**Phase 2: P1 Scenario - Email Detection (2 hours)**
- [ ] Test with real Gmail account
- [ ] Verify action files created correctly
- [ ] Test duplicate prevention
- [ ] Validate YAML frontmatter

**Phase 3: Integration & Deployment (2 hours)**
- [ ] PM2 configuration
- [ ] Health check logging
- [ ] Error handling and retry logic
- [ ] Documentation

### Dependencies
- Google Cloud Console access
- OAuth credentials (credentials.json)
- BaseWatcher already implemented ✅
- PM2 installed
- Python packages: google-auth, google-api-python-client

### Timeline
- **Total:** 10 hours
- **Critical path:** OAuth setup → Watcher implementation → Testing
- **Milestone 1:** Authentication working (2 hours)
- **Milestone 2:** First email detected (6 hours)
- **Milestone 3:** Production ready (10 hours)

---

## Best Practices

### Do's ✅
- Reference spec constantly
- Document architecture decisions
- Break into small, testable phases
- Identify blockers early
- Estimate conservatively (add 50% buffer)
- Plan for error scenarios
- Include rollback strategy
- Consider future extensibility

### Don'ts ❌
- Don't start without reading spec
- Don't assume implementation details
- Don't skip constitution check
- Don't plan too far ahead (focus on P1)
- Don't ignore dependencies
- Don't forget documentation
- Don't skip testing phases

---

## Phase Estimation Guidelines

### Research Phase (Phase 0)
- **Simple feature:** 1-2 hours
- **Medium complexity:** 2-4 hours
- **Complex integration:** 4-8 hours
- **Unknown technology:** 8+ hours

### Implementation Phases
**Per P1 scenario:**
- **Simple (CRUD):** 2-4 hours
- **Medium (API integration):** 4-8 hours
- **Complex (multi-system):** 8-16 hours

**Add for:**
- Testing: +30% of implementation time
- Documentation: +20% of implementation time
- Integration: +50% if new integration point
- Learning curve: +100% if new technology

---

## Risk Assessment

### Technical Risks
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| API rate limits | Medium | High | Implement exponential backoff |
| Auth token expiry | High | Medium | Refresh token logic |
| Duplicate processing | Medium | Medium | Track processed IDs |

### Timeline Risks
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| OAuth setup complexity | High | Medium | Allocate extra time in Phase 0 |
| Credential issues | Medium | High | Test early with sandbox |
| PM2 config problems | Low | Low | Use existing patterns |

---

## Approval Gates

### Before Starting Implementation:
- [ ] Plan reviewed by human
- [ ] Architecture decisions approved
- [ ] Dependencies available
- [ ] Credentials obtained (if needed)
- [ ] Timeline acceptable

### Before Moving to Next Phase:
- [ ] Previous phase complete
- [ ] Tests passing
- [ ] Documentation updated
- [ ] No critical bugs

---

## Integration with Other Commands

### Workflow:
```
/sp.specify → /sp.plan → /sp.tasks → /sp.implement

                Plan
                 ↓
         Constitution check
                 ↓
         Architecture design
                 ↓
         Phase breakdown
                 ↓
         ┌───────┴────────┐
         ↓                ↓
    Plan approved    Need changes?
         ↓                ↓
    /sp.tasks      Revise plan
```

---

## Skill Growth Notes

### What This Command Teaches AI:
- How to translate specs into executable plans
- How to make architecture decisions
- How to identify dependencies
- How to estimate timelines
- How to mitigate risks
- How to check constitution compliance

### Improvements Over Time:
- More accurate time estimates
- Better architecture choices
- Faster dependency identification
- Improved risk assessment
- Cleaner phase breakdowns

---

## Metrics to Track

| Metric | Target | Current |
|--------|--------|---------|
| Plans created per week | 2-4 | TBD |
| Plan acceptance rate | >85% | TBD |
| Time estimate accuracy | ±30% | TBD |
| Plans progressing to tasks | >90% | TBD |
| Architecture decisions documented | 100% | TBD |

---

## Version History

- **v1.0.0** (2026-02-05) - Initial command specification
  - Core planning logic
  - Constitution check integration
  - Architecture decision framework
  - Phase breakdown methodology

---

## Related Documentation

- **Input:** `/Specs/<feature>_spec.md`
- **Output:** `/Plans/PLAN_<feature>_implementation.md`
- **Constitution:** `/sp.constitution.md`
- **Next Step:** `/Specs/sp.tasks.md`
- **Templates:** `.specify/templates/plan-template.md`

---

**Status:** ✅ Active
**Required for:** All features before task generation
**Tier:** All tiers

---

*This command follows SpecKitPlus methodology for structured implementation planning*
