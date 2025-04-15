import os

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import msal
import requests
  
from routers import auth, data

app = FastAPI()

main_router = APIRouter(
    prefix=os.getenv("BACKEND_API_DEFAULT_ROUTE"),
    tags=[os.getenv("BACKEND_API_DEFAULT_ROUTE")]
)
main_router.include_router(auth.router)
main_router.include_router(data.router)

app.include_router(main_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Update this to restrict origins in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
)

if __name__ == "__main__":
    host = os.getenv("BACKEND_API_HOST")
    port = int(os.getenv("BACKEND_API_PORT"))

    if host is None or port is None:
        raise ValueError("BACKEND_API_HOST and BACKEND_API_PORT must be set")
    if host == "" or port == "":
        raise ValueError("BACKEND_API_HOST and BACKEND_API_PORT cannot be empty")
    
    if os.getenv("ENV") != "prod":
        uvicorn.run(app, host=host, port=port, reload=True)
    else:
        uvicorn.run(app, host=host, port=port)