#!/bin/bash

trap ctrl_c INT

function ctrl_c() {
  echo -e "\n\033[1;31m[!] Interrupted. Cleaning up...\033[0m"
  # Kill background processes
  if [ ! -z "$BACKEND_PID" ]; then
    echo -e "\033[1;33m[!] Stopping backend server (PID: $BACKEND_PID)...\033[0m"
    kill $BACKEND_PID 2>/dev/null
  fi
  if [ ! -z "$FRONTEND_PID" ]; then
    echo -e "\033[1;33m[!] Stopping frontend server (PID: $FRONTEND_PID)...\033[0m"
    kill $FRONTEND_PID 2>/dev/null
  fi
  # Kill any remaining ng serve processes
  pkill -f "ng serve" 2>/dev/null
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
  pip install -r requirements.txt > /dev/null
  
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

function check_frontend_dependencies() {
  echo -e "\033[1;33m[!] Checking frontend dependencies...\033[0m"
  
  # Check if Node.js is installed
  if ! command -v node &> /dev/null; then
    echo -e "\033[1;31m[!] Node.js is not installed. Please install Node.js first.\033[0m"
    exit 1
  fi
  
  # Check if npm is installed
  if ! command -v npm &> /dev/null; then
    echo -e "\033[1;31m[!] npm is not installed. Please install npm first.\033[0m"
    exit 1
  fi
  
  # Check if UI directory exists
  if [ ! -d "ui/zackgpt-ui" ]; then
    echo -e "\033[1;31m[!] Frontend directory not found. Make sure you're in the ZackGPT root directory.\033[0m"
    exit 1
  fi
  
  # Install frontend dependencies if needed
  if [ ! -d "ui/zackgpt-ui/node_modules" ]; then
    echo -e "\033[1;33m[!] Installing frontend dependencies...\033[0m"
    cd ui/zackgpt-ui
    npm install
    cd ../..
  fi
  
  echo -e "\033[1;32m[+] Frontend dependencies ready!\033[0m"
}

function start_backend() {
  echo -e "\033[1;32m[+] Starting ZackGPT backend server...\033[0m"
  python -m scripts.startup.main_web &
  BACKEND_PID=$!
  echo -e "\033[1;37m   Backend PID: $BACKEND_PID\033[0m"
  
  # Wait for backend to start
  echo -e "\033[1;33m[!] Waiting for backend to start...\033[0m"
  for i in {1..30}; do
    if curl -s http://localhost:8000/ > /dev/null 2>&1; then
      echo -e "\033[1;32m[+] Backend is ready!\033[0m"
      break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
      echo -e "\033[1;31m[!] Backend failed to start within 30 seconds\033[0m"
      exit 1
    fi
  done
}

function start_frontend() {
  echo -e "\033[1;32m[+] Starting ZackGPT frontend server...\033[0m"
  cd ui/zackgpt-ui
  npm start -- --host 0.0.0.0 &
  FRONTEND_PID=$!
  cd ../..
  echo -e "\033[1;37m   Frontend PID: $FRONTEND_PID\033[0m"
  
  # Wait for frontend to start
  echo -e "\033[1;33m[!] Waiting for frontend to start...\033[0m"
  for i in {1..60}; do
    if curl -s http://localhost:4200/ > /dev/null 2>&1; then
      echo -e "\033[1;32m[+] Frontend is ready!\033[0m"
      break
    fi
    sleep 1
    if [ $i -eq 60 ]; then
      echo -e "\033[1;31m[!] Frontend failed to start within 60 seconds\033[0m"
      exit 1
    fi
  done
}

function start_web_server() {
  echo -e "\033[1;36m[+] Starting ZackGPT Web Application...\033[0m"
  echo ""
  
  # Start backend first
  start_backend
  
  # Then start frontend
  start_frontend
  
  echo ""
  echo -e "\033[1;32m🎉 ZackGPT Web Application is ready!\033[0m"
  echo ""
  echo -e "\033[1;33m📡 Access your application at:\033[0m"
  echo -e "\033[1;37m   • Frontend UI: http://localhost:4200\033[0m"
  echo -e "\033[1;37m   • Backend API: http://localhost:8000\033[0m"
  echo -e "\033[1;37m   • API Docs: http://localhost:8000/docs\033[0m"
  echo ""
  echo -e "\033[1;36m💡 Press Ctrl+C to stop both servers\033[0m"
  echo ""
  
  # Wait for both processes
  wait
}

function main() {
  print_banner
  
  # Check if Python is available
  if ! command -v python3 &> /dev/null; then
    echo -e "\033[1;31m[!] Python 3 is required but not installed.\033[0m"
    exit 1
  fi
  
  setup_environment
  check_frontend_dependencies
  start_web_server
}

# Check for help flag
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
  print_banner
  echo ""
  echo "ZackGPT Web Server Launcher"
  echo ""
  echo "This script starts both the ZackGPT backend API and frontend UI servers."
  echo ""
  echo "Prerequisites:"
  echo "  • Python 3.7+"
  echo "  • Node.js and npm"
  echo "  • .env file with OPENAI_API_KEY"
  echo ""
  echo "Usage:"
  echo "  ./zackgpt_web.sh        Start both backend and frontend servers"
  echo "  ./zackgpt_web.sh -h     Show this help"
  echo ""
  echo "Once started, you can access:"
  echo "  • Frontend UI: http://localhost:4200"
  echo "  • Backend API: http://localhost:8000"
  echo "  • API Documentation: http://localhost:8000/docs"
  echo ""
  echo "Press Ctrl+C to stop both servers gracefully."
  echo ""
  exit 0
fi

main 