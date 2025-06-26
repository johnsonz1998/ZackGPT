#!/usr/bin/env python3
"""
ZackGPT OpenAI Configuration Diagnostic Script

Tests OpenAI configuration and provides detailed diagnostics for any issues.
Use this script to verify setup and troubleshoot problems.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root))  # For config module

def check_environment():
    """Check environment and dependencies."""
    print("🔍 Environment Check")
    print("=" * 20)
    
    # Check Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"Python Version: {python_version}")
    
    # Check for .env file
    env_file = project_root / ".env"
    if env_file.exists():
        print("✅ .env file found")
    else:
        print("⚠️ .env file not found - create one with OPENAI_API_KEY")
    
    # Load environment
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment variables loaded")
    except ImportError:
        print("❌ python-dotenv not installed: pip install python-dotenv")
        return False
    
    return True

def check_openai_library():
    """Check OpenAI library installation and version."""
    print("\n📚 OpenAI Library Check")
    print("=" * 25)
    
    try:
        import openai
        print(f"✅ OpenAI library version: {openai.__version__}")
        
        # Check if version is compatible
        version_parts = openai.__version__.split('.')
        major_version = int(version_parts[0])
        
        if major_version >= 1:
            print("✅ OpenAI library version is compatible")
            return True
        else:
            print(f"⚠️ OpenAI library version {openai.__version__} may be outdated")
            print("💡 Update with: pip install --upgrade openai")
            return False
            
    except ImportError:
        print("❌ OpenAI library not installed")
        print("💡 Install with: pip install openai")
        return False

def check_api_key():
    """Check API key configuration."""
    print("\n🔑 API Key Check")
    print("=" * 17)
    
    api_key = os.environ.get('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment")
        print("💡 Add to .env file: OPENAI_API_KEY=your_key_here")
        return False
    
    if api_key.startswith('test_'):
        print("⚠️ Using test API key - won't work for real requests")
        return False
    
    if not api_key.startswith('sk-'):
        print("⚠️ API key doesn't start with 'sk-' - may be invalid")
        return False
    
    print(f"✅ API key found: {api_key[:8]}...{api_key[-4:]} (length: {len(api_key)})")
    return True

def check_openai_client():
    """Test OpenAI client creation."""
    print("\n🤖 OpenAI Client Test")
    print("=" * 21)
    
    try:
        from openai import OpenAI
        
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            print("❌ Cannot test client - no API key")
            return False
        
        # Test client creation
        client = OpenAI(api_key=api_key)
        print("✅ OpenAI client created successfully")
        
        # Test basic client properties
        if hasattr(client, 'chat'):
            print("✅ Client has chat API")
        else:
            print("⚠️ Client missing chat API")
        
        return True
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ OpenAI client creation failed: {error_msg}")
        
        # Provide specific guidance
        if "proxies" in error_msg:
            print("💡 Fix: Update OpenAI library with: pip install --upgrade openai")
        elif "api_key" in error_msg.lower():
            print("💡 Fix: Check your OPENAI_API_KEY in .env file")
        elif "network" in error_msg.lower() or "connection" in error_msg.lower():
            print("💡 Fix: Check your internet connection")
        else:
            print("💡 Fix: Check OpenAI library version and dependencies")
        
        return False

def test_zackgpt_integration():
    """Test ZackGPT integration with OpenAI."""
    print("\n🧠 ZackGPT Integration Test")
    print("=" * 28)
    
    try:
        from zackgpt.core.core_assistant import CoreAssistant
        
        assistant = CoreAssistant()
        print("✅ CoreAssistant initialized")
        
        if assistant.client is None:
            print("❌ CoreAssistant has no OpenAI client")
            return False
        
        print("✅ CoreAssistant has active OpenAI client")
        
        # Test simple interaction (if we have a valid API key)
        api_key = os.environ.get('OPENAI_API_KEY', '')
        if api_key and not api_key.startswith('test_'):
            try:
                response = assistant.process_input("Hello, this is a test")
                print(f"✅ Test response generated: {response[:50]}...")
                return True
            except Exception as e:
                print(f"⚠️ Test response failed: {e}")
                return False
        else:
            print("⚠️ Skipping API test - no valid API key")
            return True
        
    except Exception as e:
        print(f"❌ ZackGPT integration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_intelligence_components():
    """Test intelligence amplification components."""
    print("\n🧬 Intelligence Components Test")
    print("=" * 32)
    
    try:
        from zackgpt.core.intelligence_amplifier import (
            ContextualIntelligenceAmplifier,
            IntelligentContextCompressor,
            PersonalityEmergenceEngine,
            DynamicTokenAllocator
        )
        
        # Test each component
        amplifier = ContextualIntelligenceAmplifier()
        print("✅ ContextualIntelligenceAmplifier")
        
        compressor = IntelligentContextCompressor()
        print("✅ IntelligentContextCompressor")
        
        personality = PersonalityEmergenceEngine()
        print("✅ PersonalityEmergenceEngine")
        
        allocator = DynamicTokenAllocator()
        print("✅ DynamicTokenAllocator")
        
        # Test basic functionality
        context = amplifier.analyze_conversation_context(
            [{"role": "user", "content": "Hello"}], 
            "Hello"
        )
        print(f"✅ Intelligence analysis working: {context['conversation_type']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Intelligence components failed: {e}")
        return False

def run_comprehensive_test():
    """Run comprehensive diagnostic test."""
    print("🔬 ZackGPT OpenAI Configuration Diagnostic")
    print("=" * 44)
    print()
    
    tests = [
        ("Environment Setup", check_environment),
        ("OpenAI Library", check_openai_library),
        ("API Key Configuration", check_api_key),
        ("OpenAI Client Creation", check_openai_client),
        ("ZackGPT Integration", test_zackgpt_integration),
        ("Intelligence Components", test_intelligence_components)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 44)
    print("📊 Diagnostic Summary")
    print("=" * 44)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! ZackGPT is ready to use.")
    else:
        print(f"\n⚠️ {total - passed} tests failed. Review the failures above.")
        print("\n📋 Quick fixes:")
        print("• Update OpenAI: pip install --upgrade openai")
        print("• Check .env file has valid OPENAI_API_KEY")
        print("• Verify internet connection")
    
    return passed == total

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1) 