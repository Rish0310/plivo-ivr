import subprocess, sys, os

# Install waitress if needed
subprocess.run([sys.executable, "-m", "pip", "install", "waitress", "flask", "requests", "--quiet"], 
               capture_output=True)

from waitress import serve
from app import app

print("=" * 50)
print("✅ IVR running on http://localhost:5000")
print("=" * 50)

serve(app, host="0.0.0.0", port=5000, trusted_proxy="*", 
      trusted_proxy_headers="x-forwarded-for x-forwarded-host x-forwarded-proto",
      clear_untrusted_proxy_headers=False)
