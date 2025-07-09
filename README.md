# DeviantArt 4K Anime Wallpaper Setter

A Python application that automatically downloads and sets high-quality 4K anime wallpapers from DeviantArt. Designed to run silently in the background via Windows Task Scheduler without any user interaction.

## Features

- **Automatic wallpaper rotation** with high-quality 4K anime images
- **Silent operation** - no user interaction required
- **Configurable content filtering** including mature content support
- **Windows Task Scheduler integration** for automated execution
- **Modern DeviantArt API** support with OAuth 2.0 authentication
- **Smart image filtering** for optimal wallpaper quality

## Requirements

- **Python 3.8+**
- **Windows 10/11** (uses Windows API for wallpaper setting)
- **DeviantArt Developer Account** (free)
- **Internet connection** for API access

## Installation

### Step 1: Install Python
1. Download Python from [python.org](https://www.python.org/downloads/)
2. During installation, **check "Add Python to PATH"**
3. Verify installation by opening Command Prompt and typing: `python --version`

### Step 2: Install Dependencies
```bash
pip install requests
```

### Step 3: Download the Script
- Save `deviantart_wallpaper_changer.py` to your desired directory
- Example: `C:\Scripts\DeviantArt-Wallpaper\`

### Step 4: Set Up DeviantArt API Credentials
1. Visit [DeviantArt Developers](https://www.deviantart.com/developers/)
2. Log in with your DeviantArt account
3. Click "Register your Application"
4. Fill in the form:
   - **Application Name**: "Personal Wallpaper Changer"
   - **Description**: "Personal wallpaper automation script"
   - **Grant Type**: Select "Authorization Code"
   - **Redirect URI**: `http://localhost:8080`
5. Submit the form and note your `client_id` and `client_secret`

## Configuration

Create a `deviantart_config.json` file in the same directory as the script:

```json
{
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET",
    "mature_content": false
}
```

### Configuration Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `client_id` | string | Your DeviantArt app client ID | Required |
| `client_secret` | string | Your DeviantArt app client secret | Required |
| `mature_content` | boolean | Include mature content in searches | `false` |

### Mature Content Setup

To enable mature content:
1. Set `mature_content` to `true` in your configuration file
2. Log into your DeviantArt account
3. Go to Account Settings → Browsing
4. Enable "View Mature Content"
5. Save settings

## Usage

### First-Time Setup and Testing

1. **Create configuration file** with your credentials
2. **Run the script manually** to complete initial authentication:
   ```bash
   cd C:\Scripts\DeviantArt-Wallpaper
   python deviantart_wallpaper_changer.py
   ```
3. **Browser will open** for DeviantArt authorization (one-time only)
4. **Approve the application** and wait for the script to complete
5. **Verify wallpaper changes** to confirm everything works

### Windows Task Scheduler Setup

#### Method 1: Using Task Scheduler GUI

1. **Open Task Scheduler**
   - Press `Win + R`, type `taskschd.msc`, press Enter
   - Or search "Task Scheduler" in Start menu

2. **Create Basic Task**
   - Click "Create Basic Task..." in the Actions panel
   - Name: "DeviantArt Wallpaper Changer"
   - Description: "Automatically changes desktop wallpaper to anime images"

3. **Set Trigger (When to run)**
   - **Daily**: Changes wallpaper once per day at specified time
   - **Weekly**: Changes wallpaper on specific days
   - **When I log on**: Changes wallpaper at Windows startup
   - **When the computer starts**: Changes wallpaper when PC boots

4. **Set Action (What to run)**
   - Action: "Start a program"
   - Program/script: `python.exe` (or full path: `C:\Python39\python.exe`)
   - Arguments: `deviantart_wallpaper_changer.py`
   - Start in: `C:\Scripts\DeviantArt-Wallpaper` (your script directory)

5. **Configure Advanced Settings**
   - Right-click your task → Properties
   - **General tab**:
     - ✅ "Run whether user is logged on or not"
     - ✅ "Run with highest privileges"
   - **Settings tab**:
     - ✅ "Allow task to be run on demand"
     - ✅ "Run task as soon as possible after a scheduled start is missed"
     - ✅ "If the running task does not end when requested, force it to stop"

#### Method 2: Using Command Line

```cmd
schtasks /create /tn "DeviantArt Wallpaper" /tr "python.exe C:\Scripts\DeviantArt-Wallpaper\deviantart_wallpaper_changer.py" /sc daily /st 09:00 /sd 01/01/2024
```

### Running the Task

- **Manual execution**: Right-click task → "Run"
- **Test immediately**: Run the script from Command Prompt
- **Check task history**: Task Scheduler → History tab

## How It Works

### 1. Authentication Process
- Uses OAuth 2.0 Authorization Code flow
- Opens browser for one-time authorization (first run only)
- Caches access token for subsequent runs
- Token automatically refreshes when expired

### 2. Image Discovery Process
- Searches DeviantArt for images tagged with: `anime`, `manga`, `yuri`
- Filters for high-resolution images (≥2560x1440 or containing "4K" in title)
- Collects up to 30 qualifying images per run
- Respects API rate limits with automatic retries

### 3. Wallpaper Setting Process
- Randomly selects one image from the collected set
- Downloads image to temporary location
- Sets as Windows desktop wallpaper using Windows API
- Cleans up temporary files

## Troubleshooting

### Configuration Issues

**❌ "Configuration file not found"**
- **Solution**: Create `deviantart_config.json` in the same directory as the script
- **Check**: File name must be exactly `deviantart_config.json`
- **Verify**: File contains valid JSON format with all required fields

**❌ "Error: Invalid JSON format"**
- **Solution**: Validate your JSON syntax at [jsonlint.com](https://jsonlint.com/)
- **Common issues**: Missing commas, quotes, or brackets
- **Example**: Make sure strings are in quotes: `"client_id": "12345"`

**❌ "Missing client_id or client_secret"**
- **Solution**: Ensure both fields are present in your configuration file
- **Check**: Values are not empty or null
- **Verify**: Copy credentials exactly from DeviantArt developer page

### Authentication Issues

**❌ "Authentication failed"**
- **Solution 1**: Verify your `client_id` and `client_secret` are correct
- **Solution 2**: Check that your DeviantArt app redirect URI is `http://localhost:8080`
- **Solution 3**: Ensure your DeviantArt app is active and approved
- **Solution 4**: Try deleting any cached token files and re-authenticate

**❌ "Browser doesn't open for authentication"**
- **Solution 1**: Copy the printed authorization URL and paste it into your browser manually
- **Solution 2**: Check your default browser settings
- **Solution 3**: Temporarily disable firewall/antivirus during authentication
- **Solution 4**: Try running the script as administrator

**❌ "Localhost connection refused"**
- **Solution**: Ensure port 8080 is not blocked by firewall
- **Check**: No other applications are using port 8080
- **Try**: Run `netstat -an | findstr "8080"` to check port usage

### Image Search Issues

**❌ "No suitable images found"**
- **Solution 1**: Enable mature content in your configuration file
- **Solution 2**: Check your internet connection
- **Solution 3**: Verify DeviantArt API is accessible
- **Solution 4**: Try running the script at different times (API rate limits)

**❌ "API rate limit exceeded (429 error)"**
- **Solution**: Wait 1-2 hours before trying again
- **Prevention**: Don't run the script too frequently
- **Recommendation**: Set Task Scheduler to run maximum once per hour

### Wallpaper Setting Issues

**❌ "Wallpaper doesn't change"**
- **Solution 1**: Run the script as administrator
- **Solution 2**: Check Windows wallpaper settings aren't locked by Group Policy
- **Solution 3**: Verify the downloaded image file is valid
- **Solution 4**: Try setting wallpaper manually to test system permissions

**❌ "Image downloads but wallpaper stays the same"**
- **Solution 1**: Restart Windows Explorer: Press `Ctrl+Shift+Esc` → Find "Windows Explorer" → Restart
- **Solution 2**: Check if image file is corrupted
- **Solution 3**: Try a different image format in the script

### Task Scheduler Issues

**❌ "Task doesn't run automatically"**
- **Solution 1**: Check that the task is enabled (right-click task → Enable)
- **Solution 2**: Verify trigger conditions are met
- **Solution 3**: Ensure Python is in system PATH
- **Solution 4**: Check task history for error messages

**❌ "Task runs but nothing happens"**
- **Solution 1**: Verify the "Start in" directory is correct
- **Solution 2**: Check that Python path is correct in the task
- **Solution 3**: Run the task manually to see immediate results
- **Solution 4**: Check Windows Event Viewer for error logs

**❌ "Task fails with error code 0x1"**
- **Solution 1**: Verify Python is installed and in PATH
- **Solution 2**: Check script file path is correct
- **Solution 3**: Run task with highest privileges
- **Solution 4**: Test the exact command in Command Prompt

**❌ "Task runs but wallpaper doesn't change"**
- **Solution 1**: Add delays between API calls in the script
- **Solution 2**: Check if user session is locked (some wallpaper changes require active session)
- **Solution 3**: Verify network connectivity during scheduled runs
- **Solution 4**: Check antivirus isn't blocking file operations

### Network and API Issues

**❌ "Connection timeout"**
- **Solution 1**: Check internet connection
- **Solution 2**: Try running script with VPN if ISP blocks DeviantArt
- **Solution 3**: Increase timeout values in the script
- **Solution 4**: Check firewall settings

**❌ "SSL certificate errors"**
- **Solution 1**: Update Python to latest version
- **Solution 2**: Update `requests` library: `pip install --upgrade requests`
- **Solution 3**: Check system date and time are correct

### Performance Issues

**❌ "Script takes too long to run"**
- **Solution 1**: Reduce search limit in the script
- **Solution 2**: Check internet speed
- **Solution 3**: Add timeout limits to API calls
- **Solution 4**: Run during off-peak hours

**❌ "High CPU usage"**
- **Solution 1**: Add delays between API calls
- **Solution 2**: Reduce concurrent image processing
- **Solution 3**: Limit image download size

## Advanced Configuration

### Custom Search Tags

Modify the `search_tags` list in the script to use different tags:

```python
self.search_tags = ["anime", "manga", "yuri", "kawaii", "otaku", "waifu"]
```

### Image Quality Settings

Adjust image quality filters in the script:

```python
# Minimum resolution requirements
min_width = 3840  # For 4K
min_height = 2160  # For 4K
```

### Logging Configuration

Add logging to track script execution:

```python
import logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s',
                   handlers=[
                       logging.FileHandler('wallpaper_changer.log'),
                       logging.StreamHandler()
                   ])
```

## File Structure

```
your-script-directory/
├── deviantart_wallpaper.py           # Main script
├── deviantart_config.json             # Configuration file
├── README.md                          # This file
├── wallpaper_changer.log             # Log file (optional)
└── temp/                             # Temporary files (created automatically)
    └── temp_wallpaper.*              # Downloaded wallpaper images
```

## Security Best Practices

- **Keep credentials secure**: Don't share your `client_id` and `client_secret`
- **File permissions**: Set appropriate permissions on configuration file
- **Regular updates**: Keep Python and dependencies updated
- **Monitor usage**: Check DeviantArt API usage to avoid rate limits
- **Backup configuration**: Keep a backup of your configuration file

## Debugging Tips

### Enable Debug Mode

Add this to the beginning of your script for detailed output:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Task Scheduler History

1. Open Task Scheduler
2. Find your task
3. Click "History" tab
4. Look for error events

### Manual Testing

Always test manually before setting up automation:

```bash
cd C:\Scripts\DeviantArt-Wallpaper
python deviantart_wallpaper_changer.py
```

### Common File Locations

- **Python executable**: `C:\Python39\python.exe`
- **pip location**: `C:\Python39\Scripts\pip.exe`
- **Task Scheduler logs**: Windows Event Viewer → Windows Logs → System

## Support

If you encounter issues not covered in this troubleshooting guide:

1. **Check the script output** for specific error messages
2. **Review Windows Event Viewer** for system-level errors
3. **Test each component individually** (config, authentication, image search)
4. **Verify all requirements** are met and properly configured

## License

This project is for personal use only. Respect DeviantArt's terms of service and the rights of content creators.

## Changelog

### v2.0 (Current)
- Added silent operation mode
- Moved mature content setting to configuration file
- Improved error handling for automated execution
- Added comprehensive troubleshooting guide
- Enhanced Windows Task Scheduler compatibility

### v1.0
- Initial release with interactive prompts
- Basic DeviantArt API integration
- Manual wallpaper setting functionality
