from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.v1 import api_router
from app.config import settings
from app.core.exceptions import CodalyraException

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.exception_handler(CodalyraException)
def codalyra_exception_handler(request: Request, exc: CodalyraException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


app.include_router(api_router)
