# ContentVIP Pro

Safe campaign-management API for validating URLs and queuing internal content-workflow jobs.

> This project does not generate fake views, automate engagement, bypass platform controls, or scrape proxy lists.

## Run locally

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Example:

```powershell
curl "http://127.0.0.1:8000/api?url=https://example.com&views=2500"
```

Render can deploy this service using `render.yaml`.
