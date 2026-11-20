# Focus Log — Capstone Brief

**One sentence:** For a solo developer whose tasks live in scattered notes
and get lost, Focus Log is a tiny task API that records one task at a time
so nothing slips — success is a task created with POST that shows up in
GET /tasks.

## Cut list (NOT in v1)
1. **Persistence** — tasks live only in memory; a restart empties the list.
   (Next: a SQLite file, same as lessons 62–64.)
2. **Auth / multi-user** — no login, no per-user lists; anyone who can
   reach the port can add tasks. (Next: the JWT/session pattern from
   lesson 65, or a single shared secret.)
3. **Edit / delete / complete endpoints** — v1 can only create and list.
   (Next: PATCH /tasks/{id} for done, DELETE for remove.)
4. **Due dates, priorities, tags** — a title is the whole task for now.
5. **A frontend UI** — v1 is API-only; curl is the client.

## What v1 does ship
- `GET /health` → `{"status": "ok", "tasks": N}`
- `POST /tasks` (title required, else clear 400) → 201 with the task
- `GET /tasks` → the list
- 4 service-behaviour tests (`test_app.py`, all passing)
- Lean container image `localhost/focus-log:v1` (124 MB), run and verified
  live with Podman; rollback is `podman stop` + `podman rm` (image kept).
