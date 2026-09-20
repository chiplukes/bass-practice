# bass-practice Instructions for AI Assistants

This project is a locally-served web app for practicing bass guitar (flashcards,
song sequences, fretboard trainer, ear trainer).

### Documentation
- Check `/notes` folder for technical documentation before starting work
- See `notes/roadmap.md` for planned and future work
- See `notes/architecture.md` for the module layout and data-flow seams
- Keep durable information in long-term notes organized by topic
- Prefer "what it is" and "how it works" over debugging history in durable notes
- Keep documentation up to date with code changes

### Dev Setup (after clone or fresh pull)
- After `uv sync --extra dev`, run `uvx pre-commit install` to activate commit hooks
- This is a one-time step per clone

### Code Style
- This is a uv-managed project: use `uv run` instead of `python` directly
- Line length limit: 120 characters
- Lint with `uv run ruff check <path>`, format with `uv run ruff format <path>`

### Testing
- Domain logic in `src/bass_practice/music/` is pure Python and must stay unit-testable
- Run tests with `uv run pytest <path> --tb=short -q`
- Use verbose flags (`-v`, `--tb=long`) only when debugging specific failures

### Architecture rules
- Keep musical logic out of the API and frontend layers; put it in `music/`
- The browser owns timing and audio; the backend owns data and logic

## Gotchas and Specific Instructions
* You are the expert. Please speak up if a request does not make sense and explain why.
* **Planning**: For any task taking more than 5 minutes, first write a plan in a `/notes/plans/plan_*.md` file before touching any code. Once work is done, fold any durable findings into the appropriate reference doc and delete the plan file. If the task goes sideways, stop and re-plan immediately.
