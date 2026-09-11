# Elvara Gradio UI - Comparison Prototype

**This is a comparison prototype only. It is NOT the production version.**

## Purpose

This Gradio version of the Elvara sepsis risk dashboard was built to compare user experience and functionality against the Streamlit version (`streamlit_app/`) before deciding which framework to keep for production deployment.

## Status

- ✅ Functional parity with Streamlit version
- ✅ Calls same FastAPI backend (`/predict-risk` endpoint)
- ✅ Multi-observation vitals (2 required + 1 optional)
- ✅ Multi-observation labs (1-2 observations)
- ✅ Same field mappings, gender mapping, validation logic
- ✅ Same disclaimer text
- ❌ NOT deployed to Render
- ❌ NOT intended for production use

## Production Version

**The current production version is:** `streamlit_app/app.py`

All deployment configurations (`render.yaml`, `docker-compose.yml`, Dockerfiles) reference the Streamlit version.

## Running Locally

```bash
# Ensure FastAPI backend is running
uvicorn app.main:app --host 0.0.0.0 --port 8000

# In a separate terminal, start Gradio
python gradio_app/app.py
```

**Access:** http://localhost:7860

## Testing

Test with the same known patients:

**Patient 747 (High Risk - True Sepsis):**
- Should predict ~100% / High risk
- Use vitals/labs from `test_patients_full.json`

## Differences from Streamlit

**Functional:** None - exact parity on all inputs, validation, API calls, results

**Visual:**
- Uses Gradio's native Blocks layout instead of Streamlit's custom CSS
- No custom gauge SVG (numeric score + color-coded category instead)
- Different overall aesthetic (Gradio's theme vs. custom clinical design)

## Decision Criteria

When comparing Gradio vs. Streamlit, consider:
- Clinical aesthetic fit (calm, precise, trustworthy)
- Ease of customization
- Multi-observation input UX
- Loading/error states
- Deployment complexity
- Long-term maintainability

## Next Steps

After comparison:
- **If keeping Streamlit:** Delete `gradio_app/` directory
- **If switching to Gradio:** Update deployment configs to reference `gradio_app/` instead of `streamlit_app/`

---

**This is a prototype for internal evaluation only.**
