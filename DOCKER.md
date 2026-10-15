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
2. `pip install http://localhost:8080/dist/resurrection_protocol-0.1.0-py3-none-any.whl`
3. `git clone ssh://recovery@localhost:2222/srv/git/modules.git && cd modules`
4. `recovery validate --module back_to_basics --task sort_signals`
5. On a new best time: `git push origin HEAD:best/time`

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | intro page |
| POST | `/recover` | body `{"sshKey": "<public key>"}`; validates with ssh-keygen and registers |
| GET | `/dist/<wheel>` | CLI wheel built into the image |
| GET | `/status` | keys registered, CLI wheel name |
| GET | `/health` | liveness |

## Notes

- Podman rootless cannot bind 22, which is why git runs on 2222.
- `localhost` may resolve to `::1`. The web app listens dual-stack so both work.
- Smoke test used during development: `chromium --headless` driven over CDP
  (type into the page, submit the form, read the on-screen log).
