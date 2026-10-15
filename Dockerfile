FROM python:3.11-slim

# Install SSH, git, and system dependencies
RUN apt-get update && apt-get install -y \
    openssh-server \
    git \
    sudo \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create ssh directory and configure SSH
RUN mkdir -p /run/sshd /home/recovery/.ssh && \
    chmod 700 /home/recovery/.ssh

# Create recovery user with git-shell (restricted shell for git-only access)
RUN useradd -m -d /home/recovery -s /usr/bin/git-shell recovery && \
    echo "recovery:recovery" | chpasswd

# Set up git repository directories
RUN mkdir -p /srv/git/framework.git /srv/git/modules.git && \
    chown -R recovery:recovery /srv/git

# Initialize bare git repositories
RUN cd /srv/git/framework.git && git init --bare && \
    cd /srv/git/modules.git && git init --bare && \
    chown -R recovery:recovery /srv/git

# Copy SSH config
COPY sshd_config /etc/ssh/sshd_config

# Install Python dependencies
RUN pip install flask flask-cors rich typer pytest gitpython

# Create app directory
WORKDIR /app

# Copy the web app
COPY server.py /app/server.py
COPY intro.html /app/intro.html

# Copy entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose ports (2222 for SSH, 8080 for web)
EXPOSE 2222 8080

ENTRYPOINT ["/entrypoint.sh"]
