#!/bin/bash
# WSL LinkedIn Watcher Setup Script
# Run: bash setup_wsl_linkedin.sh

set -e

echo "========================================"
echo "WSL LinkedIn Watcher Setup"
echo "========================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Check if x11-apps installed
echo "Step 1: Installing X11 tools..."
if ! command -v xeyes &> /dev/null; then
    echo "Installing x11-apps..."
    sudo apt update
    sudo apt install -y x11-apps
    echo -e "${GREEN}✅ X11 tools installed${NC}"
else
    echo -e "${GREEN}✅ X11 tools already installed${NC}"
fi
echo ""

# Step 2: Setup DISPLAY variable
echo "Step 2: Setting up DISPLAY variable..."
if ! grep -q "export DISPLAY=\$(cat /etc/resolv.conf" ~/.bashrc; then
    echo 'export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '"'"'{print $2}'"'"'):0' >> ~/.bashrc
    echo -e "${GREEN}✅ DISPLAY variable added to .bashrc${NC}"
else
    echo -e "${GREEN}✅ DISPLAY variable already in .bashrc${NC}"
fi

# Load the variable
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0
echo "DISPLAY set to: $DISPLAY"
echo ""

# Step 3: Check VcXsrv
echo "Step 3: Checking VcXsrv connection..."
WINDOWS_IP=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}')

if nc -zv $WINDOWS_IP 6000 2>&1 | grep -q "succeeded"; then
    echo -e "${GREEN}✅ VcXsrv is running and accessible${NC}"
else
    echo -e "${RED}❌ Cannot connect to VcXsrv${NC}"
    echo ""
    echo "Please:"
    echo "1. Download VcXsrv from: https://sourceforge.net/projects/vcxsrv/"
    echo "2. Install it on Windows"
    echo "3. Run 'XLaunch' from Start Menu"
    echo "4. Choose: Multiple windows → Start no client"
    echo "5. ✅ CHECK: 'Disable access control'"
    echo "6. Click Finish"
    echo ""
    echo "Then run this script again."
    exit 1
fi
echo ""

# Step 4: Test X11
echo "Step 4: Testing X11 display..."
echo "Opening xeyes for 3 seconds (should open window on Windows)..."
timeout 3 xeyes &
XEYES_PID=$!
sleep 3
kill $XEYES_PID 2>/dev/null || true

echo -e "${YELLOW}Did you see eyes window on Windows? (y/n)${NC}"
read -p "> " saw_window

if [[ "$saw_window" =~ ^[Yy]$ ]]; then
    echo -e "${GREEN}✅ X11 display working!${NC}"
else
    echo -e "${RED}❌ X11 display not working${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "- Make sure VcXsrv is running (check system tray)"
    echo "- Restart VcXsrv with 'Disable access control' checked"
    echo "- Check Windows Firewall allows VcXsrv"
    echo ""
    exit 1
fi
echo ""

# Step 5: Test LinkedIn Watcher
echo "Step 5: Testing LinkedIn Watcher..."
cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers

if python test_linkedin.py; then
    echo -e "${GREEN}✅ LinkedIn Watcher configuration OK${NC}"
else
    echo -e "${RED}❌ LinkedIn Watcher test failed${NC}"
    exit 1
fi
echo ""

# Done
echo "========================================"
echo -e "${GREEN}Setup Complete! ✅${NC}"
echo "========================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Test with browser (will open on Windows):"
echo "   python test_linkedin.py --full"
echo ""
echo "2. Login to LinkedIn in browser (first time only)"
echo ""
echo "3. Run watcher continuously:"
echo "   python linkedin_watcher.py ../"
echo ""
echo "4. Stop with Ctrl+C"
echo ""
echo "Documentation: SETUP_X_SERVER_WSL.md"
echo ""
