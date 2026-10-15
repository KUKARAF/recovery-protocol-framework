#!/bin/bash
# Git command wrapper for Recovery Protocol SSH access
# Only allows git-upload-pack and git-receive-pack

case "$SSH_ORIGINAL_COMMAND" in
  git-upload-pack*)
    # Allow git clone/fetch
    exec $SSH_ORIGINAL_COMMAND
    ;;
  git-receive-pack*)
    # Allow git push
    exec $SSH_ORIGINAL_COMMAND
    ;;
  git-upload-archive*)
    # Allow git archive
    exec $SSH_ORIGINAL_COMMAND
    ;;
  *)
    echo "Only git commands are allowed"
    exit 1
    ;;
esac
