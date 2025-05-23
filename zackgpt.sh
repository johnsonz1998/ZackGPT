#!/bin/bash

trap ctrl_c INT

function ctrl_c() {
  echo -e "\n\033[1;31m[!] Interrupted. Cleaning up...\033[0m"
  type deactivate &>/dev/null && deactivate
  exit 1
}

function ascii_banner() {
  echo -e "\033[1;35m"
  echo "╔═══════════════════════════════╗"
  echo "║      ⚡ ZackGPT Launcher ⚡      ║"
  echo "╚═══════════════════════════════╝"
  echo -e "\033[0m"
}

function ensure_docker_accessible() {
  if ! docker ps >/dev/null 2>&1; then
    echo -e "\033[1;31m[!] Docker is not responding on the current context.\033[0m"
    read -p "🔄 Switch Docker context to Colima? (y/n): " switch
    if [[ "$switch" == "y" ]]; then
      docker context use colima
      echo -e "\033[1;32m[+] Switched to Colima. Verifying...\033[0m"
      if ! docker ps >/dev/null 2>&1; then
        echo -e "\033[1;31m[!] Still can't connect to Docker. Exiting.\033[0m"
        exit 1
      fi
    else
      echo -e "\033[1;31m[!] Aborting due to inaccessible Docker daemon.\033[0m"
      exit 1
    fi
  fi
}

function detect_docker_backend() {
  if docker context ls | grep -q colima; then
    echo "colima"
  elif docker context ls | grep -q rancher; then
    echo "rancher"
  else
    echo "default"
  fi
}

function ensure_colima_running() {
  if ! colima status 2>/dev/null | grep -q "Running"; then
    echo -e "\033[1;33m[!] Colima is not running. Starting...\033[0m"
    colima start
  else
    echo -e "\033[1;32m[+] Colima is already running.\033[0m"
  fi
}

function choose_script() {
  echo -e "\n📂 Choose a script to run:"
  echo "1) 🧠  main.py (full assistant)"
  echo "2) 🧪  dev.py (test/dev mode)"
  read -p $'\nChoose an option (1-2): ' script_choice

  if [[ "$script_choice" == "2" ]]; then
    echo "scripts/startup/dev.py"
  else
    echo "scripts/startup/main.py"
  fi
}

function run_local() {
  script=$(choose_script)

  echo -e "\033[1;36m[+] Running on Host...\033[0m"
  if [ ! -d ".venv" ]; then
    echo -e "\033[1;33m[!] No virtualenv found. Creating...\033[0m"
    python3 -m venv .venv
  fi
  source .venv/bin/activate
  pip install --upgrade pip setuptools wheel > /dev/null
  pip install -r requirements.txt

  if [ -f .env ]; then
    set -a
    source .env 2>/dev/null
    set +a
  else
    echo -e "\033[1;31m[!] No .env file found!\033[0m"
  fi

  echo -e "\033[1;32m[+] Running $script locally...\033[0m"
  python $script
  deactivate
}

function run_docker() {
  ensure_docker_accessible
  script=$(choose_script)

  echo -e "\033[1;36m[+] Building Docker image...\033[0m"
  if ! docker build -t zackgpt .; then
    echo -e "\033[1;31m[!] Docker build failed. Aborting.\033[0m"
    exit 1
  fi

  echo -e "\033[1;32m[+] Running $script in Docker...\033[0m"
  docker run -it --rm \
    --env-file .env \
    -v "$(pwd)":/app \
    zackgpt python $script
}

# =============================
#          MAIN MENU
# =============================
ascii_banner

echo "1) 🖥️  Run on Host (Python virtualenv)"
echo "2) 🐳  Run in Docker (current backend)"
echo "3) 🧱  Run in Docker via Colima (force-start)"
echo "4) ❌  Cancel"

read -p $'\nChoose an option (1-4): ' choice

case "$choice" in
  1)
    run_local
    ;;
  2)
    backend=$(detect_docker_backend)
    echo -e "\033[1;36m[+] Docker backend detected: $backend\033[0m"
    run_docker
    ;;
  3)
    ensure_colima_running
    echo -e "\033[1;36m[+] Colima is ready.\033[0m"
    run_docker
    ;;
  *)
    echo -e "\033[1;31m[!] Cancelled by user.\033[0m"
    exit 0
    ;;
esac
