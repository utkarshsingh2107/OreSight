from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from . import models  # noqa: F401 - ensures models are registered before create_all
from .routers import mines, production, forecast, actions, reports

Base.metadata.create_all(bind=engine)

app = FastAPI(title="OreSight API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # demo only
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(mines.router, prefix="/api", tags=["mines"])
app.include_router(production.router, prefix="/api", tags=["production"])
app.include_router(forecast.router, prefix="/api", tags=["forecast"])
app.include_router(actions.router, prefix="/api", tags=["actions"])
app.include_router(reports.router, prefix="/api", tags=["reports"])
