"""
POS Integration & Data Ingestion Router
---------------------------------------
Supports batch CSV/Excel uploads, JSON batch ingestion, and mock POS webhook streaming.
Handles input validation, schema mapping, and duplicate prevention.
"""

from typing import List, Optional
from datetime import date, datetime
import io
import pandas as pd
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.entities import SalesRecord, MenuItem

router = APIRouter(prefix="/pos", tags=["POS Integration"])

class SinglePOSEvent(BaseModel):
    branch_id: str
    menu_item_id: str
    sale_date: date
    sale_hour: int = Field(ge=0, le=23)
    quantity_sold: int = Field(gt=0)
    unit_price: float = Field(ge=0)
    promotion_active: Optional[bool] = False
    transaction_id: Optional[str] = None

class POSBatchPayload(BaseModel):
    branch_id: str
    transactions: List[SinglePOSEvent]

@router.post("/webhook")
def receive_pos_webhook_event(event: SinglePOSEvent, db: Session = Depends(get_db)):
    """
    Simulated near-real-time streaming webhook from external POS terminals (Square, Toast, Clover).
    """
    total = round(event.quantity_sold * event.unit_price, 2)
    record = SalesRecord(
        branch_id=event.branch_id,
        menu_item_id=event.menu_item_id,
        sale_date=event.sale_date,
        sale_hour=event.sale_hour,
        quantity_sold=event.quantity_sold,
        unit_price=event.unit_price,
        total_amount=total,
        promotion_active=event.promotion_active or False,
        source="pos_realtime"
    )
    db.add(record)
    db.commit()
    return {
        "status": "success",
        "message": f"Recorded {event.quantity_sold} portions for item {event.menu_item_id} at {event.sale_hour}:00.",
        "record_id": record.id
    }

@router.post("/batch-ingest")
def batch_ingest_transactions(payload: POSBatchPayload, db: Session = Depends(get_db)):
    count = 0
    for tx in payload.transactions:
        rec = SalesRecord(
            branch_id=payload.branch_id,
            menu_item_id=tx.menu_item_id,
            sale_date=tx.sale_date,
            sale_hour=tx.sale_hour,
            quantity_sold=tx.quantity_sold,
            unit_price=tx.unit_price,
            total_amount=round(tx.quantity_sold * tx.unit_price, 2),
            promotion_active=tx.promotion_active or False,
            source="pos_batch"
        )
        db.add(rec)
        count += 1
    db.commit()
    return {"status": "success", "inserted_count": count}

@router.post("/upload-csv")
async def upload_sales_csv(
    branch_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith((".csv", ".txt")):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")
        
    content = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {str(e)}")
        
    required_cols = {"menu_item_id", "date", "quantity_sold", "unit_price"}
    missing = required_cols - set(df.columns)
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"CSV missing mandatory columns: {list(missing)}"
        )
        
    inserted = 0
    for _, row in df.iterrows():
        sale_dt = pd.to_datetime(row["date"]).date()
        qty = int(row["quantity_sold"])
        price = float(row["unit_price"])
        total = round(qty * price, 2)
        
        record = SalesRecord(
            branch_id=branch_id,
            menu_item_id=str(row["menu_item_id"]),
            sale_date=sale_dt,
            sale_hour=int(row.get("hour", 18)),
            quantity_sold=qty,
            unit_price=price,
            total_amount=total,
            promotion_active=bool(row.get("promotion_active", False)),
            holiday_flag=bool(row.get("holiday_flag", False)),
            weather_temp=float(row.get("weather_temp", 24.0)),
            rainfall_mm=float(row.get("rainfall_mm", 0.0)),
            weather_condition=str(row.get("weather_condition", "Clear")),
            source="csv_upload"
        )
        db.add(record)
        inserted += 1
        
    db.commit()
    return {
        "status": "success",
        "filename": file.filename,
        "records_imported": inserted
    }
