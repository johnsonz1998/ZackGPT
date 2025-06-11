#!/bin/bash

# ZackGPT Web Server Launcher
# Starts the FastAPI web server on port 8000

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
    echo "║      🌐 ZackGPT Web Server        ║"
    echo "║     FastAPI Backend Service       ║"
    echo "╚═══════════════════════════════════╝"
    echo -e "${NC}"
}

function setup_environment() {
    echo -e "${BLUE}[1/4] Setting up environment...${NC}"
    
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
    echo -e "${BLUE}[2/4] Checking configuration...${NC}"
    
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

function check_port() {
    echo -e "${BLUE}[3/4] Checking port availability...${NC}"
    
    # Check if port 8000 is already in use
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Port 8000 is already in use${NC}"
        echo -e "${YELLOW}Would you like to kill the existing process? (y/N)${NC}"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            echo -e "${BLUE}Killing process on port 8000...${NC}"
            lsof -ti:8000 | xargs kill -9 2>/dev/null || true
            sleep 2
        else
            echo -e "${RED}❌ Cannot start server while port 8000 is in use${NC}"
            exit 1
        fi
    fi
    
    echo -e "${GREEN}✅ Port 8000 is available${NC}"
}

function start_server() {
    echo -e "${BLUE}[4/4] Starting ZackGPT Web Server...${NC}"
    echo ""
    echo -e "${GREEN}🚀 Server will be available at:${NC}"
    echo -e "${CYAN}   • API Server: http://localhost:8000${NC}"
    echo -e "${CYAN}   • API Docs:   http://localhost:8000/docs${NC}"
    echo -e "${CYAN}   • OpenAPI:    http://localhost:8000/openapi.json${NC}"
    echo ""
    echo -e "${YELLOW}💡 Press Ctrl+C to stop the server${NC}"
    echo ""
    
    # Run the server
    python -m server.main
}

function cleanup() {
    echo -e "\n${YELLOW}Shutting down server...${NC}"
    # Kill any remaining processes on port 8000
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    
    # Deactivate virtual environment if active
    if [ -n "$VIRTUAL_ENV" ]; then
        deactivate
    fi
    echo -e "${GREEN}Server stopped!${NC}"
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
check_port
start_server 