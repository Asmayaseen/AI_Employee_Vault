#!/bin/bash
# VcXsrv Troubleshooting Script

echo "========================================"
echo "VcXsrv Connection Troubleshooting"
echo "========================================"
echo ""

# Get Windows IP
WINDOWS_IP=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}')
echo "Windows IP: $WINDOWS_IP"
echo ""

# Test connection
echo "Testing connection to VcXsrv (port 6000)..."
if nc -zv $WINDOWS_IP 6000 2>&1 | grep -q "succeeded"; then
    echo "✅ VcXsrv is accessible!"
    echo ""
    echo "Testing X11 display..."
    export DISPLAY=$WINDOWS_IP:0
    timeout 2 xeyes 2>/dev/null && echo "✅ X11 working!" || echo "⚠️ X11 test completed"
else
    echo "❌ Cannot connect to VcXsrv"
    echo ""
    echo "TROUBLESHOOTING STEPS:"
    echo ""
    echo "1. Is XLaunch running on Windows?"
    echo "   - Check system tray (bottom-right) for 'X' icon"
    echo "   - If not visible: Start Menu → 'XLaunch'"
    echo ""
    echo "2. XLaunch Configuration:"
    echo "   - Multiple windows → Next"
    echo "   - Start no client → Next"
    echo "   - ✅ CHECK: 'Disable access control' (CRITICAL!)"
    echo "   - Finish"
    echo ""
    echo "3. Windows Firewall:"
    echo "   Run this in Windows PowerShell (as Administrator):"
    echo ""
    echo "   New-NetFirewallRule -DisplayName \"VcXsrv\" -Direction Inbound -Program \"C:\Program Files\VcXsrv\vcxsrv.exe\" -Action Allow"
    echo ""
    echo "4. After fixing, run this script again:"
    echo "   bash fix_vcxsrv.sh"
    echo ""
fi

echo ""
echo "DISPLAY variable: $DISPLAY"
echo ""
echo "========================================"
