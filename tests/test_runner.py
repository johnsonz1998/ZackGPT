#!/usr/bin/env python3
"""
ZackGPT Comprehensive Test Runner

Organized test suite runner with coverage reporting and categorized test execution.
Supports unit tests, integration tests, performance tests, and more.
"""

import sys
import os
import subprocess
import argparse
import time
from pathlib import Path
from typing import List, Dict, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

class ZackGPTTestRunner:
    """Comprehensive test runner for ZackGPT test suite."""
    
    def __init__(self):
        self.test_root = Path(__file__).parent
        self.project_root = self.test_root.parent
        self.results = {}
        
    def discover_tests(self) -> Dict[str, List[Path]]:
        """Discover all test files organized by category."""
        categories = {
            "unit": [],
            "integration": [],
            "performance": [],
            "e2e": [],
            "frontend": [],
            "manual": []
        }
        
        # Unit tests
        unit_dir = self.test_root / "unit"
        if unit_dir.exists():
            categories["unit"] = list(unit_dir.rglob("test_*.py"))
        
        # Integration tests
        integration_dir = self.test_root / "integration"
        if integration_dir.exists():
            categories["integration"] = list(integration_dir.rglob("test_*.py"))
        
        # Performance tests
        performance_dir = self.test_root / "performance"
        if performance_dir.exists():
            categories["performance"] = list(performance_dir.rglob("test_*.py"))
        
        # E2E tests
        e2e_dir = self.test_root / "e2e"
        if e2e_dir.exists():
            categories["e2e"] = list(e2e_dir.rglob("test_*.py"))
        
        # Frontend tests
        frontend_dir = self.test_root / "frontend"
        if frontend_dir.exists():
            categories["frontend"] = list(frontend_dir.rglob("test_*.py"))
        
        # Manual tests (just count them)
        manual_dir = self.test_root / "manual"
        if manual_dir.exists():
            categories["manual"] = list(manual_dir.rglob("*.html"))
        
        return categories
    
    def run_pytest_category(self, category: str, test_files: List[Path], 
                           coverage: bool = False, verbose: bool = False) -> Dict:
        """Run pytest for a specific test category."""
        print(f"\n{'='*60}")
        print(f"🧪 Running {category.upper()} Tests")
        print(f"{'='*60}")
        
        if not test_files:
            print(f"⚠️ No {category} tests found")
            return {"status": "skipped", "count": 0, "duration": 0}
        
        # Build pytest command
        cmd = ["python3", "-m", "pytest"]
        
        if verbose:
            cmd.append("-v")
        else:
            cmd.append("-q")
        
        if coverage:
            cmd.extend([
                "--cov=src/zackgpt",
                f"--cov-report=term-missing",
                f"--cov-report=html:tests/results/coverage_{category}",
            ])
        
        # Add test files
        cmd.extend([str(f) for f in test_files])
        
        print(f"📂 Found {len(test_files)} test files")
        print(f"🚀 Running: {' '.join(cmd)}")
        
        start_time = time.time()
        
        try:
            # Change to project root for proper imports
            result = subprocess.run(
                cmd, 
                cwd=self.project_root,
                capture_output=True, 
                text=True,
                timeout=300  # 5 minute timeout per category
            )
            
            duration = time.time() - start_time
            
            print(f"\n📊 {category.upper()} Results:")
            print(f"   Exit Code: {result.returncode}")
            print(f"   Duration: {duration:.2f}s")
            
            if result.stdout:
                print("\n📋 Output:")
                print(result.stdout)
            
            if result.stderr and result.returncode != 0:
                print("\n❌ Errors:")
                print(result.stderr)
            
            return {
                "status": "passed" if result.returncode == 0 else "failed",
                "exit_code": result.returncode,
                "duration": duration,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        except subprocess.TimeoutExpired:
            print(f"⏰ {category} tests timed out after 5 minutes")
            return {"status": "timeout", "duration": 300}
        
        except Exception as e:
            print(f"💥 Error running {category} tests: {e}")
            return {"status": "error", "error": str(e)}
    
    def run_direct_test(self, test_file: Path) -> Dict:
        """Run a test file directly (for non-pytest tests)."""
        print(f"\n🎯 Running direct test: {test_file.name}")
        
        try:
            start_time = time.time()
            result = subprocess.run(
                [sys.executable, str(test_file)],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=120
            )
            duration = time.time() - start_time
            
            print(f"   Exit Code: {result.returncode}")
            print(f"   Duration: {duration:.2f}s")
            
            if result.stdout:
                print("   Output:", result.stdout[:200] + "..." if len(result.stdout) > 200 else result.stdout)
            
            return {
                "status": "passed" if result.returncode == 0 else "failed",
                "exit_code": result.returncode,
                "duration": duration
            }
            
        except Exception as e:
            print(f"   Error: {e}")
            return {"status": "error", "error": str(e)}
    
    def check_environment(self):
        """Check that required dependencies are available."""
        print("🔧 Checking Test Environment...")
        
        missing_deps = []
        
        try:
            import pytest
            print("✅ pytest available")
        except ImportError:
            missing_deps.append("pytest")
        
        try:
            import pytest_cov
            print("✅ pytest-cov available")
        except ImportError:
            missing_deps.append("pytest-cov")
        
        if missing_deps:
            print(f"❌ Missing dependencies: {', '.join(missing_deps)}")
            print("   Install with: pip install pytest pytest-cov")
            return False
        
        # Check that src directory exists
        if not (self.project_root / "src").exists():
            print("❌ src directory not found")
            return False
        
        print("✅ Environment ready")
        return True
    
    def generate_summary_report(self):
        """Generate a summary report of all test results."""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("="*80)
        
        total_duration = 0
        total_categories = 0
        passed_categories = 0
        
        for category, result in self.results.items():
            total_categories += 1
            total_duration += result.get("duration", 0)
            
            status = result.get("status", "unknown")
            if status == "passed":
                passed_categories += 1
                emoji = "✅"
            elif status == "failed":
                emoji = "❌"
            elif status == "timeout":
                emoji = "⏰"
            elif status == "skipped":
                emoji = "⏭️"
            else:
                emoji = "❓"
            
            print(f"{emoji} {category.upper()}: {status}")
            if "duration" in result:
                print(f"   Duration: {result['duration']:.2f}s")
        
        print(f"\nOverall: {passed_categories}/{total_categories} categories passed")
        print(f"Total Duration: {total_duration:.2f}s")
        
        # Save detailed results
        results_file = self.test_root / "results" / "test_summary.json"
        results_file.parent.mkdir(exist_ok=True)
        
        import json
        with open(results_file, 'w') as f:
            json.dump({
                "summary": {
                    "total_categories": total_categories,
                    "passed_categories": passed_categories,
                    "total_duration": total_duration,
                    "timestamp": time.time()
                },
                "detailed_results": self.results
            }, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: {results_file}")
        
        return passed_categories == total_categories
    
    def run_all_tests(self, coverage: bool = False, verbose: bool = False, 
                     categories: Optional[List[str]] = None):
        """Run all tests or specific categories."""
        if not self.check_environment():
            return False
        
        print("🚀 Starting ZackGPT Comprehensive Test Suite")
        print(f"📁 Test Root: {self.test_root}")
        print(f"🏠 Project Root: {self.project_root}")
        
        # Discover tests
        discovered = self.discover_tests()
        
        # Filter categories if specified
        if categories:
            discovered = {k: v for k, v in discovered.items() if k in categories}
        
        # Run each category
        for category, test_files in discovered.items():
            if category == "manual":
                print(f"\n📖 Manual tests found: {len(test_files)} files")
                print("   These require manual execution (HTML files)")
                self.results[category] = {"status": "manual", "count": len(test_files)}
                continue
            
            self.results[category] = self.run_pytest_category(
                category, test_files, coverage=coverage, verbose=verbose
            )
        
        # Generate summary
        return self.generate_summary_report()

def main():
    """Main entry point for test runner."""
    parser = argparse.ArgumentParser(description="ZackGPT Comprehensive Test Runner")
    
    parser.add_argument("--coverage", "-c", action="store_true", 
                       help="Generate coverage reports")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    parser.add_argument("--categories", nargs="+", 
                       choices=["unit", "integration", "performance", "e2e", "frontend"],
                       help="Run specific test categories")
    parser.add_argument("--list", action="store_true",
                       help="List available tests without running")
    
    args = parser.parse_args()
    
    runner = ZackGPTTestRunner()
    
    if args.list:
        print("🧪 ZackGPT Test Suite Discovery")
        print("="*40)
        discovered = runner.discover_tests()
        for category, files in discovered.items():
            print(f"\n{category.upper()}: {len(files)} files")
            for f in files[:5]:  # Show first 5
                print(f"  • {f.name}")
            if len(files) > 5:
                print(f"  ... and {len(files) - 5} more")
        return
    
    success = runner.run_all_tests(
        coverage=args.coverage,
        verbose=args.verbose,
        categories=args.categories
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 