---
command: /sp.specify
type: specification_generator
created: 2026-02-05
status: active
version: 1.0.0
---

# /sp.specify - Feature Specification Generator

## Purpose
Generate comprehensive feature specifications using SpecKitPlus methodology for AI Employee system features.

---

## Command Usage

```bash
/sp.specify <feature-name> [--description "feature description"]
```

### Examples
```bash
/sp.specify gmail-watcher --description "Monitor Gmail inbox for important emails"
/sp.specify ceo-briefing --description "Weekly business audit and reporting"
/sp.specify odoo-integration --description "Integrate Odoo accounting system"
```

---

## What This Command Does

### 1. Analyze Feature Request
- Parse feature name and description
- Identify tier (Bronze/Silver/Gold/Platinum)
- Determine complexity and dependencies
- Check Company_Handbook.md for relevant rules
- Check Business_Goals.md for alignment

### 2. Generate Specification File
- Create `/Specs/<feature-name>_spec.md`
- Use SpecKitPlus template structure
- Fill in known sections automatically
- Mark unknown sections with `[NEEDS CLARIFICATION]`
- Include user scenarios and acceptance criteria

### 3. Identify Gaps
- List missing information needed
- Suggest clarifying questions
- Identify dependencies on other features
- Flag potential blockers

### 4. Create Clarification Request (if needed)
- Generate `/Needs_Action/CLARIFY_<feature-name>.md`
- List specific questions for human
- Explain why each piece of information is needed

---

## Specification Structure Generated

```markdown
# Feature Specification: <Feature Name>

## User Scenarios & Testing
- P1 scenarios (critical)
- P2 scenarios (important)
- P3 scenarios (nice-to-have)

## Requirements
### Functional Requirements
- FR-001: System MUST...
- FR-002: System MUST...

### Non-Functional Requirements
- Performance targets
- Security requirements
- Scalability needs

## Success Criteria
- Measurable outcomes
- Acceptance tests
- Quality gates

## Technical Context
- Language/framework
- Dependencies
- Integration points

## Risks & Constraints
- Technical risks
- Resource constraints
- Timeline considerations

## Out of Scope
- Explicitly excluded features
- Future enhancements
```

---

## Input Sources

### Primary Sources
1. **User Input:** Feature name and description
2. **Company_Handbook.md:** Business rules and constraints
3. **Business_Goals.md:** Alignment with objectives
4. **0-hackathon.md:** Tier definitions and architecture
5. **sp.constitution.md:** Operating principles

### Context Sources
6. **Dashboard.md:** Current system state
7. **history_context.md:** Lessons learned
8. **Existing specs:** Related features

---

## Output Files Created

### 1. Specification File
**Location:** `/Specs/<feature-name>_spec.md`
**Content:**
- Complete feature specification
- User scenarios (prioritized P1/P2/P3)
- Functional requirements
- Technical context
- Success criteria

### 2. Clarification File (if needed)
**Location:** `/Needs_Action/CLARIFY_<feature-name>.md`
**Content:**
- List of questions
- Missing information
- Rationale for each question

### 3. Plan Trigger (optional)
**If spec complete:** Automatically suggest `/sp.plan` next

---

## Workflow Integration

```
User: /sp.specify gmail-watcher
           ↓
    Analyze request
           ↓
    Generate spec file
           ↓
    Identify gaps
           ↓
    ┌──────┴──────┐
    ↓             ↓
Complete?    Need clarity?
    ↓             ↓
Suggest      Create
/sp.plan     CLARIFY file
```

---

## Validation Rules

### Before Creating Spec:
- [ ] Feature name is clear and descriptive
- [ ] Description provided (or inferred from name)
- [ ] No duplicate spec exists
- [ ] Tier alignment identified
- [ ] Constitution compliance checked

### Spec Quality Gates:
- [ ] At least 3 user scenarios defined
- [ ] All P1 scenarios are independently testable
- [ ] Functional requirements are specific and measurable
- [ ] Success criteria are clear
- [ ] Technical context addresses tier requirements
- [ ] Risks and constraints identified

---

## Example: Gmail Watcher Spec

**Command:**
```bash
/sp.specify gmail-watcher --description "Monitor Gmail inbox for important emails and create action files"
```

**Generated Spec Includes:**

### User Scenarios
**P1:** As a user, I want important emails detected automatically so I can respond quickly
- **Given** Gmail watcher is running
- **When** an important email arrives
- **Then** action file created in /Needs_Action/ within 2 minutes

**P2:** As a user, I want to configure which emails are "important"
**P3:** As a user, I want email summaries with key information

### Functional Requirements
- FR-001: System MUST authenticate with Gmail API using OAuth 2.0
- FR-002: System MUST check inbox every 2 minutes
- FR-003: System MUST filter for emails marked "important"
- FR-004: System MUST create structured action files with email content
- FR-005: System MUST log all activities

### Technical Context
- **Tier:** Silver (multiple watchers)
- **Language:** Python 3.13+
- **Dependencies:** google-auth, google-api-python-client
- **Integration:** BaseWatcher pattern, PM2 process management

### Success Criteria
- SC-001: 95% of important emails detected within 2 minutes
- SC-002: Zero duplicate action files created
- SC-003: Watcher uptime >99% over 24 hours

---

## Constitution Compliance

### Principles Applied:
1. **Safety First:** Read-only Gmail access (no sending in watcher)
2. **Auditability:** All email checks logged
3. **Modular Engineering:** BaseWatcher pattern inheritance
4. **HITL:** No autonomous email sending (just detection)
5. **Folder Workflow:** Creates files in /Needs_Action/ only

### Checks Performed:
- [ ] Feature requires HITL approval? → Document in spec
- [ ] Handles sensitive data? → Define protection measures
- [ ] External API access? → Document credentials management
- [ ] Error scenarios defined? → Include retry logic
- [ ] Logging requirements met? → Specify log format

---

## Clarification Triggers

### When to Create CLARIFY File:

1. **Missing Critical Info:**
   - No description provided and can't infer from name
   - Feature conflicts with existing system
   - Unclear which tier this belongs to

2. **Ambiguous Requirements:**
   - Multiple valid interpretations
   - Conflicting constraints
   - Unclear success criteria

3. **Dependency Issues:**
   - Depends on unimplemented features
   - Requires external access not yet configured
   - Integration point unclear

### Clarification File Format:
```markdown
---
type: clarification_request
feature: <feature-name>
created: <timestamp>
priority: high|medium|low
---

# Clarification Needed: <Feature Name>

## Questions for Human

### Q1: [Question]
**Why needed:** [Rationale]
**Impact if missing:** [Consequence]
**Suggested answer:** [If you have a guess]

### Q2: [Question]
...

## Current Understanding
[What we know so far]

## Assumptions Made
[What we're assuming - may need correction]

## To Proceed
Answer questions above and move this file to /Approved/
```

---

## Best Practices

### Do's ✅
- Start with user scenarios (what user wants to achieve)
- Make requirements specific and measurable
- Define clear success criteria
- Identify risks early
- Document assumptions
- Reference constitution principles
- Check tier alignment

### Don'ts ❌
- Don't assume unstated requirements
- Don't skip "out of scope" section
- Don't write technical implementation in spec (that's for plan)
- Don't create specs without user scenarios
- Don't ignore Company_Handbook rules
- Don't forget non-functional requirements

---

## Integration with Other Commands

### After /sp.specify:
```
/sp.specify → Spec created → /sp.clarify (if needed)
                          → /sp.plan (if complete)
```

### Workflow:
1. **User requests feature** → `/sp.specify feature-name`
2. **Spec generated** → Review `/Specs/feature-name_spec.md`
3. **If unclear** → Answer `/Needs_Action/CLARIFY_feature-name.md`
4. **If clear** → Run `/sp.plan feature-name`
5. **Plan complete** → Run `/sp.tasks feature-name`
6. **Tasks ready** → Run `/sp.implement`

---

## Skill Growth Notes

### What This Command Teaches AI:
- How to structure feature specifications
- How to identify missing information
- How to prioritize user scenarios
- How to align with business goals
- How to check constitution compliance

### Improvements Over Time:
- Better question generation for clarifications
- Improved tier classification
- More accurate dependency identification
- Faster spec generation
- Higher quality initial drafts

---

## Metrics to Track

| Metric | Target | Current |
|--------|--------|---------|
| Specs created per week | 3-5 | TBD |
| Clarifications needed (%) | <30% | TBD |
| Spec acceptance rate | >90% | TBD |
| Time to create spec | <15 min | TBD |
| Specs progressing to plan | >80% | TBD |

---

## Version History

- **v1.0.0** (2026-02-05) - Initial command specification
  - Core spec generation logic
  - SpecKitPlus integration
  - Clarification workflow
  - Constitution compliance checks

---

## Related Documentation

- **Template:** `/Specs/spec_template.md`
- **Constitution:** `/sp.constitution.md`
- **Next Step:** `/Specs/sp.plan.md`
- **Methodology:** SpecKitPlus (0-hackathon.md)

---

**Status:** ✅ Active
**Required for:** All new features before implementation
**Tier:** All tiers

---

*This command follows SpecKitPlus methodology for structured feature specification*
