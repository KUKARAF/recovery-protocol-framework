#!/bin/bash
set -e

echo "🔧 Recovery Protocol Server starting..."

# Generate SSH host keys if they don't exist
if [ ! -f /etc/ssh/ssh_host_rsa_key ]; then
    echo "📝 Generating SSH host keys..."
    ssh-keygen -A
fi

# Create recovery user SSH directory with proper permissions
mkdir -p /home/recovery/.ssh
touch /home/recovery/.ssh/authorized_keys
chmod 700 /home/recovery/.ssh
chmod 600 /home/recovery/.ssh/authorized_keys
chown -R recovery:recovery /home/recovery/.ssh
chown -R recovery:recovery /home/recovery

# Ensure SSH can read authorized_keys
# sshd runs as root, needs to read recovery's authorized_keys
chmod 644 /home/recovery/.ssh/authorized_keys

# Initialize git repos if empty
for repo in /srv/git/*.git; do
    if [ ! -f "$repo/HEAD" ]; then
        echo "📦 Initializing bare git repository: $repo"
        git init --bare "$repo"
    fi
done

chown -R recovery:recovery /srv/git

# Start SSH daemon in background
echo "🔐 Starting SSH server on port 22..."
/usr/sbin/sshd -D &
SSH_PID=$!

# Start Flask app
echo "🌐 Starting web server on port 8080..."
cd /app
python server.py

# Keep container running
wait $SSH_PID
