#!/bin/bash
# TOTG Installation Script
# ========================

set -e  # Exit on error

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                                                                      ║"
echo "║                    TOTG Installation Script                          ║"
echo "║                                                                      ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version || {
    echo "ERROR: Python 3 not found. Please install Python 3.8 or higher."
    exit 1
}

# Install dependencies
echo ""
echo "Installing dependencies..."
pip3 install -r requirements.txt || {
    echo "ERROR: Failed to install dependencies"
    exit 1
}

# Run tests
echo ""
echo "Running tests to verify installation..."
echo ""

python3 totg_tests_comprehensive.py || {
    echo "ERROR: Comprehensive tests failed"
    exit 1
}

echo ""
python3 totg_tests_additional.py || {
    echo "ERROR: Additional tests failed"
    exit 1
}

# Success
echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                                                                      ║"
echo "║                    ✅ INSTALLATION SUCCESSFUL!                      ║"
echo "║                                                                      ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "  1. Try examples:     python3 quick_start.py"
echo "  2. Read docs:        cat README.md"
echo "  3. Start coding:     python3"
echo "                       >>> from totg_api import TOTGAPI"
echo "                       >>> api = TOTGAPI()"
echo ""
echo "For MCP Server:"
echo "  1. Configure:        See MCP_SETUP.md"
echo "  2. Run:              python3 totg_mcp_server.py"
echo ""
echo "Good luck! 🚀"
