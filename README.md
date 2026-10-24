# Grid / Elexon wind dashboard

A small full-stack decision cockpit for comparing national UK wind generation forecasts with actuals. It is scoped to January 2026 and uses the Elexon BMRS FUELHH and WINDFOR datasets. The backend uses FastAPI and the frontend uses React, Vite, and TypeScript.

## Product pitch

The cockpit answers two questions for the day-ahead buyer:

1. What wind generation forecast was available at the purchase decision cut-off?
2. How large was the forecast error, in MW, using MAE, RMSE, bias, and WAPE?

For each 30-minute delivery interval, the API selects the latest WINDFOR forecast published by 11:00 GMT on the previous day, then joins it to the national WIND row from FUELHH. The dashboard defaults to 15 January 2026 and allows any January delivery day to be inspected.

## Repository map

- `backend/app/main.py`: FastAPI application, CORS, and health check.
- `backend/app/data_loader.py`: Elexon FUELHH/WINDFOR retrieval, day-ahead matching, cache, and offline fallback.
- `backend/app/metrics.py`: forecast KPI calculations.
- `backend/app/routes.py`: JSON API endpoints.
- `backend/tests/`: metric tests.
- `frontend/src/api.ts`: typed API client.
- `frontend/src/components/`: chart and KPI components.
- `frontend/src/App.tsx`: dashboard composition and delivery-day control.
- `docker-compose.yml`: local two-service orchestration.

AI tools were used to accelerate scaffolding, implementation, and test iteration. The Elexon data contract and day-ahead matching rule were reviewed and encoded explicitly.

## Run with Docker

```bash
docker compose up --build
```

- Dashboard: <http://localhost:3000>
- API docs: <http://localhost:8000/docs>
- Health check: <http://localhost:8000/health>

The API requests the official [FUELHH](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/FUELHH/stream) and [WINDFOR](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/WINDFOR/stream) datasets, caches valid January 2026 responses under `backend/data/`, and falls back to deterministic demo data when the upstream service is unavailable or the upstream history no longer exposes the requested January window.

## Run locally

Backend:

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Set `VITE_API_URL` to the public backend URL when deploying the frontend to Vercel. For Render, use `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.

## Deployment and submission checklist

This workspace contains the deployable application, but it does not have credentials to create a public GitHub repository, deploy to Vercel/Heroku, upload an unlisted YouTube video, or submit the Microsoft form. After pushing this directory to an anonymous public repository:

1. Deploy `backend` to Render/Heroku with `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
2. Deploy `frontend` to Vercel with `VITE_API_URL` set to the backend URL.
3. Open the deployed dashboard and `/docs` in a private/incognito window.
4. Record the two requested video sections (customer pitch and technical handover, each no more than five minutes), upload as unlisted, and paste the repository, deployment, and video URLs into the supplied form.

## Tests

```bash
cd backend
pytest
```

## Testing and verification

The backend test suite covers:

- MAE, RMSE, Bias, and WAPE calculations.
- Empty-data behavior.
- Selection of the latest eligible WINDFOR forecast before the 11:00 GMT D-1 decision gate.
- Rejection of a forecast published after that gate.

The frontend has been validated with `npm run build`, including TypeScript checking and the Vite production bundle. Vite reports a bundle-size advisory because Recharts is included in the initial bundle; this does not prevent a successful build.

Docker and Docker Compose configurations are included for standard multi-stage production builds. Docker execution could not be run in the development environment because Docker Desktop/CLI was unavailable. Manual execution is available through the backend and frontend commands above.

## Suggested 10-minute demo structure

For the required unlisted video:

1. **0:00-4:30 — Client pitch:** demonstrate the January delivery-date selector, explain the 11:00 GMT D-1 forecast gate, and interpret MAE, RMSE, Bias, WAPE, and the residual chart as procurement-risk signals.
2. **4:30-9:30 — Technical review:** show the monorepo structure, the FUELHH/WINDFOR join in `backend/app/data_loader.py`, cache-first resilience, Docker orchestration, and the cutoff-focused pytest cases.
3. **9:30-10:00 — Wrap-up:** state the deployment URLs, test result, and the known limitation that historical WINDFOR availability depends on the upstream service.

AI was used for scaffolding and iteration, not as a substitute for explaining or verifying the market-data alignment, cutoff logic, metrics, and failure behavior.
