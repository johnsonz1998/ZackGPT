#!/bin/bash

# ZackGPT Master Launcher - Restructured
# Now uses proper Python package structure

set -e

function print_banner() {
  echo -e "\033[1;36m"
  echo "╔═══════════════════════════════════════════╗"
  echo "║         🚀 ZackGPT Master Launcher         ║"
  echo "║      Advanced AI Assistant Platform       ║"
  echo "║           ✨ Now Restructured! ✨           ║"
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
  echo -e "\033[1;32m✅ ZackGPT has been completely restructured!\033[0m"
  echo ""
  echo -e "\033[1;36m🎯 New unified interface options:\033[0m"
  echo -e "\033[1;37m  ./bin/zackgpt-cli          # Direct CLI access\033[0m"
  echo -e "\033[1;37m  ./bin/zackgpt-web          # Direct web server\033[0m"
  echo -e "\033[1;37m  python launcher/main.py    # Full launcher menu\033[0m"
  echo ""
  echo -e "\033[1;36m📦 New package structure:\033[0m"
  echo -e "\033[1;37m  src/zackgpt/core/          # Core AI logic\033[0m"
  echo -e "\033[1;37m  src/zackgpt/cli/           # CLI interface\033[0m"
  echo -e "\033[1;37m  src/zackgpt/web/           # Web interface\033[0m"
  echo -e "\033[1;37m  scripts/bin/               # All scripts centralized\033[0m"
  echo ""
  echo -e "\033[1;33m⚡ All imports fixed, no more sys.path hacks!\033[0m"
  echo ""
  echo -e "\033[1;33mStarting centralized launcher...\033[0m"
  echo ""
  
  # Delegate to the new centralized launcher
  python3 launcher/main.py
}

main "$@"
