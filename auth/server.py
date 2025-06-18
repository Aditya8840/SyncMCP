import os
import json
import webbrowser
import http.server
import socketserver
import urllib.parse
from threading import Thread
import socket
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

class AuthServer:
    def __init__(self):
        self.credentials_file = os.getenv("SECRET_PATH")
        self.token_file = os.getenv("TOKEN_PATH")
        self.scopes = ['https://www.googleapis.com/auth/calendar']
        self.port_range = (3500, 3510)
        self.server = None
        self.credentials = None
        self.auth_completed = False
        
    def load_existing_credentials(self):
        """Load and validate existing credentials"""
        if not os.path.exists(self.token_file):
            return None
            
        try:
            creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)
            
            if creds and creds.valid:
                return creds
                
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                self.save_credentials(creds)
                return creds
                
        except Exception as e:
            print(f"⚠️ Error loading existing credentials: {e}")
            
        return None
    
    def save_credentials(self, credentials):
        """Save credentials to file"""
        try:
            with open(self.token_file, 'w') as token:
                token.write(credentials.to_json())
        except Exception as e:
            raise
    
    def find_available_port(self):
        """Find an available port in the specified range"""
        for port in range(*self.port_range):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    return port
            except OSError:
                continue
        return None
    
    def create_request_handler(self, flow):
        """Create HTTP request handler for OAuth callback"""
        auth_server = self
        
        class AuthHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/':
                    auth_url, _ = flow.authorization_url(prompt='consent')
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    
                    html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>Google Authentication</title>
                        <style>
                            body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }}
                            .auth-container {{ text-align: center; padding: 40px; background: #f9f9f9; border-radius: 10px; }}
                            .auth-button {{ display: inline-block; padding: 12px 24px; background: #4285f4; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                            .auth-button:hover {{ background: #357ae8; }}
                        </style>
                    </head>
                    <body>
                        <div class="auth-container">
                            <h1>Google Authentication</h1>
                            <p>Click the button below to authenticate with Google:</p>
                            <a href="{auth_url}" class="auth-button">Authenticate with Google</a>
                            <p><small>You'll be redirected to Google to sign in and grant permissions.</small></p>
                        </div>
                    </body>
                    </html>
                    """
                    self.wfile.write(html.encode())
                    
                elif self.path.startswith('/oauth2callback'):
                    parsed_url = urllib.parse.urlparse(self.path)
                    query_params = urllib.parse.parse_qs(parsed_url.query)
                    
                    code = query_params.get('code')
                    error = query_params.get('error')
                    
                    if error:
                        self.send_error_response(f"Authentication error: {error[0]}")
                        return
                        
                    if not code:
                        self.send_error_response("Authorization code not found")
                        return
                    
                    try:
                        flow.fetch_token(code=code[0])
                        credentials = flow.credentials
                        
                        auth_server.save_credentials(credentials)
                        auth_server.credentials = credentials
                        auth_server.auth_completed = True
                        
                        self.send_success_response()
                        
                    except Exception as e:
                        self.send_error_response(f"Failed to exchange code for tokens: {str(e)}")
                        
                else:
                    self.send_response(404)
                    self.send_header('Content-type', 'text/plain')
                    self.end_headers()
                    self.wfile.write(b'Page not found')
            
            def send_success_response(self):
                """Send success HTML response"""
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                html = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Authentication Successful</title>
                    <style>
                        body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; text-align: center; }
                        .success { color: #4CAF50; }
                        .container { padding: 40px; background: #f0f8f0; border-radius: 10px; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1 class="success">Authentication Successful!</h1>
                        <p>Your credentials have been saved successfully.</p>
                        <p>You can now close this window and return to your application.</p>
                    </div>
                    <script>
                        setTimeout(() => {
                            window.close();
                        }, 3000);
                    </script>
                </body>
                </html>
                """
                self.wfile.write(html.encode())
            
            def send_error_response(self, error_message):
                """Send error HTML response"""
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Authentication Failed</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; text-align: center; }}
                        .error {{ color: #f44336; }}
                        .container {{ padding: 40px; background: #fff0f0; border-radius: 10px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1 class="error">Authentication Failed</h1>
                        <p>{error_message}</p>
                        <p>Please try again or check the console for more details.</p>
                    </div>
                </body>
                </html>
                """
                self.wfile.write(html.encode())
            
            def log_message(self, format, *args):
                pass
        
        return AuthHandler
    
    def authenticate(self, open_browser=True):
        """Main authentication method"""
        
        existing_creds = self.load_existing_credentials()
        if existing_creds:
            self.credentials = existing_creds
            return True
        
        if not os.path.exists(self.credentials_file):
            return False
        
        port = self.find_available_port()
        if not port:
            return False
        
        try:
            flow = Flow.from_client_secrets_file(
                self.credentials_file,
                scopes=self.scopes,
                redirect_uri=f'http://localhost:{port}/oauth2callback'
            )
            
            handler = self.create_request_handler(flow)
            with socketserver.TCPServer(("localhost", port), handler) as httpd:
                self.server = httpd
                
                auth_url, _ = flow.authorization_url(prompt='consent')
                
                if open_browser:
                    try:
                        webbrowser.open(auth_url)
                    except Exception:
                        print("⚠️ Could not open browser automatically")
                
                while not self.auth_completed:
                    httpd.handle_request()
                
                return True
                
        except Exception as e:
            return False
    
    def get_credentials(self):
        """Get the authenticated credentials"""
        if not self.credentials:
            return None
        return self.credentials
    
    def is_authenticated(self):
        """Check if user is authenticated"""
        return self.credentials is not None
