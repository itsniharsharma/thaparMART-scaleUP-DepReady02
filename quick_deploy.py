#!/usr/bin/env python3
"""
Thapar Marketplace - Quick Deploy Menu
Choose between Local or Production deployment
"""

import sys
import subprocess
from pathlib import Path

def print_menu():
    print("=" * 60)
    print("🚀 THAPAR MARKETPLACE - DEPLOYMENT MENU")
    print("=" * 60)
    print()
    print("Choose your deployment option:")
    print()
    print("1. 🏠 Local Development Deployment")
    print("   - Perfect for development and testing")
    print("   - Runs on localhost")
    print("   - Uses demo API keys")
    print("   - Hot reload enabled")
    print()
    print("2. 🏭 Production Deployment")
    print("   - Production-ready deployment")
    print("   - Requires your real API keys")
    print("   - Optimized for performance")
    print("   - Includes backup scripts")
    print()
    print("3. ❌ Exit")
    print()

def run_local_deployment():
    print("\n🏠 Starting Local Deployment...")
    try:
        subprocess.run([sys.executable, "deploy_local.py"], check=True)
    except subprocess.CalledProcessError:
        print("❌ Local deployment failed!")
        sys.exit(1)

def run_production_deployment():
    print("\n🏭 Starting Production Deployment...")
    try:
        subprocess.run([sys.executable, "deploy_production.py"], check=True)
    except subprocess.CalledProcessError:
        print("❌ Production deployment failed!")
        sys.exit(1)

def main():
    while True:
        print_menu()
        try:
            choice = input("Enter your choice (1-3): ").strip()
            
            if choice == '1':
                run_local_deployment()
                break
            elif choice == '2':
                run_production_deployment()
                break
            elif choice == '3':
                print("\n👋 Goodbye!")
                sys.exit(0)
            else:
                print("\n❌ Invalid choice! Please enter 1, 2, or 3.")
                input("Press Enter to continue...")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Error: {e}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()