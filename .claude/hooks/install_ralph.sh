#!/bin/bash
# Ralph Wiggum Hook Installation Script
#
# This script sets up the Ralph Wiggum autonomous loop for Claude Code.
#
# Usage:
#   ./install_ralph.sh         # Install and verify
#   ./install_ralph.sh test    # Run tests
#   ./install_ralph.sh status  # Check status

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT_PATH="${VAULT_PATH:-/mnt/d/Ai-Employee/AI_Employee_Vault}"
HOOKS_DIR="$SCRIPT_DIR"

echo "================================================"
echo "   Ralph Wiggum Hook Installation"
echo "================================================"
echo ""
echo "Hooks directory: $HOOKS_DIR"
echo "Vault path: $VAULT_PATH"
echo ""

# Function to check Python
check_python() {
    echo "Checking Python..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        echo "✅ Python found: $PYTHON_VERSION"
        return 0
    else
        echo "❌ Python 3 not found"
        return 1
    fi
}

# Function to verify hook files
verify_hooks() {
    echo ""
    echo "Verifying hook files..."

    local files=("stop.py" "ralph_controller.py" "ralph_integration.py")
    local missing=0

    for file in "${files[@]}"; do
        if [ -f "$HOOKS_DIR/$file" ]; then
            echo "✅ $file exists"
        else
            echo "❌ $file missing"
            missing=$((missing + 1))
        fi
    done

    if [ $missing -eq 0 ]; then
        echo ""
        echo "All hook files present!"
        return 0
    else
        echo ""
        echo "Missing $missing file(s)"
        return 1
    fi
}

# Function to make scripts executable
make_executable() {
    echo ""
    echo "Making scripts executable..."
    chmod +x "$HOOKS_DIR"/*.py 2>/dev/null || true
    chmod +x "$HOOKS_DIR"/*.sh 2>/dev/null || true
    echo "✅ Scripts are executable"
}

# Function to verify vault structure
verify_vault() {
    echo ""
    echo "Verifying vault structure..."

    local folders=("Needs_Action" "Pending_Approval" "Done" "Plans" "Logs")
    local missing=0

    for folder in "${folders[@]}"; do
        if [ -d "$VAULT_PATH/$folder" ]; then
            echo "✅ $folder/ exists"
        else
            echo "⚠️  $folder/ creating..."
            mkdir -p "$VAULT_PATH/$folder"
            echo "✅ $folder/ created"
        fi
    done

    echo ""
    echo "Vault structure ready!"
}

# Function to test hooks
test_hooks() {
    echo ""
    echo "Testing Ralph hooks..."
    echo ""

    # Test 1: Import test
    echo "Test 1: Import test"
    cd "$HOOKS_DIR"
    python3 -c "from stop import RalphWiggumHook; print('✅ stop.py imports OK')" || echo "❌ Import failed"
    python3 -c "from ralph_controller import RalphController; print('✅ ralph_controller.py imports OK')" || echo "❌ Import failed"
    python3 -c "from ralph_integration import RalphIntegration; print('✅ ralph_integration.py imports OK')" || echo "❌ Import failed"

    # Test 2: Status check
    echo ""
    echo "Test 2: Status check"
    python3 ralph_controller.py status

    # Test 3: Integration status
    echo ""
    echo "Test 3: Integration status"
    python3 ralph_integration.py status

    echo ""
    echo "Tests completed!"
}

# Function to show status
show_status() {
    echo ""
    echo "Ralph Wiggum Status"
    echo "==================="

    cd "$HOOKS_DIR"
    python3 ralph_controller.py status

    echo ""
    echo "Pending Counts:"
    python3 -c "
from ralph_integration import RalphIntegration
integration = RalphIntegration()
counts = integration.get_pending_count()
for name, count in counts.items():
    icon = '📝' if count > 0 else '✅'
    print(f'  {icon} {name}: {count}')
"
}

# Main installation function
install() {
    check_python || exit 1
    verify_hooks || exit 1
    make_executable
    verify_vault

    echo ""
    echo "================================================"
    echo "   Installation Complete!"
    echo "================================================"
    echo ""
    echo "Next steps:"
    echo "1. Add to your crontab for automatic processing:"
    echo "   */5 * * * * cd $HOOKS_DIR && python3 ralph_integration.py auto"
    echo ""
    echo "2. Start a Ralph loop manually:"
    echo "   python3 $HOOKS_DIR/ralph_controller.py start \"Your task description\""
    echo ""
    echo "3. Check status:"
    echo "   python3 $HOOKS_DIR/ralph_controller.py status"
    echo ""
    echo "4. Emergency stop:"
    echo "   python3 $HOOKS_DIR/ralph_controller.py reset"
    echo ""
}

# Command line argument handling
case "${1:-install}" in
    install)
        install
        ;;
    test)
        test_hooks
        ;;
    status)
        show_status
        ;;
    *)
        echo "Usage: $0 {install|test|status}"
        exit 1
        ;;
esac
