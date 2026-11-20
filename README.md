# Focus Log — v1.1

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
# Focus Log running at http://0.0.0.0:8000 (port comes from $PORT, default 8000)
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

Networking note: v1 bound `127.0.0.1`, which is why `--network host` was
needed. Since v1.1 the app binds `0.0.0.0`, so a plain port mapping
(`-p 8000:8000`) works too; host networking remains the verified setup.

## Roll back

```bash
podman --root "$HOME/workspace/coder-academy/tools/podman-storage" stop focus-log-v1
podman --root "$HOME/workspace/coder-academy/tools/podman-storage" rm focus-log-v1
# image localhost/focus-log:v1 is kept; re-run the `podman run` above to restore
```

## Known limits

- Tasks are in-memory only — a restart empties the list (cut-list item 1).
- No auth; anyone who can reach the port can add tasks (cut-list item 2).
- Fixed in v1.1: SIGTERM/SIGINT now shut the server down gracefully (the
  v1 server waited out the full 10 s grace period before SIGKILL).

## Deployment status

v1.1 is deploy-ready: it binds `0.0.0.0`, reads its port from `$PORT`,
and stops cleanly on SIGTERM — the three things hosted platforms require.

Public hosting was attempted on 2026-11-20 and parked by the owner's
decision: Render now requires a card on file even for its free tier, and
Hugging Face gates Docker Spaces behind its PRO subscription. Rather
than put a card on file for a capstone demo, the owner chose to keep the
project GitHub-only. The verified deployment remains the local Podman
container above; the Dockerfile in this repo will run unchanged on any
host that takes it.
