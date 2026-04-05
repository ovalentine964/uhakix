import urllib.request
import time
import sys

URL = "https://uhakix-api.onrender.com/health"

def ping():
    try:
        req = urllib.request.Request(URL)
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"[{time.strftime('%H:%M:%S')}] Success: {resp.status}")
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] Error: {e}")

if __name__ == "__main__":
    while True:
        ping()
        # Render sleeps after 15 mins, so ping every 10 mins
        time.sleep(600) 
