# Elvara Deployment Guide

## Architecture Overview

Elvara deploys as **two separate web services**:

1. **elvara-api** - FastAPI backend (ML model, prediction endpoint, monitoring)
2. **elvara-streamlit** - Streamlit frontend (clinical UI)

This separation allows independent scaling, deployment, and monitoring.

---

## Local Development (Docker Compose)

### Prerequisites
- Docker and Docker Compose installed
- Model file exists at `models/sepsis_model.joblib`

### Run locally
```bash
cd docker
docker-compose up --build
```

**Services available:**
- Streamlit UI: http://localhost:8501
- FastAPI backend: http://localhost:8000
- FastAPI docs: http://localhost:8000/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

### Stop services
```bash
docker-compose down
```

---

## Render Deployment

### Option 1: Blueprint (render.yaml) — Recommended

1. **Connect GitHub repo to Render**
   - Go to https://dashboard.render.com/
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Render will auto-detect `render.yaml` at root

2. **Deploy both services**
   - Render will create both `elvara-api` and `elvara-streamlit` services
   - Wait for `elvara-api` to deploy first (check logs for "Application startup complete")

3. **Configure Streamlit backend URL**
   - Once `elvara-api` is deployed, copy its public URL (e.g., `https://elvara-api.onrender.com`)
   - Go to `elvara-streamlit` service → Environment
   - Set `FASTAPI_URL` to the API URL: `https://elvara-api.onrender.com`
   - Click "Save Changes" (this will trigger a redeploy)

4. **Verify deployment**
   - Visit `https://elvara-api.onrender.com/health` → should return `{"status": "healthy", "model_loaded": true}`
   - Visit `https://elvara-streamlit.onrender.com` → UI should load
   - Submit a test prediction → should return risk assessment

---

### Option 2: Manual Service Creation

If you prefer to create services manually via Render dashboard:

#### Service 1: elvara-api (FastAPI Backend)

1. **Create Web Service**
   - Name: `elvara-api`
   - Runtime: Docker
   - Dockerfile Path: `./docker/Dockerfile.api`
   - Docker Context: `.`

2. **Environment Variables**
   ```
   MODEL_PATH=/app/models/sepsis_model.joblib
   PYTHONUNBUFFERED=1
   ```

3. **Health Check**
   - Path: `/health`

4. **Deploy** and wait for completion

#### Service 2: elvara-streamlit (Streamlit Frontend)

1. **Create Web Service**
   - Name: `elvara-streamlit`
   - Runtime: Docker
   - Dockerfile Path: `./docker/Dockerfile.streamlit`
   - Docker Context: `.`

2. **Environment Variables**
   ```
   FASTAPI_URL=https://elvara-api.onrender.com
   PYTHONUNBUFFERED=1
   ```
   ⚠️ Replace `elvara-api.onrender.com` with your actual API service URL

3. **Health Check**
   - Path: `/_stcore/health`

4. **Deploy**

---

## Environment Variables Reference

### elvara-api (FastAPI Backend)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MODEL_PATH` | No | `/app/models/sepsis_model.joblib` | Path to trained model file |
| `PYTHONUNBUFFERED` | No | `1` | Disable Python output buffering for real-time logs |

**No secrets required** - model is baked into Docker image.

---

### elvara-streamlit (Streamlit Frontend)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `FASTAPI_URL` | **YES** | `http://localhost:8000` | Full URL of the FastAPI backend service |
| `PYTHONUNBUFFERED` | No | `1` | Disable Python output buffering for real-time logs |

**Critical:** `FASTAPI_URL` must point to the deployed `elvara-api` service URL on Render.

---

## Render Configuration Notes

### Plan Recommendations
- **Starter plan** ($7/month per service, $14/month total) is sufficient for demo/pilot
- Both services can run on Starter (512MB RAM, 0.5 CPU)
- If traffic increases, scale to Standard plan ($25/month per service)

### Region Selection
- Deploy both services to the **same region** (e.g., Oregon) for lowest latency
- Render supports: Oregon, Frankfurt, Singapore, Ohio

### Auto-Deploy
- `render.yaml` sets `autoDeploy: true` for both services
- Every push to `main` branch triggers automatic deployment
- Disable in Render dashboard if you prefer manual deploys

### Health Checks
- FastAPI: `/health` endpoint returns model status
- Streamlit: `/_stcore/health` is Streamlit's built-in health endpoint
- Render will restart unhealthy services automatically

---

## Post-Deployment Checklist

- [ ] FastAPI `/health` endpoint returns 200 OK
- [ ] Streamlit UI loads at public URL
- [ ] Submit test prediction with default values
- [ ] Verify prediction result shows risk score + category
- [ ] Check FastAPI `/metrics` endpoint exposes Prometheus metrics
- [ ] (Optional) Set up Grafana Cloud to scrape metrics from `/metrics`

---

## Troubleshooting

### Streamlit shows "Failed to connect to prediction service"

**Cause:** `FASTAPI_URL` not set or incorrect

**Fix:**
1. Check `elvara-streamlit` environment variables in Render dashboard
2. Verify `FASTAPI_URL` is set to `https://elvara-api.onrender.com` (or your API URL)
3. Test API health: `curl https://elvara-api.onrender.com/health`

---

### FastAPI returns "model_loaded": false

**Cause:** Model file missing or path incorrect

**Fix:**
1. Verify `models/sepsis_model.joblib` exists in repo
2. Check Dockerfile.api copies `models/` directory: `COPY models/ ./models/`
3. Rebuild and redeploy

---

### CORS errors in browser console

**Cause:** Streamlit origin not allowed by FastAPI

**Fix:**
1. Check `app/main.py` has CORS middleware configured
2. Verify `allow_origins` includes `https://*.onrender.com`
3. Redeploy API service

---

## Updating the Model

**To deploy a new trained model:**

1. Replace `models/sepsis_model.joblib` with new model file
2. Update `models/model_metadata.json` with new metrics
3. Commit and push to trigger auto-deploy:
   ```bash
   git add models/
   git commit -m "Update model to v2.0"
   git push origin main
   ```
4. Render will rebuild Docker image with new model
5. Test `/predict-risk` endpoint after deployment

**No environment variable changes needed** - model is baked into image.

---

## Monitoring on Render

### Logs
- Access via Render dashboard → Service → Logs tab
- Real-time streaming logs for debugging
- FastAPI logs show prediction requests, model loading, errors

### Metrics
- Render provides basic CPU/memory metrics
- For custom metrics (prediction latency, etc.), scrape `/metrics` endpoint with Prometheus
- Grafana Cloud free tier can pull from Render-hosted `/metrics`

### Alerts
- Set up Render email/Slack alerts for:
  - Health check failures
  - Deployment failures
  - Service crashes

---

## Cost Estimate

**Render Starter Plan:**
- elvara-api: $7/month
- elvara-streamlit: $7/month
- **Total: $14/month**

**Additional costs:**
- None (no database, no persistent storage, no secrets manager needed)

**Free tier alternative:**
- Render offers free tier for web services (512MB RAM, spins down after inactivity)
- Not recommended for production but suitable for testing

---

## Production Hardening (Future)

For production clinical use, consider:

1. **Switch to Standard plan** ($25/month per service)
   - More RAM/CPU for concurrent users
   - No sleep on inactivity

2. **Add persistent storage** (Render Disks)
   - Store prediction logs for audit trail
   - Currently logs are ephemeral (lost on restart)

3. **Restrict CORS origins**
   - Update `app/main.py` to only allow specific Streamlit URL
   - Remove wildcard `*` from `allow_origins`

4. **Add authentication**
   - Streamlit Pages with login
   - FastAPI OAuth2/JWT tokens
   - Not currently implemented

5. **Set up monitoring**
   - Grafana Cloud for metrics visualization
   - Sentry for error tracking
   - PagerDuty/OpsGenie for alerts

6. **Database for audit logging**
   - PostgreSQL on Render ($7/month)
   - Log every prediction with timestamp, patient_id, result

---

## Support

For deployment issues:
- Check Render logs first
- Review this guide's troubleshooting section
- Verify all environment variables are set correctly
- Test locally with `docker-compose up` to isolate Render-specific issues
