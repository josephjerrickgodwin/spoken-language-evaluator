import logging

# !--- Configure logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from src.controller import (
    health_router,
    candidate_evaluator_router
)

app = FastAPI(
    title="Candidate English Accent Evaluator Service",
    version="v1.0.0"
)

# Accepted origins
origins = ["*"]
allowed_methods = ["*"]
allowed_headers = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=allowed_methods,
    allow_headers=allowed_headers
)

# Add routers
app.include_router(health_router)
app.include_router(candidate_evaluator_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=8080, reload=False)
