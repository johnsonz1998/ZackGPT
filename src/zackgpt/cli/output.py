"""
CLI Output Utilities
Provides colored and formatted output for the CLI interface
"""

import sys
from typing import Any


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    BOLD = '\033[1m'
    NC = '\033[0m'  # No Color


def print_banner():
    """Print the ZackGPT CLI banner"""
    print(f"{Colors.CYAN}")
    print("╔═══════════════════════════════════╗")
    print("║      🤖 ZackGPT CLI Interface      ║")
    print("║     Advanced AI Assistant         ║")
    print("╚═══════════════════════════════════╝")
    print(f"{Colors.NC}")


def print_success(message: str, details: Any = None):
    """Print a success message in green"""
    print(f"{Colors.GREEN}✅ {message}{Colors.NC}")
    if details:
        print(f"{Colors.WHITE}   {details}{Colors.NC}")


def print_error(message: str, details: Any = None):
    """Print an error message in red"""
    print(f"{Colors.RED}❌ {message}{Colors.NC}")
    if details:
        print(f"{Colors.WHITE}   {details}{Colors.NC}")


def print_warning(message: str, details: Any = None):
    """Print a warning message in yellow"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.NC}")
    if details:
        print(f"{Colors.WHITE}   {details}{Colors.NC}")


def print_info(message: str, details: Any = None):
    """Print an info message in blue"""
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.NC}")
    if details:
        print(f"{Colors.WHITE}   {details}{Colors.NC}")


def print_step(step: int, total: int, message: str):
    """Print a step in a process"""
    print(f"{Colors.CYAN}[{step}/{total}] {message}{Colors.NC}")


def get_user_choice(prompt: str, choices: list, default: str = None) -> str:
    """Get user choice from a list of options"""
    while True:
        print(f"\n{Colors.YELLOW}{prompt}{Colors.NC}")
        for i, choice in enumerate(choices, 1):
            marker = f"{Colors.GREEN}→{Colors.NC}" if default and choice.lower().startswith(default.lower()) else " "
            print(f"{marker} {i}) {choice}")
        
        try:
            user_input = input(f"\nChoose an option (1-{len(choices)}): ").strip()
            
            if not user_input and default:
                # Find default choice
                for i, choice in enumerate(choices):
                    if choice.lower().startswith(default.lower()):
                        return choice
            
            if user_input.isdigit():
                choice_idx = int(user_input) - 1
                if 0 <= choice_idx < len(choices):
                    return choices[choice_idx]
            
            print_error("Invalid choice. Please try again.")
            
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}👋 Goodbye!{Colors.NC}")
            sys.exit(0)
        except Exception as e:
            print_error(f"Error: {e}")


def confirm_action(message: str, default: bool = False) -> bool:
    """Ask user for confirmation"""
    default_text = "Y/n" if default else "y/N"
    while True:
        try:
            response = input(f"{Colors.YELLOW}{message} ({default_text}): {Colors.NC}").strip().lower()
            
            if not response:
                return default
                
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print_error("Please enter 'y' or 'n'")
                
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}👋 Goodbye!{Colors.NC}")
            sys.exit(0) 