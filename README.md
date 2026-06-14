# Analog Training

Interactive trainer for reading analog watches without numerals — learn to glance at a bare dial and know the time instantly.

## Quick Start

```bash
python3 server.py
```

Open http://localhost:8742 — that's it.

## Lessons

Lessons use a progressive reduction approach: start with full numbers, then remove them as you improve. Each phase unlocks at 80% accuracy.

| # | Lesson | Skill |
|---|--------|-------|
| 2 | [Anchors with Numbers](http://localhost:8742/lessons/0002-numbered-anchors.html) | Read a clock — numbers → anchors only → blank dial |
| 3 | [Set the Clock](http://localhost:8742/lessons/0003-set-the-clock.html) | See digital time, place the hands — builds spatial memory |
| 1 | [Four Anchors](http://localhost:8742/lessons/0001-four-anchors.html) | Numberless dial drills at 5-minute precision |

Recommended order: 2 → 3 → 1.

## Progress Tracking

Every answer is saved to a local SQLite database (`progress.db`, git-ignored). View your stats at:

**[Dashboard](http://localhost:8742/dashboard.html)** — accuracy over time, response speed, per-lesson breakdowns, session history.

## Stack

- Python stdlib only (`http.server` + `sqlite3`) — zero dependencies
- Static HTML lessons with vanilla JS + Canvas
- Chart.js (CDN) for dashboard graphs

## Reference

- [Four Anchors Cheatsheet](http://localhost:8742/reference/four-anchors-cheatsheet.html)
