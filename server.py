"""Recovery Protocol server: intro page, CLI download, and SSH key registration."""

import json
import subprocess
from datetime import datetime
from pathlib import Path

from flask import Flask, abort, jsonify, request, send_from_directory

APP_DIR = Path(__file__).resolve().parent
RECOVERY_HOME = Path("/home/recovery")
SSH_DIR = RECOVERY_HOME / ".ssh"
AUTHORIZED_KEYS = SSH_DIR / "authorized_keys"
REGISTRY = RECOVERY_HOME / ".recovery-db.json"
DIST_DIR = APP_DIR / "dist"
GIT_HOST_PORT = 2222

app = Flask(__name__)


def load_registry():
    if REGISTRY.exists():
        return json.loads(REGISTRY.read_text())
    return {"users": {}}


def save_registry(registry):
    REGISTRY.write_text(json.dumps(registry, indent=2))


def key_is_valid(public_key):
    """Let ssh-keygen decide whether this is a real public key."""
    if "\n" in public_key or "\r" in public_key:
        return False
    result = subprocess.run(
        ["ssh-keygen", "-l", "-f", "-"],
        input=public_key + "\n",
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def cli_wheel_name():
    wheels = sorted(DIST_DIR.glob("*.whl"))
    return wheels[-1].name if wheels else None


@app.route("/", methods=["GET"])
def index():
    """Serve the degrading-system intro page."""
    return send_from_directory(APP_DIR, "intro.html")


@app.route("/dist/<path:filename>", methods=["GET"])
def dist(filename):
    """Serve the CLI wheel that players install locally."""
    if not (DIST_DIR / filename).is_file():
        abort(404)
    return send_from_directory(DIST_DIR, filename, as_attachment=True)


@app.route("/recover", methods=["POST"])
def recover():
    """Register an SSH public key. The key is the player's only credential."""
    data = request.get_json(silent=True) or {}
    public_key = (data.get("sshKey") or "").strip()

    if not public_key:
        return jsonify({"status": "error", "error": "SSH key required"}), 400
    if not key_is_valid(public_key):
        return jsonify({"status": "error", "error": "Not a valid SSH public key"}), 400

    existing = AUTHORIZED_KEYS.read_text().splitlines() if AUTHORIZED_KEYS.exists() else []
    if public_key not in existing:
        with AUTHORIZED_KEYS.open("a") as f:
            f.write(public_key + "\n")
    AUTHORIZED_KEYS.chmod(0o600)

    registry = load_registry()
    user_id = f"user_{datetime.now().strftime('%s')}"
    registry["users"][user_id] = {
        "created": datetime.now().isoformat(),
        "key_type": public_key.split()[0],
    }
    save_registry(registry)

    wheel = cli_wheel_name()
    host = request.host.split(":")[0]
    return jsonify({
        "status": "success",
        "message": "Recovery SSH key registered.",
        "clone": f"git clone ssh://recovery@{host}:{GIT_HOST_PORT}/srv/git/modules.git",
        "install": f"pip install http://{request.host}/dist/{wheel}" if wheel else None,
    }), 200


@app.route("/status", methods=["GET"])
def status():
    registry = load_registry()
    keys = AUTHORIZED_KEYS.read_text().splitlines() if AUTHORIZED_KEYS.exists() else []
    return jsonify({
        "status": "online",
        "keys_registered": len(keys),
        "users_registered": len(registry["users"]),
        "cli_wheel": cli_wheel_name(),
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200


@app.errorhandler(404)
def not_found(_):
    return jsonify({"error": "Not found"}), 404


if __name__ == "__main__":
    SSH_DIR.mkdir(mode=0o700, exist_ok=True)
    AUTHORIZED_KEYS.touch(mode=0o600, exist_ok=True)
    # "::" is dual-stack on Linux: serves ::1 (localhost) and 127.0.0.1
    app.run(host="::", port=8080, debug=False)
