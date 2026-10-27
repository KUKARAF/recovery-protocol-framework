# Recovery Protocol

A git-based, Illuminae-flavoured Python learning game. An AI system recovering
from catastrophic failure rebuilds its capabilities one task at a time — you
write the code that restores it.

## Quick Start (podman)

This is the default way to run it: a container serves an intro page, lets you
register an SSH key, and hands you a CLI + the challenge repo over git.

```bash
# From this folder (recovery-protocol-framework/)
podman rm -f recovery-protocol 2>/dev/null
podman build -t recovery-protocol-server .
podman run -d --name recovery-protocol -p 2222:2222 -p 8080:8080 recovery-protocol-server
./seed.sh   # pushes ../recovery-protocol-modules into the container's modules.git
```

`seed.sh` expects `recovery-protocol-modules` cloned as a sibling directory:

```bash
git clone https://github.com/KUKARAF/recovery-protocol-modules.git ../recovery-protocol-modules
```

Keys and repos live inside the container. A rebuild wipes registered keys —
re-register through the intro page and run `./seed.sh` again after each
`podman run`.

### Play

1. Open `http://localhost:8080`, type to wake the system, paste your SSH
   public key, submit.
2. `pip install http://localhost:8080/dist/resurrection_protocol-0.1.0-py3-none-any.whl`
3. `git clone ssh://recovery@localhost:2222/srv/git/modules.git && cd modules`
4. Edit a task, e.g. `modules/back_to_basics_module/tasks/sort_signals.py`
5. `recovery validate --module back_to_basics --task sort_signals`
6. On a new best time: `git push origin HEAD:best/time`

### Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | intro page |
| POST | `/recover` | body `{"sshKey": "<public key>"}`; validates and registers |
| GET | `/dist/<wheel>` | CLI wheel built into the image |
| GET | `/status` | keys registered, CLI wheel name |
| GET | `/health` | liveness |

### Notes

- Podman rootless cannot bind 22, which is why git runs on 2222.
- `localhost` may resolve to `::1`. The web app listens dual-stack so both work.

## Local Dev (no container)

For working on the game itself, or if you'd rather run everything locally
without the SSH/web layer:

```bash
uv sync
source .venv/bin/activate

# Clone the modules repo as your game folder's `modules/` directory
git clone https://github.com/KUKARAF/recovery-protocol-modules.git recovery-game
cd recovery-game   # this folder already contains modules/back_to_basics_module

recovery info                                    # list modules found in ./modules
recovery validate                                 # run all tests for the (only) module
recovery validate --module back_to_basics --task sort_signals   # one task
```

`recovery validate` resolves module/task names loosely (`back_to_basics` or
`back_to_basics_module` both work) and reports a timing comparison against
your best recorded run when a single task passes.

## Modules

Challenge content lives in the separate
[recovery-protocol-modules](https://github.com/KUKARAF/recovery-protocol-modules)
repo, not in this one. **back_to_basics_module** currently covers data
manipulation fundamentals:

- sort_signals
- extract_callsign
- decode_status
- filter_logs
- merge_signals

Future modules planned: file_io, data_structures, algorithms, concurrency.

## Project Structure

```
recovery-protocol-framework/
├── src/resurrection/        # Installable CLI package
│   ├── cli.py              # `recovery` entry point (validate, info)
│   ├── validator.py        # Discovers modules/, runs pytest
│   ├── metrics.py          # Best-time tracking
│   └── tui/                # Terminal output (Rich)
├── server.py                # Flask app: intro page, key registration, wheel download
├── Dockerfile / entrypoint.sh  # Container: sshd (git) + web app
├── seed.sh                  # Dev tool: push modules repo into the container
├── backstory.md / character.md  # Narrative
└── pyproject.toml           # uv project config
```

---

**Welcome to the Recovery Protocol.** Every passing test is a capability restored.
