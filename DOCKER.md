# Recovery Protocol server (container)

The container runs sshd (git over ssh, port 2222) and the web app (port 8080):
the intro page, the CLI wheel download, and SSH key registration.

## Build, run, seed

Run from this folder (`recovery-protocol-framework/`):

```bash
podman rm -f recovery-protocol 2>/dev/null
podman build -t recovery-protocol-server .
podman run -d --name recovery-protocol -p 2222:2222 -p 8080:8080 recovery-protocol-server
./seed.sh   # pushes ../recovery-protocol-modules into the container's modules.git
```

Keys and repos live inside the container. A rebuild wipes registered keys, so
re-register after each rebuild and run `./seed.sh` again after each `podman run`.

## Player flow

1. Open `http://localhost:8080`, type to wake the system, paste your public key, submit.
2. Copy the one-line command the page gives you and paste it into a terminal
   (installs the CLI, clones the challenge repo, `cd`s in, runs `recovery` once).
3. Edit a task, run `recovery` again. It finds where you are on its own.
4. On a new best time, `recovery` pushes to `best/time` automatically.
5. The first time a task is solved, `recovery` benchmarks it (SPEED/SIZE)
   and records the reading to the server - view it any time at `/stats`,
   without going through the wake-up flow again.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | boot sequence + SSH key registration (first-time setup only) |
| POST | `/recover` | body `{"sshKey": "<public key>"}`; validates with ssh-keygen and registers |
| GET | `/dist/<wheel>` | CLI wheel built into the image |
| GET | `/stats` | standalone recovery-statistics page - no boot sequence |
| GET | `/roster` | modules/tasks that exist, read from the modules repo at HEAD |
| GET/POST | `/performance` | SPEED/SIZE benchmark readings from `recovery performance` |
| GET | `/status` | keys registered, CLI wheel name |
| GET | `/health` | liveness |

## Notes

- Podman rootless cannot bind 22, which is why git runs on 2222.
- `localhost` may resolve to `::1`. The web app listens dual-stack so both work.
- Smoke test used during development: `chromium --headless` driven over CDP
  (type into the page, submit the form, read the on-screen log).
