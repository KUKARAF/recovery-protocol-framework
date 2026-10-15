"""Recovery Protocol Server - Web interface and SSH key management."""

import os
import json
import subprocess
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Paths
RECOVERY_HOME = Path("/home/recovery")
SSH_DIR = RECOVERY_HOME / ".ssh"
SSH_DIR.mkdir(exist_ok=True)
AUTHORIZED_KEYS = SSH_DIR / "authorized_keys"
RECOVERY_DB = RECOVERY_HOME / ".recovery-db.json"

# Load/save recovery database
def load_db():
    if RECOVERY_DB.exists():
        with open(RECOVERY_DB) as f:
            return json.load(f)
    return {"users": {}}

def save_db(db):
    with open(RECOVERY_DB, 'w') as f:
        json.dump(db, f, indent=2)

def read_html():
    """Read intro.html from same directory as this script."""
    html_path = Path(__file__).parent / "intro.html"
    if html_path.exists():
        with open(html_path) as f:
            return f.read()
    return "<h1>intro.html not found</h1>"

# Routes

@app.route("/", methods=["GET"])
def index():
    """Serve the interactive degrading system intro."""
    html = read_html()
    return render_template_string(html)

@app.route("/recover", methods=["POST"])
def recover():
    """Register SSH public key and initialize recovery environment."""
    try:
        data = request.get_json()
        ssh_key = data.get("sshKey", "").strip()

        if not ssh_key:
            return jsonify({"error": "SSH key required"}), 400

        # Validate SSH key format (basic check)
        if not ssh_key.startswith(("ssh-rsa", "ssh-ed25519", "ssh-dss", "ecdsa-sha2")):
            return jsonify({"error": "Invalid SSH key format"}), 400

        # Load database
        db = load_db()

        # Create user entry if not exists
        user_id = f"user_{datetime.now().strftime('%s')}"
        db["users"][user_id] = {
            "created": datetime.now().isoformat(),
            "ssh_key": ssh_key,
            "status": "initialized",
        }
        save_db(db)

        # Add SSH key to authorized_keys
        with open(AUTHORIZED_KEYS, 'a') as f:
            f.write(f"command=\"/app/git-handler.sh\",no-port-forwarding,no-agent-forwarding {ssh_key}\n")

        # Set correct permissions
        AUTHORIZED_KEYS.chmod(0o600)
        SSH_DIR.chmod(0o700)

        # Create user git workspace
        user_dir = RECOVERY_HOME / user_id
        user_dir.mkdir(exist_ok=True)

        # Initialize user's clones
        framework_path = user_dir / "framework"
        modules_path = user_dir / "modules"

        # Clone from bare repos
        subprocess.run(
            ["git", "clone", "file:///srv/git/framework.git", str(framework_path)],
            check=False,
            capture_output=True
        )
        subprocess.run(
            ["git", "clone", "file:///srv/git/modules.git", str(modules_path)],
            check=False,
            capture_output=True
        )

        return jsonify({
            "status": "success",
            "user_id": user_id,
            "message": "Recovery initialized. SSH key registered.",
            "next_steps": {
                "ssh_clone_framework": f"git clone ssh://recovery@localhost/srv/git/framework.git",
                "ssh_clone_modules": f"git clone ssh://recovery@localhost/srv/git/modules.git",
                "validate": "./validate --mission 1 --task sort_signals"
            }
        }), 200

    except (ValueError, IOError, subprocess.CalledProcessError) as e:
        return jsonify({"error": str(e)}), 500

@app.route("/status", methods=["GET"])
def status():
    """Get system status."""
    db = load_db()
    return jsonify({
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "users_registered": len(db.get("users", {})),
        "git_repos": {
            "framework": "/srv/git/framework.git",
            "modules": "/srv/git/modules.git"
        }
    })

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy"}), 200

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Server error"}), 500

if __name__ == "__main__":
    # Ensure permissions
    SSH_DIR.mkdir(exist_ok=True)
    SSH_DIR.chmod(0o700)

    if AUTHORIZED_KEYS.exists():
        AUTHORIZED_KEYS.chmod(0o600)

    # Run Flask
    app.run(host="0.0.0.0", port=8080, debug=True)
