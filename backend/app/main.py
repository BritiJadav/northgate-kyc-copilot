import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.app.config import settings
from backend.app.db import init_db
from backend.app.routers import cases, chase, admin, companies, analyst, metrics, governance

app = FastAPI(
    title="Northgate KYC Copilot API",
    description="FDE Demo Platform - Document Chaser (Module A) & Analyst Assist (Module B). SYNTHETIC DEMO DATA ONLY.",
    version="1.0.0",
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(cases.router)
app.include_router(chase.router)
app.include_router(companies.router)
app.include_router(analyst.router)
app.include_router(metrics.router)
app.include_router(governance.router)
app.include_router(admin.router)

# Ensure database tables exist on startup
@app.on_event("startup")
def on_startup():
    init_db()

# Serve static PDF and image documents for viewing and citation inspection
data_path = Path(settings.DATA_DIR)
os.makedirs(data_path, exist_ok=True)
app.mount("/documents", StaticFiles(directory=str(data_path)), name="documents")

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Northgate KYC Copilot",
        "demo_mode": settings.DEMO_MODE,
        "simulated_date": settings.SIMULATED_DATE,
        "pilot_mode": settings.PILOT_MODE,
        "synthetic_notice": "SYNTHETIC DEMO DATA - NO REAL PERSONAL DATA",
    }

# Production Single-Page-App (SPA) serving for Cloud Run / Docker
frontend_dist = Path("frontend/dist")
if not frontend_dist.exists():
    frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

if frontend_dist.exists():
    assets_dir = frontend_dist / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        target_file = frontend_dist / full_path
        if target_file.exists() and target_file.is_file():
            return FileResponse(target_file)
        return FileResponse(frontend_dist / "index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
