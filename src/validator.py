from pydantic import BaseModel


class ConnectionInfo(BaseModel):
    database: str
    user: str
    password: str
    host: str
    port: int


class DatabaseConfig(BaseModel):
    image_name: str
    container_name: str
    connection_info: ConnectionInfo
    heartbeat: bool
