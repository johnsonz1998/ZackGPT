# ZackGPT Reset System Tools

⚠️ **TO BE DEPRECATED** - These tools will be replaced with an integrated option menu interface.

This directory contains powerful tools for resetting different components of your ZackGPT system.

## 🔧 Available Tools

### 1. `reset_system.py` - Comprehensive Reset Tool
Full-featured Python script with both command-line and interactive options.

**Command Line Usage:**
```bash
# Clear specific components
python3 scripts/reset_system.py --memories      # Clear memories only
python3 scripts/reset_system.py --threads       # Clear chat threads only  
python3 scripts/reset_system.py --brain         # Clear AI brain (evolution data)
python3 scripts/reset_system.py --all           # Clear everything
python3 scripts/reset_system.py --nuclear       # Nuclear option (entire database)

# Backup and restore operations
python3 scripts/reset_system.py --backup-only   # Create backups without clearing
python3 scripts/reset_system.py --list-backups  # List available backups
python3 scripts/reset_system.py --restore-brain evolution_backup_20250626_010900.json

# Interactive menu (no arguments)
python3 scripts/reset_system.py                 # Opens interactive menu
```

### 2. `quick_reset.sh` - Simple Shortcuts
Easy-to-remember shortcuts for common operations.

```bash
scripts/quick_reset.sh memories    # Clear stored memories only
scripts/quick_reset.sh threads     # Clear chat threads only
scripts/quick_reset.sh brain       # Clear AI brain (with backup)
scripts/quick_reset.sh all         # Clear everything (with backups)
scripts/quick_reset.sh nuclear     # Nuclear option
scripts/quick_reset.sh backup      # Create backups only
scripts/quick_reset.sh list        # List backups
scripts/quick_reset.sh menu        # Interactive menu
```

## 📊 What Each Component Does

### **Memories** 
- Stored facts and information the AI remembers
- Examples: "My name is John", "I work at Google", "Remember my favorite color is blue"
- **Impact**: AI forgets all personal facts but keeps personality

### **Chat Threads**
- Conversation history and message threads
- **Impact**: No conversation history, but AI keeps memories and personality

### **AI Brain (Evolution Data)**
- Learned personality traits and behavioral weights
- Examples: "witty_efficient", "direct_helpful", response patterns
- **Impact**: AI personality resets to default, loses learned behavior

### **Nuclear Option**
- Completely wipes the entire database
- **Impact**: Everything is deleted, complete fresh start

## 🔒 Safety Features

- **Automatic Backups**: Most operations create backups before clearing
- **Confirmation Prompts**: Dangerous operations require explicit confirmation
- **Restore Options**: Can restore AI brain from any backup
- **Current State Display**: Shows what's currently stored before clearing

## 📦 Backup System

Backups are stored in `backups/` directory with timestamps:
- `evolution_backup_YYYYMMDD_HHMMSS.json` - AI brain backups
- `database_backup_YYYYMMDD_HHMMSS.json` - Full database backups

## 🎯 Common Use Cases

### Reset for Testing
```bash
scripts/quick_reset.sh all          # Clear everything with backups
# Test new features with clean state
```

### Clear Just Personal Data
```bash
scripts/quick_reset.sh memories     # Keep AI personality, clear personal facts
```

### Reset AI Personality
```bash
scripts/quick_reset.sh brain        # Reset to default personality (with backup)
```

### Daily Cleanup
```bash
scripts/quick_reset.sh backup       # Create daily backups
scripts/quick_reset.sh threads      # Clear chat history, keep everything else
```

### Emergency Full Reset
```bash
scripts/quick_reset.sh nuclear      # Complete wipe (use with caution!)
```

## ⚠️ Important Notes

1. **Always backup important data** before major resets
2. **Nuclear option is irreversible** (except for automatic backups)
3. **Run from ZackGPT root directory** for proper module imports
4. **Server restart recommended** after major resets to clear memory
5. **WebSocket reconnection required** after database changes

## 🛡️ Recovery

If something goes wrong:

1. **Check backups**: `scripts/quick_reset.sh list`
2. **Restore AI brain**: `python3 scripts/reset_system.py --restore-brain <backup_file>`
3. **Interactive menu**: `scripts/quick_reset.sh menu` for guided recovery

## 📋 Current System State

To check what's currently stored:
```bash
python3 scripts/reset_system.py     # Interactive menu shows current state
```

Shows:
- Number of stored memories
- Number of chat threads  
- AI brain components count
- Evolution experiments count 