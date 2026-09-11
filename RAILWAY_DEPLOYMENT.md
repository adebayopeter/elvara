# Railway Deployment Guide — Elvara Sepsis Prediction System

> **Migration from Render to Railway**
> This deployment replaces the existing Render infrastructure (Streamlit + FastAPI) with Railway hosting 4 services: Gradio UI, FastAPI API, Prometheus metrics, and Grafana dashboards.

---

## Overview

### Services Architecture

| Service | Type | Access | Port | Purpose |
|---------|------|--------|------|---------|
| **Gradio** | Web | **Public** | 7860 | Clinical dashboard UI (replaces Streamlit) |
| **FastAPI** | Web | Private | 8000 | ML prediction API (internal only) |
| **Prometheus** | Web | Private | 9090 | Metrics collection and storage |
| **Grafana** | Web | Private | 3000 | Monitoring dashboards (internal only) |

**Private services** communicate via Railway's internal DNS (`servicename.railway.internal`) and are not exposed to the public internet.

---

## Prerequisites

1. **Railway Account** (Hobby plan recommended - $5/month)
2. **Railway CLI** installed:
   ```bash
   npm install -g @railway/cli
   # or
   brew install railway
   ```
3. **Git repository** with all code committed
4. **Model integrity verified**: `models/sepsis_model.joblib` MD5 checksum `d8285c03e1515418423c76edf3d17c48`

---

## Pre-Deployment: Commit Gradio App

```bash
# Ensure gradio_app/ is committed
git add gradio_app/
git commit -m "Add Gradio UI for Railway migration"

# Tag for rollback reference
git tag railway-migration-v1
git push origin main --tags
```

---

## Deployment Steps

### 0. Navigate to Project Root Directory

**CRITICAL**: All Railway commands must be run from the project root directory.

```bash
# Navigate to the elvara project root
cd /path/to/elvara

# Verify you're in the correct directory (should show gradio_app/, docker/, app/, etc.)
ls -la

# You should see:
# - gradio_app/
# - docker/
# - app/
# - models/
# - monitoring/
# - requirements.txt
```

**Running `railway up` from the wrong directory will upload the wrong files and cause deployment failures.**

---

### 1. Initialize Railway Project

```bash
# Ensure you're in the project root directory
pwd  # Should show /path/to/elvara

# Login to Railway
railway login

# Create new project
railway init

# Link to your GitHub repository (recommended for auto-deploys)
# Or deploy from local directory
```

### 2. Deploy FastAPI Service

```bash
# Create FastAPI service
railway add

# Select "Empty Service"
# Name it: fastapi

# Set environment variables
railway variables set MODEL_PATH=/app/models/sepsis_model.joblib
railway variables set PYTHONUNBUFFERED=1

# Set Dockerfile path
railway variables set RAILWAY_DOCKERFILE_PATH=docker/Dockerfile.api

# Deploy from project root
railway up

# Keep this service PRIVATE (do not generate a public domain)
```

**Verify**: Check Railway dashboard logs for "Model loaded successfully" message.

---

### 3. Deploy Prometheus Service

```bash
# Create Prometheus service
railway add

# Select "Empty Service"
# Name it: prometheus
```

**Configure via Railway Dashboard:**

1. Go to `prometheus` service → **Settings** → **Source**
2. Set **Dockerfile Path**: Use official Prometheus image (or create custom Dockerfile)
3. Go to **Variables** tab, add:
   - `PROMETHEUS_CONFIG`: Copy contents of `monitoring/prometheus.yml` (or mount as volume)

4. **Add Volume for Data Persistence**:
   - Go to **Volumes** tab → **New Volume**
   - **Mount Path**: `/prometheus`
   - This persists metrics history across restarts

5. **Deploy**:
   ```bash
   # Deploy from project root
   railway up
   ```

**Keep this service PRIVATE** (no public domain).

---

### 4. Deploy Grafana Service

```bash
# Create Grafana service
railway add

# Select "Empty Service"
# Name it: grafana
```

**Configure via Railway Dashboard:**

1. Go to `grafana` service → **Variables** tab:
   ```
   GF_SECURITY_ADMIN_PASSWORD=<your-secure-password>
   GF_SERVER_ROOT_URL=http://grafana.railway.internal:3000
   ```

2. **Add Volume for Data Persistence**:
   - Go to **Volumes** tab → **New Volume**
   - **Mount Path**: `/var/lib/grafana`
   - This persists dashboards, datasources, and settings across restarts

3. **Deploy**:
   ```bash
   # Deploy from project root
   railway up
   ```

4. **Connect Grafana to Prometheus**:
   - Access Grafana via Railway dashboard's private URL
   - Go to **Configuration** → **Data Sources** → **Add data source**
   - Select **Prometheus**
   - URL: `http://prometheus.railway.internal:9090`
   - Click **Save & Test**

**Keep this service PRIVATE** for security (access via Railway dashboard only).

---

### 5. Deploy Gradio UI Service

```bash
# Create Gradio service
railway add

# Select "Empty Service"
# Name it: gradio

# Set environment variables
railway variables set FASTAPI_URL=http://fastapi.railway.internal:8000
railway variables set PYTHONUNBUFFERED=1

# Set Dockerfile path
railway variables set RAILWAY_DOCKERFILE_PATH=gradio_app/Dockerfile

# Deploy from project root
railway up

# Generate public domain
railway domain
```

**Verify**: Open the generated Railway domain (e.g., `elvara-gradio.up.railway.app`) and confirm UI loads.

---

## Environment Variables Reference

### FastAPI
```bash
MODEL_PATH=/app/models/sepsis_model.joblib
PYTHONUNBUFFERED=1
```

### Gradio
```bash
FASTAPI_URL=http://fastapi.railway.internal:8000
PYTHONUNBUFFERED=1
```

### Grafana
```bash
GF_SECURITY_ADMIN_PASSWORD=<your-secure-password>  # CHANGE THIS
GF_SERVER_ROOT_URL=http://grafana.railway.internal:3000
```

### Prometheus
- No environment variables needed
- Configuration via `monitoring/prometheus.yml` (mounted or baked into image)

---

## Volume Persistence Configuration

### Prometheus Volume
- **Mount Path**: `/prometheus`
- **Purpose**: Persists metrics time-series data across restarts
- **Size**: Start with 1GB, monitor usage via Railway dashboard

### Grafana Volume
- **Mount Path**: `/var/lib/grafana`
- **Purpose**: Persists dashboards, datasources, user settings, and SQLite DB
- **Size**: Start with 512MB

**To configure volumes via Railway Dashboard:**
1. Select service (Prometheus or Grafana)
2. Go to **Volumes** tab
3. Click **New Volume**
4. Enter mount path
5. Deploy/redeploy service

---

## Service Health Checks

Railway automatically monitors service health. Verify all services are running:

```bash
railway status
```

**Manual health checks:**

- **FastAPI**: Check Railway logs for "Model loaded successfully"
- **Gradio**: Access public domain, confirm UI renders
- **Prometheus**: Access via Railway internal dashboard, check targets at `/targets` endpoint
- **Grafana**: Access via Railway internal dashboard, verify Prometheus datasource connected

---

## Migration Validation (REQUIRED before suspending Render)

### 1. Model Integrity Check

SSH into FastAPI container via Railway dashboard and verify:

```bash
md5sum /app/models/sepsis_model.joblib
# Expected: d8285c03e1515418423c76edf3d17c48
```

### 2. End-to-End Prediction Tests

Test all 3 known patients through the **live Railway Gradio UI** (use public domain):

| Patient ID | Age | Gender | Expected Risk | Expected Category |
|------------|-----|--------|---------------|-------------------|
| 747 | 93 | Female | ~99.96% | HIGH |
| 2276 | 18 | Male | ~3.5% | LOW |
| 187 | 64 | Male | ~21% | LOW |

**How to test**:
1. Open Gradio public domain
2. Enter patient data (refer to `test_patients_full.json` for exact values)
3. Submit prediction
4. Verify risk score matches expected values (±2% tolerance)

### 3. Error Handling Tests

**Test 1: Connection Error**
```bash
# Stop FastAPI service via Railway dashboard
# Attempt prediction via Gradio
# Expected: Clear error message (not traceback)
```

**Test 2: Validation Error**
```bash
# Enter invalid temperature: 50°C (outside 34-42°C range)
# Expected: Validation error before API call
```

### 4. Monitoring Validation

**Check Prometheus is scraping FastAPI:**
1. Access Prometheus via Railway internal dashboard
2. Go to **Status** → **Targets**
3. Confirm `elvara-sepsis-service` target shows "UP"

**Check Grafana can query metrics:**
1. Access Grafana via Railway internal dashboard
2. Explore → Select Prometheus datasource
3. Query: `prediction_requests_total`
4. Confirm data appears

---

## Cost Monitoring

### Railway Hobby Plan ($5/month)

**Estimated monthly cost (24/7 operation)**:

| Service | Memory | vCPU | Estimated Monthly Cost |
|---------|--------|------|------------------------|
| FastAPI | 512MB | 0.5 | ~$0.25 |
| Gradio | 256MB | 0.25 | ~$0.10 |
| Prometheus | 512MB | 0.5 | ~$0.25 |
| Grafana | 256MB | 0.25 | ~$0.10 |
| **Total (idle)** | | | **~$0.70/month** |

**⚠️ Cost Warnings:**

1. **Actual usage depends on**:
   - Prediction request volume (FastAPI CPU spikes)
   - Prometheus scrape frequency (currently 15s)
   - Grafana dashboard refresh rates

2. **If approaching $5 limit**:
   - Reduce Prometheus scrape interval from 15s → 60s in `monitoring/prometheus.yml`
   - Set Grafana dashboard auto-refresh to 30s+ (not 5s)
   - Consider scaling down Prometheus/Grafana to 256MB if not actively monitoring

3. **Monitor usage**:
   ```bash
   railway metrics
   ```
   Or check Railway dashboard → Project → Usage

**Expected fit**: Comfortably within $5/month for low-to-moderate traffic clinical tool.

---

## Suspending Render Services (After Validation Passes)

```bash
# Only proceed after ALL validation tests pass

# Via Render dashboard:
# 1. Go to elvara-api service → Settings → Delete Service (or Suspend)
# 2. Go to elvara-streamlit service → Settings → Delete Service (or Suspend)

# Keep Render project for 1 week as rollback option before full deletion
```

---

## Troubleshooting

### Gradio shows "Connection refused" error
- **Cause**: FASTAPI_URL not set or FastAPI service not running
- **Fix**: Verify `FASTAPI_URL=http://fastapi.railway.internal:8000` in Gradio service variables

### Prometheus shows "Target Down"
- **Cause**: FastAPI not exposing `/metrics` or wrong scrape target
- **Fix**: Verify `monitoring/prometheus.yml` has `fastapi.railway.internal:8000`

### Grafana can't connect to Prometheus
- **Cause**: Wrong datasource URL
- **Fix**: Ensure datasource URL is `http://prometheus.railway.internal:9090`

### Model not loading
- **Cause**: `models/` directory not copied to Docker image
- **Fix**: Verify `docker/Dockerfile.api` has `COPY models/ ./models/`

### Metrics/dashboards lost after restart
- **Cause**: Volumes not configured
- **Fix**: Add volumes for `/prometheus` (Prometheus) and `/var/lib/grafana` (Grafana) via Railway dashboard

---

## Rollback Plan

If Railway deployment fails validation:

```bash
# Re-enable Render services via dashboard
# Or rollback git to last known good state:
git reset --hard railway-migration-v1~1
git push origin main --force
```

**Render auto-deploy** will revert to previous commit.

---

## Next Steps After Successful Migration

1. **Monitor Railway usage** for first week
2. **Set up Grafana dashboards** for:
   - Prediction request rates
   - Model latency (p50, p95, p99)
   - Prediction score distribution
   - Error rates
3. **Configure alerts** in Grafana for:
   - API downtime
   - High latency (>2s)
   - Model drift detection triggers
4. **Delete Render project** (after 1 week of stable Railway operation)

---

## Support

- **Railway Docs**: https://docs.railway.app
- **Railway CLI Help**: `railway help`
- **Project Issues**: Refer to `README.md` and `DEPLOYMENT.md` for general troubleshooting
