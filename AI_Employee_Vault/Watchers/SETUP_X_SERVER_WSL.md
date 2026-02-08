# X Server Setup for WSL - LinkedIn Watcher

## Windows Side Setup (One-time)

### 1. Download and Install VcXsrv
- Download: https://sourceforge.net/projects/vcxsrv/
- Run installer (keep default settings)
- Install location: Usually `C:\Program Files\VcXsrv`

### 2. Launch XLaunch (Every time before using)
1. Start Menu → Search "XLaunch" → Run
2. **Display settings:** Select "Multiple windows" → Next
3. **Client startup:** Select "Start no client" → Next
4. **Extra settings:**
   - ✅ CHECK: "Disable access control" (IMPORTANT!)
   - ✅ CHECK: "Clipboard" (optional)
   - ❌ UNCHECK: "Native opengl" (can cause issues)
5. Click "Finish"

You should see VcXsrv icon in system tray (bottom right)

### 3. Windows Firewall (One-time)
When prompted by Windows Firewall:
- ✅ Allow VcXsrv on Private networks
- ✅ Allow VcXsrv on Public networks (if you use public WiFi)

---

## WSL Ubuntu Side Setup

### 1. Install X11 Apps (Testing tools)
```bash
sudo apt update
sudo apt install -y x11-apps
```

### 2. Set DISPLAY Environment Variable

**Method A: Automatic (Recommended)**
```bash
# Add to your .bashrc (permanent)
echo 'export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '"'"'{print $2}'"'"'):0' >> ~/.bashrc

# Reload .bashrc
source ~/.bashrc

# Verify
echo $DISPLAY
```

**Method B: Manual (Each session)**
```bash
# Find your Windows IP
cat /etc/resolv.conf | grep nameserver

# Set DISPLAY (replace with IP from above)
export DISPLAY=172.x.x.x:0
```

### 3. Test X Server Connection
```bash
# Test with xeyes (should open window on Windows)
xeyes
```

If you see eyes following your mouse cursor → **SUCCESS!** ✅
Press Ctrl+C to close.

If not working, see Troubleshooting section below.

---

## LinkedIn Watcher Commands

### Once X Server is working:

```bash
cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers

# Test configuration only (no browser)
python test_linkedin.py

# Full test with browser (will open on Windows)
python test_linkedin.py --full

# Run continuously
python linkedin_watcher.py ../
```

---

## Troubleshooting

### "Cannot open display"

**Check 1: Is VcXsrv running?**
```bash
# From WSL, try to connect
nc -zv $(cat /etc/resolv.conf | grep nameserver | awk '{print $2}') 6000
```
Should say: "Connection succeeded"

If failed:
- Make sure XLaunch is running (check system tray)
- Restart VcXsrv with "Disable access control" checked

**Check 2: DISPLAY variable set?**
```bash
echo $DISPLAY
```
Should show something like: `172.24.48.1:0`

If empty:
```bash
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0
```

**Check 3: Windows Firewall**
- Open "Windows Defender Firewall"
- Click "Allow an app through firewall"
- Find "VcXsrv windows server"
- Make sure both Private and Public are checked
- If not listed, click "Allow another app" and add it

**Check 4: Test with simple app**
```bash
xeyes  # Should open window
xclock # Should show clock
```

### "Connection refused" on port 6000

VcXsrv not running or firewall blocking.

Solution:
```bash
# Check if port 6000 is accessible
telnet $(cat /etc/resolv.conf | grep nameserver | awk '{print $2}') 6000
```

If fails:
1. Restart VcXsrv (close from system tray, run XLaunch again)
2. Make sure "Disable access control" is checked
3. Add firewall rule manually:
   ```powershell
   # Run in Windows PowerShell (as Administrator)
   New-NetFirewallRule -DisplayName "VcXsrv" -Direction Inbound -Program "C:\Program Files\VcXsrv\vcxsrv.exe" -Action Allow
   ```

### Browser opens but freezes

Try increasing shared memory:
```bash
sudo mount -o remount,size=2G /dev/shm
df -h /dev/shm  # Check new size
```

### "GPU process isn't usable"

Add to LinkedIn test command:
```bash
# Disable GPU acceleration
python test_linkedin.py --full --disable-gpu
```

Or modify `linkedin_watcher.py` line 97:
```python
args=[
    '--disable-blink-features=AutomationControlled',
    '--no-sandbox',
    '--disable-gpu',  # Add this line
    '--disable-software-rasterizer'
],
```

---

## Quick Reference Commands

```bash
# Start VcXsrv on Windows first, then:

# Set DISPLAY
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0

# Test X11
xeyes

# Test LinkedIn watcher
cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers
python test_linkedin.py --full

# Run LinkedIn watcher
python linkedin_watcher.py ../

# Stop watcher
Ctrl+C
```

---

## Permanent Setup Checklist

- [ ] VcXsrv installed on Windows
- [ ] Windows Firewall allows VcXsrv
- [ ] DISPLAY variable added to ~/.bashrc
- [ ] xeyes test successful
- [ ] LinkedIn watcher browser opens

Once all checked, you're ready! 🎉

---

## Alternative: WSLg (Windows 11 only)

If you have Windows 11 with WSLg:
```bash
# Check if WSLg available
wslg --version

# If available, just run (no X Server needed!)
python test_linkedin.py --full
```

WSLg has built-in GUI support, no VcXsrv needed!

---

## Daily Usage

**Before starting work:**
1. Start VcXsrv (XLaunch) on Windows
2. Open WSL terminal
3. DISPLAY automatically set (if added to .bashrc)
4. Run LinkedIn watcher

**To run in background:**
```bash
cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers
nohup python linkedin_watcher.py ../ > linkedin_watcher.log 2>&1 &

# Check if running
ps aux | grep linkedin_watcher

# View logs
tail -f linkedin_watcher.log

# Stop
pkill -f linkedin_watcher.py
```
