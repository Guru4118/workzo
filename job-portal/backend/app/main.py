from fastapi import FastAPI
from app.routers import ingest, admin
from app.scheduler import start_scheduler
import logging


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


app = FastAPI()

app.include_router(ingest.router)
app.include_router(admin.router)
@app.on_event("startup")
def startup_event():
    start_scheduler()
