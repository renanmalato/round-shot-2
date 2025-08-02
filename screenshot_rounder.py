#!/usr/bin/env python3
"""
Screenshot Rounder - Automatically adds rounded corners to screenshots
Author: Generated for presentation use
Description: Monitors screenshot folder and automatically applies rounded corners
"""

import os
import sys
import json
import time
import logging
import tempfile
from pathlib import Path
from typing import Optional, Tuple
import fnmatch
from datetime import datetime
import threading

# Third-party imports
from PIL import Image, ImageDraw
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
try:
    import AppKit
    from AppKit import NSPasteboard, NSPasteboardTypePNG
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False
    print("⚠️  Clipboard functionality not available. Install pyobjc-framework-Cocoa for clipboard support.")


# ------------------------------------------------- #
#                                                   #
#                                                   #
#             Configuration & Setup                 #
#                                                   #
#                                                   #
# ------------------------------------------------- #

class ScreenshotRounderConfig:
    """Configuration manager for Screenshot Rounder"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.setup_logging()
        
    def load_config(self) -> dict:
        """Load configuration from JSON file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                print(f"✅ Configuration loaded from {self.config_file}")
                return config
            else:
                print(f"⚠️  Config file {self.config_file} not found, using defaults")
                return self.get_default_config()
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            return self.get_default_config()
    
    def get_default_config(self) -> dict:
        """Return default configuration"""
        return {
            "screenshot_folder": "~/Desktop",
            "output_folder": "~/Desktop/rounded_screenshots",
            "corner_radius": 20,
            "corner_radius_percentage": 0.05,
            "use_percentage": True,
            "auto_copy_to_clipboard": True,
            "replace_original": False,
            "monitor_enabled": True,
            "log_level": "INFO",
            "file_patterns": ["Screenshot*.png", "CleanShot*.png", "Screen Shot*.png"],
            "processing_delay": 0.5
        }
    
    def setup_logging(self):
        """Setup comprehensive logging"""
        log_level = getattr(logging, self.config.get('log_level', 'INFO').upper())
        
        # Create logs directory
        log_dir = Path.home() / '.screenshot_rounder' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup file handler
        log_file = log_dir / f"screenshot_rounder_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Configure logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"🚀 Screenshot Rounder initialized - Log Level: {self.config.get('log_level', 'INFO')}")
        self.logger.info(f"📁 Log file: {log_file}")
        
    def get_expanded_path(self, path: str) -> Path:
        """Expand user path and return Path object"""
        return Path(path).expanduser().resolve()


# ------------------------------------------------- #
#                                                   #
#                                                   #
#            Image Processing Core                   #
#                                                   #
#                                                   #
# ------------------------------------------------- #

class ImageProcessor:
    """Handles all image processing operations"""
    
    def __init__(self, config: ScreenshotRounderConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def calculate_corner_radius(self, image_size: Tuple[int, int]) -> int:
        """Calculate corner radius based on configuration"""
        width, height = image_size
        
        if self.config.config.get('use_percentage', True):
            # Use percentage of smallest dimension
            min_dimension = min(width, height)
            radius = int(min_dimension * self.config.config.get('corner_radius_percentage', 0.05))
            self.logger.debug(f"📐 Calculated radius from percentage: {radius}px (min_dim: {min_dimension}px, percentage: {self.config.config.get('corner_radius_percentage', 0.05)})")
        else:
            # Use fixed pixel value
            radius = self.config.config.get('corner_radius', 20)
            self.logger.debug(f"📐 Using fixed radius: {radius}px")
            
        return max(1, radius)  # Ensure minimum radius of 1
    
    def create_rounded_mask(self, size: Tuple[int, int], radius: int) -> Image.Image:
        """Create a rounded rectangle mask"""
        width, height = size
        self.logger.debug(f"🎭 Creating rounded mask: {width}x{height} with radius {radius}px")
        
        # Create mask with rounded corners
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        
        # Draw rounded rectangle
        draw.rounded_rectangle(
            [(0, 0), (width - 1, height - 1)],
            radius=radius,
            fill=255
        )
        
        self.logger.debug(f"✅ Rounded mask created successfully")
        return mask
    
    def apply_rounded_corners(self, image_path: Path) -> Optional[Path]:
        """Apply rounded corners to an image"""
        try:
            self.logger.info(f"🔄 Processing image: {image_path.name}")
            start_time = time.time()
            
            # ------------------------------- #
            #  Load and Validate Image        #
            # ------------------------------- #
            
            with Image.open(image_path) as img:
                # Convert to RGBA if needed
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                    self.logger.debug(f"🔄 Converted image to RGBA mode")
                
                original_size = img.size
                self.logger.info(f"📸 Image loaded: {original_size[0]}x{original_size[1]} pixels")
                
                # ------------------------------- #
                #  Calculate Corner Radius        #
                # ------------------------------- #
                
                radius = self.calculate_corner_radius(original_size)
                self.logger.info(f"📐 Using corner radius: {radius}px")
                
                # ------------------------------- #
                #  Create and Apply Mask          #
                # ------------------------------- #
                
                mask = self.create_rounded_mask(original_size, radius)
                
                # Apply mask to create transparency
                img.putalpha(mask)
                self.logger.debug(f"🎭 Applied rounded corner mask")
                
                # ------------------------------- #
                #  Save Processed Image           #
                # ------------------------------- #
                
                output_path = self.get_output_path(image_path)
                
                if output_path:
                    # Save to file
                    img.save(output_path, 'PNG', optimize=True)
                    self.logger.info(f"💾 Saved to: {output_path}")
                else:
                    # Only clipboard mode - save to temp for clipboard
                    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
                    temp_path = Path(temp_file.name)
                    img.save(temp_path, 'PNG', optimize=True)
                    temp_file.close()
                    output_path = temp_path
                    self.logger.debug(f"📋 Saved to temp for clipboard: {temp_path}")
                
                processing_time = time.time() - start_time
                self.logger.info(f"✅ Image processed successfully in {processing_time:.2f}s")
                
                return output_path
                
        except Exception as e:
            self.logger.error(f"❌ Error processing image {image_path}: {str(e)}")
            return None
    
    def get_output_path(self, input_path: Path) -> Optional[Path]:
        """Determine output path for processed image"""
        
        # Check if desktop saving is disabled
        if not self.config.config.get('save_to_desktop', True):
            self.logger.debug(f"📝 Desktop saving disabled - only clipboard mode")
            return None
            
        if self.config.config.get('replace_original', False):
            output_path = input_path
            self.logger.debug(f"📝 Will replace original file: {output_path}")
        else:
            # Create output directory
            output_dir = self.config.get_expanded_path(self.config.config.get('output_folder', '~/Desktop/rounded_screenshots'))
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate output filename
            stem = input_path.stem
            suffix = input_path.suffix
            output_path = output_dir / f"{stem}_rounded{suffix}"
            
            self.logger.debug(f"📁 Output directory: {output_dir}")
            self.logger.debug(f"📝 Output filename: {output_path.name}")
        
        return output_path


# ------------------------------------------------- #
#                                                   #
#                                                   #
#           Clipboard Operations                     #
#                                                   #
#                                                   #
# ------------------------------------------------- #

class ClipboardManager:
    """Manages clipboard operations for processed images"""
    
    def __init__(self, config: ScreenshotRounderConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.clipboard_available = CLIPBOARD_AVAILABLE
        self.last_clipboard_content = None
        self.clipboard_monitor_thread = None
        self.monitoring_clipboard = False
        
        if not self.clipboard_available:
            self.logger.warning("⚠️  Clipboard functionality not available - install pyobjc-framework-Cocoa")
    
    def copy_image_to_clipboard(self, image_path: Path) -> bool:
        """Copy processed image to clipboard"""
        if not self.clipboard_available:
            self.logger.warning("⚠️  Cannot copy to clipboard - PyObjC not available")
            return False
            
        try:
            self.logger.info(f"📋 Copying to clipboard: {image_path.name}")
            
            # Read image data
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Get pasteboard and clear it
            pasteboard = NSPasteboard.generalPasteboard()
            pasteboard.clearContents()
            
            # Create NSData object and set to pasteboard
            ns_data = AppKit.NSData.dataWithBytes_length_(image_data, len(image_data))
            success = pasteboard.setData_forType_(ns_data, NSPasteboardTypePNG)
            
            if success:
                self.logger.info(f"✅ Image copied to clipboard successfully")
                return True
            else:
                self.logger.error(f"❌ Failed to copy image to clipboard")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error copying to clipboard: {str(e)}")
            return False
    
    def get_clipboard_image(self) -> Optional[bytes]:
        """Get image data from clipboard"""
        if not self.clipboard_available:
            return None
            
        try:
            pasteboard = NSPasteboard.generalPasteboard()
            data = pasteboard.dataForType_(NSPasteboardTypePNG)
            
            if data:
                return bytes(data)
            return None
            
        except Exception as e:
            self.logger.debug(f"❌ Error reading clipboard: {str(e)}")
            return None
    
    def start_clipboard_monitoring(self, processor: 'ImageProcessor'):
        """Start monitoring clipboard for new images"""
        if not self.clipboard_available:
            self.logger.warning("⚠️  Cannot monitor clipboard - PyObjC not available")
            return
            
        if self.monitoring_clipboard:
            self.logger.debug("📋 Clipboard monitoring already active")
            return
            
        self.monitoring_clipboard = True
        self.clipboard_monitor_thread = threading.Thread(
            target=self._monitor_clipboard_loop,
            args=(processor,),
            daemon=True
        )
        self.clipboard_monitor_thread.start()
        self.logger.info("📋 Started clipboard monitoring for Cmd+Shift+4 selections")
    
    def stop_clipboard_monitoring(self):
        """Stop clipboard monitoring"""
        self.monitoring_clipboard = False
        if self.clipboard_monitor_thread:
            self.clipboard_monitor_thread.join(timeout=1)
        self.logger.info("📋 Stopped clipboard monitoring")
    
    def _monitor_clipboard_loop(self, processor: 'ImageProcessor'):
        """Monitor clipboard for new images in a loop"""
        self.logger.debug("📋 Clipboard monitoring loop started")
        
        while self.monitoring_clipboard:
            try:
                # Check for new clipboard content
                current_content = self.get_clipboard_image()
                
                if current_content and current_content != self.last_clipboard_content:
                    self.logger.info("📋 New image detected in clipboard (Cmd+Shift+4 selection)")
                    
                    # Save clipboard image to temp file
                    temp_path = self._save_clipboard_to_temp(current_content)
                    if temp_path:
                        # Process the image
                        output_path = processor.apply_rounded_corners(temp_path)
                        if output_path:
                            self.logger.info(f"✅ Clipboard image processed: {output_path.name}")
                            # Copy back to clipboard
                            self.copy_image_to_clipboard(output_path)
                        else:
                            self.logger.error("❌ Failed to process clipboard image")
                        
                        # Clean up temp files
                        temp_path.unlink(missing_ok=True)
                        if output_path and output_path != temp_path:
                            output_path.unlink(missing_ok=True)
                    
                    self.last_clipboard_content = current_content
                
                time.sleep(0.5)  # Check every 500ms
                
            except Exception as e:
                self.logger.error(f"❌ Error in clipboard monitoring: {str(e)}")
                time.sleep(1)
    
    def _save_clipboard_to_temp(self, image_data: bytes) -> Optional[Path]:
        """Save clipboard image data to temporary file"""
        try:
            # Create temp file
            temp_file = tempfile.NamedTemporaryFile(
                suffix='.png',
                prefix='clipboard_',
                delete=False
            )
            temp_path = Path(temp_file.name)
            
            # Write image data
            temp_file.write(image_data)
            temp_file.close()
            
            self.logger.debug(f"📋 Saved clipboard image to temp: {temp_path}")
            return temp_path
            
        except Exception as e:
            self.logger.error(f"❌ Error saving clipboard to temp: {str(e)}")
            return None


# ------------------------------------------------- #
#                                                   #
#                                                   #
#         File System Monitoring                    #
#                                                   #
#                                                   #
# ------------------------------------------------- #

class ScreenshotHandler(FileSystemEventHandler):
    """Handles file system events for new screenshots"""
    
    def __init__(self, config: ScreenshotRounderConfig):
        super().__init__()
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.processor = ImageProcessor(config)
        self.clipboard = ClipboardManager(config)
        self.processing_files = set()  # Track files being processed
        
        self.logger.info(f"🔍 Screenshot handler initialized")
        self.logger.info(f"📁 Monitoring folder: {config.get_expanded_path(config.config['screenshot_folder'])}")
        self.logger.info(f"🎯 File patterns: {config.config.get('file_patterns', [])}")
    
    def on_created(self, event):
        """Handle new file creation"""
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        self.logger.debug(f"📁 New file detected: {file_path.name}")
        
        # Check if it matches screenshot patterns
        if self.is_screenshot_file(file_path):
            self.logger.info(f"📸 Screenshot detected: {file_path.name}")
            
            # Add delay to ensure file is completely written
            delay = self.config.config.get('processing_delay', 0.5)
            if delay > 0:
                self.logger.debug(f"⏳ Waiting {delay}s for file to complete...")
                time.sleep(delay)
            
            self.process_screenshot(file_path)
    
    def is_screenshot_file(self, file_path: Path) -> bool:
        """Check if file matches screenshot patterns"""
        patterns = self.config.config.get('file_patterns', [])
        filename = file_path.name
        
        for pattern in patterns:
            if fnmatch.fnmatch(filename, pattern):
                self.logger.debug(f"✅ File matches pattern '{pattern}': {filename}")
                return True
        
        self.logger.debug(f"❌ File doesn't match any pattern: {filename}")
        return False
    
    def process_screenshot(self, file_path: Path):
        """Process a screenshot file"""
        # Prevent duplicate processing
        if str(file_path) in self.processing_files:
            self.logger.debug(f"⏭️  File already being processed: {file_path.name}")
            return
            
        try:
            self.processing_files.add(str(file_path))
            self.logger.info(f"🔄 Starting processing: {file_path.name}")
            
            # ------------------------------- #
            #  Validate File Exists           #
            # ------------------------------- #
            
            if not file_path.exists():
                self.logger.warning(f"⚠️  File no longer exists: {file_path}")
                return
            
            # ------------------------------- #
            #  Process Image                  #
            # ------------------------------- #
            
            output_path = self.processor.apply_rounded_corners(file_path)
            
            if output_path:
                # ------------------------------- #
                #  Copy to Clipboard              #
                # ------------------------------- #
                
                if self.config.config.get('auto_copy_to_clipboard', True):
                    self.clipboard.copy_image_to_clipboard(output_path)
                
                self.logger.info(f"🎉 Screenshot processing completed: {file_path.name}")
            else:
                self.logger.error(f"❌ Failed to process screenshot: {file_path.name}")
                
        except Exception as e:
            self.logger.error(f"❌ Error processing screenshot {file_path}: {str(e)}")
        finally:
            self.processing_files.discard(str(file_path))


# ------------------------------------------------- #
#                                                   #
#                                                   #
#            Main Application                        #
#                                                   #
#                                                   #
# ------------------------------------------------- #

class ScreenshotRounder:
    """Main application class"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config = ScreenshotRounderConfig(config_file)
        self.logger = logging.getLogger(__name__)
        self.observer = None
        self.handler = None
        
        self.logger.info(f"🚀 Screenshot Rounder starting up...")
        self.validate_setup()
    
    def validate_setup(self):
        """Validate setup and dependencies"""
        self.logger.info(f"🔍 Validating setup...")
        
        # ------------------------------- #
        #  Check Screenshot Folder        #
        # ------------------------------- #
        
        screenshot_folder = self.config.get_expanded_path(self.config.config['screenshot_folder'])
        if not screenshot_folder.exists():
            self.logger.error(f"❌ Screenshot folder doesn't exist: {screenshot_folder}")
            raise FileNotFoundError(f"Screenshot folder not found: {screenshot_folder}")
        
        self.logger.info(f"✅ Screenshot folder exists: {screenshot_folder}")
        
        # ------------------------------- #
        #  Check Output Folder            #
        # ------------------------------- #
        
        if not self.config.config.get('replace_original', False):
            output_folder = self.config.get_expanded_path(self.config.config['output_folder'])
            output_folder.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"✅ Output folder ready: {output_folder}")
        
        # ------------------------------- #
        #  Check Dependencies             #
        # ------------------------------- #
        
        try:
            from PIL import Image
            self.logger.info(f"✅ PIL/Pillow available")
        except ImportError:
            self.logger.error(f"❌ PIL/Pillow not available - install with: pip install Pillow")
            raise
        
        if CLIPBOARD_AVAILABLE:
            self.logger.info(f"✅ Clipboard functionality available")
        else:
            self.logger.warning(f"⚠️  Clipboard functionality not available")
    
    def start_monitoring(self):
        """Start file system monitoring"""
        if not self.config.config.get('monitor_enabled', True):
            self.logger.info(f"📴 Monitoring disabled in configuration")
            return
        
        screenshot_folder = self.config.get_expanded_path(self.config.config['screenshot_folder'])
        
        self.logger.info(f"🔍 Starting file system monitoring...")
        self.logger.info(f"📁 Watching folder: {screenshot_folder}")
        
        # Setup file handler and observer
        self.handler = ScreenshotHandler(self.config)
        self.observer = Observer()
        self.observer.schedule(self.handler, str(screenshot_folder), recursive=False)
        
        # Start monitoring
        self.observer.start()
        self.logger.info(f"✅ File system monitoring started")
        self.logger.info(f"🎯 Watching for patterns: {self.config.config.get('file_patterns', [])}")
        
        # Start clipboard monitoring for Cmd+Shift+4 selections
        if self.config.config.get('monitor_clipboard', True):
            processor = ImageProcessor(self.config)
            self.handler.clipboard.start_clipboard_monitoring(processor)
        else:
            self.logger.info("📴 Clipboard monitoring disabled in configuration")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info(f"⏹️  Stopping screenshot monitoring...")
            self.stop_monitoring()
    
    def stop_monitoring(self):
        """Stop file system monitoring"""
        # Stop clipboard monitoring
        if self.handler and self.handler.clipboard:
            self.handler.clipboard.stop_clipboard_monitoring()
        
        # Stop file system monitoring
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.logger.info(f"✅ File system monitoring stopped")
    
    def process_single_file(self, file_path: str):
        """Process a single file manually"""
        path = Path(file_path).resolve()
        
        if not path.exists():
            self.logger.error(f"❌ File doesn't exist: {path}")
            return False
        
        self.logger.info(f"🔄 Processing single file: {path.name}")
        
        processor = ImageProcessor(self.config)
        clipboard = ClipboardManager(self.config)
        
        output_path = processor.apply_rounded_corners(path)
        
        if output_path:
            if self.config.config.get('auto_copy_to_clipboard', True):
                clipboard.copy_image_to_clipboard(output_path)
            
            self.logger.info(f"🎉 Single file processing completed: {path.name}")
            return True
        else:
            self.logger.error(f"❌ Failed to process file: {path.name}")
            return False


# ------------------------------------------------- #
#                                                   #
#                                                   #
#              CLI Interface                         #
#                                                   #
#                                                   #
# ------------------------------------------------- #

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Screenshot Rounder - Add rounded corners to screenshots')
    parser.add_argument('--config', '-c', default='config.json', help='Configuration file path')
    parser.add_argument('--file', '-f', help='Process a single file instead of monitoring')
    parser.add_argument('--no-monitor', action='store_true', help='Disable file monitoring')
    parser.add_argument('--test', action='store_true', help='Test setup and exit')
    
    args = parser.parse_args()
    
    try:
        app = ScreenshotRounder(args.config)
        
        if args.test:
            print("✅ Setup validation passed - Screenshot Rounder is ready!")
            return
        
        if args.file:
            success = app.process_single_file(args.file)
            sys.exit(0 if success else 1)
        
        if args.no_monitor:
            print("📴 Monitoring disabled - use --file to process individual files")
            return
        
        print("🎯 Screenshot Rounder is running - Press Ctrl+C to stop")
        print("📸 Take a screenshot (Cmd+Shift+3/4) to see it processed automatically!")
        app.start_monitoring()
        
    except KeyboardInterrupt:
        print("\n👋 Screenshot Rounder stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()