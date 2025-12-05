from typing import Optional
from sqlmodel import Field, SQLModel,Relationship
from .entreprise import *

class Serveur(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True,index=True)
    name: str
    ip: str
    #entreprise_id: Optional[int] = Field(default=None, foreign_key="entreprise.id")
    #entreprise: Optional[Entreprise] = Relationship(back_populates="serveur")

    def __str__(self):
        return f"#{self.id} | Host {self.name} d'ip {self.ip}"
    
    def __repr__(self):
        return f"<Host(id='{self.id}', name='{self.name}', ip='{self.ip}')>"