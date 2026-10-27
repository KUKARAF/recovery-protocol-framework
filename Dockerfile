FROM python:3.11-slim

# sshd for git access, git itself, and ssh-keygen for key validation
RUN apt-get update && apt-get install -y --no-install-recommends \
        openssh-server \
        git \
    && rm -rf /var/lib/apt/lists/*

# Git defaults: branch 'main', and trust the bare repos regardless of owner
# (sshd and the web app run as root, the repos are owned by 'recovery')
RUN git config --system init.defaultBranch main && \
    git config --system --add safe.directory '*'

# Player account: real login shell so sshd's git-over-ssh works
# '*' rather than the default '!' lock: OpenSSH without PAM rejects locked accounts
# as "invalid user" before it ever checks the public key
RUN useradd -m -d /home/recovery -s /bin/bash recovery && \
    usermod -p '*' recovery && \
    mkdir -p /home/recovery/.ssh /run/sshd && \
    chmod 700 /home/recovery/.ssh && \
    chown -R recovery:recovery /home/recovery

# Bare repositories. Content is pushed in by seed.sh
RUN mkdir -p /srv/git && \
    git init --bare /srv/git/framework.git && \
    git init --bare /srv/git/modules.git && \
    chown -R recovery:recovery /srv/git

COPY sshd_config /etc/ssh/sshd_config

# Python side: web app + CLI wheel served to players
RUN pip install --no-cache-dir flask
WORKDIR /build
COPY pyproject.toml README.md /build/
COPY src /build/src
RUN pip install --no-cache-dir build && \
    python -m build --wheel --outdir /app/dist /build && \
    rm -rf /build

WORKDIR /app
COPY server.py intro.html stats.html /app/
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 2222 8080

ENTRYPOINT ["/entrypoint.sh"]
