import os

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import msal
import requests

router = APIRouter(
    prefix="/entra_id",
    tags=["Entra ID"]
)