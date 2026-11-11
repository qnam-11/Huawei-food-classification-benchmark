# Vietnamese Food Recognition

Upload a photo of a Vietnamese dish, pick one of the 8 trained models, and see
the dish name with its macros. Classification only: no portion estimation.

- `backend/` — FastAPI + PyTorch/timm inference service
- `frontend/` — Next.js (App Router, TypeScript, Tailwind) UI, English and Vietnamese

The models are timm backbones trained on the 30 VN30 dish classes. Each
`checkpoints/<BACKBONE>/best.pt` carries its own class list, input size and
validation score, so the app needs no extra label file.

## Requirements

- Python 3.11+ with `torch`, `timm`, `torchvision` (the `huawei-food` conda env
  has the training versions: torch 2.8.0, timm 1.0.30)
- Node.js 20.9+

## Backend

```powershell
conda activate huawei-food
cd backend
pip install -r requirements.txt
python scripts/build_registry.py     # reads the 8 best.pt files -> models.json
uvicorn app.main:app --reload --port 8000
```

Open <http://localhost:8000/docs> to try the endpoints.

Configuration lives in `backend/.env` (copy `.env.example`). The defaults are
`UNKNOWN_THRESHOLD=0.70`, `MAX_UPLOAD_MB=10`, `DEVICE=auto`.

### API

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | status, device, model count |
| GET | `/api/models` | dropdown entries from `models.json` |
| POST | `/api/predict` | `multipart/form-data`: `file`, `model_id` |

Errors use `{ "error": { "code": "..." } }` with codes `invalid_image` (400),
`file_too_large` (413), `unsupported_type` (415), `unknown_model` (422) and
`inference_failed` (500). The frontend translates the code.

### Tests

```powershell
cd backend
pytest
```

## Frontend

```powershell
cd frontend
npm install
copy .env.local.example .env.local     # NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

Open <http://localhost:3000>. The language toggle (EN / VI) is stored in
`localStorage`; the default follows the browser language.

### Access from another device (LAN)

Find the host's LAN IP with `ipconfig`, then point both sides at it:

1. `backend/.env`: add the frontend origin, for example
   `ALLOWED_ORIGINS=http://localhost:3000,http://172.16.4.212:3000`
2. `frontend/.env.local`: `NEXT_PUBLIC_API_URL=http://172.16.4.212:8000`
3. `frontend/next.config.ts`: add the hostname to `allowedDevOrigins`
   (hostname only, no scheme or port) so `next dev` serves its own assets.
4. Start the backend with `--host 0.0.0.0` so it is reachable beyond loopback.

Environment files are read at startup, so restart both servers after changing
them. `backend/.env` and `frontend/.env.local` are gitignored.

## Deploy

The backend (PyTorch plus 8 checkpoints) is larger than Vercel's serverless
limit, so it runs on a Docker host; only `frontend/` goes to Vercel. Deploy
the backend first, because the frontend needs its URL at build time.

### Backend (Hugging Face Spaces)

`backend/Dockerfile` installs CPU-only torch and serves uvicorn on port 7860.

1. Create a **Docker** Space (CPU basic) and clone it.
2. Copy the contents of `backend/` into the Space root, including
   `checkpoints/`, `models.json` and `data/vn30_foods.csv`. Do not copy
   `.gitignore`; it would silently skip the `.pt` files.
3. Track the weights with `git lfs track "*.pt"` and check that all 8 appear in
   `git lfs ls-files`.
4. Add `sdk: docker` and `app_port: 7860` to the Space's `README.md` header.
5. Set `ALLOWED_ORIGINS` to the Vercel URL (comma-separated for more than one).
   You only learn that URL in the next section, so use a placeholder now and
   update it, then restart the Space, after the frontend is live.
   `UNKNOWN_THRESHOLD`, `MAX_UPLOAD_MB` and `DEVICE` are optional.
6. Push, wait for the build, then check `https://<user>-<space>.hf.space/health`.

### Frontend (Vercel)

Vercel project settings:

- **Root Directory:** `frontend`
- **Node.js:** 20.9 or newer (also pinned in `frontend/package.json`)
- **Environment variable:** `NEXT_PUBLIC_API_URL=https://<backend-host>` for
  Production, Preview and Development

`NEXT_PUBLIC_API_URL` is baked in at build time, so redeploy after changing it.
A Vercel build without it fails on purpose instead of falling back to
`http://localhost:8000`.

CLI alternative from `frontend/`:

```powershell
npx vercel
npx vercel env add NEXT_PUBLIC_API_URL production
npx vercel --prod
```

## Add a ninth model

1. Train it in the notebooks and copy `best.pt` to
   `backend/checkpoints/<backbone>/best.pt`.
2. Add a display name in `DISPLAY_NAMES` in `backend/scripts/build_registry.py`
   (optional, the backbone name is used otherwise).
3. Run `python scripts/build_registry.py` and restart the backend.

## Known limits

- Only the 30 dish classes can be returned. Staples, proteins, fruits,
  vegetables and drinks in `data/vn30_foods.csv` are unused for now.
- Nutrition values are drafts (`verified = False`); the UI shows a badge.
- Per-serving values are `serving_g` multiplied out, not an AI estimate.
- Softmax confidence is not a true probability. `UNKNOWN_THRESHOLD` (and the
  per-model `threshold` in `models.json`) is a tunable filter. A confident wrong
  answer can still pass it. Example: the apple-pie fixture
  `backend/tests/fixtures/non_vn30.jpg` is accepted as bún bò Huế at 0.738 by
  ConvNeXt-Tiny under the default 0.70; the stricter-threshold test documents
  this limit.
- `npm audit` reports moderate advisories in the dev-only eslint chain;
  `npm audit --omit=dev` is clean.
- The checkpoints are gitignored; copy them from the training repository.
