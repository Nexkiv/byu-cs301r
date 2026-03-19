# Repository Guidelines

## Project Structure & Module Organization
- `index.html` holds the single-page app markup and layout.
- `style.css` defines the visual system, layout, and component styling.
- `app.js` contains all client-side logic (game state, drag-and-drop, scoring, validation).
- `write_up.md` is project documentation/notes.

There are no build artifacts, backend services, or test directories in this repository.

## Game Rules & Assumptions
- Implements Academic Games League of America Equations tournament flow (no timer, no variations).
- Local hot-seat play for 2–3 players.
- Goal is set by drag-and-drop (1–6 cubes) and locked before R/P/F moves.
- Required/Permitted/Forbidden are drag-and-drop and apply per round for all players.
- Final solutions are typed (not drag-and-drop) and validated against Goal and R/P/F.
- Challenge terminology uses `Now` and `Never` (Never is common tournament wording).
- Scoring currently gives baseline 2 points to non-winning roles in challenge resolution.

## Cube Set
- 24 cubes: 6 each of red, blue, green, black.
- Each color uses identical templates (6 identical cubes per color):
  - green: `5, 4, x, -, 6, ^`
  - red: `0, 2, +, 3, -, 1`
  - blue: `0, 2, ÷, x, 3, 1`
  - black: `7, ÷, √, 8, 9, +`

## Build, Test, and Development Commands
This is a static browser app; no build step is required.

- Open `index.html` directly in a browser for a quick preview.
- Optional local server (recommended for drag-and-drop testing): run `python3 -m http.server` then open `http://localhost:8000` in your browser.
- No automated test runner is configured.

## Coding Style & Naming Conventions
- Indentation: 2 spaces in HTML, CSS, and JS.
- JavaScript: prefer `const`/`let`, descriptive function names (`renderZones`, `validateSubmissions`), and small focused helpers.
- CSS: use kebab-case class names (e.g., `.control-panel`, `.submission-card`) and CSS variables defined in `:root`.
- File naming: lowercase with extensions (`app.js`, `style.css`).

No formatter or linter is currently configured; keep changes consistent with existing style.

## Testing Guidelines
- No tests are present and no testing framework is configured.
- If you add tests, document the chosen framework and add a short “How to run tests” section in this file.

## Commit & Pull Request Guidelines
- No commit message convention is documented in this repository. If you introduce one, update this section.
- For PRs, include:
  - A short summary of behavior changes.
  - Screenshots or screen recordings for UI changes.
  - Notes on any manual test steps performed (e.g., “Start match, set goal, issue challenge”).

## Configuration & Security Notes
- The app runs entirely in the browser and stores state in memory only.
- Avoid introducing external dependencies unless needed; if added, document install and run steps here.
