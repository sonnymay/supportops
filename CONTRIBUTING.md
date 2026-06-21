# Contributing to SupportOps

Thanks for helping improve SupportOps. Small, focused pull requests are easiest to review.

## Fork and Clone

1. Fork the repo on GitHub.
2. Clone your fork:

```bash
git clone https://github.com/YOUR_USERNAME/supportops.git
cd supportops
```

3. Add the upstream repo:

```bash
git remote add upstream https://github.com/sonnymay/supportops.git
```

## Development Setup

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
uvicorn main:app --reload
```

Frontend:

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Set `VITE_API_BASE_URL=http://localhost:8000` in `frontend/.env`. Fill in the Supabase values in `backend/.env`; add `ANTHROPIC_API_KEY` only if you are testing the AI suggestion flow.

You can also run the full stack with Docker:

```bash
docker compose up --build
```

## Pull Request Process

- Create a branch named `fix/short-description`, `feature/short-description`, or `docs/short-description`.
- Keep changes focused on one bug, feature, or documentation improvement.
- Run the relevant tests or smoke checks before opening a PR.
- Link any related issue in the PR description.

PR description template:

```md
## Summary
-

## Testing
-

## Notes
-
```

## Bug Reports

Open a bug report in [GitHub Issues](https://github.com/sonnymay/supportops/issues). Include what happened, what you expected, steps to reproduce it, and any relevant screenshots or logs.
