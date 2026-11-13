# Northgate KYC Copilot — Google Cloud Platform (GCP) Deployment Guide

This guide is designed for engineers who are **not GCP experts**. It provides copy-paste commands to set up continuous deployment with **Docker, GitHub Actions, and Google Cloud Run**.

---

## Architecture Overview

```
 [Git Push to main]
        │
        ▼
 ┌──────────────────────────────────────────────┐
 │          GitHub Actions CI/CD                │
 │  1. Runs 44 Pytest unit & regression tests   │
 │  2. Builds multi-stage Docker container      │
 │  3. Pushes image to Google Artifact Registry │
 │  4. Deploys container to Google Cloud Run    │
 └──────────────────────┬───────────────────────┘
                        │
                        ▼
 ┌──────────────────────────────────────────────┐
 │         Google Cloud Run (Serverless)        │
 │  - Single unified HTTPS endpoint             │
 │  - Serves React Vite UI + FastAPI backend    │
 │  - Auto-scales to zero (Free tier eligible)  │
 │  - URL: https://northgate-kyc-copilot-*.run.app │
 └──────────────────────────────────────────────┘
```

---

## Step 1: Open Google Cloud Shell (No Local Tools Required)

You do **not** need to install `gcloud` or `docker` on your local Windows PC.

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. In the top-right toolbar, click the **Activate Cloud Shell** icon (`>_`).
3. An in-browser terminal will open at the bottom of your screen with `gcloud` and `docker` already installed and authenticated.

---

## Step 2: One-Click GCP Setup Script

In the **Cloud Shell terminal**, paste the following block. Replace `YOUR_PROJECT_ID` with your actual Google Cloud Project ID:

```bash
# Set your project ID
export PROJECT_ID="YOUR_PROJECT_ID"
export REGION="asia-south1"
export SA_NAME="github-actions-deployer"

gcloud config set project $PROJECT_ID

# 1. Enable required Google Cloud APIs
echo "Enabling GCP APIs..."
gcloud services enable \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    iam.googleapis.com

# 2. Create the Docker Artifact Registry repository
echo "Creating Artifact Registry repository..."
gcloud artifacts repositories create northgate-repo \
    --repository-format=docker \
    --location=$REGION \
    --description="Docker repository for Northgate KYC Copilot" \
    || echo "Repository already exists"

# 3. Create a Service Account for GitHub Actions
echo "Creating Service Account..."
gcloud iam service-accounts create $SA_NAME \
    --display-name="GitHub Actions Deployer" \
    || echo "Service account already exists"

# 4. Grant required minimal permissions (IAM)
echo "Granting IAM roles..."
# Cloud Run Admin (to deploy service)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/run.admin"

# Artifact Registry Writer (to push container images)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/artifactregistry.writer"

# Service Account User (to run the Cloud Run service)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

# 5. Generate and download the JSON Service Account Key
echo "Generating key..."
gcloud iam service-accounts keys create ~/gcp-key.json \
    --iam-account="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

echo "============================================================"
echo "YOUR GCP SETUP IS COMPLETE!"
echo "Print your JSON key by running: cat ~/gcp-key.json"
echo "============================================================"
```

---

## Step 3: Print and Copy Your Key

In Cloud Shell, run:
```bash
cat ~/gcp-key.json
```
Copy the entire JSON output (from `{` to `}`).

---

## Step 4: Add GitHub Repository Secrets

1. Open your repository on **GitHub**.
2. Navigate to: **Settings** &rarr; **Secrets and variables** &rarr; **Actions**.
3. Click **New repository secret** and add the following two secrets:

| Secret Name | Value | Description |
|---|---|---|
| `GCP_PROJECT_ID` | `YOUR_PROJECT_ID` | Your Google Cloud project ID (e.g. `northgate-kyc-prod`) |
| `GCP_SA_KEY` | *(Paste full JSON from Step 3)* | The Service Account private key JSON |
| `GEMINI_API_KEY` *(Optional)* | `AIzaSy...` | Optional: Your live Gemini API key if you want live LLM calls instead of pre-recorded demo cache |

---

## Step 5: Push Your Code to Trigger CI/CD

On your local machine, commit and push your code to GitHub:

```bash
git add .
git commit -m "feat: setup GCP Cloud Run Docker and GitHub Actions CI/CD"
git push origin main
```

1. On GitHub, click on the **Actions** tab.
2. You will see the **Build & Deploy to Google Cloud Run** workflow running.
3. Once completed (~3–4 minutes), click the workflow to see your live URL:
   ```text
   ### 🚀 Deployment Successful!
   Service URL: https://northgate-kyc-copilot-xxxxxxxx-uc.a.run.app
   ```
4. Click the URL to open your application live on the web!

---

## Alternative: 2-Minute Direct Deploy from Cloud Shell (No GitHub Actions)

If you want to deploy right now without setting up GitHub secrets first:

1. In Google Cloud Shell, clone your repository:
   ```bash
   git clone <YOUR_GITHUB_REPO_URL>
   cd <REPO_NAME>
   ```
2. Run this single command:
   ```bash
   gcloud run deploy northgate-kyc-copilot \
       --source . \
       --region asia-south1 \
       --allow-unauthenticated \
       --port 8080
   ```
3. Cloud Run will automatically build the container and output your live HTTPS URL!

---

## Cloud Run Cost & Production Details

- **Cost**: Cloud Run is **pay-per-request**. When no one is viewing the app, it scales to **0 instances** and costs **$0.00**. The first 2 million requests each month are completely free.
- **HTTPS & SSL**: Cloud Run automatically provides managed SSL/TLS certificates and a secure HTTPS endpoint.
- **Port**: Cloud Run automatically forwards traffic to container port `8080`.
