#!/usr/bin/env python3
"""
Launch Agent Creator for Screenshot Rounder
Creates a macOS LaunchAgent to run Screenshot Rounder automatically at startup
"""

import os
import sys
from pathlib import Path
import json


def create_launch_agent():
    """Create macOS LaunchAgent plist file"""
    
    # Get current directory and script path
    current_dir = Path.cwd().resolve()
    script_path = current_dir / "screenshot_rounder.py"
    config_path = current_dir / "config.json"
    
    if not script_path.exists():
        print(f"❌ Script not found: {script_path}")
        return False
        
    if not config_path.exists():
        print(f"❌ Config not found: {config_path}")
        return False
    
    # LaunchAgent directory
    launch_agents_dir = Path.home() / "Library" / "LaunchAgents"
    launch_agents_dir.mkdir(exist_ok=True)
    
    plist_file = launch_agents_dir / "com.screenshotrounder.agent.plist"
    
    # Create plist content
    plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.screenshotrounder.agent</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>{current_dir}/venv/bin/python3</string>
        <string>{script_path}</string>
        <string>--config</string>
        <string>{config_path}</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>{current_dir}</string>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <true/>
    
    <key>StandardOutPath</key>
    <string>{Path.home()}/.screenshot_rounder/logs/launchd_stdout.log</string>
    
    <key>StandardErrorPath</key>
    <string>{Path.home()}/.screenshot_rounder/logs/launchd_stderr.log</string>
    
    <key>ProcessType</key>
    <string>Background</string>
    
    <key>LowPriorityIO</key>
    <true/>
    
    <key>Nice</key>
    <integer>1</integer>
</dict>
</plist>'''
    
    # Write plist file
    try:
        with open(plist_file, 'w') as f:
            f.write(plist_content)
        
        print(f"✅ LaunchAgent created: {plist_file}")
        
        # Load the launch agent
        import subprocess
        result = subprocess.run(
            ["launchctl", "load", "-w", str(plist_file)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ LaunchAgent loaded successfully")
            print(f"🎯 Screenshot Rounder will now start automatically at login")
            
            # Start it now
            start_result = subprocess.run(
                ["launchctl", "start", "com.screenshotrounder.agent"],
                capture_output=True,
                text=True
            )
            
            if start_result.returncode == 0:
                print(f"✅ Screenshot Rounder started")
            else:
                print(f"⚠️  Could not start now, but will start at next login")
                
        else:
            print(f"❌ Failed to load LaunchAgent: {result.stderr}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error creating LaunchAgent: {e}")
        return False


def remove_launch_agent():
    """Remove the LaunchAgent"""
    launch_agents_dir = Path.home() / "Library" / "LaunchAgents"
    plist_file = launch_agents_dir / "com.screenshotrounder.agent.plist"
    
    if not plist_file.exists():
        print(f"⚠️  LaunchAgent not found: {plist_file}")
        return True
    
    try:
        import subprocess
        
        # Unload the agent
        result = subprocess.run(
            ["launchctl", "unload", "-w", str(plist_file)],
            capture_output=True,
            text=True
        )
        
        # Remove the file
        plist_file.unlink()
        
        print(f"✅ LaunchAgent removed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error removing LaunchAgent: {e}")
        return False


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Launch Agent Manager for Screenshot Rounder')
    parser.add_argument('action', choices=['install', 'remove', 'status'], 
                       help='Action to perform')
    
    args = parser.parse_args()
    
    if args.action == 'install':
        success = create_launch_agent()
        if success:
            print("\n📋 Launch Agent installed successfully!")
            print("🎯 Screenshot Rounder will now run automatically at startup")
            print("📸 Take a screenshot to test it!")
        sys.exit(0 if success else 1)
        
    elif args.action == 'remove':
        success = remove_launch_agent()
        if success:
            print("\n✅ Launch Agent removed successfully")
            print("🔄 Screenshot Rounder will no longer start automatically")
        sys.exit(0 if success else 1)
        
    elif args.action == 'status':
        launch_agents_dir = Path.home() / "Library" / "LaunchAgents"
        plist_file = launch_agents_dir / "com.screenshotrounder.agent.plist"
        
        if plist_file.exists():
            print("✅ Launch Agent is installed")
            
            # Check if it's loaded
            import subprocess
            result = subprocess.run(
                ["launchctl", "list", "com.screenshotrounder.agent"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ Launch Agent is loaded and running")
            else:
                print("⚠️  Launch Agent is installed but not loaded")
        else:
            print("❌ Launch Agent is not installed")


if __name__ == "__main__":
    main()