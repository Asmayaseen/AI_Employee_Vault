# VcXsrv Installation Guide (Windows)

## Download Link

**Direct Download:**
https://sourceforge.net/projects/vcxsrv/files/vcxsrv/1.20.14.0/vcxsrv-64.1.20.14.0.installer.exe/download

**Or Visit:**
https://sourceforge.net/projects/vcxsrv/

---

## Installation Steps

1. **Download the installer** (vcxsrv-64.1.20.14.0.installer.exe)
2. **Run the installer**
3. Click "Next" → "Next" → "Install" → "Finish"
4. Installation complete!

---

## Running XLaunch (IMPORTANT)

### Every time before using WSL LinkedIn watcher:

1. **Open Start Menu**
2. **Search "XLaunch"** and click it
3. **Configuration Wizard:**

   **Page 1 - Display Settings:**
   - Select: ⚪ **Multiple windows**
   - Display number: `-1`
   - Click **Next**

   **Page 2 - Client Startup:**
   - Select: ⚪ **Start no client**
   - Click **Next**

   **Page 3 - Extra Settings (CRITICAL!):**
   - ✅ **Clipboard** (optional)
   - ✅ **Primary Selection** (optional)
   - ❌ **Native opengl** (UNCHECK - can cause issues)
   - ✅ **Disable access control** ⚠️ **MUST CHECK THIS!**
   - Click **Next**

   **Page 4 - Save Configuration (Optional):**
   - Click "Save configuration" if you want
   - Save as: `config.xlaunch` on Desktop
   - Next time just double-click this file instead of going through wizard
   - Click **Finish**

4. **Check System Tray:**
   - You should see a black "X" icon in system tray (bottom-right)
   - This means VcXsrv is running ✅

---

## Windows Firewall Prompt

When you first run VcXsrv, Windows Firewall will ask:

**Allow VcXsrv access:**
- ✅ Private networks
- ✅ Public networks (if you use public WiFi)
- Click "Allow access"

---

## Test from WSL

After VcXsrv is running, test from WSL Ubuntu:

```bash
# 1. Set DISPLAY (already done by setup script)
echo $DISPLAY

# 2. Test connection
nc -zv $(cat /etc/resolv.conf | grep nameserver | awk '{print $2}') 6000

# Should say: "Connection to 10.255.255.254 6000 port [tcp/*] succeeded!"

# 3. Test with xeyes (should open window on Windows)
xeyes

# 4. If xeyes window appears on Windows → SUCCESS! ✅
# Press Ctrl+C to close xeyes
```

---

## Common Issues

### "Connection refused" on port 6000

**Problem:** VcXsrv not running or firewall blocking

**Solution:**
1. Check system tray for VcXsrv icon
2. If not there, run XLaunch again
3. Make sure "Disable access control" is checked
4. Check Windows Firewall settings

### Windows Firewall Blocking

**Fix manually:**

1. Open "Windows Defender Firewall with Advanced Security"
2. Click "Inbound Rules"
3. Click "New Rule..."
4. Program → Browse → `C:\Program Files\VcXsrv\vcxsrv.exe`
5. Allow the connection
6. Check all profiles (Domain, Private, Public)
7. Name: "VcXsrv X Server"
8. Finish

### VcXsrv Crashes

**Solution:**
- Uncheck "Native opengl" in XLaunch settings
- Increase Windows shared memory
- Restart VcXsrv

---

## Quick Start - Desktop Shortcut

**Save Time:** Create `config.xlaunch` file on Desktop:

1. Run XLaunch once with settings above
2. On last page, click "Save configuration"
3. Save to Desktop as `LinkedIn-XServer.xlaunch`
4. **Double-click this file** every time instead of going through wizard!

---

## Auto-Start on Windows Boot (Optional)

To start VcXsrv automatically when Windows starts:

1. Save configuration file: `C:\VcXsrv\config.xlaunch`
2. Press `Win + R`
3. Type: `shell:startup`
4. Copy `config.xlaunch` to this folder
5. VcXsrv will start automatically on boot! 🎉

---

## Verify Installation

From WSL Ubuntu:

```bash
cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers
bash setup_wsl_linkedin.sh
```

Should now show:
```
✅ VcXsrv is running and accessible
✅ X11 display working!
```

Then test LinkedIn:
```bash
python test_linkedin.py --full
```

Browser window should open on Windows! 🎉

---

## Summary Checklist

- [ ] VcXsrv downloaded and installed
- [ ] XLaunch run with "Disable access control" checked
- [ ] VcXsrv icon visible in system tray
- [ ] Windows Firewall allowed VcXsrv
- [ ] `nc -zv` test from WSL succeeds
- [ ] `xeyes` opens window on Windows
- [ ] LinkedIn watcher browser test works

Once all checked → LinkedIn watcher ready! ✅
