# claude-integration

Test and verify Claude Code integration with the AI Employee vault, ensuring read/write operations work correctly.

## What you do

Verify that Claude Code can successfully read from and write to your vault, process files from `/Needs_Action/`, and create plans.

## Prerequisites

- Vault setup completed (`/vault-setup`)
- At least one test file in `/Needs_Action/`

## Instructions

### Step 1: Navigate to Vault

```bash
cd ~/AI_Employee_Vault
```

### Step 2: Test Basic Read Operation

```bash
claude "Read Dashboard.md and tell me the current system status"
```

**Expected Output:** Claude should read and summarize the Dashboard content.

### Step 3: Test Write Operation

```bash
claude "Update Dashboard.md: Set 'Last Activity' to current timestamp and add a note in Recent Activity that Claude Code integration test was successful"
```

**Expected Output:** Dashboard.md should be updated with new timestamp and activity note.

### Step 4: Create Test Action File

```bash
cat > Needs_Action/TEST_claude_integration.md << 'EOF'
---
type: test
created: 2026-02-05T00:00:00Z
priority: high
status: pending
---

## Test Task

This is a test file to verify Claude Code can process items from Needs_Action folder.

## Required Actions
- [ ] Read this file
- [ ] Understand the context
- [ ] Create a plan in Plans/ folder
- [ ] Update Dashboard with completion

## Success Criteria
- Plan file created in Plans/
- Dashboard shows this task as processed
- File moved to Done/ when complete

## Notes
Test the end-to-end workflow.
EOF
```

### Step 5: Test Action Processing

```bash
claude "Check the Needs_Action folder. Process any pending items by creating a plan in the Plans folder with specific steps to complete the task"
```

**Expected Output:**
- Claude reads the test file
- Creates a plan file in `Plans/` folder
- Plan includes specific actionable steps

### Step 6: Verify Plan Creation

```bash
ls -la Plans/
cat Plans/PLAN_*.md
```

**Expected Output:** A plan file should exist with proper structure and steps.

### Step 7: Test Approval Workflow

```bash
claude "For the test task, create an approval request in Pending_Approval folder that requires human review before marking as complete"
```

**Expected Output:**
- New file created in `Pending_Approval/`
- File has proper frontmatter and approval instructions

### Step 8: Test Manual Approval

```bash
# Review the approval request
cat Pending_Approval/APPROVAL_*.md

# Manually approve by moving to Approved folder
mv Pending_Approval/APPROVAL_*.md Approved/
```

### Step 9: Test Completion Flow

```bash
claude "Check the Approved folder. If there are approved items, execute them and move completed tasks from Needs_Action to Done folder. Update Dashboard with completion status"
```

**Expected Output:**
- Test file moved from `Needs_Action/` to `Done/`
- Dashboard updated with completion
- Log entry created (optional for Bronze tier)

### Step 10: Verify Complete Workflow

```bash
# Check folder states
echo "=== Needs_Action ==="
ls -la Needs_Action/

echo "=== Plans ==="
ls -la Plans/

echo "=== Approved ==="
ls -la Approved/

echo "=== Done ==="
ls -la Done/

# Check Dashboard update
echo "=== Dashboard Recent Activity ==="
grep -A 5 "Recent Activity" Dashboard.md
```

### Step 11: Test Company Handbook Integration

```bash
claude "Read Company_Handbook.md and explain what actions require human approval (HITL) vs what can be done autonomously"
```

**Expected Output:** Claude correctly identifies HITL boundaries from handbook.

### Step 12: Test Business Goals Integration

```bash
claude "Read Business_Goals.md and summarize Q1 2026 objectives. What is the status of Objective 1?"
```

**Expected Output:** Claude summarizes objectives and current progress.

### Step 13: Advanced Test - Multi-File Analysis

```bash
claude "Read Dashboard.md, Company_Handbook.md, and Business_Goals.md. Give me a complete status report of the AI Employee system including: current tier, active objectives, and next steps needed"
```

**Expected Output:** Comprehensive report pulling data from all three core files.

### Step 14: Test Error Handling

```bash
# Create a malformed file
echo "Bad content" > Needs_Action/MALFORMED.md

claude "Process all items in Needs_Action. If any file is malformed or cannot be processed, move it to a 'Rejected' folder with a note explaining the issue"
```

**Expected Output:**
- Claude identifies malformed file
- Moves it to `Rejected/` with explanation
- Processes valid files normally

### Step 15: Test Logging

```bash
claude "Create a log entry in Logs/2026-02-05.json documenting this integration test, including: timestamp, actions taken, files processed, and test result (success/failure)"
```

**Expected Output:** JSON log file created with proper structure.

## Validation Checklist

After completing all steps, verify:

- [ ] Claude can read Dashboard.md
- [ ] Claude can write/update Dashboard.md
- [ ] Claude can read files from Needs_Action/
- [ ] Claude creates plans in Plans/
- [ ] Claude creates approval requests in Pending_Approval/
- [ ] Claude processes approved items from Approved/
- [ ] Claude moves completed items to Done/
- [ ] Claude updates Dashboard with activities
- [ ] Claude understands Company_Handbook rules
- [ ] Claude references Business_Goals correctly
- [ ] Claude handles malformed files gracefully
- [ ] Claude creates proper log entries

## Success Criteria

**Bronze Tier Integration Complete When:**

1. **Read Operations:** Claude successfully reads all core files (Dashboard, Handbook, Goals)
2. **Write Operations:** Claude updates Dashboard and creates new files
3. **Workflow Understanding:** Claude follows the folder-based state machine (Needs_Action → Plans → Pending_Approval → Approved → Done)
4. **HITL Compliance:** Claude correctly identifies actions requiring approval
5. **Error Handling:** Claude handles malformed files appropriately

## Common Issues & Solutions

**Issue:** Claude says "file not found"
**Solution:** Ensure you're in the vault directory: `cd ~/AI_Employee_Vault`

**Issue:** Claude creates files in wrong location
**Solution:** Use absolute paths or verify working directory

**Issue:** Frontmatter errors
**Solution:** Check YAML syntax (use `---` delimiters, no tabs)

**Issue:** Claude doesn't follow handbook rules
**Solution:** Explicitly reference handbook in prompt: "According to Company_Handbook.md, ..."

**Issue:** Dashboard not updating
**Solution:** Check file permissions: `chmod 644 Dashboard.md`

## Integration Test Report Template

After completing all tests, create a report:

```bash
cat > Integration_Test_Report.md << 'EOF'
---
test_date: 2026-02-05
tier: Bronze
tester: [Your Name]
status: [Pass/Fail]
---

# Claude Code Integration Test Report

## Environment
- Vault Path: ~/AI_Employee_Vault
- Claude Code Version: [version]
- Python Version: [version]

## Test Results

### Read Operations
- [x] Dashboard.md: PASS
- [x] Company_Handbook.md: PASS
- [x] Business_Goals.md: PASS

### Write Operations
- [x] Update Dashboard: PASS
- [x] Create plan file: PASS
- [x] Create approval request: PASS

### Workflow Tests
- [x] Process Needs_Action: PASS
- [x] Create Plans: PASS
- [x] Handle Approvals: PASS
- [x] Move to Done: PASS

### HITL Compliance
- [x] Identifies actions requiring approval: PASS
- [x] Creates approval requests correctly: PASS
- [x] Respects handbook boundaries: PASS

### Error Handling
- [x] Handles malformed files: PASS
- [x] Creates error logs: PASS

## Issues Encountered
[List any issues and how they were resolved]

## Recommendations
[Any improvements or next steps]

## Overall Status
✅ PASS - Ready for Bronze Tier Demo

---
**Tested by:** [Name]
**Date:** 2026-02-05
EOF
```

## Next Steps

After successful integration:

1. `/bronze-demo` - Record Bronze tier demo video
2. Test with real watcher (Gmail or Filesystem)
3. Run end-to-end test with actual email or file
4. Proceed to Silver tier planning

## References

- Constitution Principle IX: Obsidian Vault as State Machine
- Constitution Principle II: Human-in-the-Loop for Sensitive Actions
- Hackathon Section 2B: Reasoning (Claude Code)
