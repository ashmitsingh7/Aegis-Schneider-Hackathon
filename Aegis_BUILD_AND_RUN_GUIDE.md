# Aegis Build And Run Guide

Created: 2026-09-11

## What Is Built

Aegis is an AI-powered decision intelligence prototype for critical electrical infrastructure. It focuses on transformer asset monitoring and demonstrates the workflow:

```text
Observe -> Predict -> Simulate -> Evaluate -> Recommend -> Explain
```

## Project Location

```bash
cd /home/singh/Aegis
```

## Built Components

### Backend

The backend is a FastAPI service in `/home/singh/Aegis/backend`.

It includes:

- Asset health prediction engine.
- Failure probability model.
- Remaining useful life model.
- Transformer digital twin simulator.
- Decision intelligence optimizer.
- REST API with Swagger documentation.

Important backend files:

- `/home/singh/Aegis/backend/main.py`
- `/home/singh/Aegis/backend/models/model_manager.py`
- `/home/singh/Aegis/backend/digital_twin/transformer.py`
- `/home/singh/Aegis/backend/decision_engine/optimizer.py`
- `/home/singh/Aegis/backend/requirements.txt`

Main API endpoints:

- `GET /health`
- `GET /assets/{asset_id}/health`
- `GET /assets/{asset_id}/telemetry`
- `POST /assets/{asset_id}/simulate`
- `POST /assets/{asset_id}/decision`
- `GET /assets/{asset_id}/summary`

Swagger UI:

```text
http://localhost:8000/docs
```

### Frontend

The frontend is a Next.js app in `/home/singh/Aegis/frontend`.

It includes:

- Dashboard command center at `/`.
- Guided demo mode at `/demo`.
- Asset detail page at `/asset/T-01`.
- Decision center at `/decision`.
- Digital twin simulation page at `/simulation`.
- Degradation sequence page at `/degradation`.
- Validation testing suite at `/validation`.

Important frontend files:

- `/home/singh/Aegis/frontend/app/page.tsx`
- `/home/singh/Aegis/frontend/app/demo/page.tsx`
- `/home/singh/Aegis/frontend/app/asset/[assetId]/page.tsx`
- `/home/singh/Aegis/frontend/app/decision/page.tsx`
- `/home/singh/Aegis/frontend/app/simulation/page.tsx`
- `/home/singh/Aegis/frontend/app/degradation/page.tsx`
- `/home/singh/Aegis/frontend/app/validation/page.tsx`
- `/home/singh/Aegis/frontend/app/layout.tsx`
- `/home/singh/Aegis/frontend/app/globals.css`

### Data And Docs

Mock data is stored in `/home/singh/Aegis/data`.

Included datasets:

- Healthy transformer telemetry.
- Degrading transformer telemetry.
- Critical transformer telemetry.
- Mock API response examples.

Documentation is stored in `/home/singh/Aegis/docs`.

Included docs:

- `/home/singh/Aegis/docs/architecture.md`
- `/home/singh/Aegis/docs/api.md`

## What Was Fixed Today

The frontend had multiple malformed generated TSX files, with errors such as:

- `Unexpected token div. Expected jsx identifier`
- Headings closed as `</div>`.
- Paragraphs closed as `</div>`.
- One route file starting in the middle of JSX.
- A remote Google font fetch blocking sandboxed builds.

Fixes completed:

- Rebuilt the broken frontend route components as valid Next.js pages.
- Added `"use client"` to pages using React state/hooks.
- Removed the `next/font/google` dependency from the root layout.
- Replaced the global CSS with a local system font stack.
- Verified the frontend production build.

## How To Run The Backend

Open a terminal:

```bash
cd /home/singh/Aegis
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cd backend
python3 main.py
```

Backend URL:

```text
http://localhost:8000
```

API docs:

```text
http://localhost:8000/docs
```

Quick health check:

```bash
curl http://localhost:8000/health
```

## How To Run The Frontend

Open a second terminal:

```bash
cd /home/singh/Aegis/frontend
npm install
npm run dev
```

Frontend URL:

```text
http://localhost:3000
```

Useful frontend routes:

```text
http://localhost:3000/
http://localhost:3000/demo
http://localhost:3000/asset/T-01
http://localhost:3000/decision
http://localhost:3000/simulation
http://localhost:3000/degradation
http://localhost:3000/validation
```

## How To Build And Validate

Frontend type check:

```bash
cd /home/singh/Aegis/frontend
npx tsc --noEmit --pretty false
```

Frontend production build:

```bash
cd /home/singh/Aegis/frontend
npm run build
```

Backend unit checks from the project root:

```bash
cd /home/singh/Aegis
python3 test_decision_engine.py
python3 test_decision_engine2.py
python3 test_weights.py
```

## Current Verification Status

Completed successfully:

- `npm run build`
- `npx tsc --noEmit --pretty false`
- Next.js dev server startup

The frontend dev server was started successfully at:

```text
http://localhost:3000
```

## Known Notes

- The rebuilt frontend pages use local demo data so the UI works reliably for presentation.
- The backend Swagger UI is available and the core health, telemetry, simulation, and summary endpoints are present.
- In `/home/singh/Aegis/backend/main.py`, the `/assets/{asset_id}/decision` endpoint contains a reference to `engine.transformer_simulator`, but `engine` is not defined in that file. If that endpoint is needed live, replace it with the existing `transformer_simulator` object or a fixed transformer rating value.

## Portable Zip Archive

The portable source archive is stored at:

```text
/home/singh/Aegis_portable_2026-09-11.zip
```

It includes the files needed for another system to install, build, run, and inspect the project:

- Backend source and requirements.
- Frontend source, public assets, package files, and lockfile.
- Mock data.
- Documentation.
- Test scripts.
- Root README, build log, and project plan.

It excludes generated or machine-local files:

- `frontend/node_modules/`
- `frontend/.next/`
- Python `__pycache__/`
- TypeScript build info.
- Local virtual environments and editor/cache files.
