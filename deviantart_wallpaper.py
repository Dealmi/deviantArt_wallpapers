#!/usr/bin/env python3
"""
DeviantArt 4 K Anime Wallpaper Setter
------------------------------------

• Authenticates to DeviantArt with OAuth 2.0 (authorization-code flow)
• Searches /api/v1/oauth2/browse/tags for anime-style 4 K artwork
• Honors a silent JSON configuration that includes mature-content preference
• Randomly picks one image, downloads it, and sets it as the Windows wallpaper
• Designed for unattended execution from Windows Task Scheduler
"""

import ctypes
import json
import os
import random
import sys
import tempfile
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlencode, urlparse, parse_qs

import requests

CONFIG_FILE = "deviantart_config.json"
TOKEN_FILE = "deviantart_token.json"
REDIRECT_URI = "http://localhost:8080"
AUTH_URL = "https://www.deviantart.com/oauth2/authorize"
TOKEN_URL = "https://www.deviantart.com/oauth2/token"
BROWSE_TAGS_URL = "https://www.deviantart.com/api/v1/oauth2/browse/tags"
LIMIT_PER_TAG = 50          # DeviantArt max = 50
DESIRED_RESULTS = 30        # total unique images to gather
MIN_WIDTH, MIN_HEIGHT = 2560, 1440  # ~4 K (allows ultrawide crops)

class OAuthHandler(BaseHTTPRequestHandler):
    """Minimal HTTP handler to capture ?code=… callback."""
    code = None
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        if "code" in params:
            OAuthHandler.code = params["code"][0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(
                b"<html><body><h1>You may close this window.</h1></body></html>"
            )
        else:
            self.send_error(400, "Missing code parameter")

    def log_message(self, *_args, **_kwargs):
        # Suppress noisy HTTP logs
        pass

class DeviantArtWallpaperSetter:
    def __init__(self):
        self.client_id = None
        self.client_secret = None
        self.mature_content = False
        self.search_tags = ["anime", "manga", "yuri"]  # Default tags
        self.show_terminal = True  # Default to showing terminal
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        self.session = requests.Session()

    def log(self, message: str, error: bool = False):
        """Print message only if show_terminal is True."""
        if self.show_terminal:
            if error:
                print(message, file=sys.stderr)
            else:
                print(message)

    # ---------- Configuration ---------- #
    def load_config(self) -> bool:
        """Load credentials and options from JSON file without prompting."""
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            self.client_id = cfg.get("client_id")
            self.client_secret = cfg.get("client_secret")
            self.mature_content = bool(cfg.get("mature_content", False))
            self.search_tags = cfg.get("search_tags", ["anime", "manga", "yuri"])  # Read tags from config
            self.show_terminal = bool(cfg.get("show_terminal", True))  # Read terminal setting from config
        except FileNotFoundError:
            self.log(f"[ERROR] Configuration file {CONFIG_FILE} not found.", error=True)
            return False
        except json.JSONDecodeError as exc:
            self.log(f"[ERROR] Invalid JSON: {exc}", error=True)
            return False

        missing = [k for k in ("client_id", "client_secret") if not getattr(self, k)]
        if missing:
            self.log(f"[ERROR] Missing fields in config: {', '.join(missing)}", error=True)
            return False
        return True

    # ---------- OAuth 2.0 ---------- #
    def load_token(self) -> bool:
        """Load existing token from file if it's still valid."""
        try:
            with open(TOKEN_FILE, "r", encoding="utf-8") as f:
                token_data = json.load(f)
            
            self.access_token = token_data.get("access_token")
            self.refresh_token = token_data.get("refresh_token")
            self.token_expires_at = token_data.get("expires_at")
            
            # Check if token is still valid (with 5 minute buffer)
            if self.access_token and self.token_expires_at:
                import time
                if time.time() < self.token_expires_at - 300:  # 5 minute buffer
                    self.log("[INFO] Using existing valid token")
                    return True
                elif self.refresh_token:
                    self.log("[INFO] Token expired, attempting refresh...")
                    return self.refresh_access_token()
                    
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            pass
        
        return False

    def save_token(self, token_response: dict):
        """Save token data to file."""
        import time
        token_data = {
            "access_token": token_response.get("access_token"),
            "refresh_token": token_response.get("refresh_token"),
            "expires_at": time.time() + token_response.get("expires_in", 3600)
        }
        
        try:
            with open(TOKEN_FILE, "w", encoding="utf-8") as f:
                json.dump(token_data, f, indent=2)
        except Exception as e:
            self.log(f"[WARN] Failed to save token: {e}", error=True)

    def refresh_access_token(self) -> bool:
        """Refresh the access token using refresh token."""
        if not self.refresh_token:
            return False
            
        data = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
        }
        
        try:
            resp = self.session.post(TOKEN_URL, data=data, timeout=30)
            if resp.status_code == 200:
                token_response = resp.json()
                self.access_token = token_response.get("access_token")
                self.refresh_token = token_response.get("refresh_token", self.refresh_token)
                self.save_token(token_response)
                self.log("[INFO] Token refreshed successfully")
                return bool(self.access_token)
            else:
                self.log(f"[WARN] Token refresh failed: {resp.text}", error=True)
                return False
        except Exception as e:
            self.log(f"[WARN] Token refresh error: {e}", error=True)
            return False

    def authenticate(self) -> bool:
        """Perform the authorization-code flow and obtain an access-token."""
        # First try to load existing token
        if self.load_token():
            return True
            
        # If no valid token, perform full OAuth flow
        state = os.urandom(8).hex()
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": REDIRECT_URI,
            "scope": "browse",
            "state": state,
        }
        auth_url_full = f"{AUTH_URL}?{urlencode(params)}"

        # Start local server in background
        server = HTTPServer(("localhost", 8080), OAuthHandler)
        threading.Thread(target=server.serve_forever, daemon=True).start()

        # Open browser for user login once (token persists until script ends)
        self.log("[INFO] Opening browser for DeviantArt authorization…")
        webbrowser.open(auth_url_full, new=1)

        # Wait until OAuthHandler sets the code
        while OAuthHandler.code is None:
            pass
        server.shutdown()

        # Exchange code for token
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": REDIRECT_URI,
            "code": OAuthHandler.code,
        }
        resp = self.session.post(TOKEN_URL, data=data, timeout=30)
        if resp.status_code != 200:
            self.log(f"[ERROR] Token request failed: {resp.text}", error=True)
            return False
            
        token_response = resp.json()
        self.access_token = token_response.get("access_token")
        self.refresh_token = token_response.get("refresh_token")
        
        # Save token for future use
        self.save_token(token_response)
        
        return bool(self.access_token)

    # ---------- Image Retrieval ---------- #
    def collect_image_links(self) -> list:
        """Return a list of deviation objects meeting 4 K criteria."""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        deviations = {}
        for tag in self.search_tags:
            params = {
                "tag": tag,
                "limit": LIMIT_PER_TAG,
                "mature_content": str(self.mature_content).lower(),  # "true" or "false"
            }
            resp = self.session.get(BROWSE_TAGS_URL, params=params, headers=headers, timeout=30)
            
            # Handle token expiration during API call
            if resp.status_code == 401:
                self.log("[INFO] Token expired during API call, attempting refresh...")
                if self.refresh_access_token():
                    headers = {"Authorization": f"Bearer {self.access_token}"}
                    resp = self.session.get(BROWSE_TAGS_URL, params=params, headers=headers, timeout=30)
                else:
                    self.log("[ERROR] Failed to refresh token, re-authentication required", error=True)
                    return []
                    
            if resp.status_code != 200:
                self.log(f"[WARN] /browse/tags failed for tag '{tag}': {resp.text}", error=True)
                continue
            for d in resp.json().get("results", []):
                # Skip premium/restricted content
                if d.get("is_downloadable") is False or d.get("is_premium") is True:
                    continue
                    
                content = d.get("content") or {}
                w, h = content.get("width", 0), content.get("height", 0)
                title = d.get("title", "").lower()
                
                # Check if image has valid content and meets size requirements
                if (w >= MIN_WIDTH and h >= MIN_HEIGHT) or "4k" in title or "uhd" in title:
                    # Additional check: ensure the image URL is accessible
                    if content.get("src") and not content.get("src").endswith((".gif", ".webm")):
                        deviations[d["deviationid"]] = d
                if len(deviations) >= DESIRED_RESULTS:
                    break
            if len(deviations) >= DESIRED_RESULTS:
                break
        return list(deviations.values())

    # ---------- Download & Set Wallpaper ---------- #
    def download_and_set_wallpaper(self, deviation: dict) -> bool:
        url = deviation.get("content", {}).get("src")
        if not url:
            self.log("[ERROR] No image URL found", error=True)
            return False
            
        # Validate file extension
        file_ext = os.path.splitext(url)[1].split("?")[0].lower()
        if not file_ext or file_ext not in [".jpg", ".jpeg", ".png", ".bmp"]:
            file_ext = ".jpg"
            
        tmp_fd, tmp_path = tempfile.mkstemp(suffix=file_ext)
        os.close(tmp_fd)

        try:
            self.log(f"[INFO] Downloading: {deviation.get('title', 'Unknown')}")
            with self.session.get(url, stream=True, timeout=60) as r:
                r.raise_for_status()
                
                # Check content type to ensure it's an image
                content_type = r.headers.get('content-type', '').lower()
                if not content_type.startswith('image/'):
                    self.log(f"[ERROR] Invalid content type: {content_type}", error=True)
                    return False
                
                # Download the image
                with open(tmp_path, "wb") as f:
                    for chunk in r.iter_content(1 << 16):
                        f.write(chunk)
                        
                # Verify file size (must be > 1KB to be a valid image)
                if os.path.getsize(tmp_path) < 1024:
                    self.log("[ERROR] Downloaded file is too small (likely not an image)", error=True)
                    os.unlink(tmp_path)
                    return False
                    
        except Exception as exc:
            self.log(f"[ERROR] Download failed: {exc}", error=True)
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            return False

        self.log(f"[INFO] Setting wallpaper: {deviation.get('title')}")
        SPI_SETDESKWALLPAPER = 0x14
        SPIF_UPDATEINIFILE = 0x01
        SPIF_SENDWININICHANGE = 0x02
        
        try:
            res = ctypes.windll.user32.SystemParametersInfoW(
                SPI_SETDESKWALLPAPER, 0, tmp_path, SPIF_UPDATEINIFILE | SPIF_SENDWININICHANGE
            )
            if not res:
                self.log("[ERROR] Failed to set wallpaper", error=True)
                return False
                
            # Verify the wallpaper was actually set by checking if file still exists
            if not os.path.exists(tmp_path):
                self.log("[ERROR] Wallpaper file was deleted during setting", error=True)
                return False
                
            self.log(f"[SUCCESS] Wallpaper set successfully: {tmp_path}")
            return True
            
        except Exception as exc:
            self.log(f"[ERROR] Wallpaper setting failed: {exc}", error=True)
            return False

# ---------- Main ---------- #
def main() -> bool:
    app = DeviantArtWallpaperSetter()
    
    # Load config first to determine if we should show terminal
    if not app.load_config():
        print("[ERROR] Failed to load configuration", file=sys.stderr)
        return False
    
    # Show header only if terminal is enabled
    if app.show_terminal:
        print("=== DeviantArt 4K Anime Wallpaper Setter ===")
    
    if not app.authenticate():
        return False

    images = app.collect_image_links()
    if not images:
        app.log("[ERROR] No suitable images found", error=True)
        return False

    # Try up to 3 different images if one fails
    max_attempts = min(3, len(images))
    for attempt in range(max_attempts):
        if attempt > 0:
            app.log(f"[INFO] Retry attempt {attempt + 1}/{max_attempts}")
            
        choice = random.choice(images)
        if app.download_and_set_wallpaper(choice):
            app.log("[SUCCESS] Wallpaper updated")
            return True
        else:
            # Remove failed image from list to avoid retrying it
            images.remove(choice)
            if not images:
                app.log("[ERROR] No more images to try", error=True)
                return False

    app.log("[ERROR] Failed to set wallpaper after all attempts", error=True)
    return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"[FATAL] {e}", file=sys.stderr)
        sys.exit(1)
