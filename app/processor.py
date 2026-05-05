import csv
from pydantic import ValidationError
from app.models import Record
from app.database import get_db_connection
from app.logger import logger
import time
import os

processing_state = {
    "status": "idle",
    "total_processed": 0,
    "valid_records": 0,
    "invalid_records": 0,
    "elapsed_time": 0.0,
    "is_processing": False,
    "start_time": None
}

def get_stats():
    if processing_state["is_processing"] and processing_state.get("start_time"):
        processing_state["elapsed_time"] = time.time() - processing_state["start_time"]
    return processing_state

def process_csv_file(file_path: str, batch_size: int = 1000):
    global processing_state
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return {"error": "File not found"}
        
    logger.info(f"Starting data processing from {file_path}")
    start_time = time.time()
    
    processing_state.update({
        "status": "processing",
        "total_processed": 0,
        "valid_records": 0,
        "invalid_records": 0,
        "start_time": start_time,
        "elapsed_time": 0.0,
        "is_processing": True
    })
    
    valid_records = []
    
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            processing_state["total_processed"] += 1
            try:
                # Validation Workflow
                record = Record(**row)
                valid_records.append(record)
                processing_state["valid_records"] += 1
            except ValidationError as e:
                processing_state["invalid_records"] += 1
                logger.debug(f"Validation failed for record id {row.get('id', 'Unknown')}")
            
            if len(valid_records) >= batch_size:
                _save_batch(valid_records)
                valid_records = []
                # Slight sleep to allow UI to visually show progress
                time.sleep(0.2)
                
        # Save remaining
        if valid_records:
            _save_batch(valid_records)
            
    end_time = time.time()
    processing_state.update({
        "status": "completed",
        "is_processing": False,
        "elapsed_time": end_time - start_time
    })
    
    logger.info(f"Processing completed in {end_time - start_time:.2f} seconds.")
    logger.info(f"Total processed: {processing_state['total_processed']}, Valid: {processing_state['valid_records']}, Invalid: {processing_state['invalid_records']}")
    
    return {"total": processing_state["total_processed"], "valid": processing_state["valid_records"], "invalid": processing_state["invalid_records"]}

def _save_batch(records: list[Record]):
    # Transaction Workflow
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("BEGIN TRANSACTION;")
            
            for record in records:
                cursor.execute(
                    """
                    INSERT INTO records (id, name, email, amount, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        name=excluded.name,
                        email=excluded.email,
                        amount=excluded.amount,
                        status=excluded.status,
                        created_at=excluded.created_at
                    """,
                    (record.id, record.name, record.email, record.amount, record.status, record.created_at.isoformat())
                )
            
            conn.commit()
            logger.info(f"Successfully committed batch of {len(records)} records.")
        except Exception as e:
            conn.rollback()
            logger.error(f"Transaction failed, rolling back batch. Error: {e}")
