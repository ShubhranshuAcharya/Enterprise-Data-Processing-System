from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from app.processor import process_csv_file, get_stats
from app.database import init_db
from app.logger import logger
import os

app = FastAPI(title="Enterprise Data Processing System")

class ProcessRequest(BaseModel):
    file_path: str

@app.on_event("startup")
def startup_event():
    logger.info("Starting up application...")
    init_db()

@app.get("/", response_class=HTMLResponse)
def read_root():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"error": "index.html not found. Please ensure it is present in the root directory."}

@app.get("/stats")
def processing_stats():
    return get_stats()

@app.post("/process_sync")
def trigger_processing_sync(request: ProcessRequest):
    if not os.path.exists(request.file_path):
        return {"error": "File not found"}
    result = process_csv_file(request.file_path)
    return result

@app.post("/process")
def trigger_processing(request: ProcessRequest, background_tasks: BackgroundTasks):
    if not os.path.exists(request.file_path):
        return {"error": "File not found"}
    
    # Run processing in background to not block the API
    background_tasks.add_task(process_csv_file, request.file_path)
    return {"message": "Data processing started in the background."}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
