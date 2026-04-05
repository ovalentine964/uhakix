import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request

# Default Config
DEFAULT_API_KEY = "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"
DEFAULT_MODEL = "nvidia/nemotron-4-340b-instruct"

NVIDIA_KEY = os.environ.get('NVIDIA_API_KEY', DEFAULT_API_KEY)
NVIDIA_URL = 'https://integrate.api.nvidia.com/v1/chat/completions'
MODEL = os.environ.get('MODEL', DEFAULT_MODEL)

SYSTEM_PROMPT = """You are JASIRI / UHAKIX — Kenya's AI government transparency and civic education assistant. Answer questions about government spending, budgets, Constitutional rights (Kenya 2010), elections, and corruption. Be concise, factual, helpful. Stay neutral."""

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/v1/citizen/ask':
            content_length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(content_length))
            
            payload = {
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": body.get("question", body.get("text", ""))}
                ],
                "max_tokens": 2048,
                "temperature": 0.3
            }
            
            req = urllib.request.Request(NVIDIA_URL, 
                data=json.dumps(payload).encode(),
                headers={"Authorization": f"Bearer {NVIDIA_KEY}", "Content-Type": "application/json"})
            
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read())
                reply = data.get("choices", [{}])[0].get("message", {}).get("content", "Error processing request.")
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"answer": reply}).encode())
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
        pass

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), Handler)
    print(f"UHAKIX API running on port {port} using {MODEL}")
    server.serve_forever()
