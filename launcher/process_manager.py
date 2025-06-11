"""
Process Manager
Handles background process lifecycle, PID tracking, and graceful shutdowns
"""

import os
import sys
import signal
import subprocess
import time
import psutil
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ServiceProcess:
    """Represents a managed service process"""
    name: str
    pid: int
    command: str
    port: Optional[int] = None
    start_time: float = 0
    status: str = "running"


class ProcessManager:
    """Manages ZackGPT service processes"""
    
    def __init__(self):
        self.processes: Dict[str, ServiceProcess] = {}
        self.shutdown_handlers = []
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n🛑 Received shutdown signal ({signum})")
        self.shutdown_all()
        sys.exit(0)
    
    def add_shutdown_handler(self, handler):
        """Add a custom shutdown handler"""
        self.shutdown_handlers.append(handler)
    
    def start_process(self, name: str, command: List[str], port: Optional[int] = None, 
                     cwd: Optional[str] = None, env: Optional[Dict] = None) -> ServiceProcess:
        """Start a new managed process"""
        print(f"🚀 Starting {name}...")
        
        try:
            # Check if port is already in use
            if port and self.is_port_in_use(port):
                existing_pid = self.get_process_on_port(port)
                if existing_pid:
                    print(f"⚠️  Port {port} is already in use by PID {existing_pid}")
                    print(f"   Killing existing process...")
                    self.kill_process_on_port(port)
                    time.sleep(2)
            
            # Start the process
            process = subprocess.Popen(
                command,
                cwd=cwd or os.getcwd(),
                env=env or os.environ.copy(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid  # Create new process group
            )
            
            # Create service process record
            service_process = ServiceProcess(
                name=name,
                pid=process.pid,
                command=' '.join(command),
                port=port,
                start_time=time.time()
            )
            
            self.processes[name] = service_process
            print(f"✅ {name} started with PID {process.pid}")
            
            return service_process
            
        except Exception as e:
            print(f"❌ Failed to start {name}: {e}")
            raise
    
    def stop_process(self, name: str, timeout: int = 10) -> bool:
        """Stop a managed process gracefully"""
        if name not in self.processes:
            print(f"⚠️  Process {name} not found in managed processes")
            return False
        
        service_process = self.processes[name]
        print(f"🛑 Stopping {name} (PID {service_process.pid})...")
        
        try:
            # Check if process is already dead
            if not psutil.pid_exists(service_process.pid):
                print(f"✅ {name} was already stopped")
                service_process.status = "stopped"
                return True
            
            # Try graceful shutdown first
            process = psutil.Process(service_process.pid)
            process.terminate()
            
            # Wait for graceful shutdown
            try:
                process.wait(timeout=timeout)
                print(f"✅ {name} stopped gracefully")
                service_process.status = "stopped"
                return True
            except psutil.TimeoutExpired:
                # Force kill if graceful shutdown failed
                print(f"⚠️  {name} didn't stop gracefully, forcing shutdown...")
                process.kill()
                try:
                    process.wait(timeout=2)
                    print(f"✅ {name} force stopped")
                    service_process.status = "killed"
                    return True
                except psutil.TimeoutExpired:
                    print(f"❌ Failed to stop {name}")
                    return False
                
        except psutil.NoSuchProcess:
            print(f"✅ {name} was already stopped")
            service_process.status = "stopped"
            return True
        except Exception as e:
            print(f"❌ Error stopping {name}: {e}")
            return False
    
    def shutdown_all(self):
        """Shutdown all managed processes"""
        print("🧹 Shutting down all services...")
        
        # Run custom shutdown handlers first
        for handler in self.shutdown_handlers:
            try:
                handler()
            except Exception as e:
                print(f"⚠️  Error in shutdown handler: {e}")
        
        # Stop all managed processes
        for name in list(self.processes.keys()):
            self.stop_process(name)
        
        # Clean up any remaining processes on known ports
        self._cleanup_known_ports()
        
        print("✅ All services stopped")
    
    def _cleanup_known_ports(self):
        """Clean up processes on known ZackGPT ports"""
        known_ports = [8000, 3000, 4200, 8001]
        
        for port in known_ports:
            if self.is_port_in_use(port):
                print(f"🧹 Cleaning up process on port {port}")
                self.kill_process_on_port(port)
                # Give it a moment to release the port
                time.sleep(0.5)
    
    def is_port_in_use(self, port: int) -> bool:
        """Check if a port is currently in use"""
        for conn in psutil.net_connections():
            if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
                return True
        return False
    
    def get_process_on_port(self, port: int) -> Optional[int]:
        """Get the PID of the process using a specific port"""
        for conn in psutil.net_connections():
            if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
                return conn.pid
        return None
    
    def kill_process_on_port(self, port: int):
        """Kill the process using a specific port"""
        pid = self.get_process_on_port(port)
        if pid:
            try:
                process = psutil.Process(pid)
                process.terminate()
                process.wait(timeout=5)
            except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                if psutil.pid_exists(pid):
                    psutil.Process(pid).kill()
    
    def get_status(self) -> Dict:
        """Get status of all managed processes"""
        status = {}
        
        for name, service_process in self.processes.items():
            # Check if process is still running
            if psutil.pid_exists(service_process.pid):
                try:
                    process = psutil.Process(service_process.pid)
                    cpu_percent = process.cpu_percent()
                    memory_mb = process.memory_info().rss / 1024 / 1024
                    
                    status[name] = {
                        "pid": service_process.pid,
                        "status": "running",
                        "port": service_process.port,
                        "uptime": time.time() - service_process.start_time,
                        "cpu_percent": cpu_percent,
                        "memory_mb": round(memory_mb, 1)
                    }
                except psutil.NoSuchProcess:
                    status[name] = {"status": "not_found"}
            else:
                status[name] = {"status": "stopped"}
        
        return status
    
    def health_check(self) -> bool:
        """Perform health check on all services"""
        all_healthy = True
        
        for name, service_process in self.processes.items():
            if not psutil.pid_exists(service_process.pid):
                print(f"❌ {name} is not running")
                all_healthy = False
            elif service_process.port:
                # Check if port is still being used by the process
                if not self.is_port_in_use(service_process.port):
                    print(f"❌ {name} is not listening on port {service_process.port}")
                    all_healthy = False
        
        return all_healthy 