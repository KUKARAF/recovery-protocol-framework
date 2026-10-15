# Recovery Protocol Docker Setup

Full containerized recovery protocol server with SSH, Git, and Web interface.

## Build & Run with Podman

```bash
# Build the image
podman build -t recovery-protocol-server .

# Run the container (with podman or docker)
podman run -d \
  --name recovery-protocol \
  -p 2222:2222 \
  -p 8080:8080 \
  recovery-protocol-server

# Check logs
podman logs -f recovery-protocol

# Test it works
curl http://localhost:8080/
curl http://localhost:8080/status

# Stop
podman stop recovery-protocol
```

(Replace `podman` with `docker` if using Docker instead)

## Testing the System

### 1. Open Web Interface

```bash
# View intro page with degrading system
open http://localhost:8080/
# or
curl http://localhost:8080/
```

### 2. Register SSH Key

Generate an SSH key if you don't have one:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/test_key -N ""
```

Send your public key to the server:

```bash
# Manually post the key
curl -X POST http://localhost:8080/recover \
  -H "Content-Type: application/json" \
  -d "{\"sshKey\": \"$(cat ~/.ssh/test_key.pub)\"}"

# Response will be:
# {
#   "status": "success",
#   "user_id": "user_1729010400",
#   "message": "Recovery initialized. SSH key registered.",
#   "next_steps": { ... }
# }
```

### 3. Clone Repositories

```bash
# Configure SSH to use the test key and connect without host key checking
export GIT_SSH_COMMAND="ssh -i ~/.ssh/test_key -p 2222 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"

# Clone framework (using port 2222)
git clone ssh://recovery@localhost:2222/srv/git/framework.git test-framework

# Clone modules (using port 2222)
git clone ssh://recovery@localhost:2222/srv/git/modules.git test-modules
```

### 4. Run Local Validation

```bash
cd test-framework
source .venv/bin/activate
recovery validate --mission 1 --task sort_signals
```

### 5. Push to Best Time Branch

```bash
cd test-modules
git checkout -b best/time
echo "# Optimized solution" >> README.md
git add -A
git commit -m "Optimize sort_signals"
git push origin best/time
```

## Container Architecture

```
recovery-protocol-server (container)
├── SSH Server (openssh-server)
│   └── Handles git operations
├── Flask Web App (port 8080)
│   ├── GET / → serves intro.html
│   ├── POST /recover → registers SSH key
│   ├── GET /status → system status
│   └── GET /health → health check
├── Git Repositories
│   ├── /srv/git/framework.git (bare)
│   └── /srv/git/modules.git (bare)
└── Recovery User
    └── /home/recovery (home directory)
```

## API Endpoints

### GET /
Serves the interactive intro.html with degrading system experience.

**Response**: HTML page with blinking cursor and error cascades

### GET /status
Returns system status.

**Response**:
```json
{
  "status": "online",
  "timestamp": "2026-10-15T...",
  "users_registered": 1,
  "git_repos": {
    "framework": "/srv/git/framework.git",
    "modules": "/srv/git/modules.git"
  }
}
```

### POST /recover
Register SSH public key and initialize recovery environment.

**Request**:
```json
{
  "sshKey": "ssh-ed25519 AAAAC3NzaC1lZDI1... user@host"
}
```

**Response**:
```json
{
  "status": "success",
  "user_id": "user_1729010400",
  "message": "Recovery initialized. SSH key registered.",
  "next_steps": {
    "ssh_clone_framework": "git clone ssh://recovery@localhost:/srv/git/framework.git",
    "ssh_clone_modules": "git clone ssh://recovery@localhost:/srv/git/modules.git",
    "validate": "./validate --mission 1 --task sort_signals"
  }
}
```

### GET /health
Health check endpoint.

**Response**: 200 OK
```json
{
  "status": "healthy"
}
```

## Troubleshooting

### SSH Connection Refused
- Make sure port 22 is exposed: `-p 22:22`
- Check if container is running: `docker ps`
- View logs: `docker logs recovery-protocol`

### Cannot Clone Repository
- Verify SSH key is registered: `curl http://localhost:8080/status`
- Check SSH key format (must start with ssh-rsa, ssh-ed25519, etc.)
- Use proper SSH command with key: `GIT_SSH_COMMAND="ssh -i ~/.ssh/key" git clone ...`

### Web Server Not Responding
- Port 8080 might be in use: `lsof -i :8080`
- Check Flask app logs: `docker logs recovery-protocol`

### Permissions Error on Git Repo
- Container needs write access to volumes
- Rebuild if volumes are corrupted: `docker volume rm recovery_git`

## Environment Variables

- `FLASK_ENV` - Set to `development` for debug mode
- `PYTHONUNBUFFERED` - Set to `1` for real-time logs

## Next Steps

1. **Interactive Testing**: Open browser, type in terminal, watch system degrade
2. **SSH Key Registration**: Use the intro form to register
3. **Clone & Develop**: Clone repos and start solving challenges
4. **Push & Validate**: Push to best/* branches, trigger server-side validation
5. **Dashboard** (future): Add progress visualization to web UI

## Security Notes

- This is a **test/demo container** - not for production
- SSH keys are stored in plain text in authorized_keys
- No authentication on the Flask app (SSH key IS the auth)
- Container runs SSH daemon as root (standard for SSH containers)
- Network isolated to localhost by default

For production deployment, consider:
- Gitea for full Git hosting with web UI
- Reverse proxy (nginx) for HTTPS
- Database for user management
- Rate limiting and DDoS protection
- Proper secret management
