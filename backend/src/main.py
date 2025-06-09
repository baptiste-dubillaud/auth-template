import os
import logging

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import fastapi.security
import uvicorn
  
from routers import authentication, data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

main_router = APIRouter(
    prefix=os.getenv("BACKEND_API_DEFAULT_ROUTE"),
    tags=[os.getenv("BACKEND_API_DEFAULT_ROUTE")]
)
main_router.include_router(authentication.router)
main_router.include_router(data.router)

@app.get("/", tags=["Root"])
async def read_root():
    """Root endpoint."""
    return {"message": "Welcome to the backend API!"}

app.include_router(main_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Update this to restrict origins in production
    #allow_origins=["*"],  # Update this to restrict origins in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
    #allow_headers=["*"],
)

if __name__ == "__main__":
    host = os.getenv("BACKEND_API_HOST")
    port_str = os.getenv("BACKEND_API_PORT")

    if host is None or port_str is None:
        raise ValueError("BACKEND_API_HOST and BACKEND_API_PORT must be set")
    if host == "" or port_str == "":
        raise ValueError("BACKEND_API_HOST and BACKEND_API_PORT cannot be empty")
    
    port = int(port_str)
    
    if os.getenv("ENV") != "prod":
        uvicorn.run("main:app", host=host, port=port, reload=True, log_level="info")
    else:
        uvicorn.run(app, host=host, port=port)