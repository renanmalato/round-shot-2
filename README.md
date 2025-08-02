# Screenshot Rounder

Automatically add rounded corners to your macOS screenshots for presentations and better visual appeal.

## Features

- 🔄 **Automatic Processing**: Monitors your screenshot folder and processes images automatically
- 📋 **Clipboard Integration**: Automatically copies processed images to clipboard
- ⚙️ **Configurable**: Customize corner radius, output location, and file patterns
- 📊 **Comprehensive Logging**: Detailed logs for debugging and monitoring
- 🚀 **Background Service**: Run as a macOS LaunchAgent for automatic startup
- 🎯 **Smart Detection**: Recognizes various screenshot patterns (Screenshot, CleanShot, etc.)

## Quick Start

1. **Install dependencies**:
   ```bash
   python3 setup.py
   ```

2. **Run Screenshot Rounder**:
   ```bash
   python3 screenshot_rounder.py
   ```

3. **Take a screenshot** (Cmd+Shift+3 or Cmd+Shift+4)

4. **Check results**:
   - Processed image saved to `~/Desktop/rounded_screenshots/`
   - Image automatically copied to clipboard
   - Ready to paste into presentations!

## Installation

### Manual Installation

```bash
# Clone or download the files
# Install Python dependencies
pip3 install -r requirements.txt

# Run setup
python3 setup.py

# Test the setup
python3 screenshot_rounder.py --test
```

### Automatic Startup (Recommended)

To run Screenshot Rounder automatically at startup:

```bash
# Install as macOS LaunchAgent
python3 launch_agent.py install

# Check status
python3 launch_agent.py status

# Remove if needed
python3 launch_agent.py remove
```

## Configuration

Edit `config.json` to customize behavior:

```json
{
  "screenshot_folder": "~/Desktop",
  "output_folder": "~/Desktop/rounded_screenshots",
  "corner_radius": 20,
  "corner_radius_percentage": 0.05,
  "use_percentage": true,
  "auto_copy_to_clipboard": true,
  "replace_original": false,
  "monitor_enabled": true,
  "log_level": "INFO",
  "file_patterns": ["Screenshot*.png", "CleanShot*.png", "Screen Shot*.png"],
  "processing_delay": 0.5
}
```

### Configuration Options

- **`corner_radius`**: Fixed pixel radius (when `use_percentage` is false)
- **`corner_radius_percentage`**: Percentage of smallest dimension (when `use_percentage` is true)
- **`use_percentage`**: Use percentage-based radius for responsive sizing
- **`auto_copy_to_clipboard`**: Automatically copy processed images to clipboard
- **`replace_original`**: Replace original screenshots instead of creating new files
- **`file_patterns`**: List of filename patterns to monitor
- **`processing_delay`**: Delay in seconds before processing new files

## Usage

### Automatic Mode (Recommended)

```bash
# Start monitoring (runs until Ctrl+C)
python3 screenshot_rounder.py
```

### Single File Processing

```bash
# Process a specific file
python3 screenshot_rounder.py --file /path/to/screenshot.png
```

### Command Line Options

```bash
python3 screenshot_rounder.py --help

Options:
  --config, -c    Configuration file path (default: config.json)
  --file, -f      Process a single file instead of monitoring
  --no-monitor    Disable file monitoring
  --test          Test setup and exit
```

## Logging

Comprehensive logs are written to:
- **Console**: Real-time output with colors and emojis
- **File**: `~/.screenshot_rounder/logs/screenshot_rounder_YYYYMMDD.log`

Log levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`

### Sample Log Output

```
2024-01-15 10:30:15 | INFO  | __init__:89 | 🚀 Screenshot Rounder initialized - Log Level: INFO
2024-01-15 10:30:15 | INFO  | validate_setup:145 | ✅ Screenshot folder exists: /Users/username/Desktop
2024-01-15 10:30:15 | INFO  | start_monitoring:167 | 🔍 Starting file system monitoring...
2024-01-15 10:30:20 | INFO  | on_created:205 | 📸 Screenshot detected: Screenshot 2024-01-15 at 10.30.20 AM.png
2024-01-15 10:30:20 | INFO  | apply_rounded_corners:142 | 🔄 Processing image: Screenshot 2024-01-15 at 10.30.20 AM.png
2024-01-15 10:30:20 | INFO  | apply_rounded_corners:155 | 📸 Image loaded: 2880x1800 pixels
2024-01-15 10:30:20 | INFO  | apply_rounded_corners:160 | 📐 Using corner radius: 90px
2024-01-15 10:30:21 | INFO  | apply_rounded_corners:175 | ✅ Image processed successfully in 0.85s
2024-01-15 10:30:21 | INFO  | copy_image_to_clipboard:245 | ✅ Image copied to clipboard successfully
```

## How It Works

1. **File System Monitoring**: Uses `watchdog` to monitor your Desktop for new screenshot files
2. **Pattern Matching**: Recognizes screenshots by filename patterns (configurable)
3. **Image Processing**: Uses `Pillow` to apply rounded corners with transparency
4. **Clipboard Integration**: Uses `pyobjc` to copy processed images to macOS clipboard
5. **Smart Processing**: Adds delay to ensure files are completely written before processing

## Troubleshooting

### Common Issues

**Clipboard not working**:
```bash
# Install PyObjC for clipboard support
pip3 install pyobjc-framework-Cocoa pyobjc-framework-Quartz
```

**Screenshots not detected**:
- Check if screenshot location is `~/Desktop` (System Preferences > Keyboard > Shortcuts > Screenshots)
- Verify file patterns in `config.json` match your screenshot app
- Check logs for detailed information

**Permission issues**:
- Ensure Python has disk access permissions in System Preferences > Security & Privacy

### Debug Mode

Enable debug logging for detailed information:

```json
{
  "log_level": "DEBUG"
}
```

### Test Setup

```bash
# Validate configuration and dependencies
python3 screenshot_rounder.py --test
```

## Dependencies

- **Python 3.7+**
- **Pillow**: Image processing
- **watchdog**: File system monitoring  
- **pyobjc-framework-Cocoa**: macOS clipboard integration
- **pyobjc-framework-Quartz**: macOS system integration

## Files Structure

```
screenshot-rounder/
├── screenshot_rounder.py    # Main application
├── config.json             # Configuration file
├── requirements.txt        # Python dependencies
├── setup.py               # Setup script
├── launch_agent.py        # macOS LaunchAgent manager
└── README.md              # This file
```

## Logs Location

```
~/.screenshot_rounder/logs/
├── screenshot_rounder_20240115.log    # Daily log files
├── launchd_stdout.log                 # LaunchAgent output
└── launchd_stderr.log                 # LaunchAgent errors
```

## License

This is a personal utility script. Use and modify as needed for your presentations!

## Stopping the Service

### **Temporary Stop (Until Next Restart)**
```bash
# Stop the service immediately
python3 launch_agent.py remove

# Or manually stop the process
pkill -f screenshot_rounder.py
```

### **Permanent Stop (Disable Auto-Start)**
```bash
# Remove LaunchAgent completely
python3 launch_agent.py remove

# Verify it's stopped
python3 launch_agent.py status
```

### **Manual Control**
```bash
# Check if running
ps aux | grep screenshot_rounder

# Force stop all instances
pkill -f screenshot_rounder
```

## Resource Monitoring

### **CPU and Memory Usage**
```bash
# Check current resource usage
ps aux | grep screenshot_rounder

# Monitor in real-time
top -pid $(pgrep -f screenshot_rounder.py)

# Detailed resource info
ps -o pid,ppid,pcpu,pmem,command -p $(pgrep -f screenshot_rounder.py)
```

### **Expected Resource Usage**
- **CPU**: < 1% (idle monitoring)
- **Memory**: ~15-25MB (Python + dependencies)
- **Disk**: Minimal (only log files)
- **Network**: None (local operations only)

### **Performance Impact**
- ✅ **Minimal CPU usage** - Only active when processing screenshots
- ✅ **Low memory footprint** - ~20MB total
- ✅ **No network activity** - All operations local
- ✅ **No disk I/O** - Only writes logs and processed images

### **Monitoring Commands**
```bash
# Real-time monitoring
watch -n 1 'ps aux | grep screenshot_rounder'

# Memory usage
memory_profiler screenshot_rounder.py

# System impact
sudo powermetrics -i 1000 -n 1 | grep -i screenshot
```

## Troubleshooting

### **Service Not Starting**
```bash
# Check LaunchAgent logs
tail -f ~/.screenshot_rounder/logs/launchd_stdout.log
tail -f ~/.screenshot_rounder/logs/launchd_stderr.log

# Reinstall service
python3 launch_agent.py remove
python3 launch_agent.py install
```

### **High Resource Usage**
If you notice high CPU/memory usage:
```bash
# Restart the service
python3 launch_agent.py remove
python3 launch_agent.py install

# Check for multiple instances
ps aux | grep screenshot_rounder
```

## Contributing

This is a personal utility, but feel free to suggest improvements or report issues.