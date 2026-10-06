from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import settings
from backend.app.database import engine, Base, SessionLocal
from backend.app.models.entities import *
from backend.app.services.seed_data import seed_database_if_empty

from backend.app.routers.health import router as health_router
from backend.app.routers.branches import router as branches_router
from backend.app.routers.demand import router as demand_router
from backend.app.routers.inventory import router as inventory_router
from backend.app.routers.waste import router as waste_router
from backend.app.routers.simulation import router as simulation_router
from backend.app.routers.alerts import router as alerts_router
from backend.app.routers.donations import router as donations_router
from backend.app.routers.sustainability import router as sustainability_router
from backend.app.routers.pos_integration import router as pos_router
from backend.app.routers.copilot import router as copilot_router

# Ensure tables exist immediately
Base.metadata.create_all(bind=engine)
_seed_session = SessionLocal()
try:
    seed_database_if_empty(_seed_session)
finally:
    _seed_session.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Production-grade AI/ML Demand Prediction, Smart Inventory Optimization, and Closed-Loop Food Waste Reduction Platform.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers under API v1
api_prefix = settings.API_V1_STR
app.include_router(health_router, prefix=api_prefix)
app.include_router(branches_router, prefix=api_prefix)
app.include_router(demand_router, prefix=api_prefix)
app.include_router(inventory_router, prefix=api_prefix)
app.include_router(waste_router, prefix=api_prefix)
app.include_router(simulation_router, prefix=api_prefix)
app.include_router(alerts_router, prefix=api_prefix)
app.include_router(donations_router, prefix=api_prefix)
app.include_router(sustainability_router, prefix=api_prefix)
app.include_router(pos_router, prefix=api_prefix)
app.include_router(copilot_router, prefix=api_prefix)

@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "docs": "/docs",
        "api_v1": api_prefix,
        "status": "online"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
