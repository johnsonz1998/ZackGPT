#!/usr/bin/env python3
"""
🧪 ZackGPT Test Suite Runner
Master test runner for comprehensive ZackGPT testing
"""

import subprocess
import sys
import os
import time
import argparse
import requests
from pathlib import Path

# Colors for output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")

def check_backend_running():
    """Check if the backend server is running."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            if health_data.get('status') == 'healthy':
                return True, "Backend is healthy"
            else:
                return False, f"Backend status: {health_data.get('status', 'unknown')}"
        else:
            return False, f"Backend returned status code: {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "Backend server not running"
    except Exception as e:
        return False, f"Backend check failed: {e}"

def install_test_dependencies():
    """Install test dependencies."""
    print_info("Installing test dependencies...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "tests/requirements.txt"
        ], check=True, capture_output=True)
        print_success("Test dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install dependencies: {e}")
        return False

def run_tests(test_path=None, markers=None, verbose=False, coverage=False):
    """Run pytest with specified options."""
    cmd = [sys.executable, "-m", "pytest"]
    
    if test_path:
        cmd.append(test_path)
    
    if markers:
        cmd.extend(["-m", markers])
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=app", "--cov=src", "--cov-report=term-missing"])
    
    # Add configuration file
    cmd.extend(["-c", "tests/pytest.ini"])
    
    try:
        result = subprocess.run(cmd, cwd=Path.cwd())
        return result.returncode == 0
    except Exception as e:
        print_error(f"Failed to run tests: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="ZackGPT Test Suite Runner")
    parser.add_argument("test_path", nargs="?", help="Specific test file or directory to run")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--e2e", action="store_true", help="Run end-to-end tests only")
    parser.add_argument("--performance", action="store_true", help="Run performance tests only")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--backend", action="store_true", help="Run backend tests only")
    parser.add_argument("--frontend", action="store_true", help="Run frontend tests only")
    parser.add_argument("--install-deps", action="store_true", help="Install test dependencies")
    parser.add_argument("--check-backend", action="store_true", help="Check backend status")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    print_header("🧪 ZackGPT Test Suite Runner")
    
    # Install dependencies if requested
    if args.install_deps:
        if not install_test_dependencies():
            sys.exit(1)
        return
    
    # Check backend if requested
    if args.check_backend:
        is_running, message = check_backend_running()
        if is_running:
            print_success(f"Backend check: {message}")
        else:
            print_error(f"Backend check: {message}")
        return
    
    # Determine what tests to run
    test_markers = []
    test_paths = []
    
    # Check if a specific test path was provided
    if args.test_path:
        test_paths.append(args.test_path)
    
    if args.unit:
        test_markers.append("unit")
    elif args.integration:
        test_markers.append("integration")
        # Check if backend is running for integration tests
        is_running, message = check_backend_running()
        if not is_running:
            print_warning(f"Backend not running: {message}")
            print_info("Start backend with: ./server/scripts/start-server.sh")
            print_info("Continuing with non-integration tests...")
            test_markers.append("not integration")
    elif args.e2e:
        test_markers.append("e2e")
    elif args.performance:
        test_markers.append("performance")
    elif args.backend:
        test_paths.append("tests/backend")
    elif args.frontend:
        test_paths.append("tests/frontend")
    elif args.all:
        # Run all tests
        pass
    else:
        # Default: run unit tests and basic integration tests
        print_info("No specific test type specified, running unit and basic tests")
        test_markers.append("unit or not integration")
    
    # Run the tests
    print_header("🚀 Running Tests")
    
    test_path = " ".join(test_paths) if test_paths else None
    markers = " or ".join(test_markers) if test_markers else None
    
    if markers:
        print_info(f"Running tests with markers: {markers}")
    if test_path:
        print_info(f"Running tests from: {test_path}")
    
    start_time = time.time()
    success = run_tests(
        test_path=test_path,
        markers=markers,
        verbose=args.verbose,
        coverage=args.coverage
    )
    end_time = time.time()
    
    print_header("📊 Test Results")
    
    if success:
        print_success(f"All tests passed! ({end_time - start_time:.2f}s)")
        if args.coverage:
            print_info("Coverage report generated in tests/coverage_html/")
    else:
        print_error(f"Some tests failed! ({end_time - start_time:.2f}s)")
        sys.exit(1)

if __name__ == "__main__":
    main() 