DermaGlowAI - Run & Deploy

This repository contains a Flask app that loads a TensorFlow model and serves a simple skin analysis site.

Quick local run (Windows PowerShell):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

Docker (build & run locally):

```bash
# from project root
docker build -t dermaglowai:latest .
docker run -p 5000:5000 --rm dermaglowai:latest
```

Deploy options (recommended):

- Render.com (use a Docker web service). Ensure the `models/skin_model.keras` file is included in the repo.
- Fly.io or Railway.app (both support Docker deployments).
- Azure App Service with Docker container.

Notes:
- The container uses the official `tensorflow/tensorflow:2.21.0` base image so TensorFlow is preinstalled.
- Model file `models/skin_model.keras` must be present in the repository when building the image.
- The Docker image may be large due to TensorFlow.

If you want, I can:
- Build and test the Docker image locally for you.
- Prepare deployment steps for Render or Fly.io and a sample `render.yaml`.
- Create a GitHub repo and push (you'll need to provide remote credentials).
