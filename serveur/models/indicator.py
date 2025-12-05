from typing import Optional
from sqlmodel import Field, SQLModel

## CETTE CLASS N'EST PAS ENCORE UTILISEE DANS LE CODE ##

class Indicator(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    host_id: Optional[int] = Field(default=None, foreign_key="host.id")
    name: str
    action_id: Optional[int] = Field(default=None, foreign_key="action.id")

    def __str__(self):
        return f"#{self.id} | Indicator {self.name} for host_id {self.host_id}"
    
    def __repr__(self):
        return f"<Indicator(id='{self.id}', name='{self.name}', host_id='{self.host_id}', action_id='{self.action_id}')>"