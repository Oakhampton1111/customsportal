#!/usr/bin/env python3
"""
Phase 4 Verification Script
Verifies that Phase 4 cleanup has been completed successfully.
"""

import os
import sys
from pathlib import Path

def verify_phase4_completion():
    """Verify Phase 4 cleanup completion."""
    print("=== Phase 4 Cleanup Verification ===")
    
    base_dir = Path(__file__).parent
    results = {
        'legacy_scraper_archived': False,
        'requirements_cleaned': False,
        'backup_created': False,
        'documentation_updated': False
    }
    
    # Check if legacy scraper was archived
    legacy_scraper = base_dir / "abf_tariff_scraper_LEGACY.py"
    original_scraper = base_dir / "abf_tariff_scraper.py"
    
    if legacy_scraper.exists() and not original_scraper.exists():
        results['legacy_scraper_archived'] = True
        print("[OK] Legacy scraper archived: abf_tariff_scraper.py -> abf_tariff_scraper_LEGACY.py")
    else:
        print("[FAIL] Legacy scraper not properly archived")
    
    # Check requirements.txt for removed dependencies
    requirements_file = base_dir / "requirements.txt"
    if requirements_file.exists():
        content = requirements_file.read_text(encoding='utf-8')
        legacy_deps = ['selenium==4.15.2', 'webdriver-manager==4.0.1', 'requests==2.31.0']
        commented_count = sum(1 for dep in legacy_deps if f"# {dep}" in content)
        
        if commented_count == len(legacy_deps):
            results['requirements_cleaned'] = True
            print("[OK] Legacy dependencies commented out in requirements.txt")
        else:
            print(f"[FAIL] Only {commented_count}/{len(legacy_deps)} legacy dependencies commented out")
    else:
        print("[FAIL] requirements.txt not found")
    
    # Check if backup was created
    backup_dir = base_dir / "backups" / "phase4_backup"
    if backup_dir.exists():
        results['backup_created'] = True
        print("[OK] Backup directory created")
    else:
        print("[FAIL] Backup directory not found")
    
    # Check if README was updated
    readme_file = base_dir / "README.md"
    if readme_file.exists():
        content = readme_file.read_text(encoding='utf-8')
        if "Phase 4: Legacy Cleanup and Optimization - COMPLETED" in content:
            results['documentation_updated'] = True
            print("[OK] Documentation updated with Phase 4 completion")
        else:
            print("[FAIL] Documentation not updated")
    
    # Summary
    completed_tasks = sum(results.values())
    total_tasks = len(results)
    
    print(f"\n=== Phase 4 Completion Summary ===")
    print(f"Completed: {completed_tasks}/{total_tasks} tasks")
    
    if completed_tasks == total_tasks:
        print("SUCCESS: Phase 4 cleanup COMPLETED successfully!")
        print("\nBenefits achieved:")
        print("- Clean, optimized codebase")
        print("- Modern Browserless API infrastructure")
        print("- Reduced maintenance overhead")
        print("- Ready for data migration when needed")
        return True
    else:
        print("WARNING: Phase 4 cleanup incomplete")
        return False

if __name__ == "__main__":
    success = verify_phase4_completion()
    sys.exit(0 if success else 1)
