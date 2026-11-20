# Focus Log — v1

A tiny task API (Python standard library only). The capstone product for
lesson 94 of the Become a Coder & Programmer curriculum.

**Brief:** for a solo developer whose tasks live in scattered notes and get
lost, Focus Log records one task at a time so nothing slips. Success: a task
created with POST shows up in `GET /tasks`.

## Endpoints

| Method | Path | Result |
| --- | --- | --- |
| GET | `/health` | `{"status": "ok", "tasks": N}` |
| POST | `/tasks` `{"title": "..."}` | 201 with the created task; 400 `{"error": "title is required"}` for an empty/missing title |
| GET | `/tasks` | JSON list of tasks |

## Run it (no dependencies)

```bash
python3 app.py
# Focus Log running at http://127.0.0.1:8000
curl http://127.0.0.1:8000/health
curl -X POST http://127.0.0.1:8000/tasks -H "Content-Type: application/json" \
  -d '{"title": "Ship v1"}'
curl http://127.0.0.1:8000/tasks
```

Stop with Ctrl+C (or kill the process).

## Test it

```bash
python3 test_app.py
# 4 tests: health, create-then-list, empty title → 400 (and nothing stored),
# unknown route → 404
```

## Run it as a container (Podman)

Podman here is the durable static install under
`~/workspace/coder-academy/tools/podman-linux-amd64/`; `/usr/local/bin`
was wiped by a VM restart, so the helpers need explicit config — see
`containers.conf` (conmon + netavark paths) and `~/.config/containers/policy.json`.

```bash
export PATH="$HOME/workspace/coder-academy/tools/podman-linux-amd64/usr/local/bin:$PATH"
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/tmp/podman-run}"
export CONTAINERS_CONF="$HOME/workspace/coder-academy/lesson-94/containers.conf"
podman --root "$HOME/workspace/coder-academy/tools/podman-storage" build -t focus-log:v1 .
podman --root "$HOME/workspace/coder-academy/tools/podman-storage" run -d \
  --network host --name focus-log-v1 localhost/focus-log:v1
curl http://127.0.0.1:8000/health   # {"status": "ok", "tasks": 0}
```

Why `--network host`: `app.py` binds `127.0.0.1`, so a port mapping to the
container's IP would not reach it; host networking makes the container's
loopback the host's loopback.

## Roll back

```bash
podman --root "$HOME/workspace/coder-academy/tools/podman-storage" stop focus-log-v1
podman --root "$HOME/workspace/coder-academy/tools/podman-storage" rm focus-log-v1
# image localhost/focus-log:v1 is kept; re-run the `podman run` above to restore
```

## Known v1 limits

- Tasks are in-memory only — a restart empties the list (cut-list item 1).
- No auth; anyone who can reach the port can add tasks (cut-list item 2).
- The server does not handle SIGTERM gracefully: `podman stop` waits the
  full 10 s grace period, then SIGKILLs it. A v1.1 fix is a signal handler
  that calls `server.shutdown()`.

## Next deployment step (not done here)

Push the image to a registry and run it behind HTTPS on a VPS — the
lesson-78 pattern (PM2/nginx) or a hosted container service. Blockers:
no registry account is configured for this project and there is no domain
or VPS assigned to it, so the verified deployment for v1 is the local
Podman container above.
