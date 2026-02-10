# filesystem-monitor

Monitor filesystem drop folders for new files and process them into action items.

## What you do

You watch designated drop folders for new files, extract metadata, and create corresponding action files in the vault for Claude to process.

## When to use

- Continuously running as part of orchestrator
- When user drops files into `/Inbox` folder
- When new documents need processing
- For automated file ingestion workflow

## Prerequisites

- Python watchdog library installed
- Vault folder structure set up
- Drop folder (`/Inbox`) exists

## Instructions

### Step 1: Verify Drop Folder Exists

```bash
cd /mnt/d/Ai-Employee/AI_Employee_Vault
test -d Inbox && echo "✅ Inbox exists" || mkdir -p Inbox
```

### Step 2: Start Filesystem Watcher

```bash
cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers
python filesystem_watcher.py
```

This will:
1. Monitor `/Inbox` folder for new files
2. Detect file creation events immediately
3. Extract file metadata (name, size, type)
4. Create action file in `/Needs_Action`

### Step 3: File Processing Logic

When new file detected:

1. **Copy file** to `/Needs_Action/FILES/[filename]`
2. **Create metadata file** in `/Needs_Action/FILE_[timestamp]_[filename].md`
3. **Log event** to `/Logs/filesystem.log`

### Step 4: Action File Format

```markdown
---
type: file_drop
original_name: invoice_template.pdf
file_size: 245 KB
file_type: application/pdf
dropped_at: 2026-02-08T12:30:00Z
status: pending
---

## New File Detected

A new file has been dropped in the Inbox folder.

**File:** invoice_template.pdf
**Size:** 245 KB
**Type:** PDF Document

## Suggested Actions

Based on file name/type, suggested actions:
- [ ] Review file content
- [ ] Extract relevant information
- [ ] File appropriately
- [ ] Take required action

**File Location:** `/Needs_Action/FILES/invoice_template.pdf`
```

### Step 5: Smart Categorization

Detect file purpose based on name/extension:

**Invoices:**
- Keywords: invoice, bill, receipt
- Action: Process invoice, update accounting

**Client Files:**
- Keywords: contract, proposal, agreement
- Action: Review and file in client folder

**Reports:**
- Keywords: report, summary, analysis
- Action: Review and summarize

**Media:**
- Extensions: .jpg, .png, .mp4
- Action: Process for social media or documentation

## Output format

```
Filesystem Monitor Active
Watching: /Inbox

New file detected!
- File: client_contract.pdf
- Size: 1.2 MB
- Type: PDF
- Action file created: /Needs_Action/FILE_20260208_120000_client_contract.md

📁 File ready for processing
```

## Error handling

**Permission denied:**
```bash
chmod -R 755 /mnt/d/Ai-Employee/AI_Employee_Vault/Inbox
```

**Disk space low:**
- Check available space
- Archive old files
- Alert user if < 1GB free

**File in use:**
- Wait 2 seconds and retry
- If still locked, skip and alert

**Large files (>100MB):**
- Create action file but don't copy
- Reference original location
- Alert user for manual review

## Examples

**Example 1: Invoice dropped**
```
User drops: invoice_jan2026.pdf into /Inbox
→ Filesystem watcher detects immediately
→ Copies to /Needs_Action/FILES/
→ Creates: FILE_20260208_120000_invoice_jan2026.md
→ Claude processes: Recognizes as invoice
→ Creates plan to extract and record payment
```

**Example 2: Client document**
```
File dropped: client_proposal_v2.docx
→ Detected as proposal document
→ Action file created with high priority
→ Claude suggests: Review, compare with v1, respond to client
```

**Example 3: Screenshot**
```
File dropped: error_screenshot.png
→ Detected as image file
→ Action file created
→ Claude can analyze image content
→ Suggests debugging steps
```

## Integration points

- **Orchestrator**: Runs filesystem watcher continuously
- **Claude Processor**: Processes file action items
- **Dashboard**: Updates file processing stats
- **Logs**: Records all file events

## Supported file types

### Documents
- PDF (.pdf)
- Word (.docx, .doc)
- Excel (.xlsx, .xls)
- Text (.txt, .md)

### Images
- PNG, JPG, JPEG
- GIF, BMP
- SVG

### Code
- Python (.py)
- JavaScript (.js)
- JSON, YAML, XML

### Archives
- ZIP, RAR, 7z
- TAR, GZ

### Other
- CSV (data files)
- Email (.eml)
- Audio/Video (reference only)

## Security notes

⚠️ **Important:**
- Scan files for malware before processing
- Don't auto-execute unknown file types
- Validate file extensions match content
- Limit file size to prevent DOS
- Never auto-run scripts

## Performance

- Instant detection (<1 second)
- Low CPU usage (~1%)
- Efficient file watching (no polling)
- Handles multiple simultaneous drops

## Success criteria

✅ Filesystem watcher running
✅ Drop folder monitored
✅ New files detected instantly
✅ Action files created with metadata
✅ Files copied to Needs_Action
✅ Events logged properly

---

**Skill Type:** Watcher
**Tier:** Bronze (Enhanced in Silver)
**Automation:** Always running
**Performance:** Real-time file detection
