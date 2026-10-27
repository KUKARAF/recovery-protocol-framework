"""Recovery Protocol server: intro page, CLI download, and SSH key registration."""

import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

from flask import Flask, abort, jsonify, request, send_from_directory

APP_DIR = Path(__file__).resolve().parent
RECOVERY_HOME = Path("/home/recovery")
SSH_DIR = RECOVERY_HOME / ".ssh"
AUTHORIZED_KEYS = SSH_DIR / "authorized_keys"
REGISTRY = RECOVERY_HOME / ".recovery-db.json"
PERFORMANCE_LOG = RECOVERY_HOME / ".recovery-performance.json"
DIST_DIR = APP_DIR / "dist"
GIT_HOST_PORT = 2222
MODULES_BARE_REPO = Path("/srv/git/modules.git")

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


def load_performance():
    if PERFORMANCE_LOG.exists():
        return json.loads(PERFORMANCE_LOG.read_text())
    return {"runs": []}


def save_performance(data):
    PERFORMANCE_LOG.write_text(json.dumps(data, indent=2))


def _git_show(path_in_repo):
    """One file's content at HEAD of the modules bare repo, or None."""
    result = subprocess.run(
        ["git", "--git-dir", str(MODULES_BARE_REPO), "show", f"HEAD:{path_in_repo}"],
        capture_output=True, text=True,
    )
    return result.stdout if result.returncode == 0 else None


def _task_order(module_name, task_ids):
    """Prefer metadata.json's authored order - same convention the CLI's
    Validator.list_tasks uses - falling back to sorted names."""
    metadata_raw = _git_show(f"modules/{module_name}/metadata.json")
    if metadata_raw:
        try:
            data = json.loads(metadata_raw)
            ordered = [m["id"] for m in data.get("missions", []) if m.get("id") in task_ids]
            if ordered:
                return ordered
        except json.JSONDecodeError:
            pass
    return sorted(task_ids)


def list_module_roster():
    """Modules and their tasks, in authored order, read straight from the
    bare modules repo at HEAD.

    This is the same roster `recovery info`/`recovery validate` discover
    client-side from a checked-out clone, read here server-side instead so
    the stats page can show unsolved tasks too, not just ones that already
    have a recorded benchmark.
    """
    result = subprocess.run(
        ["git", "--git-dir", str(MODULES_BARE_REPO), "ls-tree", "-r", "--name-only", "HEAD"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return []

    modules = {}
    for path in result.stdout.splitlines():
        m = re.match(r"^modules/([^/]+)/tests/test_(.+)\.py$", path)
        if m:
            modules.setdefault(m.group(1), set()).add(m.group(2))

    return [
        {"id": module_name, "tasks": _task_order(module_name, task_ids)}
        for module_name, task_ids in sorted(modules.items())
    ]


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
    install = f"pip install http://{request.host}/dist/{wheel}" if wheel else None
    clone = f"git clone ssh://recovery@{host}:{GIT_HOST_PORT}/srv/git/modules.git"
    # One line covering the whole setup: install the CLI, clone the
    # challenge repo, cd into it, and run the CLI once - it finds where
    # you are on its own, so there's nothing else to type.
    command = f"{install} && {clone} && cd modules && recovery" if install else None
    return jsonify({
        "status": "success",
        "message": "Recovery SSH key registered.",
        "clone": clone,
        "install": install,
        "command": command,
    }), 200


@app.route("/performance", methods=["POST"])
def submit_performance():
    """Record one SPEED/SIZE (+ optional complexity class) benchmark
    reading from `recovery performance`."""
    data = request.get_json(silent=True) or {}
    required = ("module", "task", "time_ms_best", "time_ms_median", "size_lines")
    if not all(k in data for k in required):
        return jsonify({"status": "error", "error": "missing fields"}), 400

    log = load_performance()
    log["runs"].append({
        "module": data["module"],
        "task": data["task"],
        "time_ms_best": data["time_ms_best"],
        "time_ms_median": data["time_ms_median"],
        "size_lines": data["size_lines"],
        # Empirical estimates, not every task has one (no size to scale) -
        # None/absent means "not available", not "zero".
        "time_class": data.get("time_class"),
        "space_class": data.get("space_class"),
        "no_imports_bonus": bool(data.get("no_imports_bonus", False)),
        "recorded": datetime.now().isoformat(),
    })
    save_performance(log)
    return jsonify({"status": "success"}), 200


@app.route("/performance", methods=["GET"])
def get_performance():
    """All recorded benchmark readings, for the stats page."""
    return jsonify(load_performance())


@app.route("/roster", methods=["GET"])
def roster():
    """Which modules and tasks actually exist, read from the modules repo
    itself - so the stats page can show unsolved tasks, not just solved
    ones that happen to have a recorded benchmark."""
    return jsonify({"modules": list_module_roster()})


@app.route("/stats", methods=["GET"])
def stats_page():
    """Standalone recovery-statistics view: no boot sequence, no wake-up
    theater. For a player who's already recovering and just wants to check
    progress, not go through registration again."""
    return send_from_directory(APP_DIR, "stats.html")


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
