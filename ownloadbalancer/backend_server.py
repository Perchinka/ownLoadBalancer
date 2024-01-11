from pydantic import BaseModel

class BackendServer(BaseModel):
        host: str
        port: int