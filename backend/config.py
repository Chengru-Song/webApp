from pydantic import BaseSettings
from typing import List

class Settings(BaseSettings):
    app_name: str = 'Image Classification app'
    workers: List[str] = ["http://localhost:8001", "http://localhost:8002"]
    
