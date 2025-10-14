#!/usr/bin/env python3
"""
Test script to verify Satoshi's Arcade MCP is ready for deployment
"""
import subprocess
import sys
import os
import requests
import time
import threading

def test_imports():
    """Test that all modules can be imported"""
    print("Testing module imports...")
    
    try:
        import api.main
        print("✅ api.main imported successfully")
    except Exception as e:
        print(f"❌ api.main import failed: {e}")
        return False
    
    try:
        import database
        print("✅ database imported successfully")
    except Exception as e:
        print(f"❌ database import failed: {e}")
        return False
    
    try:
        import ai.difficulty_agent
        print("✅ ai.difficulty_agent imported successfully")
    except Exception as e:
        print(f"❌ ai.difficulty_agent import failed: {e}")
        return False
    
    return True

def test_server_startup():
    """Test that the server can start"""
    print("\nTesting server startup...")
    
    try:
        # Start server in background
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "api.main:app", 
            "--host", "127.0.0.1", 
            "--port", "8005"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        time.sleep(3)
        
        # Test health endpoint
        try:
            response = requests.get("http://127.0.0.1:8005/health", timeout=5)
            if response.status_code == 200:
                print("✅ Health check passed")
                health_data = response.json()
                print(f"   Status: {health_data.get('status')}")
                print(f"   Games: {health_data.get('games')}")
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
        
        # Test main page
        try:
            response = requests.get("http://127.0.0.1:8005/", timeout=5)
            if response.status_code == 200:
                print("✅ Main page loads successfully")
            else:
                print(f"❌ Main page failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Main page error: {e}")
            return False
        
        # Stop server
        process.terminate()
        process.wait()
        
        return True
        
    except Exception as e:
        print(f"❌ Server startup test failed: {e}")
        return False

def test_file_structure():
    """Test that all required files exist"""
    print("\nTesting file structure...")
    
    required_files = [
        "requirements.txt",
        "render.yaml",
        "api/main.py",
        "database.py",
        "ai/difficulty_agent.py",
        "frontend/arcade/index.html",
        "frontend/pingpong/index.html",
        "frontend/tetris/index.html"
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            all_exist = False
    
    return all_exist

def main():
    print("🧪 Testing Satoshi's Arcade MCP for deployment")
    print("=" * 50)
    
    # Test file structure
    if not test_file_structure():
        print("\n❌ File structure test failed")
        return False
    
    # Test imports
    if not test_imports():
        print("\n❌ Import test failed")
        return False
    
    # Test server startup
    if not test_server_startup():
        print("\n❌ Server startup test failed")
        return False
    
    print("\n🎉 All tests passed! Ready for deployment!")
    print("\nNext steps:")
    print("1. Go to https://dashboard.render.com")
    print("2. Create new Web Service")
    print("3. Connect GitHub repository: polydeuces32/satoshis-arcade-mcp")
    print("4. Use the settings from DEPLOYMENT_GUIDE.md")
    print("5. Deploy and enjoy your live arcade!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
