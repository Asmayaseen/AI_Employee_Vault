#!/bin/bash
# Quick Start Script for AI Employee Silver Tier
# This script helps you get started quickly

set -e  # Exit on error

echo "======================================"
echo "  AI Employee - Silver Tier Setup"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VAULT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${YELLOW}Vault Directory:${NC} $VAULT_DIR"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Step 1: Check Prerequisites
echo "📋 Step 1: Checking Prerequisites..."
echo ""

MISSING_DEPS=0

if command_exists python3; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}✓${NC} Python 3 installed: $PYTHON_VERSION"
else
    echo -e "${RED}✗${NC} Python 3 not found"
    MISSING_DEPS=1
fi

if command_exists pip; then
    echo -e "${GREEN}✓${NC} pip installed"
else
    echo -e "${RED}✗${NC} pip not found"
    MISSING_DEPS=1
fi

if command_exists node; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓${NC} Node.js installed: $NODE_VERSION"
else
    echo -e "${YELLOW}⚠${NC} Node.js not installed (optional, needed for PM2)"
fi

if [ $MISSING_DEPS -eq 1 ]; then
    echo ""
    echo -e "${RED}Missing required dependencies. Please install them first.${NC}"
    exit 1
fi

echo ""

# Step 2: Check .env file
echo "🔧 Step 2: Checking Configuration..."
echo ""

if [ -f "$VAULT_DIR/.env" ]; then
    echo -e "${GREEN}✓${NC} .env file exists"

    # Check if DRY_RUN is set
    if grep -q "DRY_RUN=true" "$VAULT_DIR/.env"; then
        echo -e "${YELLOW}⚠${NC} DRY_RUN=true (testing mode - no real actions)"
    else
        echo -e "${GREEN}✓${NC} DRY_RUN=false (production mode)"
    fi
else
    echo -e "${RED}✗${NC} .env file not found"
    echo "Creating from .env.example..."
    cp "$VAULT_DIR/.env.example" "$VAULT_DIR/.env"
    echo -e "${YELLOW}⚠${NC} Please edit .env and add your credentials"
    exit 1
fi

echo ""

# Step 3: Install Python Dependencies
echo "📦 Step 3: Checking Python Dependencies..."
echo ""

if pip list | grep -q "google-api-python-client"; then
    echo -e "${GREEN}✓${NC} Google API client installed"
else
    echo -e "${YELLOW}⚠${NC} Installing Python dependencies..."
    pip install -r "$SCRIPT_DIR/requirements.txt"
fi

if command_exists playwright; then
    echo -e "${GREEN}✓${NC} Playwright installed"

    # Check if chromium is installed
    if [ -d "$HOME/.cache/ms-playwright/chromium"* ]; then
        echo -e "${GREEN}✓${NC} Chromium browser installed"
    else
        echo -e "${YELLOW}⚠${NC} Installing Playwright browsers..."
        playwright install chromium
    fi
else
    echo -e "${YELLOW}⚠${NC} Installing Playwright..."
    pip install playwright
    playwright install chromium
fi

echo ""

# Step 4: Check Gmail Credentials
echo "📧 Step 4: Checking Gmail Setup..."
echo ""

if [ -f "$SCRIPT_DIR/credentials/credentials.json" ]; then
    echo -e "${GREEN}✓${NC} Gmail credentials.json found"

    if [ -f "$SCRIPT_DIR/token.json" ]; then
        echo -e "${GREEN}✓${NC} Gmail token.json exists (already authenticated)"
    else
        echo -e "${YELLOW}⚠${NC} Gmail token not found - first run will require authentication"
    fi
else
    echo -e "${RED}✗${NC} Gmail credentials.json not found"
    echo ""
    echo "To enable Gmail watcher:"
    echo "1. Go to: https://console.cloud.google.com/"
    echo "2. Create a project and enable Gmail API"
    echo "3. Create OAuth credentials (Desktop app)"
    echo "4. Download credentials.json"
    echo "5. Move to: $SCRIPT_DIR/credentials/"
    echo ""
fi

echo ""

# Step 5: Check Folder Structure
echo "📁 Step 5: Checking Folder Structure..."
echo ""

FOLDERS=("Needs_Action" "Plans" "Pending_Approval" "Approved" "Rejected" "Done" "Logs" "Briefings" "Inbox")

for folder in "${FOLDERS[@]}"; do
    if [ -d "$VAULT_DIR/$folder" ]; then
        echo -e "${GREEN}✓${NC} $folder/"
    else
        echo -e "${YELLOW}⚠${NC} Creating $folder/"
        mkdir -p "$VAULT_DIR/$folder"
    fi
done

echo ""

# Step 6: Offer to start watchers
echo "======================================"
echo "  Setup Complete!"
echo "======================================"
echo ""

echo "What would you like to do?"
echo ""
echo "1) Test individual watchers (recommended first time)"
echo "2) Start all watchers with Orchestrator"
echo "3) Install PM2 and run as daemon"
echo "4) Generate cron schedule"
echo "5) Exit"
echo ""

read -p "Choose option (1-5): " option

case $option in
    1)
        echo ""
        echo "Testing Individual Watchers..."
        echo ""
        echo "1. FileSystem Watcher:"
        echo "   cd $SCRIPT_DIR"
        echo "   python filesystem_watcher.py $VAULT_DIR"
        echo ""
        echo "2. Gmail Watcher (will open browser for auth):"
        echo "   python gmail_watcher.py $VAULT_DIR $SCRIPT_DIR/credentials/credentials.json"
        echo ""
        echo "3. WhatsApp Watcher (will show QR code):"
        echo "   python whatsapp_watcher.py $VAULT_DIR"
        echo ""
        echo "4. LinkedIn Watcher (will prompt login):"
        echo "   python linkedin_watcher.py $VAULT_DIR"
        echo ""
        ;;
    2)
        echo ""
        echo "Starting Orchestrator (manages all watchers)..."
        cd "$SCRIPT_DIR"
        python orchestrator.py
        ;;
    3)
        if command_exists pm2; then
            echo ""
            echo "Starting with PM2..."
            cd "$SCRIPT_DIR"
            pm2 start orchestrator.py --name "ai-employee" --interpreter python3
            pm2 save
            echo ""
            echo "PM2 Commands:"
            echo "  pm2 status          - View status"
            echo "  pm2 logs            - View logs"
            echo "  pm2 restart all     - Restart"
            echo "  pm2 stop all        - Stop"
        else
            echo ""
            echo "PM2 not installed. Install with:"
            echo "  npm install -g pm2"
        fi
        ;;
    4)
        echo ""
        echo "Generating cron schedule..."
        cd "$SCRIPT_DIR"
        python scheduler.py --generate-cron
        echo ""
        echo "To add to your crontab, run:"
        echo "  crontab -e"
        echo "Then paste the lines above."
        ;;
    5)
        echo "Exiting."
        exit 0
        ;;
    *)
        echo "Invalid option"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}Done!${NC}"
