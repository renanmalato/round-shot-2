#!/usr/bin/env python3
"""
Demo script for Screenshot Rounder
Creates a sample image to test the rounded corners functionality
"""

import sys
from pathlib import Path
from PIL import Image, ImageDraw
import time

def create_demo_screenshot():
    """Create a demo screenshot image"""
    width, height = 1200, 800
    
    # Create a sample screenshot-like image
    img = Image.new('RGB', (width, height), '#f0f0f0')
    draw = ImageDraw.Draw(img)
    
    # Draw some sample content
    draw.rectangle([50, 50, width-50, height-50], fill='#ffffff', outline='#cccccc', width=2)
    draw.rectangle([100, 100, width-100, 200], fill='#007AFF')
    draw.rectangle([100, 250, width-100, 350], fill='#34C759')
    draw.rectangle([100, 400, width-100, 500], fill='#FF9500')
    
    # Add some text areas
    draw.rectangle([100, 550, width-100, 650], fill='#F2F2F7', outline='#D1D1D6')
    draw.rectangle([100, 680, width-100, height-100], fill='#F2F2F7', outline='#D1D1D6')
    
    # Save as demo screenshot
    demo_path = Path.cwd() / 'Demo_Screenshot.png'
    img.save(demo_path, 'PNG')
    
    print(f"✅ Demo screenshot created: {demo_path}")
    return demo_path

def test_processing():
    """Test the screenshot processing"""
    try:
        from screenshot_rounder import ScreenshotRounder
        
        print("🔄 Testing Screenshot Rounder...")
        
        # Create demo image
        demo_file = create_demo_screenshot()
        
        # Process it
        app = ScreenshotRounder()
        success = app.process_single_file(str(demo_file))
        
        if success:
            print("🎉 Demo processing completed successfully!")
            print("📁 Check the output folder for the rounded version")
            print("📋 The processed image should also be in your clipboard")
        else:
            print("❌ Demo processing failed")
            
        return success
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        return False

def main():
    """Main demo function"""
    print("🎯 Screenshot Rounder Demo")
    print("=" * 50)
    
    if "--create-only" in sys.argv:
        create_demo_screenshot()
        return
    
    success = test_processing()
    
    if success:
        print("\n📋 Next steps:")
        print("1. Take a real screenshot (Cmd+Shift+3 or Cmd+Shift+4)")
        print("2. Run: python3 screenshot_rounder.py")
        print("3. Your screenshots will be automatically processed!")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()