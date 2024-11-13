

# Contents of app.py
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import uvicorn

# Create FastAPI instance
app = FastAPI(
    title="noobtunerLLM",
    description="A simple LLM fine-tuning interface",
    version="1.0.0"
)

# Get the root directory (where app.py is located)
ROOT_DIR = Path(__file__).parent.resolve()

# Mount static files directory
app.mount(
    "/static",
    StaticFiles(directory=str(ROOT_DIR / "static")),
    name="static"
)

# Set up Jinja2 templates
templates = Jinja2Templates(
    directory=str(ROOT_DIR / "templates")
)

@app.get("/", tags=["Pages"])
async def home(request: Request):
    """
    Render the home page
    """
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "page_title": "Home"}
    )

@app.get("/dashboard", tags=["Pages"])
async def dashboard(request: Request):
    """
    Render the dashboard page
    """
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "page_title": "Dashboard"}
    )

# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint to verify the service is running
    """
    return {
        "status": "healthy",
        "service": "noobtunerLLM"
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """
    Handle 404 Not Found errors
    """
    return templates.TemplateResponse(
        "404.html",
        {"request": request},
        status_code=404
    )

@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    """
    Handle 500 Internal Server errors
    """
    return templates.TemplateResponse(
        "500.html",
        {"request": request},
        status_code=500
    )

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """
    Execute any necessary startup tasks
    """
    print("Starting noobtunerLLM service...")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Execute any necessary cleanup tasks
    """
    print("Shutting down noobtunerLLM service...")

def create_required_directories():
    """
    Create necessary directories if they don't exist
    """
    (ROOT_DIR / "static").mkdir(exist_ok=True)
    (ROOT_DIR / "static" / "css").mkdir(exist_ok=True)
    (ROOT_DIR / "static" / "js").mkdir(exist_ok=True)
    (ROOT_DIR / "static" / "images").mkdir(exist_ok=True)
    (ROOT_DIR / "templates").mkdir(exist_ok=True)

if __name__ == "__main__":
    # Create required directories
    create_required_directories()
    
    # Run the application
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=7000,
        reload=True,  # Enable auto-reload during development
        workers=1     # Number of worker processes
    )