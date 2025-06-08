#!/bin/bash

trap ctrl_c INT

function ctrl_c() {
  echo -e "\n\033[1;31m[!] Interrupted. Cleaning up...\033[0m"
  type deactivate &>/dev/null && deactivate
  exit 1
}

function print_banner() {
  echo -e "\033[1;36m"
  echo "╔═══════════════════════════════════╗"
  echo "║      🌐 ZackGPT Web Server 🌐      ║"
  echo "║     Advanced AI with Web UI       ║"
  echo "╚═══════════════════════════════════╝"
  echo -e "\033[0m"
}

function setup_environment() {
  echo -e "\033[1;32m[+] Setting up environment...\033[0m"
  
  # Create virtual environment if it doesn't exist
  if [ ! -d ".venv" ]; then
    echo -e "\033[1;33m[!] Creating virtual environment...\033[0m"
    python3 -m venv .venv
  fi
  
  # Activate virtual environment
  source .venv/bin/activate
  
  # Upgrade pip and install dependencies
  echo -e "\033[1;33m[!] Installing/updating dependencies...\033[0m"
  pip install --upgrade pip setuptools wheel > /dev/null
  pip install -r requirements.txt
  
  # Check for .env file
  if [ ! -f .env ]; then
    echo -e "\033[1;31m[!] No .env file found!\033[0m"
    echo -e "\033[1;33m[!] Please create a .env file with your OPENAI_API_KEY\033[0m"
    echo -e "\033[1;33m[!] Example: echo 'OPENAI_API_KEY=your_key_here' > .env\033[0m"
    exit 1
  fi
  
  # Load environment variables
  export OPENAI_API_KEY=$(grep OPENAI_API_KEY .env | cut -d '=' -f2-)
  
  if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "\033[1;31m[!] OPENAI_API_KEY not found in .env file!\033[0m"
    exit 1
  fi
  
  echo -e "\033[1;32m[+] Environment ready!\033[0m"
}

function start_web_server() {
  echo -e "\033[1;36m[+] Starting ZackGPT Web API Server...\033[0m"
  echo ""
  echo -e "\033[1;33m📡 Server will be available at:\033[0m"
  echo -e "\033[1;37m   • Frontend: http://localhost:4200\033[0m"
  echo -e "\033[1;37m   • API: http://localhost:8000\033[0m"
  echo -e "\033[1;37m   • API Docs: http://localhost:8000/docs\033[0m"
  echo ""
  echo -e "\033[1;32m🚀 Starting backend server...\033[0m"
  echo ""
  
  python -m scripts.startup.main_web
}

function main() {
  print_banner
  
  # Check if Python is available
  if ! command -v python3 &> /dev/null; then
    echo -e "\033[1;31m[!] Python 3 is required but not installed.\033[0m"
    exit 1
  fi
  
  setup_environment
  start_web_server
}

# Check for help flag
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
  print_banner
  echo ""
  echo "ZackGPT Web Server Launcher"
  echo ""
  echo "This script starts the ZackGPT web API server with all dependencies."
  echo ""
  echo "Prerequisites:"
  echo "  • Python 3.7+"
  echo "  • .env file with OPENAI_API_KEY"
  echo ""
  echo "Usage:"
  echo "  ./zackgpt_web.sh        Start the web server"
  echo "  ./zackgpt_web.sh -h     Show this help"
  echo ""
  echo "After starting, you can:"
  echo "  1. Visit http://localhost:8000/docs for API documentation"
  echo "  2. Start the frontend with: cd ui/zackgpt-ui && npm start"
  echo "  3. Visit http://localhost:4200 for the web interface"
  echo ""
  exit 0
fi

main 