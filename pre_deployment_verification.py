#!/usr/bin/env python3
"""
Pre-deployment verification script for Digital Ocean deployment.

This script performs comprehensive checks to ensure all fixes are in place
and the configuration is correct before pushing to Git and triggering
automatic deployment to Digital Ocean.
"""

import os
import sys
import yaml
import json
from pathlib import Path
from typing import Dict, List, Tuple

def check_file_exists(filepath: str) -> bool:
    """Check if a file exists."""
    return Path(filepath).exists()

def read_file_content(filepath: str) -> str:
    """Read file content safely."""
    try:
        return Path(filepath).read_text(encoding='utf-8')
    except Exception as e:
        print(f"  ❌ Error reading {filepath}: {e}")
        return ""

def check_backend_dockerfile() -> bool:
    """Verify backend Dockerfile has correct health check configuration."""
    print("🔍 Checking backend Dockerfile...")
    
    if not check_file_exists("backend/Dockerfile"):
        print("  ❌ backend/Dockerfile not found")
        return False
    
    content = read_file_content("backend/Dockerfile")
    
    checks = [
        ("Health check uses 0.0.0.0:8000", "0.0.0.0:8000/health" in content),
        ("Start period is 60 seconds", "start-period=60s" in content),
        ("Curl is available", "curl" in content),
        ("Health check timeout is 30s", "timeout=30s" in content),
    ]
    
    all_passed = True
    for check_name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"  {status} {check_name}")
        if not passed:
            all_passed = False
    
    return all_passed

def check_frontend_dockerfile() -> bool:
    """Verify frontend Dockerfile has correct health check configuration."""
    print("🔍 Checking frontend Dockerfile...")
    
    if not check_file_exists("frontend/Dockerfile"):
        print("  ❌ frontend/Dockerfile not found")
        return False
    
    content = read_file_content("frontend/Dockerfile")
    
    checks = [
        ("Curl is installed", "apk add --no-cache curl" in content),
        ("Start period is 30 seconds", "start-period=30s" in content),
        ("Health check uses /health endpoint", "localhost/health" in content),
        ("Health check timeout is 3s", "timeout=3s" in content),
    ]
    
    all_passed = True
    for check_name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"  {status} {check_name}")
        if not passed:
            all_passed = False
    
    return all_passed

def check_app_yaml() -> bool:
    """Verify app.yaml has correct configuration."""
    print("🔍 Checking app.yaml configuration...")
    
    if not check_file_exists("app.yaml"):
        print("  ❌ app.yaml not found")
        return False
    
    try:
        with open("app.yaml", "r") as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"  ❌ Invalid YAML syntax: {e}")
        return False
    
    checks = []
    all_passed = True
    
    # Check backend service
    backend_service = None
    frontend_service = None
    
    for service in config.get("services", []):
        if service.get("name") == "backend":
            backend_service = service
        elif service.get("name") == "frontend":
            frontend_service = service
    
    if backend_service:
        backend_checks = [
            ("Backend has deploy_on_push enabled", backend_service.get("git", {}).get("deploy_on_push") is True),
            ("Backend has correct repo URL", "Oakhampton1111/customsportal" in backend_service.get("git", {}).get("repo_clone_url", "")),
            ("Backend has correct branch", backend_service.get("git", {}).get("branch") == "master"),
            ("Backend has health check config", "health_check" in backend_service),
            ("Backend health check has initial_delay_seconds", backend_service.get("health_check", {}).get("initial_delay_seconds") == 60),
            ("Backend has HOST environment variable", any(env.get("key") == "HOST" for env in backend_service.get("envs", []))),
            ("Backend has PORT environment variable", any(env.get("key") == "PORT" for env in backend_service.get("envs", []))),
        ]
        checks.extend(backend_checks)
    else:
        checks.append(("Backend service exists", False))
        all_passed = False
    
    if frontend_service:
        frontend_checks = [
            ("Frontend has deploy_on_push enabled", frontend_service.get("git", {}).get("deploy_on_push") is True),
            ("Frontend has correct repo URL", "Oakhampton1111/customsportal" in frontend_service.get("git", {}).get("repo_clone_url", "")),
            ("Frontend has correct branch", frontend_service.get("git", {}).get("branch") == "master"),
        ]
        checks.extend(frontend_checks)
    else:
        checks.append(("Frontend service exists", False))
        all_passed = False
    
    # Check database
    database_checks = [
        ("Database is configured", "databases" in config and len(config["databases"]) > 0),
        ("Database engine is PostgreSQL", config.get("databases", [{}])[0].get("engine") == "PG" if config.get("databases") else False),
    ]
    checks.extend(database_checks)
    
    for check_name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"  {status} {check_name}")
        if not passed:
            all_passed = False
    
    return all_passed

def check_backend_main_py() -> bool:
    """Verify backend main.py has improved health check."""
    print("🔍 Checking backend main.py health check...")
    
    if not check_file_exists("backend/main.py"):
        print("  ❌ backend/main.py not found")
        return False
    
    content = read_file_content("backend/main.py")
    
    checks = [
        ("Health check endpoint exists", "/health" in content and "async def health_check_endpoint" in content),
        ("Graceful database handling", "initializing" in content and "db_status" in content),
        ("Error handling improved", "try:" in content and "except Exception" in content),
    ]
    
    all_passed = True
    for check_name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"  {status} {check_name}")
        if not passed:
            all_passed = False
    
    return all_passed

def check_backend_database_py() -> bool:
    """Verify backend database.py has retry logic."""
    print("🔍 Checking backend database.py retry logic...")
    
    if not check_file_exists("backend/database.py"):
        print("  ❌ backend/database.py not found")
        return False
    
    content = read_file_content("backend/database.py")
    
    checks = [
        ("Asyncio import exists", "import asyncio" in content),
        ("Retry logic implemented", "max_retries" in content and "retry_delay" in content),
        ("Exponential backoff", "retry_delay *= 2" in content),
        ("Graceful startup", "allow the app to start" in content.lower()),
    ]
    
    all_passed = True
    for check_name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"  {status} {check_name}")
        if not passed:
            all_passed = False
    
    return all_passed

def check_git_configuration() -> bool:
    """Check Git configuration and repository status."""
    print("🔍 Checking Git configuration...")
    
    if not check_file_exists(".git"):
        print("  ❌ Not a Git repository")
        return False
    
    # Check if we're on the correct branch
    try:
        import subprocess
        result = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True)
        current_branch = result.stdout.strip()
        
        checks = [
            ("On master branch", current_branch == "master"),
            ("Git repository exists", True),
        ]
        
        # Check for uncommitted changes
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        has_changes = bool(result.stdout.strip())
        checks.append(("Has uncommitted changes (expected)", has_changes))
        
        all_passed = True
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"  {status} {check_name}")
            if check_name != "Has uncommitted changes (expected)" and not passed:
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"  ❌ Error checking Git status: {e}")
        return False

def check_digital_ocean_requirements() -> bool:
    """Check Digital Ocean specific requirements."""
    print("🔍 Checking Digital Ocean requirements...")
    
    checks = [
        ("App spec file exists", check_file_exists("app.yaml")),
        ("Backend Dockerfile exists", check_file_exists("backend/Dockerfile")),
        ("Frontend Dockerfile exists", check_file_exists("frontend/Dockerfile")),
        ("Backend requirements.txt exists", check_file_exists("backend/requirements.txt")),
        ("Frontend package.json exists", check_file_exists("frontend/package.json")),
    ]
    
    all_passed = True
    for check_name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"  {status} {check_name}")
        if not passed:
            all_passed = False
    
    return all_passed

def generate_deployment_summary() -> Dict:
    """Generate a summary of the deployment configuration."""
    summary = {
        "app_name": "customs-broker-portal",
        "services": [],
        "auto_deploy": False,
        "health_checks_configured": False,
        "database_configured": False,
    }
    
    if check_file_exists("app.yaml"):
        try:
            with open("app.yaml", "r") as f:
                config = yaml.safe_load(f)
            
            summary["app_name"] = config.get("name", "unknown")
            
            for service in config.get("services", []):
                service_info = {
                    "name": service.get("name"),
                    "source_dir": service.get("source_dir"),
                    "auto_deploy": service.get("git", {}).get("deploy_on_push", False),
                    "has_health_check": "health_check" in service,
                }
                summary["services"].append(service_info)
            
            summary["auto_deploy"] = all(s["auto_deploy"] for s in summary["services"])
            summary["health_checks_configured"] = all(s["has_health_check"] for s in summary["services"] if s["name"] == "backend")
            summary["database_configured"] = len(config.get("databases", [])) > 0
            
        except Exception as e:
            print(f"Error reading app.yaml: {e}")
    
    return summary

def main():
    """Run all verification checks."""
    print("🚀 Pre-Deployment Verification for Digital Ocean")
    print("=" * 60)
    
    checks = [
        ("Backend Dockerfile", check_backend_dockerfile),
        ("Frontend Dockerfile", check_frontend_dockerfile),
        ("App.yaml Configuration", check_app_yaml),
        ("Backend Main.py", check_backend_main_py),
        ("Backend Database.py", check_backend_database_py),
        ("Git Configuration", check_git_configuration),
        ("Digital Ocean Requirements", check_digital_ocean_requirements),
    ]
    
    results = []
    for check_name, check_func in checks:
        print(f"\n{check_name}:")
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"  ❌ Check failed with exception: {e}")
            results.append((check_name, False))
    
    # Generate deployment summary
    print(f"\n{'='*60}")
    print("📊 Deployment Configuration Summary:")
    summary = generate_deployment_summary()
    
    print(f"  App Name: {summary['app_name']}")
    print(f"  Services: {len(summary['services'])}")
    for service in summary['services']:
        print(f"    - {service['name']}: Auto-deploy={service['auto_deploy']}, Health-check={service['has_health_check']}")
    print(f"  Auto-deploy enabled: {'✅' if summary['auto_deploy'] else '❌'}")
    print(f"  Health checks configured: {'✅' if summary['health_checks_configured'] else '❌'}")
    print(f"  Database configured: {'✅' if summary['database_configured'] else '❌'}")
    
    # Results summary
    print(f"\n{'='*60}")
    print("📋 Verification Results:")
    
    passed = 0
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {check_name}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} checks")
    
    if passed == len(results):
        print("\n🎉 All verification checks passed!")
        print("\n🚀 Ready for Git push and Digital Ocean deployment!")
        print("\nNext steps:")
        print("1. git add .")
        print("2. git commit -m 'Fix: Resolve Digital Ocean health check failures'")
        print("3. git push origin master")
        print("4. Monitor Digital Ocean App Platform for automatic deployment")
        return 0
    else:
        print(f"\n⚠️  {len(results) - passed} check(s) failed.")
        print("Please fix the issues above before pushing to Git.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
