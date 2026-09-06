"""
CampusCare - Application Entry Point
--------------------------------------
Run this file to start the Flask development server.

Usage:
    python run.py
"""

import os
from app import create_app

# Determine config mode from environment (defaults to development)
config_name = os.getenv("FLASK_ENV", "development")

app = create_app(config_name)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "1") == "1"
    print("=" * 60)
    print("  CampusCare - Campus Maintenance & Complaint System")
    print("  REST API + Web Console")
    print(f"  Running at: http://127.0.0.1:{port}")
    print(f"  API Base:   http://127.0.0.1:{port}/api")
    print("=" * 60)
    app.run(host="0.0.0.0", port=port, debug=debug)
