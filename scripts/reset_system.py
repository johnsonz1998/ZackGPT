#!/usr/bin/env python3
"""
ZackGPT System Reset Tool
========================
⚠️ TO BE DEPRECATED - Will be replaced with option menu interface
Comprehensive reset options for different components of the ZackGPT system.
"""

import os
import sys
import json
import argparse
import pymongo
from datetime import datetime
from pathlib import Path

# Add src to path so we can import ZackGPT modules
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from src.zackgpt.data.database import get_database
    from src.zackgpt.data.thread_manager import ThreadManager
    from src.zackgpt.data.memory_manager import MemoryManager
except ImportError as e:
    print(f"❌ Error importing ZackGPT modules: {e}")
    print("Make sure you're running this from the ZackGPT root directory")
    sys.exit(1)

class ZackGPTResetter:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.root_dir = self.script_dir.parent
        self.evolution_file = self.root_dir / 'config' / 'prompt_evolution' / 'evolution_data.json'
        self.backup_dir = self.root_dir / 'backups'
        self.backup_dir.mkdir(exist_ok=True)
        
    def create_timestamp(self):
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def backup_evolution_data(self):
        """Create a backup of current prompt evolution data"""
        if not self.evolution_file.exists():
            print("⚠️ No evolution data file found to backup")
            return None
            
        timestamp = self.create_timestamp()
        backup_file = self.backup_dir / f'evolution_backup_{timestamp}.json'
        
        with open(self.evolution_file, 'r') as src, open(backup_file, 'w') as dst:
            dst.write(src.read())
            
        print(f"📦 Evolution data backed up to: {backup_file}")
        return backup_file
    
    def backup_database(self):
        """Create a backup of database content"""
        timestamp = self.create_timestamp()
        backup_file = self.backup_dir / f'database_backup_{timestamp}.json'
        
        try:
            db = get_database()
            tm = ThreadManager()
            
            # Get all data
            memories = db.get_all_memories(limit=1000)
            threads = tm.get_all_threads()
            
            backup_data = {
                'timestamp': timestamp,
                'memories': memories,
                'threads': threads,
                'total_memories': len(memories),
                'total_threads': len(threads)
            }
            
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2, default=str)
                
            print(f"📦 Database backed up to: {backup_file}")
            print(f"   - {len(memories)} memories")
            print(f"   - {len(threads)} threads")
            return backup_file
            
        except Exception as e:
            print(f"❌ Error backing up database: {e}")
            return None
    
    def get_current_state(self):
        """Get current system state"""
        try:
            # Database state
            db = get_database()
            tm = ThreadManager()
            memories = db.get_all_memories(limit=1000)
            threads = tm.get_all_threads()
            
            # Evolution data state
            evolution_components = 0
            evolution_experiments = 0
            if self.evolution_file.exists():
                with open(self.evolution_file, 'r') as f:
                    evolution_data = json.load(f)
                    evolution_components = sum(len(comps) for comps in evolution_data.get('components', {}).values())
                    evolution_experiments = len(evolution_data.get('experiments', []))
            
            return {
                'memories': len(memories),
                'threads': len(threads),
                'evolution_components': evolution_components,
                'evolution_experiments': evolution_experiments,
                'evolution_file_exists': self.evolution_file.exists()
            }
        except Exception as e:
            print(f"❌ Error getting current state: {e}")
            return None
    
    def clear_memories(self):
        """Clear all stored memories"""
        print("🗑️ Clearing memories...")
        try:
            # Direct MongoDB approach for thorough cleanup
            client = pymongo.MongoClient('localhost', 27017)
            db = client['zackgpt']
            
            if 'memories' in db.list_collection_names():
                result = db.memories.delete_many({})
                print(f"✅ Deleted {result.deleted_count} memories")
            else:
                print("ℹ️ No memories collection found")
                
            client.close()
            return True
        except Exception as e:
            print(f"❌ Error clearing memories: {e}")
            return False
    
    def clear_threads(self):
        """Clear all chat threads"""
        print("🗑️ Clearing chat threads...")
        try:
            tm = ThreadManager()
            threads = tm.get_all_threads()
            deleted_count = 0
            
            for thread in threads:
                if tm.delete_thread(thread['id']):
                    deleted_count += 1
            
            print(f"✅ Deleted {deleted_count} chat threads")
            return True
        except Exception as e:
            print(f"❌ Error clearing threads: {e}")
            return False
    
    def clear_evolution_data(self):
        """Reset prompt evolution data to default"""
        print("🧠 Clearing AI brain (prompt evolution data)...")
        try:
            # Create backup first
            backup_file = self.backup_evolution_data()
            
            # Reset to default state
            default_evolution_data = {
                'components': {
                    'personality': [],
                    'task_approach': [],
                    'communication_style': [],
                    'problem_solving': []
                },
                'experiments': [],
                'learning_metrics': {
                    'total_interactions': 0,
                    'successful_adaptations': 0,
                    'failed_adaptations': 0,
                    'last_reset': datetime.now().isoformat()
                }
            }
            
            with open(self.evolution_file, 'w') as f:
                json.dump(default_evolution_data, f, indent=2)
            
            print("✅ AI brain reset to default state")
            print(f"📦 Previous state backed up to: {backup_file}")
            return True
        except Exception as e:
            print(f"❌ Error clearing evolution data: {e}")
            return False
    
    def clear_database_completely(self):
        """Clear all database collections completely"""
        print("🗑️ Clearing entire database...")
        try:
            client = pymongo.MongoClient('localhost', 27017)
            db = client['zackgpt']
            
            collections = db.list_collection_names()
            total_deleted = 0
            
            for collection_name in collections:
                result = db[collection_name].delete_many({})
                print(f"  ✅ Deleted {result.deleted_count} documents from {collection_name}")
                total_deleted += result.deleted_count
            
            print(f"✅ Total: {total_deleted} documents deleted across {len(collections)} collections")
            client.close()
            return True
        except Exception as e:
            print(f"❌ Error clearing database: {e}")
            return False
    
    def restore_evolution_data(self, backup_file):
        """Restore evolution data from backup"""
        print(f"🔄 Restoring evolution data from {backup_file}...")
        try:
            if not Path(backup_file).exists():
                print(f"❌ Backup file not found: {backup_file}")
                return False
            
            # Copy backup to evolution file
            with open(backup_file, 'r') as src, open(self.evolution_file, 'w') as dst:
                dst.write(src.read())
            
            # Verify restoration
            with open(self.evolution_file, 'r') as f:
                data = json.load(f)
            
            total_components = sum(len(comps) for comps in data['components'].values())
            print(f"✅ Restored evolution data:")
            print(f"   - {total_components} learned components")
            print(f"   - {len(data.get('experiments', []))} experiments")
            
            return True
        except Exception as e:
            print(f"❌ Error restoring evolution data: {e}")
            return False
    
    def list_backups(self):
        """List available backup files"""
        evolution_backups = list(self.backup_dir.glob('evolution_backup_*.json'))
        database_backups = list(self.backup_dir.glob('database_backup_*.json'))
        
        print("📦 Available backups:")
        print("\n🧠 Evolution Data Backups:")
        if evolution_backups:
            for backup in sorted(evolution_backups):
                print(f"   - {backup.name}")
        else:
            print("   (none)")
            
        print("\n💾 Database Backups:")
        if database_backups:
            for backup in sorted(database_backups):
                print(f"   - {backup.name}")
        else:
            print("   (none)")
    
    def interactive_menu(self):
        """Interactive menu for reset options"""
        while True:
            # Show current state
            state = self.get_current_state()
            if state:
                print("\n" + "="*60)
                print("🤖 ZackGPT System Reset Tool")
                print("="*60)
                print("📊 Current State:")
                print(f"   - Memories: {state['memories']}")
                print(f"   - Chat Threads: {state['threads']}")
                print(f"   - AI Brain Components: {state['evolution_components']}")
                print(f"   - Evolution Experiments: {state['evolution_experiments']}")
            
            print("\n🔧 Reset Options:")
            print("1. Clear memories only")
            print("2. Clear chat threads only")
            print("3. Clear AI brain (prompt evolution) only")
            print("4. Clear memories + threads (keep AI brain)")
            print("5. Clear EVERYTHING (memories + threads + AI brain)")
            print("6. Clear entire database (nuclear option)")
            print("")
            print("🔄 Restore Options:")
            print("7. Restore AI brain from backup")
            print("8. List all backups")
            print("9. Create backups without clearing")
            print("")
            print("0. Exit")
            
            choice = input("\nEnter your choice (0-9): ").strip()
            
            if choice == '0':
                print("👋 Goodbye!")
                break
            elif choice == '1':
                self.clear_memories()
            elif choice == '2':
                self.clear_threads()
            elif choice == '3':
                self.clear_evolution_data()
            elif choice == '4':
                self.backup_database()
                self.clear_memories()
                self.clear_threads()
            elif choice == '5':
                self.backup_database()
                self.backup_evolution_data()
                self.clear_memories()
                self.clear_threads()
                self.clear_evolution_data()
            elif choice == '6':
                confirm = input("⚠️ This will delete EVERYTHING. Type 'YES' to confirm: ")
                if confirm == 'YES':
                    self.backup_database()
                    self.backup_evolution_data()
                    self.clear_database_completely()
                    self.clear_evolution_data()
                else:
                    print("❌ Operation cancelled")
            elif choice == '7':
                self.list_backups()
                backup_file = input("\nEnter backup filename (from backups/ directory): ").strip()
                if backup_file:
                    full_path = self.backup_dir / backup_file
                    self.restore_evolution_data(full_path)
            elif choice == '8':
                self.list_backups()
            elif choice == '9':
                self.backup_database()
                self.backup_evolution_data()
            else:
                print("❌ Invalid choice. Please try again.")
            
            input("\nPress Enter to continue...")

def main():
    parser = argparse.ArgumentParser(description='ZackGPT System Reset Tool')
    parser.add_argument('--memories', action='store_true', help='Clear memories only')
    parser.add_argument('--threads', action='store_true', help='Clear chat threads only')
    parser.add_argument('--brain', action='store_true', help='Clear AI brain (evolution data) only')
    parser.add_argument('--all', action='store_true', help='Clear everything')
    parser.add_argument('--nuclear', action='store_true', help='Clear entire database (nuclear option)')
    parser.add_argument('--restore-brain', type=str, help='Restore AI brain from backup file')
    parser.add_argument('--list-backups', action='store_true', help='List available backups')
    parser.add_argument('--backup-only', action='store_true', help='Create backups without clearing')
    
    args = parser.parse_args()
    resetter = ZackGPTResetter()
    
    # If no arguments, run interactive menu
    if not any(vars(args).values()):
        resetter.interactive_menu()
        return
    
    # Handle command line arguments
    if args.list_backups:
        resetter.list_backups()
    elif args.backup_only:
        resetter.backup_database()
        resetter.backup_evolution_data()
    elif args.restore_brain:
        backup_file = Path(args.restore_brain)
        if not backup_file.is_absolute():
            backup_file = resetter.backup_dir / backup_file
        resetter.restore_evolution_data(backup_file)
    elif args.nuclear:
        print("⚠️ NUCLEAR OPTION: This will delete EVERYTHING")
        confirm = input("Type 'YES' to confirm: ")
        if confirm == 'YES':
            resetter.backup_database()
            resetter.backup_evolution_data()
            resetter.clear_database_completely()
            resetter.clear_evolution_data()
        else:
            print("❌ Operation cancelled")
    elif args.all:
        resetter.backup_database()
        resetter.backup_evolution_data()
        resetter.clear_memories()
        resetter.clear_threads()
        resetter.clear_evolution_data()
    elif args.memories:
        resetter.clear_memories()
    elif args.threads:
        resetter.clear_threads()
    elif args.brain:
        resetter.clear_evolution_data()

if __name__ == '__main__':
    main() 