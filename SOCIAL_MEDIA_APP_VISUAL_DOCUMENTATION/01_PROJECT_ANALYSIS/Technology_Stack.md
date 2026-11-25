# Technology Stack

## Frontend

- React 19.3.1 and React DOM 19.3.1
- React Router 7.18.5
- Axios 1.21.0
- Vite 8.3.6
- Scripts: `dev`, `build`, `lint`, `preview`; no `npm test`
- Active stylesheet: `frontend/src/index.css`; `App.css` exists but is not imported
- Service worker: `frontend/public/sw.js`, registered only in production
- Theme key: `socialconnect-theme`

## Backend

- Django 6.1
- Django REST Framework 3.18.0
- SimpleJWT 5.5.1
- Channels 4.3.2 and channels_redis 4.3.0
- Daphne 4.2.3
- django-cors-headers 4.9.0
- psycopg2-binary 2.9.12
- Pillow 12.3.0
- python-dotenv 1.2.2
- redis 8.1.0

## Runtime topology verified from source

- Browser → Vite dev server during development (default `http://localhost:5173`).
- Browser → Django HTTP API at `http://127.0.0.1:8000/api/` by default, overridable with `VITE_API_BASE_URL`.
- Browser → Django ASGI WebSockets at `ws://127.0.0.1:8000/ws/...` by default, overridable with `VITE_API_ORIGIN`.
- Django → PostgreSQL for all persistent application data and JWT blacklist tables.
- Django Channels → Redis channel layer when `REDIS_URL` is set; otherwise in-memory.
- Django admin at `/admin/` uses custom templates and static assets.

## Environment variables by name only

`DJANGO_SECRET_KEY`, `DEBUG` / `DJANGO_DEBUG`, `ALLOWED_HOSTS`, database credentials, `REDIS_URL`, `FRONTEND_URL`, CORS settings, and email settings are referenced by configuration. No values are reproduced in this package. Runtime values are `[NOT VERIFIED - USER CONFIRMATION REQUIRED]`.

## Verification tooling

- Backend: `..\venv\Scripts\python.exe manage.py check`, `makemigrations --check --dry-run`, `test --keepdb`.
- Frontend: `npm.cmd run lint`, `npm.cmd run build`.
- Visual rendering in this package: Python 3 with Pillow for PNG, hand-authored SVG for vector output, standard-library ZIP/XML for XLSX/DOCX, and a direct PDF writer. Mermaid/PlantUML source files are provided as editable diagrams; no external renderer was installed in the checkout.
