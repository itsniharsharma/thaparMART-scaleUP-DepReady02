#!/usr/bin/env python3
"""
Fix Frontend Dependencies
Run this if you're having yarn/npm issues
"""

import os
import subprocess
import shutil
from pathlib import Path

def fix_frontend_dependencies():
    print("🔧 Fixing frontend dependencies...")
    
    frontend_dir = Path("frontend")
    
    # Remove problematic files
    files_to_remove = [
        frontend_dir / "yarn.lock",
        frontend_dir / "package-lock.json", 
        frontend_dir / "node_modules"
    ]
    
    for file_path in files_to_remove:
        if file_path.exists():
            print(f"🗑️  Removing {file_path}")
            if file_path.is_dir():
                shutil.rmtree(file_path)
            else:
                file_path.unlink()
    
    print("✅ Cleaned up frontend dependencies")
    print("Now run: python deploy_local.py")

if __name__ == "__main__":
    fix_frontend_dependencies()