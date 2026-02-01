#!/usr/bin/env python3
"""HTTP server with JSON save endpoint and password protection.
Works locally and on cloud platforms (Railway, Render, Fly.io)."""

import http.server
import json
import os
import shutil
import hmac
import hashlib
import secrets
import time
import urllib.parse
from datetime import datetime
from http.cookies import SimpleCookie

DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get('DATA_DIR', DIR)
JSON_FILE = os.path.join(DATA_DIR, 'ads_data.json')
PORT = int(os.environ.get('PORT', 8080))

# Auth config — set APP_PASSWORD env var to enable protection
APP_PASSWORD = os.environ.get('APP_PASSWORD', '')
SECRET_KEY = os.environ.get('APP_SECRET', secrets.token_hex(32))
SESSION_MAX_AGE = 60 * 60 * 24  # 24 hours

# On first deploy, copy ads_data.json to persistent volume if needed
if DATA_DIR != DIR and not os.path.exists(JSON_FILE):
    src = os.path.join(DIR, 'ads_data.json')
    if os.path.exists(src):
        os.makedirs(DATA_DIR, exist_ok=True)
        shutil.copy2(src, JSON_FILE)
        print(f'Copied ads_data.json to {DATA_DIR}')

LOGIN_PAGE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Login - Fowler Homes Ads Editor</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #f5f6fa;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .login-box {
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 2px 12px rgba(0,0,0,.08), 0 0 0 1px rgba(0,0,0,.04);
    padding: 40px;
    width: 100%;
    max-width: 380px;
  }
  .login-box h1 {
    font-size: 20px;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 4px;
  }
  .login-box p {
    font-size: 13px;
    color: #64748b;
    margin-bottom: 24px;
  }
  .field {
    margin-bottom: 16px;
  }
  .field label {
    display: block;
    font-size: 12px;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 6px;
  }
  .field input {
    width: 100%;
    padding: 10px 14px;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    font-size: 14px;
    outline: none;
    transition: border-color .15s;
  }
  .field input:focus { border-color: #e94560; }
  .btn {
    width: 100%;
    padding: 10px;
    border: none;
    border-radius: 6px;
    background: #e94560;
    color: #fff;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: background .15s;
  }
  .btn:hover { background: #c93550; }
  .error {
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 6px;
    padding: 8px 14px;
    font-size: 13px;
    color: #b91c1c;
    margin-bottom: 16px;
  }
</style>
</head>
<body>
<div class="login-box">
  <h1>Fowler Homes Ads</h1>
  <p>Enter the password to access the ad editor.</p>
  {error}
  <form method="POST" action="/login">
    <div class="field">
      <label for="password">Password</label>
      <input type="password" id="password" name="password" autofocus required>
    </div>
    <button type="submit" class="btn">Sign In</button>
  </form>
</div>
</body>
</html>'''


def make_token(timestamp):
    """Create an HMAC-signed session token."""
    msg = f'session:{timestamp}'.encode()
    sig = hmac.new(SECRET_KEY.encode(), msg, hashlib.sha256).hexdigest()
    return f'{timestamp}:{sig}'


def verify_token(token):
    """Verify a session token is valid and not expired."""
    if not token:
        return False
    try:
        parts = token.split(':')
        if len(parts) != 2:
            return False
        timestamp, sig = parts
        timestamp = int(timestamp)
        if time.time() - timestamp > SESSION_MAX_AGE:
            return False
        expected = make_token(timestamp)
        return hmac.compare_digest(token, expected)
    except (ValueError, TypeError):
        return False


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)

    def get_session_token(self):
        """Extract session token from cookies."""
        cookie_header = self.headers.get('Cookie', '')
        cookie = SimpleCookie()
        try:
            cookie.load(cookie_header)
        except Exception:
            return None
        if 'session' in cookie:
            return cookie['session'].value
        return None

    def is_authenticated(self):
        """Check if request has a valid session."""
        if not APP_PASSWORD:
            return True  # No password set, auth disabled
        return verify_token(self.get_session_token())

    def send_login_page(self, error=''):
        """Serve the login page."""
        error_html = f'<div class="error">{error}</div>' if error else ''
        page = LOGIN_PAGE.replace('{error}', error_html)
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(page.encode('utf-8'))

    def set_session_cookie(self):
        """Set a signed session cookie."""
        token = make_token(int(time.time()))
        cookie_parts = [
            f'session={token}',
            f'Max-Age={SESSION_MAX_AGE}',
            'Path=/',
            'HttpOnly',
            'SameSite=Lax',
        ]
        # Add Secure flag for non-localhost
        host = self.headers.get('Host', 'localhost')
        if 'localhost' not in host and '127.0.0.1' not in host:
            cookie_parts.append('Secure')
        self.send_header('Set-Cookie', '; '.join(cookie_parts))

    def do_GET(self):
        # Login page is always accessible
        if self.path == '/login':
            self.send_login_page()
            return

        # Everything else requires auth
        if not self.is_authenticated():
            self.send_response(302)
            self.send_header('Location', '/login')
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            return

        # Serve ads_data.json from DATA_DIR (persistent volume)
        if self.path == '/ads_data.json':
            try:
                with open(JSON_FILE, 'r', encoding='utf-8') as f:
                    data = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Cache-Control', 'no-cache')
                self.end_headers()
                self.wfile.write(data.encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())
            return
        # Redirect root to editor
        if self.path == '/':
            self.send_response(302)
            self.send_header('Location', '/ads_editor.html')
            self.end_headers()
            return
        super().do_GET()

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)

        # Login handler
        if self.path == '/login':
            params = urllib.parse.parse_qs(body.decode('utf-8'))
            password = params.get('password', [''])[0]

            if hmac.compare_digest(password, APP_PASSWORD):
                self.send_response(302)
                self.set_session_cookie()
                self.send_header('Location', '/ads_editor.html')
                self.send_header('Cache-Control', 'no-store')
                self.end_headers()
                print(f'  Login successful from {self.client_address[0]}')
            else:
                print(f'  Failed login attempt from {self.client_address[0]}')
                self.send_login_page(error='Incorrect password. Please try again.')
            return

        # Logout handler
        if self.path == '/logout':
            self.send_response(302)
            self.send_header('Set-Cookie', 'session=; Max-Age=0; Path=/; HttpOnly; SameSite=Lax')
            self.send_header('Location', '/login')
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            return

        # All other POST endpoints require auth
        if not self.is_authenticated():
            self.send_response(401)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Not authenticated'}).encode())
            return

        if self.path == '/save':
            try:
                data = json.loads(body)
                # Keep a backup before saving
                if os.path.exists(JSON_FILE):
                    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                    backup = JSON_FILE.replace('.json', f'_backup_{ts}.json')
                    shutil.copy2(JSON_FILE, backup)
                    # Keep only last 10 backups
                    backups = sorted([
                        f for f in os.listdir(DATA_DIR)
                        if f.startswith('ads_data_backup_') and f.endswith('.json')
                    ])
                    for old in backups[:-10]:
                        os.remove(os.path.join(DATA_DIR, old))
                with open(JSON_FILE, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'ok': True}).encode())
                print(f'  Saved ads_data.json ({len(body):,} bytes)')
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def log_message(self, format, *args):
        # Suppress default logging for static files to reduce noise
        if 'login' in str(args) or 'save' in str(args) or '302' in str(args):
            super().log_message(format, *args)


if APP_PASSWORD:
    print(f'Auth ENABLED — password required to access editor')
else:
    print(f'Auth DISABLED — set APP_PASSWORD env var to enable')
print(f'Serving at http://localhost:{PORT}/ads_editor.html')
print(f'JSON file: {JSON_FILE}')
print(f'Data dir:  {DATA_DIR}')
http.server.HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
