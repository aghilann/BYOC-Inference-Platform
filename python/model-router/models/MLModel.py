from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime, timezone


class MLModel(BaseModel):
    image_url: str
    exposed_port: int
    name: str
    version: str
    min_replicas: Optional[int] = 1
    max_replicas: Optional[int] = 10
    description: Optional[str] = None
    created_at: Optional[str] = datetime.now(timezone.utc)
    author: Optional[str] = None
    tags: Optional[List[str]] = None
    dependencies: Optional[Dict[str, str]] = None
    input_schema: Optional[str] = None
    output_schema: Optional[str] = None
    license: Optional[str] = None
    framework: Optional[str] = None
    hyperparameters: Optional[Dict[str, str]] = None
    metrics: Optional[Dict[str, float]] = None
    endpoint: Optional[str] = None
    environment_variables: Optional[Dict[str, str]] = None
