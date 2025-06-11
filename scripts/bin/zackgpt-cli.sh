#!/bin/bash

# ZackGPT CLI Launcher
# Pure command-line interface - no web services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

function print_banner() {
    echo -e "${CYAN}"
    echo "╔═══════════════════════════════════╗"
    echo "║      🤖 ZackGPT CLI Launcher      ║"
    echo "║     Pure Command Line Interface   ║"
    echo "╚═══════════════════════════════════╝"
    echo -e "${NC}"
}

function setup_environment() {
    echo -e "${BLUE}[1/3] Setting up environment...${NC}"
    
    # Check if we're in the right directory
    if [ ! -f "requirements.txt" ]; then
        echo -e "${RED}❌ Error: Please run this script from the ZackGPT root directory${NC}"
        exit 1
    fi
    
    # Create virtual environment if it doesn't exist
    if [ ! -d ".venv" ]; then
        echo -e "${YELLOW}Creating virtual environment...${NC}"
        python3 -m venv .venv
    fi
    
    # Activate virtual environment
    echo -e "${BLUE}Activating virtual environment...${NC}"
    source .venv/bin/activate
    
    # Install/update dependencies
    echo -e "${BLUE}Installing dependencies...${NC}"
    pip install --upgrade pip setuptools wheel > /dev/null 2>&1
    pip install -r requirements.txt > /dev/null 2>&1
    
    echo -e "${GREEN}✅ Environment ready${NC}"
}

function check_env_file() {
    echo -e "${BLUE}[2/3] Checking configuration...${NC}"
    
    if [ ! -f ".env" ]; then
        echo -e "${RED}❌ No .env file found${NC}"
        echo -e "${YELLOW}Please create a .env file with your API keys:${NC}"
        echo -e "${YELLOW}Example: echo 'OPENAI_API_KEY=your_key_here' > .env${NC}"
        exit 1
    fi
    
    # Check for OpenAI API key
    if ! grep -q "OPENAI_API_KEY" .env; then
        echo -e "${RED}❌ OPENAI_API_KEY not found in .env file${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Configuration valid${NC}"
}

function start_cli() {
    echo -e "${BLUE}[3/3] Starting ZackGPT CLI...${NC}"
    echo ""
    
    # Run the CLI main script with any passed arguments
    python -m cli.main "$@"
}

function cleanup() {
    echo -e "\n${YELLOW}Cleaning up...${NC}"
    # Deactivate virtual environment if active
    if [ -n "$VIRTUAL_ENV" ]; then
        deactivate
    fi
    echo -e "${GREEN}Goodbye!${NC}"
}

# Set up cleanup trap
trap cleanup INT TERM EXIT

# Main execution
print_banner

# Check Python availability
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is required but not installed${NC}"
    exit 1
fi

setup_environment
check_env_file
start_cli "$@" 