#!/usr/bin/env python3
"""
ZackGPT Master Launcher
Centralized entry point for all ZackGPT modes and services
"""

import os
import sys
import subprocess
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from launcher.process_manager import ProcessManager


def print_banner():
    """Print the main ZackGPT banner"""
    print("\033[1;36m")
    print("╔═══════════════════════════════════════════╗")
    print("║         🚀 ZackGPT Master Launcher         ║")
    print("║      Advanced AI Assistant Platform       ║")
    print("╚═══════════════════════════════════════════╝")
    print("\033[0m")


def check_environment():
    """Check if the environment is properly set up"""
    # Check if we're in the right directory
    if not Path("requirements.txt").exists():
        print("❌ Error: Please run this script from the ZackGPT root directory")
        return False
    
    # Check for .env file
    if not Path(".env").exists():
        print("❌ No .env file found")
        print("💡 Please create a .env file with your API keys")
        print("   Example: echo 'OPENAI_API_KEY=your_key_here' > .env")
        return False
    
    # Check for Python
    if not subprocess.run(["python3", "--version"], capture_output=True).returncode == 0:
        print("❌ Python 3 is required but not found")
        return False
    
    return True


def launch_cli_mode():
    """Launch CLI mode using the dedicated CLI launcher"""
    print("\n🖥️  Launching CLI Mode...")
    print("=" * 40)
    
    try:
        # Use the dedicated CLI launcher
        result = subprocess.run([
            "bash", "cli/scripts/zackgpt-cli.sh"
        ], cwd=os.getcwd())
        
        if result.returncode != 0:
            print("❌ CLI mode exited with error")
        else:
            print("✅ CLI mode completed successfully")
            
    except KeyboardInterrupt:
        print("\n🛑 CLI mode interrupted by user")
    except Exception as e:
        print(f"❌ Error launching CLI mode: {e}")


def launch_web_server():
    """Launch web server using the dedicated server launcher"""
    print("\n🌐 Launching Web Server...")
    print("=" * 40)
    
    try:
        # Use the dedicated server launcher
        result = subprocess.run([
            "bash", "server/scripts/start-server.sh"
        ], cwd=os.getcwd())
        
        if result.returncode != 0:
            print("❌ Web server exited with error")
        else:
            print("✅ Web server completed successfully")
            
    except KeyboardInterrupt:
        print("\n🛑 Web server interrupted by user")
    except Exception as e:
        print(f"❌ Error launching web server: {e}")


def launch_full_web_application():
    """Launch full web application (backend + frontend)"""
    print("\n🌐 Launching Full Web Application...")
    print("=" * 50)
    
    process_manager = ProcessManager()
    
    try:
        # Start backend server
        backend_process = process_manager.start_process(
            "backend",
            ["python3", "-m", "server.main"],
            port=8000
        )
        
        print("⏳ Waiting for backend to be ready...")
        import time
        import requests
        
        # Wait for backend to be ready
        for i in range(30):
            try:
                response = requests.get("http://localhost:8000/", timeout=1)
                if response.status_code == 200:
                    print("✅ Backend is ready!")
                    break
            except:
                pass
            time.sleep(1)
        else:
            print("❌ Backend failed to start within 30 seconds")
            process_manager.shutdown_all()
            return
        
        # Check if frontend exists and start it
        if Path("frontend").exists():
            print("🎨 Starting frontend...")
            frontend_process = process_manager.start_process(
                "frontend",
                ["npm", "start"],
                port=3000,
                cwd="frontend"
            )
        else:
            print("⚠️  Frontend directory not found, running backend only")
        
        # Show status
        print("\n" + "=" * 50)
        print("🎉 ZackGPT Web Application is running!")
        print("")
        print("📡 Access points:")
        print("   • Backend API: http://localhost:8000")
        print("   • API Docs:    http://localhost:8000/docs")
        
        if Path("frontend").exists():
            print("   • Frontend UI: http://localhost:3000")
        
        print("")
        print("💡 Press Ctrl+C to stop all services")
        print("=" * 50)
        
        # Keep running until interrupted
        try:
            while True:
                # Health check every 30 seconds
                time.sleep(30)
                if not process_manager.health_check():
                    print("⚠️  Health check failed, restarting services...")
                    break
        except KeyboardInterrupt:
            print("\n🛑 Shutting down web application...")
        
        process_manager.shutdown_all()
        
    except Exception as e:
        print(f"❌ Error in web application: {e}")
        process_manager.shutdown_all()


def launch_docker_mode():
    """Launch using Docker"""
    print("\n🐳 Launching Docker Mode...")
    print("=" * 40)
    
    try:
        # Check if Docker is available
        result = subprocess.run(["docker", "--version"], capture_output=True)
        if result.returncode != 0:
            print("❌ Docker is not available")
            return
        
        # Check for docker-compose
        if Path("docker-compose.yml").exists():
            print("📦 Using docker-compose...")
            result = subprocess.run(["docker-compose", "up", "--build"])
        else:
            print("📦 Using Dockerfile...")
            # Build and run
            print("🔧 Building Docker image...")
            build_result = subprocess.run(["docker", "build", "-t", "zackgpt", "."])
            if build_result.returncode != 0:
                print("❌ Docker build failed")
                return
            
            print("🚀 Running Docker container...")
            result = subprocess.run([
                "docker", "run", "-it", "--rm",
                "--env-file", ".env",
                "-v", f"{os.getcwd()}:/app",
                "zackgpt"
            ])
        
        if result.returncode == 0:
            print("✅ Docker mode completed successfully")
        else:
            print("❌ Docker mode exited with error")
            
    except KeyboardInterrupt:
        print("\n🛑 Docker mode interrupted by user")
    except Exception as e:
        print(f"❌ Error launching Docker mode: {e}")


def show_status():
    """Show status of running ZackGPT services"""
    print("\n📊 ZackGPT Service Status")
    print("=" * 40)
    
    process_manager = ProcessManager()
    
    # Check common ports
    ports_to_check = {
        8000: "Backend API",
        3000: "Frontend (React)",
        4200: "Frontend (Angular)",
        8001: "Development Tools"
    }
    
    running_services = []
    
    for port, service_name in ports_to_check.items():
        if process_manager.is_port_in_use(port):
            pid = process_manager.get_process_on_port(port)
            running_services.append(f"✅ {service_name}: http://localhost:{port} (PID: {pid})")
        else:
            print(f"⭕ {service_name}: Not running")
    
    if running_services:
        print("\n🟢 Running services:")
        for service in running_services:
            print(f"   {service}")
    else:
        print("\n⭕ No ZackGPT services are currently running")


def main():
    """Main launcher entry point"""
    print_banner()
    
    # Environment check
    if not check_environment():
        sys.exit(1)
    
    print("🎯 Select a launch mode:\n")
    print("1) 🖥️  CLI Mode          (Pure command-line interface)")
    print("2) 🌐 Web Server        (API server only, port 8000)")  
    print("3) 🎨 Full Web App      (Backend + Frontend)")
    print("4) 🐳 Docker Mode       (Containerized deployment)")
    print("5) 📊 Show Status       (Check running services)")
    print("6) ❌ Exit\n")
    
    while True:
        try:
            choice = input("Choose an option (1-6): ").strip()
            
            if choice == "1":
                launch_cli_mode()
                break
            elif choice == "2":
                launch_web_server()
                break
            elif choice == "3":
                launch_full_web_application()
                break
            elif choice == "4":
                launch_docker_mode()
                break
            elif choice == "5":
                show_status()
                print("\nPress Enter to continue...")
                input()
                continue
            elif choice == "6":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-6.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main() 