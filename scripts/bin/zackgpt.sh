#!/bin/bash

# ZackGPT Master Launcher - Simplified
# Delegates to the new centralized launcher system

set -e

function print_banner() {
  echo -e "\033[1;36m"
  echo "╔═══════════════════════════════════════════╗"
  echo "║         🚀 ZackGPT Master Launcher         ║"
  echo "║      Advanced AI Assistant Platform       ║"
  echo "╚═══════════════════════════════════════════╝"
  echo -e "\033[0m"
}

function check_python() {
  if ! command -v python3 &> /dev/null; then
    echo -e "\033[1;31m❌ Python 3 is required but not installed\033[0m"
    exit 1
  fi
}

function check_environment() {
  if [ ! -f "requirements.txt" ]; then
    echo -e "\033[1;31m❌ Error: Please run this script from the ZackGPT root directory\033[0m"
    exit 1
  fi
  
  if [ ! -f ".env" ]; then
    echo -e "\033[1;31m❌ No .env file found\033[0m"
    echo -e "\033[1;33m💡 Please create a .env file with your API keys\033[0m"
    echo -e "\033[1;33m   Example: echo 'OPENAI_API_KEY=your_key_here' > .env\033[0m"
    exit 1
  fi
}

function main() {
  print_banner
  check_python
  check_environment
  
  echo ""
  echo -e "\033[1;33m🎯 ZackGPT now uses a centralized launcher system!\033[0m"
  echo ""
  echo -e "\033[1;36mFor the new organized experience:\033[0m"
  echo -e "\033[1;37m  python launcher/main.py    # New centralized launcher\033[0m"
  echo ""
  echo -e "\033[1;36mOr use direct launchers:\033[0m"
  echo -e "\033[1;37m  cli/scripts/zackgpt-cli.sh     # Pure CLI mode\033[0m"
  echo -e "\033[1;37m  server/scripts/start-server.sh # Web server only\033[0m"
  echo ""
  echo -e "\033[1;33mStarting centralized launcher...\033[0m"
  echo ""
  
  # Delegate to the new centralized launcher
  python3 launcher/main.py
}

main "$@"
