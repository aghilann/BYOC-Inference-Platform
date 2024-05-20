from pydantic import BaseModel


class MLModel(BaseModel):
    image_url: str
    exposed_port: int
    name: str
    version: str
