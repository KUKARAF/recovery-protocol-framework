#!/bin/bash
# Dev tool: push the modules repo into the running container's bare repo.
# Run after `podman run`. Keys are still registered through the intro page.
set -euo pipefail

CONTAINER="${CONTAINER:-recovery-protocol}"
HERE="$(cd "$(dirname "$0")" && pwd)"
MODULES="${MODULES:-$HERE/../recovery-protocol-modules}"

podman exec "$CONTAINER" rm -rf /tmp/seed-modules
podman cp "$MODULES/." "$CONTAINER:/tmp/seed-modules"
podman exec "$CONTAINER" sh -c '
  set -e
  cd /tmp/seed-modules
  git push -q --force /srv/git/modules.git HEAD:refs/heads/main
  git -C /srv/git/modules.git symbolic-ref HEAD refs/heads/main
  chown -R recovery:recovery /srv/git
  rm -rf /tmp/seed-modules
'
echo "[seed] modules.git seeded from $MODULES"
