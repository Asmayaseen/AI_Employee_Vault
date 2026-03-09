# Skill: E2E Pipeline Testing (Gold Tier)

## Overview
End-to-end validation of the complete AI Employee pipeline from input ingestion through processing to output generation and approval.

## Prerequisites
- All watchers operational
- Dashboard API running
- Vault structure complete
- Audit logging active

## Capabilities
- **Input Simulation**: Generate test emails, files, and messages
- **Pipeline Tracing**: Track items through the full processing chain
- **Output Validation**: Verify correct vault folder placement
- **Integration Testing**: Test watcher-to-dashboard-to-approval flow
- **Performance Benchmarks**: Measure processing latency

## Implementation Details

### Test Pipeline: test_pipeline.py
- Location: `AI_Employee_Vault/Watchers/test_pipeline.py`
- Generates synthetic test inputs
- Traces through: Inbox -> Needs_Action -> Plans -> Pending_Approval

### Test Scenarios
| Scenario | Input | Expected Output |
|----------|-------|----------------|
| Email processing | Test email | Action file in Needs_Action/ |
| File drop | .md in Inbox/ | Processed and moved |
| Approval flow | File in Pending_Approval/ | Moved to Approved/ on approve |
| Rejection flow | File in Pending_Approval/ | Moved to Rejected/ on reject |
| Error recovery | Simulated failure | Queued and retried |

### Validation Checks
1. File exists in correct folder after processing
2. Audit log entry created for each action
3. No orphaned files in intermediate folders
4. Processing completes within timeout threshold
5. Dashboard API reflects current state

## Acceptance Criteria
- [ ] All test scenarios pass
- [ ] Pipeline handles concurrent inputs
- [ ] Error cases are tested
- [ ] Performance within acceptable thresholds
- [ ] Audit trail is complete for all test actions
