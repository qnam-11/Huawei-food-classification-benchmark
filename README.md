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
- Node.js 20+

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

## Deploy

Set `NEXT_PUBLIC_API_URL` to the public backend URL before `npm run build`.
Without it the browser falls back to `http://localhost:8000` and every
visitor gets a `network_error`.

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
