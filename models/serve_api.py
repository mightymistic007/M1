from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
import pandas as pd
import uvicorn
import time
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from models.pipeline import SupplyChainPipeline
    from models.prescriptive_solver import PrescriptiveSolver
except ModuleNotFoundError:
    from pipeline import SupplyChainPipeline
    from prescriptive_solver import PrescriptiveSolver

app = FastAPI(
    title="SupplyPrescript Decision API",
    description="High-performance ML inference and prescriptive optimization service",
    version="1.0.0"
)

# Initialize engines at startup
pipeline = SupplyChainPipeline()
solver = PrescriptiveSolver()

class ShipmentItem(BaseModel):
    shipping_mode: int
    type: int
    market: int
    order_region: int
    customer_segment: int
    category_name: int
    days_for_shipment_scheduled: int = Field(..., ge=0)
    order_item_quantity: int = Field(..., gt=0)
    order_item_product_price: float = Field(..., gt=0.0)
    sales: float = Field(..., gt=0.0)
    order_item_id: str = "SHIP-INSPECT"

class BatchShipmentRequest(BaseModel):
    shipments: List[ShipmentItem]

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "SupplyPrescript Engine", "version": "1.0.0"}

@app.post("/prescribe")
def prescribe_batch(request: BatchShipmentRequest):
    start_time = time.time()
    try:
        raw_data = [item.model_dump() for item in request.shipments]
        df = pd.DataFrame(raw_data)
        
        predictions = pipeline.predict_delay_risk(df)
        prescriptions = [solver.solve_shipment(pred) for pred in predictions]
        
        latency_ms = round((time.time() - start_time) * 1000, 2)
        return {
            "processed_records": len(prescriptions),
            "inference_latency_ms": latency_ms,
            "results": prescriptions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("serve_api:app", host="0.0.0.0", port=8000, reload=False)

