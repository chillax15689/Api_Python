from datetime import datetime
from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, JSON



class ScanResult(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    host_id: int
    date: datetime = Field(default_factory=datetime.utcnow)
    open_ports: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    def __str__(self):
        return f"ScanResult(id={self.id}, host_id={self.host_id}, date={self.date}, open_ports={self.open_ports})"