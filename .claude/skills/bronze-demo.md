# bronze-demo

Record a demonstration video showcasing Bronze tier functionality for hackathon submission.

## What you do

Create a 5-10 minute demo video that demonstrates all Bronze tier deliverables working together.

## Prerequisites

- Vault setup completed
- One watcher operational
- Claude Code integration tested
- Screen recording software installed

## Demo Script

### Part 1: Introduction (1 minute)

**Script:**
```
"Hi, this is my Bronze Tier submission for the Personal AI Employee Hackathon.

In this demo, I'll show:
1. The Obsidian vault structure
2. A working watcher (Gmail OR Filesystem)
3. Claude Code reading and processing files
4. The complete workflow from detection to completion

Let's get started."
```

**Actions:**
- Show your face/avatar (optional)
- Display hackathon document briefly
- Show your setup environment

### Part 2: Vault Structure Tour (1-2 minutes)

**Script:**
```
"First, let me show you the Obsidian vault structure that serves as the AI Employee's brain."
```

**Actions:**
1. Open Obsidian
2. Show folder structure (Needs_Action, Plans, Pending_Approval, etc.)
3. Open and explain Dashboard.md
4. Open and explain Company_Handbook.md (focus on HITL rules)
5. Open and explain Business_Goals.md

**Key Points to Highlight:**
- "This is the Dashboard - real-time status of the AI Employee"
- "The Company Handbook defines rules like what requires approval"
- "Business Goals guide the AI's prioritization"
- "The folder structure creates a state machine for workflows"

### Part 3: Watcher Demonstration (2-3 minutes)

**Choose Gmail OR Filesystem:**

#### Option A: Gmail Watcher Demo

**Script:**
```
"Now I'll demonstrate the Gmail watcher. It monitors my inbox for important emails and creates action files automatically."
```

**Actions:**
1. Show watcher code briefly (base_watcher.py, gmail_watcher.py)
2. Show PM2 status (if using): `pm2 status`
3. Send yourself a test email marked as important
4. Show watcher logs: `pm2 logs ai-employee-gmail` or `tail -f Logs/GmailWatcher.log`
5. Watch as new file appears in `Needs_Action/`
6. Open the created markdown file in Obsidian

**Key Points:**
- "The watcher runs continuously in the background"
- "It creates structured markdown files with frontmatter"
- "All activity is logged for debugging and audit"

#### Option B: Filesystem Watcher Demo

**Script:**
```
"I've set up a filesystem watcher that monitors a drop folder for new files."
```

**Actions:**
1. Show watcher code briefly
2. Show PM2 status: `pm2 status`
3. Show the drop folder: `ls -la ~/AI_Employee_Drop`
4. Drop a test file: `echo "Client invoice request" > ~/AI_Employee_Drop/client_request.txt`
5. Show watcher logs detecting the file
6. Show new file and metadata in `Needs_Action/`

**Key Points:**
- "Any file dropped here is immediately detected"
- "The watcher creates metadata and copies to the vault"
- "This enables drag-and-drop workflow integration"

### Part 4: Claude Code Integration (3-4 minutes)

**Script:**
```
"Now let's see Claude Code process this action and follow the workflow."
```

**Actions:**

1. **Show Current State:**
   ```bash
   ls Needs_Action/
   ls Plans/
   ls Pending_Approval/
   ```

2. **Process with Claude:**
   ```bash
   claude "Check Needs_Action folder. Process the pending item by creating a plan in Plans/ folder with specific steps"
   ```

3. **Show Plan Created:**
   - Open the plan file in Obsidian
   - Highlight the task breakdown

4. **Request Approval:**
   ```bash
   claude "Based on Company_Handbook.md, this action requires approval. Create an approval request in Pending_Approval/ folder"
   ```

5. **Show HITL Workflow:**
   - Open approval request in Obsidian
   - Explain why approval is needed
   - Manually move file: `mv Pending_Approval/APPROVAL_*.md Approved/`

6. **Complete Task:**
   ```bash
   claude "Check Approved folder. Execute approved actions and move completed task to Done/. Update Dashboard with completion"
   ```

7. **Show Final State:**
   - Show Dashboard update in Obsidian
   - Show file in Done/ folder
   - Show log entry (if created)

**Key Points:**
- "Claude reads the handbook to understand approval boundaries"
- "Human-in-the-loop prevents autonomous mistakes"
- "Files move through the workflow: Needs_Action → Plans → Pending_Approval → Approved → Done"
- "Dashboard provides real-time status"

### Part 5: Workflow Summary (1 minute)

**Script:**
```
"Let me show you the complete workflow in the updated Dashboard."
```

**Actions:**
1. Open Dashboard.md in Obsidian
2. Highlight the "Recent Activity" section
3. Show status updates
4. Show folder structure with files in Done/

**Script:**
```
"As you can see, the AI Employee successfully:
1. Detected the new email/file via the watcher
2. Created an action file in Needs_Action
3. Analyzed it and created a plan
4. Requested approval following the handbook rules
5. Waited for human approval
6. Completed the task and updated the dashboard

This is the Bronze tier foundation - a working autonomous system with proper safeguards."
```

### Part 6: Code & Architecture (1 minute)

**Script:**
```
"Let me quickly show the code architecture that makes this work."
```

**Actions:**
1. Show directory structure:
   ```bash
   tree -L 2 ~/AI_Employee_Code
   tree -L 1 ~/AI_Employee_Vault
   ```

2. Show base_watcher.py (briefly)
3. Show constitution file:
   ```bash
   head -50 .specify/memory/constitution.md
   ```

**Key Points:**
- "BaseWatcher pattern enables easy extension"
- "Constitution defines the core principles"
- "All functionality is implemented as Agent Skills"

### Part 7: Conclusion (30 seconds)

**Script:**
```
"That completes my Bronze tier demonstration.

Bronze Deliverables Completed:
✅ Obsidian vault with full structure
✅ One working watcher (Gmail/Filesystem)
✅ Claude Code integration tested
✅ Complete workflow demonstrated
✅ HITL safeguards working
✅ All functionality as Agent Skills

Next steps:
- Add more watchers (Silver tier)
- Implement MCP servers for actions (Silver)
- Add CEO briefings (Gold)

Thank you for watching!"
```

**Actions:**
- Show completion checklist
- Show next tier goals briefly

## Recording Setup

### Recommended Tools

**Screen Recording:**
- macOS: QuickTime Player (built-in) or OBS Studio
- Windows: OBS Studio or Xbox Game Bar
- Linux: SimpleScreenRecorder or OBS Studio

**Video Editing (Optional):**
- DaVinci Resolve (free)
- OpenShot (free)
- iMovie (macOS)

### Recording Settings

- **Resolution:** 1920x1080 (1080p)
- **Frame Rate:** 30 fps
- **Length:** 5-10 minutes
- **Format:** MP4 or MOV
- **Audio:** Clear microphone or voice-over

### Tips for Good Demo

1. **Clean Your Desktop:** Close unnecessary applications
2. **Increase Font Size:** Make terminal text readable (18-20pt)
3. **Practice First:** Do a dry run before recording
4. **Speak Clearly:** Explain what you're doing as you do it
5. **Show, Don't Tell:** Demonstrate actual functionality
6. **Highlight Key Features:** Use cursor or annotations
7. **Keep It Focused:** Don't go off on tangents
8. **Test Audio:** Ensure voice is clear and audible
9. **Add Captions (Optional):** Makes video more accessible
10. **Show Errors (If Any):** Briefly show how you debugged issues

## Pre-Recording Checklist

- [ ] Vault setup complete and clean
- [ ] Watcher running and tested
- [ ] Test files ready (email sent / file to drop)
- [ ] Claude Code tested and working
- [ ] Screen recording software tested
- [ ] Audio checked
- [ ] Desktop clean
- [ ] Terminal font size increased
- [ ] Obsidian vault open
- [ ] Demo script reviewed
- [ ] Timer ready (aim for 5-10 min)

## Post-Recording Checklist

- [ ] Video length: 5-10 minutes
- [ ] Audio clear and audible
- [ ] All key features demonstrated
- [ ] No sensitive information visible (API keys, emails)
- [ ] Video format: MP4 or MOV
- [ ] File size reasonable (<500MB)

## Video Upload

Upload your video to:
- YouTube (unlisted or public)
- Google Drive (public link)
- Vimeo
- Or hackathon submission platform

## Submission Package

Your Bronze tier submission should include:

1. **Demo Video Link** (required)
2. **GitHub Repository** with:
   - Vault structure (without sensitive data)
   - Watcher code (base_watcher.py + chosen watcher)
   - Constitution file
   - README with setup instructions
   - .gitignore (ensure .env excluded)
3. **Documentation:**
   - Setup instructions
   - Architecture overview
   - Security disclosure (how credentials handled)
   - Integration test report

## Example README for Submission

```markdown
# Personal AI Employee - Bronze Tier Submission

## Demo Video
[Your Video Link Here]

## Overview
A local-first AI employee using Obsidian vault, Python watchers, and Claude Code.

## Features Implemented (Bronze)
- ✅ Obsidian vault with complete structure
- ✅ Gmail/Filesystem watcher (choose one)
- ✅ Claude Code integration
- ✅ HITL approval workflow
- ✅ State machine (Needs_Action → Plans → Pending_Approval → Approved → Done)
- ✅ All functionality as Agent Skills

## Architecture
- **Brain:** Obsidian vault (local markdown)
- **Perception:** Python watcher (BaseWatcher pattern)
- **Reasoning:** Claude Code
- **Safeguards:** HITL for sensitive actions

## Setup Instructions
[Link to detailed setup guide]

## Security
- Credentials stored in .env (gitignored)
- API keys use environment variables
- No sensitive data in repository
- HITL prevents autonomous actions

## Next Steps
- Silver tier: Add WhatsApp watcher, MCP email server
- Gold tier: CEO briefings, Odoo integration
- Platinum tier: 24/7 cloud deployment

## License
MIT
```

## Submit

Submit via: https://forms.gle/JR9T1SJq5rmQyGkGA

## Next Steps After Submission

1. Proceed to Silver tier planning
2. Add second watcher
3. Implement MCP email server
4. Add HITL approval workflow automation

## References

- Hackathon Document Section "Submission Requirements"
- Constitution Version 1.0.0
- Bronze Tier Requirements (8-12 hours)
