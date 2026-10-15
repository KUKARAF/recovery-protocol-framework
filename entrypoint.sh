#!/bin/bash
set -e

echo "[recovery] generating host keys if missing"
ssh-keygen -A >/dev/null

# Keys are re-registered through the intro page after each container start
chown -R recovery:recovery /home/recovery /srv/git
chmod 700 /home/recovery/.ssh
touch /home/recovery/.ssh/authorized_keys
chown recovery:recovery /home/recovery/.ssh/authorized_keys
chmod 600 /home/recovery/.ssh/authorized_keys

echo "[recovery] sshd listening on 2222 (git)"
/usr/sbin/sshd -D -e &

echo "[recovery] web listening on 8080 (intro, CLI download, key registration)"
cd /app
exec python server.py
