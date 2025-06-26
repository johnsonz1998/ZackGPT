#!/bin/bash
# ZackGPT Quick Reset Shortcuts
# ⚠️ TO BE DEPRECATED - Will be replaced with option menu interface
# Easy commands for common reset operations

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESET_SCRIPT="$SCRIPT_DIR/reset_system.py"

echo "🤖 ZackGPT Quick Reset Tool"
echo "=========================="

case "$1" in
    "memories")
        echo "🗑️ Clearing memories only..."
        python3 "$RESET_SCRIPT" --memories
        ;;
    "threads")
        echo "🗑️ Clearing chat threads only..."
        python3 "$RESET_SCRIPT" --threads
        ;;
    "brain")
        echo "🧠 Clearing AI brain (with backup)..."
        python3 "$RESET_SCRIPT" --brain
        ;;
    "all")
        echo "🗑️ Clearing everything (with backups)..."
        python3 "$RESET_SCRIPT" --all
        ;;
    "nuclear")
        echo "☢️ NUCLEAR OPTION - clearing entire database..."
        python3 "$RESET_SCRIPT" --nuclear
        ;;
    "backup")
        echo "📦 Creating backups without clearing..."
        python3 "$RESET_SCRIPT" --backup-only
        ;;
    "list")
        echo "📦 Listing available backups..."
        python3 "$RESET_SCRIPT" --list-backups
        ;;
    "menu")
        echo "🔧 Opening interactive menu..."
        python3 "$RESET_SCRIPT"
        ;;
    *)
        echo "Usage: $0 {memories|threads|brain|all|nuclear|backup|list|menu}"
        echo ""
        echo "Options:"
        echo "  memories  - Clear stored memories only"
        echo "  threads   - Clear chat threads only"
        echo "  brain     - Clear AI brain (prompt evolution)"
        echo "  all       - Clear memories + threads + brain"
        echo "  nuclear   - Clear entire database (everything)"
        echo "  backup    - Create backups without clearing"
        echo "  list      - List available backups"
        echo "  menu      - Open interactive menu"
        echo ""
        echo "Examples:"
        echo "  $0 memories     # Clear just the memories"
        echo "  $0 brain        # Reset AI personality to default"
        echo "  $0 all          # Full reset with backups"
        echo "  $0 menu         # Interactive menu with all options"
        exit 1
        ;;
esac 