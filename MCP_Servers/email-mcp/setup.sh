#!/bin/bash

###############################################################################
# Email MCP Server Setup Script
#
# This script sets up the Email MCP Server for AI Employee
###############################################################################

set -e

echo "======================================"
echo "Email MCP Server Setup"
echo "======================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Paths
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VAULT_PATH="/mnt/d/Ai-Employee/AI_Employee_Vault"
WATCHERS_PATH="$VAULT_PATH/Watchers"
CREDENTIALS_PATH="$WATCHERS_PATH/credentials.json"
TOKEN_PATH="$SCRIPT_DIR/token.json"
MCP_CONFIG="$HOME/.config/claude-code/mcp.json"

# Step 1: Check Node.js
echo "Step 1: Checking Node.js installation..."
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found. Please install Node.js v20+${NC}"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 20 ]; then
    echo -e "${RED}❌ Node.js version too old. Please install v20+${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Node.js $(node -v) installed${NC}"
echo ""

# Step 2: Install npm dependencies
echo "Step 2: Installing npm dependencies..."
npm install
echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Step 3: Check Gmail credentials
echo "Step 3: Checking Gmail API credentials..."
if [ ! -f "$CREDENTIALS_PATH" ]; then
    echo -e "${YELLOW}⚠️  Gmail credentials not found at: $CREDENTIALS_PATH${NC}"
    echo ""
    echo "To set up Gmail API credentials:"
    echo "1. Go to https://console.cloud.google.com/"
    echo "2. Create a new project (or use existing)"
    echo "3. Enable Gmail API"
    echo "4. Create OAuth 2.0 credentials"
    echo "5. Download as credentials.json"
    echo "6. Place in: $CREDENTIALS_PATH"
    echo ""
    echo -e "${YELLOW}Skipping authentication step...${NC}"
else
    echo -e "${GREEN}✅ Credentials found${NC}"

    # Step 4: Check token
    echo ""
    echo "Step 4: Checking authentication token..."
    if [ ! -f "$TOKEN_PATH" ]; then
        echo -e "${YELLOW}⚠️  Authentication token not found${NC}"
        echo "Running Gmail authentication..."
        echo ""

        # Check if authenticate_gmail.py exists
        if [ -f "$WATCHERS_PATH/authenticate_gmail.py" ]; then
            cd "$WATCHERS_PATH"
            python3 authenticate_gmail.py

            # Copy token to MCP server directory
            if [ -f "$WATCHERS_PATH/token.json" ]; then
                cp "$WATCHERS_PATH/token.json" "$TOKEN_PATH"
                echo -e "${GREEN}✅ Authentication complete${NC}"
            else
                echo -e "${RED}❌ Authentication failed${NC}"
                exit 1
            fi
        else
            echo -e "${RED}❌ authenticate_gmail.py not found${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}✅ Token found${NC}"
    fi
fi

echo ""

# Step 5: Configure Claude Code MCP
echo "Step 5: Configuring Claude Code MCP..."
mkdir -p "$(dirname "$MCP_CONFIG")"

if [ -f "$MCP_CONFIG" ]; then
    echo -e "${YELLOW}⚠️  MCP config already exists: $MCP_CONFIG${NC}"
    echo "Backing up to mcp.json.backup..."
    cp "$MCP_CONFIG" "$MCP_CONFIG.backup"
fi

cat > "$MCP_CONFIG" << EOF
{
  "mcpServers": {
    "email": {
      "command": "node",
      "args": ["$SCRIPT_DIR/index.js"],
      "env": {
        "GMAIL_CREDENTIALS_PATH": "$CREDENTIALS_PATH",
        "VAULT_PATH": "$VAULT_PATH",
        "DRY_RUN": "false"
      }
    }
  }
}
EOF

echo -e "${GREEN}✅ Claude Code MCP configured${NC}"
echo ""

# Step 6: Test server
echo "Step 6: Testing Email MCP Server..."
echo "Running in DRY_RUN mode..."
echo ""

DRY_RUN=true timeout 5s npm test || true

echo ""
echo -e "${GREEN}======================================"
echo "✅ Email MCP Server Setup Complete!"
echo "======================================${NC}"
echo ""
echo "Next steps:"
echo "1. Restart Claude Code to load MCP server"
echo "2. Test with: npm test"
echo "3. Use in Claude Code with email tools"
echo ""
echo "Configuration file: $MCP_CONFIG"
echo "Logs: $VAULT_PATH/Logs/email-mcp.log"
echo ""
echo "To test manually:"
echo "  cd $SCRIPT_DIR"
echo "  npm test"
echo ""
