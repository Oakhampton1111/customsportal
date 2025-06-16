#!/usr/bin/env python3
"""
Test script to validate deployment fixes locally before Digital Ocean deployment.

This script tests the key components that were causing health check failures.
"""

import asyncio
import subprocess
import sys
import time
import requests
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=cwd,
            timeout=60
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"

def test_docker_builds():
    """Test that both Docker containers build successfully."""
    print("🔨 Testing Docker builds...")
    
    # Test backend build
    print("  Building backend container...")
    success, stdout, stderr = run_command("docker build -t test-backend .", cwd="backend")
    if not success:
        print(f"  ❌ Backend build failed: {stderr}")
        return False
    print("  ✅ Backend build successful")
    
    # Test frontend build
    print("  Building frontend container...")
    success, stdout, stderr = run_command("docker build -t test-frontend .", cwd="frontend")
    if not success:
        print(f"  ❌ Frontend build failed: {stderr}")
        return False
    print("  ✅ Frontend build successful")
    
    return True

def test_backend_health_check():
    """Test backend health check endpoint."""
    print("🏥 Testing backend health check...")
    
    # Start backend container
    print("  Starting backend container...")
    success, stdout, stderr = run_command(
        "docker run -d --name test-backend -p 8000:8000 "
        "-e DATABASE_URL=sqlite+aiosqlite:///./test.db "
        "-e ENVIRONMENT=development "
        "test-backend"
    )
    
    if not success:
        print(f"  ❌ Failed to start backend: {stderr}")
        return False
    
    try:
        # Wait for container to start
        print("  Waiting for backend to start...")
        time.sleep(10)
        
        # Test health endpoint
        print("  Testing health endpoint...")
        try:
            response = requests.get("http://localhost:8000/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                print(f"  ✅ Health check successful: {health_data.get('status', 'unknown')}")
                return True
            else:
                print(f"  ❌ Health check failed with status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Health check request failed: {e}")
            return False
            
    finally:
        # Cleanup
        run_command("docker stop test-backend")
        run_command("docker rm test-backend")

def test_frontend_health_check():
    """Test frontend health check endpoint."""
    print("🌐 Testing frontend health check...")
    
    # Start frontend container
    print("  Starting frontend container...")
    success, stdout, stderr = run_command(
        "docker run -d --name test-frontend -p 80:80 test-frontend"
    )
    
    if not success:
        print(f"  ❌ Failed to start frontend: {stderr}")
        return False
    
    try:
        # Wait for container to start
        print("  Waiting for frontend to start...")
        time.sleep(5)
        
        # Test health endpoint
        print("  Testing health endpoint...")
        try:
            response = requests.get("http://localhost/health", timeout=10)
            if response.status_code == 200:
                print("  ✅ Frontend health check successful")
                return True
            else:
                print(f"  ❌ Frontend health check failed with status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Frontend health check request failed: {e}")
            return False
            
    finally:
        # Cleanup
        run_command("docker stop test-frontend")
        run_command("docker rm test-frontend")

def test_app_yaml_syntax():
    """Test that app.yaml has valid syntax."""
    print("📄 Testing app.yaml syntax...")
    
    try:
        import yaml
        with open("app.yaml", "r") as f:
            yaml.safe_load(f)
        print("  ✅ app.yaml syntax is valid")
        return True
    except yaml.YAMLError as e:
        print(f"  ❌ app.yaml syntax error: {e}")
        return False
    except ImportError:
        print("  ⚠️  PyYAML not installed, skipping syntax check")
        return True

def test_dockerfile_health_checks():
    """Test that Dockerfiles have proper health check syntax."""
    print("🔍 Testing Dockerfile health checks...")
    
    # Check backend Dockerfile
    backend_dockerfile = Path("backend/Dockerfile").read_text()
    if "0.0.0.0:8000/health" in backend_dockerfile and "start-period=60s" in backend_dockerfile:
        print("  ✅ Backend Dockerfile health check looks correct")
        backend_ok = True
    else:
        print("  ❌ Backend Dockerfile health check issues detected")
        backend_ok = False
    
    # Check frontend Dockerfile
    frontend_dockerfile = Path("frontend/Dockerfile").read_text()
    if "apk add --no-cache curl" in frontend_dockerfile and "start-period=30s" in frontend_dockerfile:
        print("  ✅ Frontend Dockerfile health check looks correct")
        frontend_ok = True
    else:
        print("  ❌ Frontend Dockerfile health check issues detected")
        frontend_ok = False
    
    return backend_ok and frontend_ok

def main():
    """Run all tests."""
    print("🚀 Testing Digital Ocean Deployment Fixes")
    print("=" * 50)
    
    tests = [
        ("Dockerfile Health Checks", test_dockerfile_health_checks),
        ("App.yaml Syntax", test_app_yaml_syntax),
        ("Docker Builds", test_docker_builds),
        ("Backend Health Check", test_backend_health_check),
        ("Frontend Health Check", test_frontend_health_check),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} tests")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Ready for Digital Ocean deployment.")
        return 0
    else:
        print(f"\n⚠️  {len(results) - passed} test(s) failed. Please fix issues before deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
