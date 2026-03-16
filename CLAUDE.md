# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Games

No build step or server required. Open any HTML file directly in a browser:

```
open tictactoe.html
open shooter.html
```

## Repository Workflow

Every change should be committed and pushed to GitHub:

```bash
git add <file>
git commit -m "descriptive message"
git push
```

GitHub repo: https://github.com/nherman-cbi/noas-project

## Architecture

Each game is a **single self-contained HTML file** — all CSS and JavaScript are inline. No external dependencies, no bundler, no framework.

### shooter.html

Class-based game engine running on a fixed 800×600 Canvas (CSS-scaled to fit the viewport):

- **`CONFIG`** — all tunable constants (speeds, HP, colors, scoring)
- **`LEVELS[]`** — 5 level definitions with per-wave grunt/tank counts and speed multipliers
- **`AudioManager`** — Web Audio API synth sounds, lazy-initialized on first user click (required by browser autoplay policy)
- **`InputManager`** — keyboard + mouse state; corrects mouse coordinates for CSS canvas scaling
- **`Particle`** — square particles with exponential drag and alpha fade
- **`Bullet`** — rendered as a line trail from `prevX/prevY` to `x/y`
- **`Enemy` / `EnemyGrunt` / `EnemyTank`** — base class + two subtypes with different HP, speed, shoot cooldown, and draw logic
- **`Player`** — WASD/arrow movement, mouse aim, 4-frame walk animation, iframes after hit
- **`Game`** — state machine (`MENU → PLAYING → LEVEL_COMPLETE → PLAYING → VICTORY/GAME_OVER`), game loop, wave spawner, collision resolution, render dispatch

Game loop uses `requestAnimationFrame` with dt capped at 50ms to prevent spiral-of-death on backgrounded tabs.

### tictactoe.html

Simple DOM-based Tic Tac Toe — no canvas, no classes.
