# src/noobTunerLLM/main.py

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import uvicorn

from noobTunerLLM.utils.configuration_checker import ConfigurationChecker, SystemRequirements
from noobTunerLLM.logger import logger
from noobTunerLLM.exception import FineTuningException

# Initialize FastAPI app
app = FastAPI(
    title="NoobTuner LLM",
    description="LLM Fine-Tuning Platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = Path(__file__).parent / "frontend" / "static"
templates_path = Path(__file__).parent / "frontend" / "templates"

app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Pydantic models
class SystemCheckResponse(BaseModel):
    status: str
    system_stats: dict
    checks: dict
    missing_requirements: list
    flash_attention: dict
    can_proceed: bool

# Routes for serving frontend
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the main frontend page"""
    try:
        html_file = templates_path / "pages" / "index.html"
        return HTMLResponse(content=html_file.read_text(), status_code=200)
    except Exception as e:
        logger.error(f"Error serving frontend: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# API endpoints
@app.get("/api/system-check", response_model=SystemCheckResponse)
async def check_system():
    """Check system compatibility"""
    try:
        checker = ConfigurationChecker()
        return checker.check_system_compatibility()
    except Exception as e:
        logger.error(f"Error checking system: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/install-flash-attention")
async def install_flash_attention():
    """Install Flash Attention"""
    try:
        checker = ConfigurationChecker()
        success = checker.install_flash_attention()
        return {"success": success}
    except Exception as e:
        logger.error(f"Error installing Flash Attention: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/recommended-batch-size")
async def get_batch_size():
    """Get recommended batch size"""
    try:
        checker = ConfigurationChecker()
        batch_size = checker.get_recommended_batch_size()
        return {"recommended_batch_size": batch_size}
    except Exception as e:
        logger.error(f"Error getting batch size: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def run_server():
    """Run the FastAPI server"""
    uvicorn.run(
        "noobTunerLLM.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        # reload_dirs=["src/noobTunerLLM"]
    )

if __name__ == "__main__":
    run_server()