#!/usr/bin/env python3
"""
Setup script for Screenshot Rounder
Creates necessary directories and installs dependencies
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} failed: {e}")
        return False


def main():
    """Main setup function"""
    print("🚀 Setting up Screenshot Rounder...")
    
    # Create necessary directories
    home = Path.home()
    app_dir = home / '.screenshot_rounder'
    logs_dir = app_dir / 'logs'
    
    print(f"📁 Creating directories...")
    app_dir.mkdir(exist_ok=True)
    logs_dir.mkdir(exist_ok=True)
    print(f"✅ Directories created: {app_dir}")
    
    # Install Python dependencies
    print(f"🔄 Installing Python dependencies...")
    
    # Try different installation methods
    install_commands = [
        "pip3 install --user -r requirements.txt",
        "python3 -m pip install --user -r requirements.txt",
        "pip3 install --break-system-packages -r requirements.txt"
    ]
    
    success = False
    for cmd in install_commands:
        print(f"🔄 Trying: {cmd}")
        if run_command(cmd, f"Installing with: {cmd.split()[0]}"):
            success = True
            break
        print(f"⚠️  Command failed, trying next method...")
    
    if not success:
        print("❌ Failed to install dependencies automatically.")
        print("📋 Please install manually using one of these commands:")
        print("   pip3 install --user -r requirements.txt")
        print("   OR create a virtual environment:")
        print("   python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt")
        return False
    
    # Make script executable
    if not run_command("chmod +x screenshot_rounder.py", "Making script executable"):
        print("⚠️  Could not make script executable, but continuing...")
    
    # Test the setup
    if not run_command("python3 screenshot_rounder.py --test", "Testing setup"):
        print("❌ Setup test failed")
        return False
    
    print("🎉 Screenshot Rounder setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Run: python3 screenshot_rounder.py")
    print("2. Take a screenshot (Cmd+Shift+3 or Cmd+Shift+4)")
    print("3. Check your Desktop/rounded_screenshots folder")
    print("4. The processed image should also be in your clipboard!")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)