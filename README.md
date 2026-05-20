# Mint Street

> *Where new money meets new ideas.*

Mint Street is a startup intelligence platform tracking funding rounds, M&A,
IPOs, policy shifts, and deep-tech developments across India and globally.
It pulls signal from trusted publishers, rewrites every story in-house, and
surfaces what matters to operators, investors, and policymakers. The stack is
React + FastAPI + MongoDB, deployed on Railway.

## Stack

- **Frontend:** React 18, Tailwind CSS
- **Backend:** FastAPI (Python 3.11+)
- **Database:** MongoDB
- **Workers:** Celery
- **Hosting:** Railway

## Local dev

Frontend:

```bash
cd frontend && yarn && yarn start
```

Backend:

```bash
cd backend && pip install -r requirements.txt && uvicorn server:app --reload
```

The frontend expects `REACT_APP_BACKEND_URL` to point at the running API.
The backend expects `MONGO_URL`, `DB_NAME`, and a handful of integration keys
(see `backend/.env.example` if present, otherwise the deployment guide).

## Editorial standards

Every article summary on Mint Street is original — rephrased in-house by our
editorial engine before publication. We always attribute the source publisher
with a link back to the original reporting. We never republish copy verbatim
and we never strip watermarks or credits from third-party imagery.

## License

© 2026 Mint Street Media Pvt Ltd. All rights reserved.
